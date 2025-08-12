import random
import pandas as pd
from faker import Faker

fake = Faker()

# Configuración
NUM_USERS = 1000

# Opciones para campos personalizados
dance_styles = ['salsa', 'hiphop', 'ballet', 'contemporary', 'jazz', 'flamenco', 'breakdance']
categorias = ['tutorial', 'performance', 'freestyle', 'battle', 'class', 'challenge', 'duet']

# Generar datos
users = []

for i in range(NUM_USERS):
    name = fake.name()
    edad = random.randint(13, 60)
    dance = random.sample(dance_styles, k=random.randint(1, 3))
    favoritas = random.sample(categorias, k=random.randint(2, 4))

    users.append({
        'id': i,
        'name': name,
        'edad': edad,
        'danceStyles': dance,
        'categorias_preferidas': favoritas
    })
# Usuario 1 adicional para pruebas
users.append({
    'id': NUM_USERS,
    'name': "Walter White",
    'edad': 50,
    'danceStyles': ['jazz'] ,
    'categorias_preferidas': ['tutorial', 'challenge']
})

# Usuario 2 adicional para pruebas
users.append({
    'id': NUM_USERS+1,
    'name': "Manolo",
    'edad': 35,
    'danceStyles': ['salsa', 'flamenco'] ,
    'categorias_preferidas': ['duet']
})

# Usuario 3 adicional para pruebas
users.append({
    'id': NUM_USERS+2,
    'name': "Emo",
    'edad': 27,
    'danceStyles': ['hiphop', 'breakdance'] ,
    'categorias_preferidas': ['freestyle', 'battle', 'challenge']
})


# Convertir a DataFrame
df = pd.DataFrame(users)

# Guardar como CSV
df.to_csv("usuarios.csv", index=False)

print(f"Generados {NUM_USERS} usuarios en 'usuarios.csv'")