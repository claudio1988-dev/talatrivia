# TalaTrivia

API para gestionar un juego de trivia de recursos humanos.

## Tecnologías

- **Python 3.10+**: Lenguaje principal.
- **Flask**: Framework web.
- **SQLite**: Base de datos relacional (ligera y portable).
- **SQLAlchemy**: ORM.
- **Flask-JWT-Extended**: Autenticación JWT.
- **Docker & Docker Compose**: Contenedorización para fácil despliegue.

## Cómo ejecutar el proyecto

Tienes dos opciones para ejecutar el proyecto: usando Docker (recomendado para revisión rápida) o localmente.

### Opción A: Docker (Recomendada)

Prerrequisitos: Tener instalado Docker Desktop.

1. Clonar el repositorio.
2. Navegar a la carpeta del proyecto.
3. Construir y levantar el contenedor:

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:5000`.
La base de datos SQLite se creará automáticamente en la carpeta `instance/`.

### Opción B: Ejecución Local

1. Crear un entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate # Mac/Linux
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar el servidor:
   ```bash
   python run.py
   ```

## Poblar Base de Datos (Seeding)

Para facilitar las pruebas, se incluye un script que llena la base de datos con usuarios, preguntas reales de RRHH y una simulación de juego.

**Ejecutar Seed:**

```bash
# Si usas Docker (en otra terminal)
docker-compose exec web python seed.py

# Si estás en local
python seed.py
```

Esto creará:
- **Admin**: `admin@talana.com` (Pass: `admin123`)
- **Jugadores**: `jugador1@talana.com` a `jugador5@talana.com` (Pass: `123456`)
- **Preguntas**: Sobre legislación laboral (Fácil, Media, Difícil).
- **Trivia**: "Onboarding Talana 2026".
- **Ranking**: Resultados simulados (Jugador 1 con puntaje perfecto).

## Endpoints Principales

### Autenticación
- `POST /auth/register`: Registrar usuario.
- `POST /auth/login`: Login (Devuelve JWT).

### Gestión (Admin)
- `POST /questions`: Crear pregunta (JSON incluye `options` y `difficulty`).
- `POST /trivias`: Crear trivia asignando preguntas y usuarios.
- `DELETE /questions/<id>`: Eliminar pregunta.
- `DELETE /trivias/<id>`: Eliminar trivia.

### Juego (Jugador)
- `GET /my-trivias`: Ver trivias asignadas.
- `GET /trivias/<id>/play`: Obtener preguntas para jugar.
  - **Nota**: Este endpoint NO devuelve `is_correct` ni la dificultad, para evitar trampas.
- `POST /trivias/<id>/submit`: Enviar respuestas.
  - **Puntuación**: Se calcula automáticamente: 1 pto (Fácil), 2 ptos (Media), 3 ptos (Difícil).
- `GET /trivias/<id>/ranking`: Ver tabla de posiciones ordenadas por puntaje.

