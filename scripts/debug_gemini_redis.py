import os
from dotenv import load_dotenv
import google.generativeai as genai
import redis

def test_redis():
    print("\n=== Testing Redis Connection ===")
    host = os.getenv("REDIS_HOST", "redis")
    port = int(os.getenv("REDIS_PORT", 6379))
    pw = os.getenv("REDIS_PASSWORD")
    db = int(os.getenv("REDIS_DB", 0))
    
    print(f"Redis config: host={host}, port={port}, password={'*****' if pw else 'None'}, db={db}")
    
    try:
        client = redis.Redis(host=host, port=port, password=pw, db=db, socket_connect_timeout=5)
        if client.ping():
            print("✅ Redis connection successful!")
        else:
            print("❌ Redis ping failed!")
    except Exception as e:
        print(f"❌ Redis connection error: {str(e)}")

def test_gemini():
    print("\n=== Testing Gemini API ===")
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key configured: {'Yes' if api_key else 'No'}")
    
    try:
        genai.configure(api_key=api_key)
        print("\nListing available models:")
        models = genai.list_models()
        for m in models:
            print(f"- {m.name}")
        
        print("\nTesting simple generation with different models:")
        test_models = ["gemini-pro", "gemini-2.0-flash"]
        for model_name in test_models:
            try:
                print(f"\nTesting model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Olá, tudo bem?")
                print(f"✅ Response: {response.text}")
            except Exception as e:
                print(f"❌ Error with {model_name}: {str(e)}")
    
    except Exception as e:
        print(f"❌ Gemini API error: {str(e)}")

if __name__ == "__main__":
    print("Loading environment variables...")
    load_dotenv()
    
    test_redis()
    test_gemini()