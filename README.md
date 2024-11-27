# Despliegue de la Aplicación de Recolección de Información en AWS

Este proyecto permite recolectar información del sistema operativo (procesador, procesos, usuarios, etc.) y enviarla a una API, que almacena los datos en una base de datos MySQL. Tambíen permite consultar la información envíada vía API utilizando como indice las IPs de los dispositivos utilizados en el agente.


-La aplicación está dividida en dos componentes principales:

- **Agente:** Recolecta la información del sistema y la envía a la API.
- **API:** Recibe la información del agente y la almacena en una base de datos MySQL.
>Para la API se definió el puerto 5012.

Este archivo describe los pasos necesarios para desplegar tanto el **Agente** como la **API** en AWS, utilizando instancias EC2 y RDS dentro de la misma **VPC** para asegurar el tráfico interno.

---

## **1. Despliegue de la API**

### **1.1. Crear y Configurar las Instancias EC2**
1. Ve a la consola de **EC2** en AWS.
2. Crea dos instancias EC2 con las siguientes configuraciones:
   - **Sistema operativo:** Amazon Linux 2 o Ubuntu 20.04.
   - **Tipo de instancia:** `t2.micro` (free tier elegible).
   - **Almacenamiento:** 8 GB estándar.
   - **Grupo de seguridad:** Permitir el acceso desde la IP pública en el SG de la VPC en puerto `22` para SSH, de lo contrario no se podrá utilizar este metodo desde el equipo remoto.

**Nota:** Configurar las instancias EC2 dentro de la misma **VPC** para que el tráfico entre ellas y la base de datos RDS sea interno.

### **1.2. Crear y Configurar RDS**
1. Ve al servicio **RDS** en AWS.
2. Crea una instancia de base de datos MySQL con las siguientes configuraciones:
   - **Motor:** MySQL 8.0 o superior.
   - **Clase:** `db.t2.micro`.
   - **Almacenamiento:** 20 GB estándar.
   - **Autenticación:** Configura un usuario administrador y su contraseña.
   - **Deshabilitar conexiones públicas:** Deshabilita las conexiones públicas, de forma que la base de datos solo sea accesible desde la VPC interna.

3. **Configura la VPC para que las instancias EC2 puedan comunicarse con la base de datos RDS.** Asegúrate de que la VPC tenga las configuraciones adecuadas de subredes y que las instancias EC2 tengan acceso a la base de datos solo dentro de la misma red privada.

4. Copia la dirección del **endpoint** de la base de datos MySQL.
   ej: database.XXXXXXXX.XX-XXXX-X.rds.amazonaws.com

---

## **2. Preparar la Instancia EC2 para la API / Agente**

>Estos pasos sirven tanto para conectarse y configurar la API y el Agente.
### **2.1. Conectarse a la Instancia EC2**
Conéctate a la instancia EC2 mediante SSH:
```
chmod 400 "agent-key.pem"
ssh -i "agent-key.pem" ec2-user@<IP_PUBLICA_DE_LA_API/Agente>
```

### **2.2. Instalar Dependencias**
Ejecuta los siguientes comandos en la instancia EC2 para instalar Docker y otras dependencias:
1. Actualizar el sistema operativo:
```
sudo yum update -y                       # Para Amazon Linux también se puede usar dnf en vez de yum.
```
2. Instalar Docker y Git
```
sudo yum install -y docker git
```
3. Iniciar Docker y habilitar el servicio:
```
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```
4. Clonar el repositorio del proyecto:
> Al clonar todo el repositorio es necesario eliminar los archivos que no se necesiten dependiendo en el servidor que se encuentre, es decir, en la API o en el Agente.
```
git clone <URL_REPOSITORIO_DEL_PROYECTO>
cd <NOMBRE_DEL_PROYECTO>
```

---

## **3. Configurar y Desplegar la API

### **3.1. Editar el script deploy_api.sh**
Abre el archivo deploy_api.sh y edita las variables de entorno:
```
DB_HOST=<ENDPOINT_DE_RDS>
DB_PORT=3306
DB_USER=<USUARIO_RDS>
DB_PASSWORD=<CONTRASEÑA_RDS>
DB_NAME=system_info_db
```
### **3.2. Dar Permisos de Ejecución al Script**
```
chmod +x deploy_api.sh
```
### **3.3. Ejecutar el Script para Desplegar la API**
Ejecuta el script para construir y desplegar la API:
```
./deploy_api.sh
```
### **3.4. Verificar que el Contenedor de la API Esté Corriendo**
```
docker ps
```

---

## **4. Configurar y Desplegar el Agente

### **4.1. Editar Variables de Entorno**
Abre el archivo deploy_agent.sh y edita la variable API_HOST:
```
API_HOST="http://<IP_PRIVADA_DE_LA_API>:5012"  # Cambiar por la IP privada de la instancia EC2 de la API
```
### **4.2. Dar Permisos de Ejecución al Script**
```
chmod +x deploy_agent.sh
```
### **4.3. Dar Permisos de Ejecución al Script**
Ejecuta el script para construir y desplegar el agente:
```
./deploy_agent.sh
```
### **4.4. Verificar que el Contenedor del Agente Esté Corriendo**
Comprueba que el contenedor del agente esté corriendo:
```
docker ps
```

---

## **5. Validar la Comunicación entre el Agente y la API

1. Verifica que el agente envíe correctamente la información del sistema a la API:
  - Consulta los logs del contenedor del agente:
```
docker logs agent_container
```
2. Verifica en la base de datos (o mediante el endpoint /query de la API) que los datos del agente hayan sido recibidos correctamente.

---

### **6. Problemas Comunes**
- **El agente no puede conectarse a la API:**
  - Asegúrate de que el grupo de seguridad de la instancia de la API permita conexiones entrantes desde la instancia del agente.
  - Revisa que el `API_HOST` esté configurado correctamente en `deploy_agent.sh`.

- **El contenedor del agente no inicia:**
  - Revisa los permisos de ejecución y la configuración del script `deploy_agent.sh`.
  - Valida que el archivo `requirements.txt` tenga las dependencias correctas.

- **Problemas de conexión a la base de datos desde la API:**
  - Si la API no puede conectarse a la base de datos RDS, puedes probar la conexión a la base de datos manualmente utilizando el siguiente comando:
  
    **Para sistemas basados en Linux (Ubuntu o Amazon Linux):**
    ```bash
    mysql -h <ENDPOINT_DE_RDS> -u <USUARIO_RDS> -p
    ```

    - Asegúrate de que el grupo de seguridad de la base de datos permita conexiones entrantes desde la IP de la instancia EC2 donde corre la API.
    - Verifica que la instancia de RDS esté configurada correctamente para aceptar conexiones dentro de la VPC.

    Si la conexión es exitosa, deberías poder ver el prompt de MySQL. En caso de error, verifica el nombre del host y las credenciales, así como las configuraciones de red y de seguridad.

    **Comando para verificar si MySQL está escuchando en el puerto correcto (3306):**
    ```bash
    sudo netstat -tuln | grep 3306
    ```
    Esto te ayudará a verificar si el servicio de base de datos está activo y escuchando en el puerto correcto.

---

## **8. Riesgos Asumidos y Oportunidades de Mejora**

### **Riesgos Asumidos**
1. **Falta de Autenticación y Autorización (Auth & AuthZ):**
   - La comunicación entre el **Agente** y la **API** no está protegida mediante mecanismos de autenticación o autorización. Esto puede permitir que actores no autorizados envíen datos o consulten información sensible desde cualquier fuente. 
   - **Oportunidad de mejora:** Implementar un sistema de autenticación basado en tokens (por ejemplo, JWT) para autenticar a los agentes y permitir acceso solo a usuarios autorizados.

2. **Contraseñas "quemadas" en el código:**
   - Actualmente, las contraseñas y credenciales de la base de datos están incluidas en el código y luego se cargan en variables de entorno. Este es un riesgo, ya que las contraseñas podrían ser fácilmente accesibles si el código o las variables de entorno no están correctamente protegidas.
   - **Oportunidad de mejora:** Utilizar un **gestor de secretos** como AWS Secrets Manager o HashiCorp Vault para almacenar de manera segura las credenciales y otros datos sensibles, en lugar de tener contraseñas en el código.

3. **No sanitización de entrada del usuario:**
   - La API no está realizando una correcta sanitización de los datos enviados por el agente o cualquier otro cliente. Esto deja abierta la posibilidad de ataques como inyección de código (por ejemplo, **SQL Injection**) que podrían comprometer la integridad de los datos.
   - **Oportunidad de mejora:** Implementar sanitización de entradas para todas las solicitudes que reciba la API, asegurándose de que los datos sean validados y escapados antes de ser utilizados en consultas SQL o cualquier otro procesamiento.

4. **Falta de validaciones de seguridad en la API:**
   - La API no implementa validaciones suficientes de seguridad, como limitación de tasa (rate limiting) para prevenir **ataques de denegación de servicio** (DoS) o ataques de **fuerza bruta**.
   - **Oportunidad de mejora:** Incorporar **rate limiting** y técnicas de **throttling** para evitar abusos de la API, además de establecer un sistema de monitorización para detectar actividades sospechosas.

5. **Falta de cifrado en la comunicación:**
   - Actualmente, no se especifica si la comunicación entre el Agente y la API está cifrada. La ausencia de cifrado podría exponer los datos a ataques de **intercepción** como **man-in-the-middle** (MITM).
   - **Oportunidad de mejora:** Implementar **HTTPS** en la API y usar certificados SSL/TLS para cifrar la comunicación entre el Agente y la API.

6. **Logs sin protección de datos sensibles:**
   - Los logs generados por la API y el Agente podrían contener información sensible, como contraseñas o detalles de configuración, si no se gestionan adecuadamente.
   - **Oportunidad de mejora:** Asegurar que los logs no contengan información sensible (como contraseñas, credenciales o datos de usuarios). Además, se podrían implementar niveles de logs (INFO, WARN, ERROR) y almacenar los logs de forma segura.

### **Oportunidades de Mejora**
1. **Monitoreo y Alertas:**
   - No se ha implementado un sistema de monitoreo o alertas para la API o el Agente. Esto podría dificultar la detección temprana de fallas en el sistema o de posibles intentos de intrusión.
   - **Oportunidad de mejora:** Implementar un sistema de **monitorización** (por ejemplo, con **AWS CloudWatch**) y configurar alertas para detectar eventos sospechosos o fallos en el sistema.

2. **Escalabilidad de la API y el Agente:**
   - La implementación actual podría no ser escalable para grandes cantidades de agentes o datos. A medida que la empresa crezca, la API podría enfrentar problemas de rendimiento bajo carga.
   - **Oportunidad de mejora:** Considerar la implementación de mecanismos de **caching** para reducir la carga de la base de datos, así como la implementación de **balanceadores de carga** y una arquitectura basada en microservicios para mejorar la escalabilidad y disponibilidad.

3. **Seguridad de la Base de Datos:**
   - Aunque se recomienda utilizar variables de entorno para las credenciales, la base de datos RDS está accesible desde la VPC, lo que podría ser riesgoso si las credenciales se exponen.
   - **Oportunidad de mejora:** Asegurarse de que la base de datos esté configurada con **políticas de acceso mínimo** y que las conexiones solo se realicen a través de redes privadas o conexiones VPN seguras.

4. **Pruebas de Carga y Seguridad:**
   - No se mencionan pruebas de carga o pruebas de seguridad como parte del proceso de implementación. La falta de pruebas podría llevar a problemas de rendimiento o vulnerabilidades de seguridad no detectadas.
   - **Oportunidad de mejora:** Implementar pruebas de carga utilizando herramientas como **JMeter** y realizar auditorías de seguridad regulares para detectar vulnerabilidades potenciales.

5. **Respaldo de Datos:**
   - Aunque se mencionan las operaciones con la base de datos, no hay un sistema automatizado de respaldo para los datos.
   - **Oportunidad de mejora:** Implementar **políticas de respaldo automático** y almacenamiento en **Amazon S3** para garantizar la protección de los datos a largo plazo.

6. **Documentación de la API:**
   - La documentación actual es básica. La falta de documentación detallada puede dificultar el mantenimiento y escalabilidad del sistema.
   - **Oportunidad de mejora:** Utilizar herramientas como **Swagger** o **OpenAPI** para generar y mantener una documentación interactiva y detallada de la API.

---

Este apartado de **Riesgos Asumidos y Oportunidades de Mejora** proporciona una visión clara sobre los aspectos que necesitan atención para mejorar la seguridad, escalabilidad y fiabilidad de la aplicación. Las oportunidades mencionadas son pasos importantes para asegurar que la infraestructura crezca de forma segura y eficiente.

---



