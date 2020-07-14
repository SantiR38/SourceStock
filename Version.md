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


## Cambios en la versión 1.3

1. **Bug fixed:** 
    * No se actualizan las existencias cuando se agrega un nuevo artículo.
    * Error cuando la base de datos esta vacía
2. **Favicon agregado**
3. **Nuevas tablas en base de datos**:
    * ArtState: Utilizada como foreign key para la tabla Article, Entrada, Venta y Perdida.
    * Entrada: Registra cada compra o entrada de mercadería, Utilizada como foreign key de DetalleEntrada. 
    * DetalleEntrada: Registra cada uno de los articulos de una Entrada.
    * Venta: Registra cada venta de mercadería, Utilizada como foreign key de DetalleVenta. 
    * DetalleVenta: Registra cada uno de los articulos de una Venta.
    * Perdida (aun no utilizada)
    * DetallePerdida (aun no utilizada)
4. **Nuevas views**:
    * Entrada
    * Venta
    * Transacción Exitosa
    * Venta Exitosa
    * Cancelar
5. **Funcionalidades**: Ahora tanto la compra como la venta crean una lista a la derecha donde se van enumerando los productos que son parte de la transacción. La misma se puede confirmar o cancelar antes de afectar a la tabla principal 'Article'.

## Cambios en la versión 1.3.1

1. **Bug fixed:** Se quitó el porcentaje_ganancia de la tabla DetalleEntrada y se lo colocó en la tabla Article. Se eliminó ese campo de la vista entrada y del formulario entrada, para que ahora esten en agregar_modificar.
2. **Sidebar:** Las pestañas hijas ahora son mas pequeñas y tienen un margen mayor para distinguirlas de las pestañas contenedoras.
3. **Documentación:** 
    * Se cambió la escritura del Readme de HTML a Markdown.
    * Se agregó una nueva imagen de la interfaz.
4. **Interfaz de Formulario:** Se quitaron los errorlist y se alineó el formulario como tabla (antes estaba como párrafo).

## Cambios en la versión 1.3.2

1. **Bug fixed:** En la sección 'Agregar o modificar' habia un KeyError, debido a que no se adaptó el formulario ni la funcionalidad de la vista a la nueva estructura del modelo Article.

## Cambios en la versión 1.4

1. **Control de inventario:** Esta sección previamente era muy dificil de utilizar, por lo que, de ahora en más se utiliza en la interfaz el mismo estilo que en el panel de administración de Django. La lista completa de articulos de la base de datos. Cuando se hace click sobre uno de ellos, se le pueden editar sus campos comodamente.
2. Asterisco (*) utilizado para señalar campo obligatorio en formularios.
3. Cambios en templates entrada, agregar_modificar y venta.
4. Eliminados templates en desuso.

## Cambios en la versión 1.5

1. **FormCliente:** Se creó el formulario cliente para la futura emisión de recibos y facturas.
2. **Modelo Cliente:** Los datos de cada cliente se guardan en la base de datos.
3. El detalle de venta se muestra apenas se carga la vista venta.
4. Modelo Cliente implementado en vista venta.
5. Costo y precio sin iva agregados.
6. Opción de eliminar elemento a vender (vista 'cancelar_unidad').