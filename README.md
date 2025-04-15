
# Meli Challenge – Secure User Data Ingestion and Encryption App

## Overview

This application is designed to securely ingest, encrypt, store, and retrieve user data, with a strong emphasis on protecting sensitive information such as credit card numbers, CCVs, and bank account numbers. The app leverages Python, Docker, Elasticsearch, and Kibana, and implements robust cryptographic techniques to ensure data confidentiality and integrity.

## Technical Architecture

### Main Components

- **Python Application** (in `app/`): Handles data ingestion, encryption/decryption, and communication with Elasticsearch.
- **Elasticsearch**: Stores user records, including encrypted sensitive fields.
- **Kibana**: Provides a UI for querying and visualizing user data (excluding sensitive fields, which remain encrypted).
- **Docker**: Used to orchestrate the Python app, Elasticsearch, and Kibana for reproducible, isolated deployments.

### Core Workflow

1. **Data Ingestion**:
   - The app fetches user data from an external API (URL specified in `.env`).
   - Dates are normalized for consistency.

2. **Encryption Process**:
   - For each user, a Data Encryption Key (DEK) is generated.
   - Sensitive fields (`credit_card_num`, `credit_card_ccv`, `cuenta_numero`) are encrypted using AES-256 in EAX mode with the DEK.
   - Encrypted data, along with associated tags and nonces, are Base64-encoded for storage.
   - A Key Encryption Key (KEK) is derived using the user's username concatenated with a master key (environment variable) and a random salt, via the scrypt KDF.
   - The DEK is encrypted with the KEK, and all components (encrypted data, encrypted DEK, tags, nonces, salts) are stored in Elasticsearch.

3. **Data Storage**:
   - All user records, with encrypted sensitive fields, are indexed in Elasticsearch under the `user` index.

4. **Data Retrieval & Decryption**:
   - To access sensitive data, the app requires the correct `MASTER_KEY` environment variable.
   - The app retrieves the encrypted DEK and decrypts it using the KEK (derived as above).
   - It then uses the DEK to decrypt sensitive fields and reconstruct the original user data.
   - If the `MASTER_KEY` is missing or incorrect, decryption fails, ensuring data remains protected.

5. **Kibana Integration**:
   - Kibana is used for querying and visualizing user data. Sensitive fields remain encrypted and are not directly visible.

### Security Features

- **Field-level Encryption**: Only sensitive fields are encrypted, allowing non-sensitive data to be queried and analyzed without risk.
- **Per-user Encryption Keys**: Each user's sensitive data is encrypted with a unique DEK, itself encrypted with a KEK derived from a master key and username.
- **Environment-based Master Key**: The master key is never stored in code or in the database, only as an environment variable, and should be securely managed.
- **Hashing Option for CCV**: The app includes functions to hash and verify the CCV field, supporting best practices for storing non-reversible secrets.

### Additional Documentation

- `docs/Encryption and Decryption.md`: Deep dive into the cryptographic approach.
- `docs/Input Data.md`: Describes the structure and source of the input data.
- `docs/Analisis de riesgo.md`: Risk analysis for the solution.
- `docs/Suposiciones.md`: Assumptions made during development.

### Running the App

- The app is containerized; see below for Docker usage and environment setup.
- Data can be ingested and encrypted via the Python CLI (`main.py`), and decrypted only with the correct master key.

---

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
