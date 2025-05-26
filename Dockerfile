FROM python:3.9-slim 
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        libpango-1.0-0 \
        libharfbuzz-dev \
        libcairo2 \
        fonts-liberation \
        fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*
# 2) Instalamos pip (cacheado)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 3) Copiamos la configuración de tema de Streamlit
#    (tu .streamlit/config.toml con los colores)
COPY .streamlit /app/.streamlit

# 4) Copiamos el resto de tu código
COPY . .
# 5) Arranque
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
