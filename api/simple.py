"""
API mais simples possível para testar CORS
"""

def handler(request):
    """Handler básico para Vercel"""
    
    # Headers CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json'
    }
    
    # Se for preflight request (OPTIONS)
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': '{"status": "ok"}'
        }
    
    # Resposta normal
    body = '{"message": "API funcionando", "cors": "enabled", "method": "' + request.get('method', 'GET') + '"}'
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': body
    }