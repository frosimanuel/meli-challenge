from model import Dato
from dao import UserDao
import json
import requests
from elasticsearchdb import ElasticsearchDb
from datetime import datetime
from dotenv import load_dotenv
import os

def get_users():
    response = requests.get(os.environ['API_URL'], timeout=10)
    response.raise_for_status()
    users = response.json() #Borro user 0 porque tiene mal la fecha desp arreglarlo
    users[0]["fec_alta"] = "2022-01-11T00:00:00.001Z"
    # Normalizamos las fechas
    for user in users:
        user['fec_birthday'] = datetime.fromisoformat(user['fec_birthday'][:-1])
        user['fec_birthday'] = user['fec_birthday'].strftime('%Y-%m-%d %H:%M:%S')
        user['fec_alta'] = datetime.fromisoformat(user['fec_alta'][:-1])
        user['fec_alta'] = user['fec_alta'].strftime('%Y-%m-%d %H:%M:%S')
    return users

def get_user_dao():    
    esdb = ElasticsearchDb(os.environ.get("ELASTIC_HOST"), 9200, 
        protocol="https",  
        ca_certs=os.environ.get("CERT_PATH"),
        username="elastic",
        password=os.environ.get("ELASTIC_PASSWORD")
    )

    es = ElasticsearchDb.elasticsearch.fget(esdb)
    userDao = UserDao(es)
    return userDao

def insert_and_encrypt_all():
    users = get_users()
    for user in users:
        user_data = Dato(
        user['id'], 
        user['fec_alta'], 
        user['user_name'], 
        user['codigo_zip'],
        user['credit_card_num'],
        user['credit_card_ccv'],
        user['cuenta_numero'],
        user['direccion'],
        user['geo_latitud'],
        user['geo_longitud'], 
        user['color_favorito'],
        user['foto_dni'],
        user['ip'],
        user['auto'],
        user['auto_modelo'],
        user['auto_tipo'],
        user['auto_color'],
        user['cantidad_compras_realizadas'],
        user['avatar'],
        user['fec_birthday'])
        es_response = register_new_user(user_data)
        print(es_response)

def insert_and_encrypt_one():
    user = get_users()[2]
    user_data = Dato(
    user['id'], 
    user['fec_alta'], 
    user['user_name'], 
    user['codigo_zip'],
    user['credit_card_num'],
    user['credit_card_ccv'],
    user['cuenta_numero'],
    user['direccion'],
    user['geo_latitud'],
    user['geo_longitud'], 
    user['color_favorito'],
    user['foto_dni'],
    user['ip'],
    user['auto'],
    user['auto_modelo'],
    user['auto_tipo'],
    user['auto_color'],
    user['cantidad_compras_realizadas'],
    user['avatar'],
    user['fec_birthday'])
    es_response = register_new_user(user_data)
    print(es_response)

def register_new_user(user:Dato):
    userDao = get_user_dao()
    resp = userDao.insert_user(user)
    return resp

def get_user_decrypted(username:str):
    userDao = get_user_dao()
    resp = userDao.get_user_decrypted(username)
    return resp


def main():
    load_dotenv()

    print("\n - Hello user, what do you want to do? :D\n")
    print("1. Populate the database with the encrypted data")
    print("2. Get the decrypted data from the database for a giver username")
    print("3. Get all decrypted users from the database\n")
    print("*------------#---------------#--------------#-------------------*\n")
    intent = input(" - now, enter your intention: ")
    if intent == "1":
        insert_and_encrypt_all()
        
    elif intent == "2":
        usernameRequested = input("enter username: ")
        user = get_user_decrypted(usernameRequested)
        print(vars(user))
        
    elif intent == "3":
        users = get_user_dao().get_all_users()
        json_users = []
        for user in users:
            user = get_user_decrypted(user["username"])
            json_users.append(vars(user))
        print(json.dumps(json_users, indent=4))
    
            
main()