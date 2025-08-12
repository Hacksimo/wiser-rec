import random
import pandas as pd
from faker import Faker

fake = Faker()

# Configuración
NUM_VIDEOS = 500

# Categorías y etiquetas posibles
categorias = ['tutorial', 'performance', 'freestyle', 'battle', 'class', 'challenge', 'duet']
etiquetas_posibles = ['energia', 'nivel_facil', 'nivel_medio', 'nivel_avanzado', 'pareja', 'grupo', 'solo', 'ritmo', 'coreografia', 'creatividad']
DANCE_STYLES = ['salsa', 'hiphop', 'ballet', 'contemporary', 'jazz', 'flamenco', 'breakdance']

# Generar vídeos
videos = []

for i in range(NUM_VIDEOS):
    title = fake.sentence(nb_words=random.randint(2, 5)).rstrip(".")
    categoria = random.choice(categorias)
    etiquetas = random.sample(etiquetas_posibles, k=random.randint(2, 5))
    estilo = random.sample(DANCE_STYLES, k=random.randint(1, 2))

    videos.append({
        'id': i,
        'videoTitle': title,
        'etiquetas': etiquetas,
        'categoria': categoria,
        'estilo': estilo
    })

# Convertir a DataFrame
df_videos = pd.DataFrame(videos)

# Guardar como CSV
df_videos.to_csv("videos.csv", index=False)

print(f"Generados {NUM_VIDEOS} vídeos en 'videos.csv'")
