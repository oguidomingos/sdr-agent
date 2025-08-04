"""
Versão simplificada da API para testar CORS
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="SDR Agent Test API")

# Configure CORS - versão simplificada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=False,  # Deve ser False quando origins = "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400
)

@app.get("/")
async def root():
    return {"message": "Test API funcionando", "cors": "enabled"}

@app.get("/health")
async def health():
    return {"status": "healthy", "cors": "working"}

@app.post("/test-cors")
async def test_cors():
    return {"message": "CORS POST funcionando"}

# Handler para Vercel
def handler(request):
    return app(request)