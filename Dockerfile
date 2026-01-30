# Usa una imagen oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requerimientos e instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto
COPY . .

# Expone el puerto en el que corre tu app (ejemplo: 5000 para Flask)
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "run.py"]