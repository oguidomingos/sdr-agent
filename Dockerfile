# Use a imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Copia o arquivo .env
COPY .env .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Define as variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expõe a porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["python", "main.py"]