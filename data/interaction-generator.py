import pandas as pd
import random
from faker import Faker

fake = Faker()

# Constantes
NUM_INTERACCIONES = 100000
CATEGORIAS = ['tutorial', 'performance', 'freestyle', 'battle', 'class', 'challenge', 'duet']
ETIQUETAS_POSIBLES = ['energia', 'nivel_facil', 'nivel_medio', 'nivel_avanzado', 'pareja', 'grupo', 'solo', 'ritmo', 'coreografia', 'creatividad']
DANCE_STYLES = ['salsa', 'hiphop', 'ballet', 'contemporary', 'jazz', 'flamenco', 'breakdance']

# Carga de datos
users_df = pd.read_csv("usuarios_2.csv")
videos_df = pd.read_csv("videos.csv")

# Aseguramos que los IDs estén en listas
user_ids = users_df['id'].tolist()
video_ids = videos_df['id'].tolist()

# Convertimos videos a diccionario para acceso rápido
videos_dict = videos_df.set_index('id').to_dict(orient='index')

# Creamos las interacciones
interacciones = []
for i in range(NUM_INTERACCIONES):
    user = users_df.sample(1).iloc[0]
    video_id = random.choice(video_ids)
    video = videos_dict[video_id]

    # Preferencias del usuario (simulamos que tiene columnas 'categorias_preferidas' y 'estilos_preferidos')
    categorias_preferidas = eval(user.get('categorias_preferidas', '[]'))
    estilos_preferidos = eval(user.get('estilos_preferidos', '[]'))

    # Categoría y estilo del video
    video_categoria = video.get('categoria')
    video_estilo = video.get('estilo')

    # Like probability
    like_prob = 0.7 if (video_categoria in categorias_preferidas or video_estilo in estilos_preferidos) else 0.1
    like = int(random.random() < like_prob)

    # Watchtime (mayor si hay like)
    watchtime = round(random.uniform(60.0, 600.0) if like else random.uniform(5.0, 60.0), 2)

    # Comentario (50% chance)
    comentario = fake.sentence(nb_words=10) if random.random() < 0.5 else None

    # Dont suggest (1% chance)
    dont_suggest = int(random.random() < 0.01)

    # Guardamos la interacción
    interacciones.append({
        'id': i,
        'user_id': user['id'],
        'video_id': video_id,
        'like': like,
        'comentario': comentario,
        'watchtime': watchtime,
        'dont_suggest': dont_suggest
    })

# Guardamos en CSV
interacciones_df = pd.DataFrame(interacciones)
interacciones_df.to_csv("interacciones.csv", index=False)
print("Interacciones generadas:", len(interacciones_df))
