import uvicorn
import os
from dotenv import load_dotenv

from src.api.routes import app
from src.config.settings import settings


def main():
    """
    Função principal para iniciar o servidor FastAPI
    """
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Configura o uvicorn
    config = {
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.DEBUG,
        "workers": os.cpu_count(),
        "log_level": "debug" if settings.DEBUG else "info"
    }
    
    # Inicia o servidor
    print(f"Iniciando servidor em {config['host']}:{config['port']}")
    uvicorn.run("main:app", **config)


if __name__ == "__main__":
    main()