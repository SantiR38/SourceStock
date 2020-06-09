# SourceStock

<p>Esta Web-App Django tiene como propósito, controlar el stock de mercaderías de locales comerciales,
mediante lectura de código de barras. Tiene dos views principales (compra y venta), donde se puede agregar
y quitar existencias respectivamente.</p>

<h2>Ramas</h2>
<p>El proyecto cuenta con 2 branches:</p>
<ul>
  <li><strong>Master:</strong> Contiene las versiones oficiales de la aplicación.</li>
  <li><strong>Development:</strong> Contiene el proceso de desarrollo y es la rama que debe recibir los pull requests.</li>
</ul>

<h2>Instalación</h2>

<p>Para poder correr el proyecto en local será necesario instalar lo siguiente:</p>

<ul>
  <li><a href='https://www.python.org/downloads/'>Python 3.8 32-bit</a></li>
  <li><a href='https://www.postgresql.org/download/'>PostgreSQL</a></li>
</ul>

<p>Las librerías de python instalables con PyPi están en el documento requirements.txt.</p>

<h2>Configuracion de la base de datos</h2>

<p>En el archivo settings.py, se debe modificar el diccionario DATABASES, 
colocando la configuración de la base de datos del servidor local</p>

<h2>Despliegue</h2>

<p>Para poder ejecutar correctamente la aplicación, debemos entrar por consola al directorio 
principal del proyecto y escribir "python manage.py runserver". En algunos casos se ejecuta otra versión de 
python no compatible con el proyecto. De ser así, escribir en consola "python3 manage.py runserver" o el 
comando que sea necesario para invocar al entorno de Python 3.8</p>
<p>Una forma de automatizar esto es creando un archivo .bat con la línea de comandos descripta en el párrafo anterior.</p>

<h2>Interfaz</h2>

<p>La aplicación tiene el siguiente aspecto:</p>

<img src="https://raw.githubusercontent.com/SantiR38/SourceStock/development/erp/static/dist/img/interfaz.png" />

<p>El frontend está realizado con la platilla de código abierto <a href="https://adminlte.io/">AdminLTE.io</a></p>
