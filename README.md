# SourceStock

Esta Web-App Django tiene como propósito, controlar el stock de mercaderías de locales comerciales,
mediante lectura de código de barras. Tiene dos views principales (compra y venta), donde se puede agregar
y quitar existencias respectivamente.

## Ramas
El proyecto cuenta con 2 branches:
  * **Master:** Contiene las versiones oficiales de la aplicación.</li>
  * **Development:** Contiene el proceso de desarrollo y es la rama que debe recibir los pull requests.</li>

## Instalación

Para poder correr el proyecto en local será necesario instalar lo siguiente:

  * <a href='https://www.python.org/downloads/'>Python 3.8 32-bit</a>
  * <a href='https://www.postgresql.org/download/'>PostgreSQL</a>

Las librerías de python instalables con PyPi están en el documento requirements.txt.

## Configuracion de la base de datos

En el archivo settings.py, se debe modificar el diccionario DATABASES, 
colocando la configuración de la base de datos del servidor local

## Despliegue

Para poder ejecutar correctamente la aplicación, debemos entrar por consola al directorio 
principal del proyecto y escribir "python manage.py runserver". En algunos casos se ejecuta otra versión de 
python no compatible con el proyecto. De ser así, escribir en consola "python3 manage.py runserver" o el 
comando que sea necesario para invocar al entorno de Python 3.8
Una forma de automatizar esto es creando un archivo .bat con la línea de comandos descripta en el párrafo anterior.

## Interfaz

La aplicación tiene el siguiente aspecto:

<img src="https://raw.githubusercontent.com/SantiR38/SourceStock/development/erp/static/dist/img/interfaz.png" />

El frontend está realizado con la plantilla de código abierto <a href="https://adminlte.io/">AdminLTE.io</a>


### Para elegir que archivo de settings estará en nuestro path, editarlo en wsgi.py y manage.py
