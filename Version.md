# SourceStock

## Cambios en la versión 1.0.1

1. **View compra_simple:** Corrección de bug de la versión anterior que no permitía agregar artículos solo con el campo cógido y cantidad. Ahora, para hacer una compra detallada, hay una página específica llamada 'agregar o modificar productos'.
2. **Problemas con campo código:** Se cambió el campo codigo de IntegerField() a BigIntegerField() para que acepte numeros de mayor tamaño.
3. **Enlaces de inicio a admin:** Se enlazan las páginas mediante pestañas, sin tener que modificar la url a mano.
4. **Costo y precio decimales:** Estos campos aceptaban solo valores enteros, pero ahora aceptan numeros de hasta 2 decimales.
5. **'Active' condicional:** Corrección de bug estético que no resaltaba la pestaña que estaba activa en el sidebar.
6. **Panel de Administracion:** Pequeños cambios en el '/admin'.
7. **Version.md:** Creación de archivo para registrar los cambios realizados en cada versión.

## Cambios en la versión 1.2

1. **Repositorio:** Migración a un nuevo repositorio, ignorando pycache, librerías, y datos sensibles.
2. **Settings:** El archivo settings.py ahora es un package que contiene las configuraciones adaptables para correr en local o en producción.


## Cambios en la versión 2.0

1. **Bug fixed:** 
    * No se actualizan las existencias cuando se agrega un nuevo artículo.
    * Error cuando la base de datos esta vacía
2. **Favicon agregado**