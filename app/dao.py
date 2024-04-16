from model import Dato
from crypto import Crypto
import os

import base64

class UserDao:
    USER_INDEX = "user"
    DOC_SOURCE = "_source"
    HITS = "hits"
    ID = "_id"

    def __init__(self, es):
        self.__es = es

    def insert_user(self, user:Dato):
        # 1. Genero la DEK para encriptar los datos
        data_encryption_key = Crypto.random_bytes(Crypto.AES_KEY_SIZE)

        # 2. Encripto los datos usando la DEK
        encrypted_user_cc, cc_tag, cc_nonce = Crypto.encrypt(bytes(user.credit_card_num, "ascii"), data_encryption_key)
        encrypted_user_ccv, ccv_tag, ccv_nonce = Crypto.encrypt(bytes(user.credit_card_ccv, "ascii"), data_encryption_key)
        encrypted_user_acc, acc_tag, acc_nonce = Crypto.encrypt(bytes(user.cuenta_numero, "ascii"), data_encryption_key)

        # 3. Base64Encode data encriptada en conjunto con su tag(MAC) y nonce.

        # CC
        b64_encrypted_user_cc = base64.b64encode(encrypted_user_cc).decode("ascii")
        b64_cc_tag = base64.b64encode(cc_tag).decode("ascii")
        b64_cc_nonce = base64.b64encode(cc_nonce).decode("ascii")
        
        # CCV        En cuanto al CCV, deje todo el proceso listo para hashearlo, la función hash_secret y verify_secret sirven para esto
        #            Lo hice porque es una buena práctica solo guardar el hash y checkear vs el, pero para poder devolver el json inicial en este caso
        #            solo lo estoy encriptando y guardando como a los otros datos sensibles.

        b64_encrypted_user_ccv = base64.b64encode(encrypted_user_ccv).decode("ascii")
        b64_ccv_tag = base64.b64encode(ccv_tag).decode("ascii")
        b64_ccv_nonce = base64.b64encode(ccv_nonce).decode("ascii")
    
        # ACC
        b64_encrypted_user_acc = base64.b64encode(encrypted_user_acc).decode("ascii")
        b64_acc_tag = base64.b64encode(acc_tag).decode("ascii")
        b64_acc_nonce = base64.b64encode(acc_nonce).decode("ascii")

        # 4. Generamos la KEK, que usamos para encriptar la DEK.
        kek_salt = Crypto.random_bytes(Crypto.SALT_LENGTH)
        master_key_username = user.user_name + os.environ.get("MASTER_KEY")
        key_encryption_key = Crypto.key_derivation_function(master_key_username, kek_salt)  
        #           Al generar la KEK, lo hago utilizando el user_name, pero también 
        #           concateno una llave maestra del equipo correspondiente que va a des-encriptar esta data
        #           esto agrega el control de que, por mas que un atacante tuviera acceso a la data y al código, no podría desencriptar.

        # 5. Encriptamos la DEK con la KEK.
        encrypted_dek, dek_tag, dek_nonce = Crypto.encrypt(data_encryption_key, key_encryption_key)

        # 6. Base64Encode the encrypted DEK, tag, and nonce.
        b64_encrypted_dek = base64.b64encode(encrypted_dek).decode("ascii")
        b64_dek_tag = base64.b64encode(dek_tag).decode("ascii")
        b64_dek_nonce = base64.b64encode(dek_nonce).decode("ascii")

        # 7. Hash the ccv         ## Este dato sería utilizado en el caso que mencioné previamente donde no storeamos el ccv encriptado de forma reversible sino solo para chequear
        hashed_ccv = Crypto.hash_secret(user.credit_card_ccv).decode("ascii")        

        # 8. Base 64 Encode the KEK salt        
        b64_kek_salt = base64.b64encode(kek_salt).decode("ascii")

        # 9. Store the document in Elasticsearch.
        resp = self.__es.index(index="user", id=user.id, document={
            "id" : int(user.id),
            "fec_alta" : user.fec_alta,
            "username" : user.user_name,
            "hash_ccv" : hashed_ccv,
            "code_zip" : user.codigo_zip, 
            "cc" : b64_encrypted_user_cc,
            "cc_tag": b64_cc_tag,
            "cc_nonce" : b64_cc_nonce,
            "ccv" : b64_encrypted_user_ccv,
            "ccv_tag" : b64_ccv_tag,
            "ccv_nonce" : b64_ccv_nonce,
            "cuenta_numero" : b64_encrypted_user_acc,
            "cuenta_tag" : b64_acc_tag,
            "cuenta_nonce" : b64_acc_nonce,
            "direccion" : user.direccion,
            "geo_latitud" : user.geo_latitud,
            "geo_longitud" : user.geo_longitud,
            "color_favorito" : user.color_favorito,
            "foto_dni" : user.foto_dni,
            "ip" : user.ip,
            "auto" : user.auto,
            "auto_modelo" : user.auto_modelo,
            "auto_tipo" : user.auto_tipo,
            "auto_color" : user.auto_color,
            "cantidad_compras_realizadas" : user.cantidad_compras_realizadas,
            "fec_birthday" : user.fec_birthday,
            "avatar" : user.avatar,
            "dek" : b64_encrypted_dek,
            "dek_tag" : b64_dek_tag,
            "dek_nonce" : b64_dek_nonce,
            "kek_salt" : b64_kek_salt
        })
        return resp
    
    # Fetch the user object when they login.
    def get_user_decrypted(self, username):
        # 1. Fetch the user document.
        user_hit = self.__get_user_by_username(username)
        user_doc = None

        if user_hit is not None:
            user_doc = user_hit
        else:
            return (None, None)

        # 2. Extract the kek salt and base 64 decode it.
        b64_kek_salt = user_doc["kek_salt"]
        kek_salt = base64.b64decode(b64_kek_salt)

        # 3. Regenerate the key encryption key.
        master_key_username = username + os.environ.get("MASTER_KEY")
        key_encryption_key = Crypto.key_derivation_function(master_key_username, kek_salt)

        # 4. Decrypt the DEK.
        dek = self.__decrypt_dek(user_doc, key_encryption_key)

        decrypted_ccv = self.__decrypt_std(user_doc["ccv"],user_doc["ccv_nonce"],user_doc["ccv_tag"], dek)
        decrypted_cc = self.__decrypt_std(user_doc["cc"],user_doc["cc_nonce"],user_doc["cc_tag"], dek)
        decrypted_acc = self.__decrypt_std(user_doc["cuenta_numero"],user_doc["cuenta_nonce"],user_doc["cuenta_tag"], dek)

        # Save
        user = Dato(
            user_doc["id"],
            user_doc["fec_alta"],
            user_doc["username"],
            user_doc["code_zip"],
            decrypted_cc.decode("ascii"),
            decrypted_ccv.decode("ascii"),
            decrypted_acc.decode("ascii"),
            user_doc["direccion"],
            user_doc["geo_latitud"],
            user_doc["geo_longitud"],
            user_doc["color_favorito"],
            user_doc["foto_dni"],
            user_doc["ip"],
            user_doc["auto"],
            user_doc["auto_modelo"],
            user_doc["auto_tipo"],
            user_doc["auto_color"],
            user_doc["cantidad_compras_realizadas"],
            user_doc["avatar"],
            user_doc["fec_birthday"],
        )

        # 8. Return the user object and KEK. Note: The KEK should be stored in the user session.
        return (user)


    def __get_user_by_username(self, username):
        # Query for the user document.
        response = self.__es.search(index=self.USER_INDEX, query={
            "match": {"username.keyword": username}
        })
        
        hits = response.get(self.HITS, {}).get(self.HITS, [])
        
        if not hits:
            return None
        
        return hits[0].get(self.DOC_SOURCE)

        
    def __decrypt_dek(self, user_doc, kek):
        # 4. Fetch the base 64 encoded and encrypted DEK and tag and nonce, and base 64 decode them.
        b64_encrypted_dek = user_doc["dek"]
        b64_dek_tag = user_doc["dek_tag"]
        b64_dek_nonce = user_doc["dek_nonce"]

        encrypted_dek = base64.b64decode(b64_encrypted_dek)
        dek_tag = base64.b64decode(b64_dek_tag)
        dek_nonce = base64.b64decode(b64_dek_nonce)

        # 5. Decrypt the DEK
        dek = Crypto.decrypt(encrypted_dek, dek_nonce, dek_tag, kek)
        return dek
    
    # Funcion para desencriptar standard values

    def __decrypt_std(self, encrypted, nonce, tag, dek):
        
        # 6. Base64 decode the encrypted value, nonce, and tag.
        encrypted = base64.b64decode(encrypted)
        nonce = base64.b64decode(nonce)
        tag = base64.b64decode(tag)

        # 7. decrypt the data and return the decrypted value.
        decrypted_value = Crypto.decrypt(encrypted, nonce, tag, dek)

        return decrypted_value
    

    def get_all_users(self):

        # Get max ID
        res = self.__es.search(index=self.USER_INDEX, size=0, aggregations={"max_id": {"max": {"field": "id"}} })        
        max_id = int(res['aggregations']['max_id']['value'])
        
        users = []

        # Loop from first to max
        for id in range(1, max_id+1): 
            user = self.__es.get(index=self.USER_INDEX, id=str(id))['_source']
            users.append(user)
        return users
    
    def __get_user_by_id(self, user_id):
        # Query for the user document by ID.
        response = self.__es.get(index=self.USER_INDEX, id=user_id)
        
        if not response:
            return None
        
        # Get the user document source.
        user_doc = response.get("_source")
        
        return user_doc