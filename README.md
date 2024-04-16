
### Preparations

Clone all the contents, make sure to have docker and docker compose installed, in my case i have `Docker version 26.0.1`

Run the following
`docker compose build`
`docker compose up`

Cuando empiece a levantar kibana, ya podemos ir conectandonos al nodo de la app.

### Using App

Desde otra terminal, acceder al nodo que contiene el python script > 
`docker exec -it app-python-1 /usr/bin/bash`  // Tener en cuenta que app es el nombre de la carpeta donde yo tenía la app, puede variar en otro caso.

Correr el script
`python main.py`
Interactuar con la app para llenar la base de datos con la información encriptada (opción 1)

### Consuming data

http://localhost:5601/
Login con elastic:passworld

Desde la app de kibana, cada equipo podrá generar las búsquedas pertinentes sobre la información, más los datos crediticios quedarán encriptados.

![Pasted image 20240416110202](https://github.com/frosimanuel/meli-challenge/assets/31355296/f7c6e5db-8ae2-4d9c-b4c8-b228b8e90a0b)

- _Disclaimer_: La conexion con kibana no está seteada con https, pero solo no lo hice por la complicación de compartir el certificado generado por elasticsearch que si se usa para la carga y descarga de la información.

### Acceder a información encriptada

Para acceder a la información encriptada, usamos la opción 3 de la python app.
Algo a tener en cuenta, es que para poder desencriptar correctamente vamos a necesitar la MASTER_KEY que en este caso para simplificar está como una variable de entorno, esta key debería ser guardada de forma segura luego de generar la carga de la información, de esta forma, por más que alguien accediera a la información y ADEMAS también accediera al código fuente de la app, no podría desencriptar los datos. 
El equipo que quisiera consumir esta información sensible, tendría que declarar esta variable antes de utilizar la opción 3 de nuestra app.

Se puede hacer la prueba de que al comentar o modificar dicha variable en el archivo .env, ya no podemos traer la data.


![Pasted image 20240416131809](https://github.com/frosimanuel/meli-challenge/assets/31355296/4a0c9a18-6e42-499c-9b21-670702f28a06)


## Troubleshooting
### vm.max_map_count

If getting this error, need to modify max mapping mem, in ubuntu run the following
````bash
sysctl -w vm.max_map_count=262144
````

### Cert 

- inside the container
`/usr/share/elasticsearch/config/certs/ca/ca.crt`
- inside local machine (as root)
`/var/lib/docker/volumes/test_certs/_data/ca/ca.crt`
for running python locally
```bash
sudo cp /var/lib/docker/volumes/test_certs/_data/ca/ca.crt ./ca.crt
```

