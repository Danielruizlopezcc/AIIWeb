import sqlite3
import pandas as pd
from itertools import combinations

# ---------------------------
# 📊 Cargar Juegos
# ---------------------------
def load_games():
    """Cargar los datos de juegos desde SQLite con preprocesamiento."""
    conn = sqlite3.connect('gog_games.db')
    query = """
        SELECT id, nombre, precio, valoracion, fecha_lanzamiento, tamaño, genero, etiquetas
        FROM juegos
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Preprocesar géneros y etiquetas como conjuntos
    df = df.dropna(subset=['genero', 'etiquetas'])
    df['genero'] = df['genero'].apply(lambda x: set(x.split(',')) if isinstance(x, str) else set())
    df['etiquetas'] = df['etiquetas'].apply(lambda x: set(x.split(',')) if isinstance(x, str) else set())
    
    return df


# ---------------------------
# 🧠 Lógica de Combinaciones
# ---------------------------
def recommend_with_combinations(game_id, attribute='genero', top_n=5):
    """Recomendar juegos por combinaciones de atributos."""
    df = load_games()
    
    # Validar el atributo
    if attribute not in ['genero', 'etiquetas']:
        raise ValueError("El atributo debe ser 'genero' o 'etiquetas'")
    
    # Obtener atributos del juego actual
    current_game = df[df['id'] == game_id]
    if current_game.empty:
        return pd.DataFrame()
    
    current_attributes = current_game.iloc[0][attribute]
    if not current_attributes:
        return pd.DataFrame()
    
    recommendations = pd.DataFrame()
    
    # Buscar coincidencias exactas
    recommendations = df[df[attribute] == current_attributes]
    
    # Buscar combinaciones si no hay suficientes
    if len(recommendations) < top_n:
        for i in range(len(current_attributes) - 1, 0, -1):
            for combo in combinations(current_attributes, i):
                combo_set = set(combo)
                filtered = df[df[attribute].apply(lambda x: combo_set.issubset(x))]
                recommendations = pd.concat([recommendations, filtered])
                recommendations.drop_duplicates(subset=['id'], inplace=True)
                
                if len(recommendations) >= top_n:
                    break
            if len(recommendations) >= top_n:
                break
    
    # Excluir el juego actual y ordenar
    recommendations = recommendations[recommendations['id'] != game_id]
    recommendations = recommendations.sort_values(
        by=['valoracion', 'precio'],
        ascending=[False, False]
    )
    
    return recommendations.head(top_n)

