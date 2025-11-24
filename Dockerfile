# Imagem base leve com Python 3.11
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia apenas requirements primeiro para otimizar cache
COPY backend/requirements.txt ./requirements.txt

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . .

# Gera o índice FAISS a partir dos PDFs
RUN python backend/init_index.py

# Expõe a porta padrão do Hugging Face Spaces
EXPOSE 7860

# Comando para rodar FastAPI via Uvicorn
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "7860"]
