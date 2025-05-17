FROM python:3.9-slim 
WORKDIR /app

# Instala LibreOffice, OpenCV deps y otras dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        libgl1 \
        libpango-1.0-0 \
        libharfbuzz-dev \
        libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Copia TODO el contenido del repositorio al contenedor
COPY . .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
