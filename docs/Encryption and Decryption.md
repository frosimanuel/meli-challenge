### Encriptado

Para alamcenar de forma segura la información sensible >

1. **Generar la DEK**: Sigue siendo necesario generar una clave de datos aleatoria (DEK) para cifrar los datos sensibles, para esta usamos la función de la libraría Crypto que es más segura que la función random normal.
2. **Cifrar los datos sensibles con la DEK**: Utiliza la DEK generada en el paso anterior para cifrar los datos sensibles.
3. **Codificar en Base64 los datos cifrados**: Codifica en Base64 los datos cifrados para su almacenamiento seguro.
4. **Generar la KEK con la contraseña del usuario, la master key y la sal aleatoria**: Generamos la KEK, que sirve para encriptar la DEK del paso 1, a esta le agregamos un valor ageno a la app para generar más seguridad.
5. **Cifrar la DEK con la KEK**: Utiliza la KEK generada en el paso anterior para cifrar la DEK antes de almacenarla en la base de datos. 
6. **Codificar en Base64 la DEK cifrada**: Como en los pasos anteriores, codifica en Base64 la DEK cifrada para su almacenamiento seguro en la base de datos.
7. **Codificar en Base64 la sal de la KEK**: Encodeamos b64 y storeamos.
8. **Almacenar en ElasticSearch**: Guarda todos los datos cifrados, la sal y otros metadatos necesarios en la base para la recuperación posterior.

### Desencriptado

1. **Fetch user**: Nos traemos el registro que vamos a desencriptar de la base.
2. **Extraer KEK salt**: De este registro vamos a desencodear la kek_salt.
3. **Regeneramos la KEK**: Para esto utilizamos esta salt desencodeada, el username del registro y también la master-key en la KDF.
4. **B64 decode campos**: Para cada campo que queramos desencriptar desencodeamos `campo|tag|nonce` empezando por la DEK.
5. **Decrypt DEK con la KEK**: Usamos la ya generada KEK, para poder conseguir la DEK que usaremos para repetir este mismo proceos en todos los campos.
6. **Decrypt fields con DEK**: Ya teniendo la DEK, la usamos para desencriptar cada campo utilizando el mismo formato previo `campo|tag|nonce` luego de haberlo b64decode.
7. Luego creamos nuestro dato con lo campos ya desencriptados.