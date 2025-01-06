from datetime import datetime
import locale
from django.shortcuts import render, redirect
from .services.scraping import extraer_urls_juegos, extraer_detalles_juego
from .services.database import inicializar_bd, almacenar_juego_bd
from .services.indexing import inicializar_indice, indexar_juego
from whoosh.qparser import QueryParser
from django.core.paginator import Paginator
import sqlite3
from .services.recommendations import recommend_with_combinations
from django.http import JsonResponse


def main(request):
    try:
        conn = sqlite3.connect("gog_games.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM juegos")
        cantidad_juegos = cursor.fetchone()[0]
        hay_juegos = cantidad_juegos > 0
    except Exception as e:
        print(f"❌ Error al verificar los juegos: {e}")
        hay_juegos = False

    return render(request, 'main.html', {'hay_juegos': hay_juegos})




def juegos(request):
    try:
        conn = sqlite3.connect("gog_games.db")
        cursor = conn.cursor()

        orden = request.GET.get('orden', '-------')
        termino_busqueda = request.GET.get('buscar', '').strip()
        precio_min = request.GET.get('precio_min', '').strip()
        precio_max = request.GET.get('precio_max', '').strip()

        if orden == 'populares':
            orden_sql = 'CAST(valoracion AS FLOAT) DESC'
        elif orden == 'precio_asc':
            orden_sql = 'CAST(precio AS FLOAT) ASC'
        elif orden == 'precio_desc':
            orden_sql = 'CAST(precio AS FLOAT) DESC'
        elif orden == 'lanzamientos_recientes':
            orden_sql = "ABS(julianday('now') - julianday(fecha_lanzamiento)) ASC"
        else:
            orden_sql = 'CAST(valoracion AS FLOAT) DESC'

        where_clauses = []
        params = []

        if termino_busqueda:
            where_clauses.append("LOWER(nombre) LIKE ?")
            params.append(f"%{termino_busqueda.lower()}%")
        
        if precio_min:
            try:
                precio_min = float(precio_min)
                if precio_min < 0:
                    raise ValueError("El precio mínimo no puede ser negativo.")
                where_clauses.append("CAST(precio AS FLOAT) >= ?")
                params.append(precio_min)
            except ValueError as e:
                return render(request, 'juegos.html', {
                    'error': str(e),
                    'orden': orden,
                    'termino_busqueda': termino_busqueda,
                    'precio_min': precio_min,
                    'precio_max': precio_max,
                })
        
        if precio_max:
            try:
                precio_max = float(precio_max)
                if precio_max < 0:
                    raise ValueError("El precio máximo no puede ser negativo.")
                where_clauses.append("CAST(precio AS FLOAT) <= ?")
                params.append(precio_max)
            except ValueError as e:
                return render(request, 'juegos.html', {
                    'error': str(e),
                    'orden': orden,
                    'termino_busqueda': termino_busqueda,
                    'precio_min': precio_min,
                    'precio_max': precio_max,
                })
        
        if orden == 'lanzamientos_recientes':
            where_clauses.append("fecha_lanzamiento IS NOT NULL AND fecha_lanzamiento != ''")

        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
            SELECT id, nombre, precio, valoracion, fecha_lanzamiento, tamaño, genero, etiquetas, imagen_principal
            FROM juegos
            {where_clause}
            ORDER BY {orden_sql}
        """
        
        cursor.execute(query, params)
        juegos_raw = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return redirect('juegos')
    finally:
        conn.close()
    
    juegos_lista = []
    for juego in juegos_raw:
        fecha_lanzamiento = None
        if juego[4]:
            try:
                fecha_lanzamiento = datetime.strptime(juego[4], "%Y-%m-%d").strftime('%d de %B de %Y')
            except ValueError:
                fecha_lanzamiento = None

        juegos_lista.append({
            'id': juego[0],
            'nombre': juego[1],
            'precio': juego[2],
            'valoracion': juego[3],
            'fecha_lanzamiento': fecha_lanzamiento,
            'tamaño': juego[5],
            'genero': [g.strip() for g in juego[6].split(',')] if juego[6] else [],
            'etiquetas': [e.strip() for e in juego[7].split(',')] if juego[7] else [],
            'imagen_principal': juego[8],
        })
    
    if not juegos_lista:
        return render(request, 'juegos.html', {
            'error': 'No hay juegos disponibles para los filtros aplicados.',
            'orden': orden,
            'termino_busqueda': termino_busqueda,
            'precio_min': precio_min,
            'precio_max': precio_max,
        })
    
    paginator = Paginator(juegos_lista, 48)
    pagina = request.GET.get('page')
    juegos_paginados = paginator.get_page(pagina)
    
    # 📤 Renderizar la 
    return render(request, 'juegos.html', {
        'juegos': juegos_paginados,
        'orden': orden,
        'termino_busqueda': termino_busqueda,
        'precio_min': precio_min,
        'precio_max': precio_max,
    })



def scraping(request):
    return render(request, 'scraping.html')



def scraping_manual(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            inicializar_bd()
            ix = inicializar_indice()
            writer = ix.writer()

            for pagina in range(1, 6):
                print(f"🌍 Procesando página {pagina}...")
                urls = extraer_urls_juegos(pagina)
                for url in urls:
                    detalles = extraer_detalles_juego(url)
                    if detalles:
                        almacenar_juego_bd(detalles)
                        indexar_juego(writer, detalles)
            writer.commit()
            print("✅ Scraping completado correctamente.")

            return JsonResponse({'status': 'success'})
        
        except Exception as e:
            print(f"❌ Error durante el scraping: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return render(request, 'scraping_manual.html')



def detalle_juego(request, juego_id):
    try:
        conn = sqlite3.connect("gog_games.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM juegos WHERE id=?", (juego_id,))
        juego = cursor.fetchone()
        
        if not juego:
            return redirect('juegos')

        recomendaciones_genres = recommend_with_combinations(
            game_id=juego_id,
            attribute='genero',
            top_n=5
        ).to_dict(orient='records')

        recomendaciones_etiqueta = recommend_with_combinations(
            game_id=juego_id,
            attribute='etiquetas',
            top_n=5
        ).to_dict(orient='records')

        recomendaciones_genres_completas = []
        for reco in recomendaciones_genres:
            cursor.execute("SELECT id, nombre, precio, valoracion, genero, etiquetas, imagen_principal FROM juegos WHERE id=?", (reco['id'],))
            datos = cursor.fetchone()
            if datos:
                recomendaciones_genres_completas.append({
                    'id': datos[0],
                    'nombre': datos[1],
                    'precio': datos[2],
                    'valoracion': datos[3],
                    'genero': datos[4].split(',') if datos[4] else [],
                    'etiquetas': datos[5].split(',') if datos[5] else [],
                    'imagen_principal': datos[6] if datos[6] else 'https://via.placeholder.com/180x100'
                })

        recomendaciones_etiqueta_completas = []
        for reco in recomendaciones_etiqueta:
            cursor.execute("SELECT id, nombre, precio, valoracion, genero, etiquetas, imagen_principal FROM juegos WHERE id=?", (reco['id'],))
            datos = cursor.fetchone()
            if datos:
                recomendaciones_etiqueta_completas.append({
                    'id': datos[0],
                    'nombre': datos[1],
                    'precio': datos[2],
                    'valoracion': datos[3],
                    'genero': datos[4].split(',') if datos[4] else [],
                    'etiquetas': datos[5].split(',') if datos[5] else [],
                    'imagen_principal': datos[6] if datos[6] else 'https://via.placeholder.com/180x100'
                })

    except sqlite3.Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return redirect('juegos')
    finally:
        conn.close()

    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES')  
        except locale.Error:
            print("⚠️ No se pudo configurar locale a español. Usando por defecto.")

    fecha_lanzamiento = None
    if juego[4]:
        try:
            fecha_lanzamiento = datetime.strptime(juego[4], "%Y-%m-%d").strftime('%d de %B de %Y')
        except ValueError:
            fecha_lanzamiento = None

    juego_detalle = {
        'id': juego[0],
        'nombre': juego[1],
        'precio': juego[2],
        'valoracion': juego[3],
        'fecha_lanzamiento': fecha_lanzamiento,
        'tamaño': juego[5],
        'genero': juego[6].split(',') if juego[6] else [],
        'etiquetas': juego[7].split(',') if juego[7] else [],
        'multimedia': juego[8].split(',') if juego[8] else [],
        'imagen_principal': juego[9],
        'url': juego[10],
    }

    return render(
        request,
        'detalle_juego.html',
        {
            'juego': juego_detalle,
            'recomendaciones_genres': recomendaciones_genres_completas,
            'recomendaciones_etiqueta': recomendaciones_etiqueta_completas
        }
    )






