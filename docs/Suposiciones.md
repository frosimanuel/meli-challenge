### GET inicial

- El link de donde tomamos la información https://62433a7fd126926d0c5d296b.mockapi.io/api/v1/usuarios es un secreto.

### Dockerfile

- Al ser la dockerización un opcional, asumo que no tengo que cubrir aspectos de hardening en los containers.
- El mismo puede contener secretos así como también el `.env`, en el escenario real estos serían manejados con keystores/trustores.

### Database

- No hace falta normalizar la información, las vistas y los consumos de las mismas serán organizadas por los equipos desde elasticsearch con todas las herramientas que kibana provee para esto.

### Recover of information

- Cuando dice `deberás disponibilizar esta información para que distintos equipos y aplicaciones de la empresa puedan consumirlos, teniendo en cuenta cada uno de los atributos que vienen desde este proveedor.` , me imaginé una api de consultas, pero al utilizar elasticsearch toda la disponibilización queda en kibana para que el disponibilizador de la data haga que cada equipo se genere las descargas necesarias y hasta pueda tomar métricas e info. Esto lo hice en particular por la naturaleza de la información.
- No todos los equipos deberían poder consumir la información encriptada.

### Encryption and Data sensibility

- A la hora de definir el método de encripción, entiendo que un AES-CBC hubiera sido más rápido y su simpleza hubiera cubierto el objetivo de este ejercicio, pero me gustó agregarle la vuelta de rosca de AES-GCM ya que es más utilizado en el mundo blockchain por ejemplo Litecoin lo usa para definir la dificultad de sus bloques. Las diferencias entre estos algoritmos y los pros que trae utilizar GCM están bastante bien descriptos en [este post](https://www.linkedin.com/posts/max-g-4b508a34_cbc-vs-gcm-the-main-difference-between-cipher-activity-7093298543620149248-h0jM/).
- A la hora de seleccionar qué datos deberían estar encriptados, la consigna menciona a tener en cuenta PCI DSS, NIST, LGPD, las cuales solo hacen referencia a la obligación de encriptar la información crediticia por lo que me limité a encriptar esa información.
