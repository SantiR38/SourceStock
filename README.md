# SourceStock

Esta Web-App Django tiene como propósito, controlar el stock de mercaderías de locales comerciales,
mediante lectura de código de barras. Tiene dos views principales (compra y venta), donde se puede agregar
y quitar existencias respectivamente.

## Ramas
El proyecto cuenta con 2 branches:
  * **Master:** Contiene las versiones oficiales de la aplicación.</li>
  * **Development:** Contiene el proceso de desarrollo y es la rama que debe recibir los pull requests.</li>

## Setting up

For running this project it will be necesary to **download and install** the following things:

  1. [Python 3.8 32-bit](https://www.python.org/downloads/).

  2. [PostgreSQL](https://www.postgresql.org/download/).

  3. [Git](https://git-scm.com/download/win).

  4. [Pip](https://www.neoguias.com/como-instalar-pip-python/#Como_instalar_PIP_en_Windows).

  5. Virtualenv: `pip install virtualenv`.


**Clone this project** in your local machine:

  6. Use `git clone` and the url of this project.


**Launch a virtual enviroment** in the directory where is the project saved on your system:

  7. [Info](https://programwithus.com/learn/python/pip-virtualenv-windows)

  8. Install the requirements.txt


Now you need to **configurate the data base**.

  9. Create a data base in postgres.
  10. In punto_venta/settings/ create two files called local.py and production.py, and put there the following things:
    * Import base
    * DEBUG: True or False
    * ALLOWED HOSTS: Url address
    * DATABASES: Dict with your database info (see the [docs](https://docs.djangoproject.com/en/3.0/ref/settings/#databases))
    * STATIC_URL
  11. In punto_venta/ create a file called env_variables.py and there create a dict called 'enterprise' with the following keys:
    * name
    * iva_situation
    * cuit
    * phone
    * address
    * image: the image should be in static directory.

  This will be displayed in the tickets and estimations pdfs.


Next, you have to create a superuser:

  12. `python manage.py createsuperuser`


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
