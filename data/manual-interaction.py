import pandas as pd
import random
from faker import Faker

CATEGORIAS = ['tutorial', 'performance', 'freestyle', 'battle', 'class', 'challenge', 'duet']
ETIQUETAS_POSIBLES = ['energia', 'nivel_facil', 'nivel_medio', 'nivel_avanzado', 'pareja', 'grupo', 'solo', 'ritmo', 'coreografia', 'creatividad']
DANCE_STYLES = ['salsa', 'hiphop', 'ballet', 'contemporary', 'jazz', 'flamenco', 'breakdance']

# Carga de datos
inter_df = pd.read_csv("interacciones.csv")

# Nuevas interacciones
nuevas_filas = [
    # Walter White
    {'id': 100000, 'user_id': 1000, 'video_id': 2, 'like': 1, 'comentario': "Say my name", 'watchtime': 60, 'dont_suggest': 0},
    {'id': 100001, 'user_id': 1000, 'video_id': 30, 'like': 0, 'comentario': "More", 'watchtime': 10, 'dont_suggest': 0},
    {'id': 100002, 'user_id': 1000, 'video_id': 40, 'like': 1, 'comentario': "More", 'watchtime': 120, 'dont_suggest': 0},
    {'id': 100003, 'user_id': 1000, 'video_id': 42, 'like': 0, 'comentario': None, 'watchtime': 2, 'dont_suggest': 0},

    # Manolo Pacolo
    {'id': 100004, 'user_id': 1001, 'video_id': 189, 'like': 1, 'comentario': "Genial", 'watchtime': 120, 'dont_suggest': 0},
    {'id': 100005, 'user_id': 1001, 'video_id': 248, 'like': 0, 'comentario': None, 'watchtime': 5, 'dont_suggest': 0},
    {'id': 100006, 'user_id': 1001, 'video_id': 268, 'like': 1, 'comentario': None, 'watchtime': 35, 'dont_suggest': 0},
    {'id': 100007, 'user_id': 1001, 'video_id': 440, 'like': 1, 'comentario': "Me encanta mucho", 'watchtime': 130, 'dont_suggest': 0},

    # Emo
    {'id': 100008, 'user_id': 1002, 'video_id': 27, 'like': 1, 'comentario': "Good Content", 'watchtime': 60, 'dont_suggest': 0},
    {'id': 100009, 'user_id': 1002, 'video_id': 43, 'like': 1, 'comentario': "Keep up", 'watchtime': 80, 'dont_suggest': 0},
    {'id': 100010, 'user_id': 1002, 'video_id': 68, 'like': 0, 'comentario': None, 'watchtime': 3, 'dont_suggest': 0},
    {'id': 100011, 'user_id': 1002, 'video_id': 58, 'like': 0, 'comentario': "Cringe", 'watchtime': 10, 'dont_suggest': 1},
    {'id': 100012, 'user_id': 1002, 'video_id': 421, 'like': 1, 'comentario': "Good stuff", 'watchtime': 50, 'dont_suggest': 0},

    # Walter White extra
    {'id': 100013, 'user_id': 1000, 'video_id': 105, 'like': 1, 'comentario': "Me gusta!", 'watchtime': 80, 'dont_suggest': 0}
]

# Añadir las nuevas filas al DataFrame original
inter_df = pd.concat([inter_df, pd.DataFrame(nuevas_filas)], ignore_index=True)

# Puedes guardar el nuevo DataFrame si lo necesitas
# inter_df.to_csv("interacciones_actualizado.csv", index=False)
inter_df.to_csv("interacciones2.csv", index=False)
print("Interacciones generadas:", len(inter_df))