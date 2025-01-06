## Como usar GoGgames

### 1. **Página de Inicio:**

- Al acceder a la URL, se muestra la página de inicio con una breve descripción del proyecto y un botón para acceder a la página de búsqueda.

### 2. **Página de Búsqueda:**

- En este caso ya está todo el contenido Scrapeado debido a su gran cantidad de datos (240), pero también se puede aceder a la sección de Scraping Manual y volver a cargar los datos.

### 3. **Juegos Disponibles:**

- Se muestran 5 páginas de juegos disponibles con su imagen, nombre, precio, géneros y su valoración. Al hacer clic en un juego, se accede a su página de detalles.

- En esta página, también existen filtros que permiten:
  - Realizar una busqueda por nombre
  - Ordenar por lo más populares, lo más baratos, lo más caros y lo más recientes
  - Filtrar por un intervalo de precios

### 4. **Página de Detalles del Juego:**

- Al hacer clic en un juego, se accede a su página de detalles, donde se muestra información detallada sobre el juego, incluyendo su imagen, nombre, precio, valoración, fecha de lanzamiento, tamaño, géneros, etiquetas, url oficial de la página web y un carrusel de imágenes.

- En esta página se calcula directamente los dos sistemas de recomendación basado en contenido el cual muestran del juego que has seleccionado, los 5 juegos mejor valorados que tengan el mismo género y etiquetas. También se muestra un botón que permite acceder a la página de los juegos recomendados y mostrar toda la información mencionada anteriormente.

### 5. **Sistema de Recomendación:**

**Recomendaciones Basadas en Género:**

- Se muestran los 5 juegos mejor valorados que tengan el mismo género que el juego seleccionado. El algortimo es sencillo, se obtienen todos los n géneros del juego seleccionado y se buscan todos los juegos que contengan estos n géneros. Si no se encuentran suficientes juegos, se buscan juegos que contengan n-1 géneros, y así sucesivamente hasta que se encuentren suficientes juegos. Una vez se encuentran suficientes juegos, se ordenan por valoración y se muestran los 5 mejores.

**Recomendaciones Basadas en Etiquetas:**

- Se muestran los 5 juegos mejor valorados que tengan las mismas etiquetas que el juego seleccionado. El algortimo es sencillo, se obtienen todas las etiquetas del juego seleccionado y se buscan todos los juegos que contengan estas etiquetas. Si no se encuentran suficientes juegos, se buscan juegos que contengan n-1 etiquetas, y así sucesivamente hasta que se encuentren suficientes juegos. Una vez se encuentran suficientes juegos, se ordenan por valoración y se muestran los 5 mejores.
