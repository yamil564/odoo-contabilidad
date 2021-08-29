

# Instalación y Configuración Inicial

## Preparación Inicial
1. Instalar docker -> https://docs.docker.com/get-docker/
2. Instalar docker-compose -> https://docs.docker.com/compose/install/

## Instalación de Odoo con docker
1. Descargar el repositorio
~~~
git clone https://gitlab.com/hespejo/fe-gestion-it.git
~~~
2. Ingresar a la carpeta 
~~~
cd fe-gestion-it
~~~
3. Crear archivo .env y docker-compose.yaml
~~~
cp .env.copy .env
cp docker-compose.yaml.copy docker-compose.yaml
cp nginx.conf.copy nginx.conf
~~~
4. Editar parámetros de entorno en .env, estos parámetros los tomará docker-compose.yaml para crear los contenedores
~~~
Ejemplo:
WEB_HOST=fe_odoo_empresa1 
~~~
5. Cambiar los parámetros de entorno en los siguientes archivos:
~~~
config/odoo.conf
nginx/conf.d/nginx.conf
.env
~~~
6. Opcional: Editar docker-compose.yaml, esto siempre y cuando se requiera añadir nuevos servicios o modificar parámetros.
7. Ejecutar docker-compose
~~~
docker-compose up -d
~~~

## Comandos frecuentes








