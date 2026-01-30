# TalaTrivia

API para gestionar un juego de trivia de recursos humanos.
Desarrollado como desafío técnico para postulación a Software Developer Engineer en Talana.

## Tecnologías

- **Python 3.10**: Lenguaje principal.
- **Flask**: Framework web.
- **PostgreSQL**: Base de datos relacional.
- **SQLAlchemy**: ORM.
- **Flask-JWT-Extended**: Autenticación JWT.
- **Docker & Docker Compose**: Contenedorización y orquestación.

## Cómo ejecutar el proyecto

Prerrequisitos: Tener instalado Docker y Docker Compose.

1. Clonar el repositorio (si aplica).
2. Navegar a la carpeta del proyecto.
3. Construir y levantar los contenedores:

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:5000`.

## Endpoints Principales

### Autenticación
- `POST /auth/register`: Registrar un nuevo usuario.
  - Body: `{ "name": "Juan", "email": "juan@example.com", "password": "pass", "role": "player" }`
- `POST /auth/login`: Iniciar sesión.
  - Body: `{ "email": "juan@example.com", "password": "pass" }`
  - Response: `{ "access_token": "..." }`

### Usuarios y Preguntas (Admin)
- `GET /users`: Listar usuarios.
- `POST /questions`: Crear pregunta.
  - Body: 
    ```json
    {
      "text": "¿Pregunta?",
      "difficulty": "EASY",
      "options": [
        {"text": "Opción 1", "is_correct": true},
        {"text": "Opción 2", "is_correct": false}
      ]
    }
    ```
- `GET /questions`: Listar preguntas.

### Trivias
- `POST /trivias`: Crear una trivia y asignar preguntas/usuarios.
  - Body:
    ```json
    {
      "name": "Trivia RRHH 101",
      "description": "Conceptos básicos",
      "question_ids": [1, 2],
      "user_ids": [1] 
    }
    ```
- `GET /trivias`: Listar todas las trivias.

### Juego (Jugador)
- `GET /my-trivias`: (Auth Requerido) Ver trivias asignadas al usuario actual.
- `GET /trivias/<id>/play`: (Auth Requerido) Obtener preguntas de la trivia (sin respuestas correctas).
- `POST /trivias/<id>/submit`: (Auth Requerido) Enviar respuestas.
  - Body:
    ```json
    {
      "answers": [
        {"question_id": 1, "option_id": 5},
        {"question_id": 2, "option_id": 8}
      ]
    }
    ```

### Ranking
- `GET /trivias/<id>/ranking`: Ver el ranking de usuarios para una trivia específica.

## Decisiones de Diseño y Supuestos

1. **Puntajes**: Se siguió rigurosamente la regla: Easy=1, Medium=2, Hard=3 puntos.
2. **Seguridad**: Se implementó autenticación JWT básica. Para jugar hay que estar autenticado y asignado a la trivia.
3. **Privacidad**: El endpoint de juego no devuelve el campo `is_correct` ni la `difficulty` (para no dar pistas), cumpliendo con el requisito "No les muestres cuál es la respuesta correcta ni la dificultad".
4. **Base de Datos**: Se usa PostgreSQL en Docker para persistencia robusta.
5. **Asignación**: Se asumió que las trivias son "cerradas" o "asignadas" por un admin, por lo que se crean con una lista de IDs de usuarios permitidos.

## Testing Manual (Ejemplo)

1. Registrar un usuario (`POST /auth/register`).
2. Loguearse (`POST /auth/login`) para obtener el token.
3. Crear preguntas (`POST /questions`).
4. Crear una trivia asignando al usuario y las preguntas (`POST /trivias`).
5. Usar el token para obtener las preguntas (`GET /trivias/1/play`).
6. Enviar respuestas (`POST /trivias/1/submit`).
7. Consultar ranking (`GET /trivias/1/ranking`).
