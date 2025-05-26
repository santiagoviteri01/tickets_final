FROM python:3.9-slim 
WORKDIR /app

# 1) Instala dependencias del SO (cacheable)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 \
        libpango-1.0-0 libharfbuzz-dev libcairo2 \
        fonts-liberation fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# 2) Copia y instala deps de Python (cacheable)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copia sólo tu tema de Streamlit
COPY .streamlit /root/.streamlit

# 4) Copia únicamente main.py
COPY main.py dashboard.py .

# 5) Copia las carpetas que realmente existen en tu proyecto

COPY archivos_coberturas ./archivos_coberturas
COPY images ./images

# 6) Arranque
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
