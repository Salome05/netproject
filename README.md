# NetProject — MQTT, PostgreSQL, Docker Compose y TLS

Este repositorio integra los Laboratorios 3 y 4, enfocados en construir una arquitectura para recibir datos mediante MQTT, procesarlos con un cliente en Python y almacenarlos en PostgreSQL. En el Laboratorio 3 se implementa la comunicación básica entre Mosquitto, el cliente Python y PostgreSQL. El flujo consiste en publicar datos en un tópico MQTT, recibirlos desde el cliente y almacenarlos posteriormente en la base de datos.

El cliente Python actúa como intermediario entre MQTT y PostgreSQL. Para la comunicación con Mosquitto utiliza Paho MQTT y para la conexión con la base de datos utiliza las credenciales definidas en variables de entorno.

Las credenciales no se almacenan directamente en el código. Por esta razón, después de clonar el repositorio es necesario crear manualmente un archivo . env en la raíz del proyecto con las variables correspondientes a PostgreSQL y MQTT. Este archivo no se encuentra en GitHub y está excluido mediante .gitignore.

Durante el Laboratorio 3 también se trabajó con la disponibilidad de los servicios. Debido a que PostgreSQL y Mosquitto pueden tardar algunos segundos en estar listos después de iniciar sus contenedores, se utilizó un mecanismo de espera para evitar que el cliente intentara conectarse antes de tiempo. 

El Laboratorio 4 mantiene el mismo flujo de recepción y almacenamiento, pero agrega mecanismos de seguridad y administración. La principal modificación corresponde al uso de TLS para proteger la comunicación MQTT. Para utilizar TLS se genera una autoridad certificadora local y un certificado para Mosquitto mediante OpenSSL. Estos archivos no están incluidos en el repositorio, por lo que deben ser creados localmente después de clonar el proyecto.
Otros de los archivos que se necesitan son las carpetas broker/ca_certs y broker/certs ya que dentro de ellas se generan la clave y el certificado de la autoridad certificadora, además de la clave privada y el certificado del servidor Mosquitto. El certificado del broker debe incluir como nombres válidos mosquitto, localhost y 127.0.0.1, ya que el servicio puede ser accedido desde otros contenedores o desde la máquina anfitriona.

Las claves privadas y certificados sensibles no deben subirse al repositorio. Por esta razón, las carpetas de certificados y los archivos .key deben permanecer incluidos dentro de .gitignore. Como Mosquitto se ejecuta dentro de un contenedor, los certificados creados en la máquina anfitriona se hacen visibles mediante bind mounts. Esto permite que el broker utilice los archivos TLS sin necesidad de almacenarlos dentro de la imagen.

En el Laboratorio 4 también se utiliza Docker Compose para administrar conjuntamente PostgreSQL, Mosquitto y el cliente Python. Los servicios se comunican mediante la red interna appnet, lo que permite utilizar los nombres mosquitto y postgres en lugar de depender de direcciones IP internas, ademas a diferencia del 3 Laboratorio, se incorporaron healthchecks para comprobar que los servicios realmente estén preparados antes de iniciar el cliente. PostgreSQL utiliza una comprobación de disponibilidad propia, mientras que Mosquitto verifica sus puertos mediante Netcat.
Como resultado final se debe poder realizar publicaciones de mosquitto, recibirlas en el suscriptor y que estas queden almacenadas en la base de datos de postgres

El resultado esperado es que un mensaje publicado en `sensors/temp` sea recibido por Mosquitto mediante una conexión segura, procesado por el cliente Python y almacenado correctamente en PostgreSQL.
