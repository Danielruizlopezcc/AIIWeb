import sqlite3
from datetime import datetime


DB_NAME = "gog_games.db"


def conectar_bd():
    """Establece y devuelve una conexión con la base de datos."""
    return sqlite3.connect(DB_NAME)


def inicializar_bd():
    """Inicializa la base de datos y crea la tabla si no existe."""
    conn = conectar_bd()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS juegos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            precio REAL,
            valoracion REAL,
            fecha_lanzamiento TEXT,
            tamaño TEXT,
            genero TEXT,
            etiquetas TEXT,
            multimedia TEXT,
            imagen_principal TEXT,
            url TEXT UNIQUE
        )''')
        conn.commit()
        print("✅ Base de datos inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
    finally:
        conn.close()


def almacenar_juego_bd(juego):
    """
    Almacena un juego en la base de datos.
    """
    conn = conectar_bd()
    try:
        conn.execute('''INSERT OR IGNORE INTO juegos 
            (nombre, precio, valoracion, fecha_lanzamiento, tamaño, genero, etiquetas, multimedia, imagen_principal, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                juego['nombre'],
                juego['precio'],
                juego['valoracion'],
                juego['fecha_lanzamiento'].strftime("%Y-%m-%d") if juego['fecha_lanzamiento'] else None,
                juego['tamaño'],
                juego['genero'],
                juego['etiquetas'],
                juego['multimedia'],
                juego['imagen_principal'],
                juego['url']
            ))
        conn.commit()
        print(f"✅ Juego almacenado: {juego['nombre']}")
    except sqlite3.Error as e:
        print(f"❌ Error al almacenar juego: {e}")
    finally:
        conn.close()

