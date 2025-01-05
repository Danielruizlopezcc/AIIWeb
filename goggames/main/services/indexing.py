from whoosh import index
from whoosh.fields import Schema, TEXT, NUMERIC, DATETIME, ID, KEYWORD
from datetime import datetime
import os

# ----------------------------
# 📚 ESQUEMA DE WHOOSH
# ----------------------------
schema = Schema(
    nombre=TEXT(stored=True),
    precio=NUMERIC(stored=True, decimal_places=2),
    valoracion=NUMERIC(stored=True, decimal_places=1),
    fecha_lanzamiento=DATETIME(stored=True),
    tamaño=TEXT(stored=True),
    genero=KEYWORD(stored=True, commas=True),
    etiquetas=KEYWORD(stored=True, commas=True),
    multimedia=KEYWORD(stored=True, commas=True),
    imagen_principal=TEXT(stored=True),  # Añadida correctamente
    url=ID(stored=True, unique=True)
)


# ----------------------------
# 🔧 INICIALIZAR ÍNDICE
# ----------------------------
def inicializar_indice():
    """
    Inicializa o abre un índice Whoosh para los juegos.
    """
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
        return index.create_in("indexdir", schema)
    return index.open_dir("indexdir")


# ----------------------------
# 📥 INDEXAR JUEGO
# ----------------------------
def indexar_juego(writer, juego):
    """
    Añade un juego al índice Whoosh.
    """
    try:
        # Asegurar que fecha_lanzamiento sea datetime
        if isinstance(juego['fecha_lanzamiento'], datetime):
            fecha_lanzamiento = juego['fecha_lanzamiento']
        elif juego['fecha_lanzamiento'] is None:
            fecha_lanzamiento = None
        else:
            fecha_lanzamiento = datetime.strptime(juego['fecha_lanzamiento'], "%Y-%m-%d")

        writer.add_document(
            nombre=juego['nombre'],
            precio=juego['precio'],
            valoracion=juego['valoracion'],
            fecha_lanzamiento=fecha_lanzamiento,
            tamaño=juego['tamaño'],
            genero=juego['genero'],
            etiquetas=juego['etiquetas'],
            multimedia=juego['multimedia'],
            imagen_principal=juego['imagen_principal'],
            url=juego['url']
        )
        print(f"✅ Juego indexado correctamente: {juego['nombre']}")
    except Exception as e:
        print(f"❌ Error al indexar el juego: {e}")
