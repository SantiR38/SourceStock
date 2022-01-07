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

In order to execute the app correctly, you should create an isolated environment with venv (python 3.8), and run the following command.
```bash
python manage.py runserver
```
You can do this automatically creating a script with the previous command (`.bat`on windows or `.sh`on linux).

## Interfaz

The interface has the following aspect:

<img src="https://raw.githubusercontent.com/SantiR38/SourceStock/development/erp/static/dist/img/interfaz.png" />

The visual has been made with the open source template <a href="https://adminlte.io/">AdminLTE.io</a>


### You can set in wsgi.py and in manage.py the settings file that you need to use.
