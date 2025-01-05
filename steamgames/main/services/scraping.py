import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# Encabezados para la solicitud HTTP
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

# ----------------------------
# 🌐 FUNCIONES DE SCRAPING
# ----------------------------

def extraer_urls_juegos(pagina=1):
    """
    Extrae las URLs de los juegos desde la página principal de GOG.
    """
    url = f"https://www.gog.com/en/games?page={pagina}"
    urls_juegos = []

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        juegos = soup.find_all("a", class_="product-tile")

        for juego in juegos:
            enlace = juego.get('href', '#')
            urls_juegos.append(f"https://www.gog.com{enlace}" if not enlace.startswith("https") else enlace)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener URLs de juegos: {e}")
    
    return urls_juegos


def extraer_detalles_juego(url):
    """
    Extrae los detalles de un juego específico desde su URL.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Nombre
        nombre = soup.find("h1", class_="productcard-basics__title")
        nombre = nombre.text.strip() if nombre else "Desconocido"

        # Precio
        precio = soup.find("span", class_="product-actions-price__final-amount")
        precio = precio.text.strip().replace(",", ".") if precio else "Gratis"

        # Valoración
        valoracion = soup.find("div", class_="rating productcard-rating__score")
        valoracion = float(valoracion.text.split("/")[0].strip()) if valoracion else 0.0

        # Fecha de lanzamiento
        fecha_label = soup.find("div", class_="details__category table__row-label", string=lambda text: text and "Release date" in text)
        if fecha_label:
            contenedor_fecha = fecha_label.find_next("div", class_="details__content table__row-content")
            if contenedor_fecha:
                match = re.search(r"\d{4}-\d{2}-\d{2}", contenedor_fecha.text)
                if match:
                    fecha_texto = match.group(0)
                    try:
                        fecha_lanzamiento = datetime.strptime(fecha_texto, "%Y-%m-%d")
                    except ValueError:
                        print(f"⚠️ Error al parsear la fecha: {fecha_texto}")
                        fecha_lanzamiento = None
                else:
                    fecha_lanzamiento = None
            else:
                fecha_lanzamiento = None
        else:
            fecha_lanzamiento = None

        # Tamaño
        tamaño_label = soup.find("div", class_="details__category table__row-label", string=lambda text: text and "Size" in text)
        tamaño = tamaño_label.find_next("div").text.strip() if tamaño_label else "Desconocido"

        # Géneros
        generos_div = soup.find("div", class_="details__category table__row-label", string="Genre:")
        if generos_div:
            contenedor_generos = generos_div.find_next("div", class_="details__content table__row-content")
            generos = [g.text.strip() for g in contenedor_generos.find_all("a", class_="details__link")] if contenedor_generos else []
            generos = ",".join(set(generos)) if generos else "Desconocido"
        else:
            generos = "Desconocido"

        # Etiquetas
        etiquetas_div = soup.find("div", class_="details__category table__row-label", string="Tags:")
        if etiquetas_div:
            contenedor_etiquetas = etiquetas_div.find_next("div", class_="details__content table__row-content")
            etiquetas = [
                e.find("span", class_="details__link-text").text.strip()
                for e in contenedor_etiquetas.find_all("a", class_="details__link details__link--tag")
                if e.find("span", class_="details__link-text")
            ] if contenedor_etiquetas else []
            etiquetas = ",".join(set(etiquetas)) if etiquetas else "Desconocido"
        else:
            etiquetas = "Desconocido"

        # Multimedia
        multimedia = [thumb.get("src") for thumb in soup.find_all("img", class_="productcard-thumbnails-slider__image")]
        multimedia = ",".join(multimedia) if multimedia else "Desconocido"

        # 📸 **Imagen Principal desde el Slider**
        imagen_principal = None

        # Busca el contenedor que tiene la imagen principal
        slider_div = soup.find("div", class_=re.compile(r"mobile-slider__slide.*gog-slider__item.*"))

        if slider_div:
            picture_tag = slider_div.find("picture")
            if picture_tag:
                img_tag = picture_tag.find("img", class_=re.compile(r"mobile-slider__image"))
                if img_tag and img_tag.get("src"):
                    imagen_principal = img_tag.get("src")
                    print(f"✅ Imagen Principal encontrada: {imagen_principal}")
                else:
                    print("⚠️ No se encontró el tag <img> dentro de <picture>")
            else:
                print("⚠️ No se encontró el tag <picture> dentro de slider_div")
        else:
            print("⚠️ No se encontró slider_div")

        # Fallback si no encuentra la imagen principal
        if not imagen_principal:
            imagen_principal = "https://via.placeholder.com/480x270?text=No+Image"


        return {
            "nombre": nombre,
            "precio": float(precio) if precio.replace(".", "").isdigit() else 0.0,
            "valoracion": valoracion,
            "fecha_lanzamiento": fecha_lanzamiento,
            "tamaño": tamaño,
            "genero": generos,
            "etiquetas": etiquetas,
            "multimedia": multimedia,
            "imagen_principal": imagen_principal,
            "url": url
        }

    except Exception as e:
        print(f"❌ Error al extraer detalles del juego: {e}")
        return None
