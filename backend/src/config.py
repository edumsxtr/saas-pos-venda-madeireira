import os
from datetime import timedelta
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

class Config:
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-super-segura-aqui'
    
    # Configurações do Supabase
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or 'https://seu-projeto.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY') or 'sua-chave-supabase-aqui'
    
    # Configurações JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurações Evolution API
    EVOLUTION_API_URL = os.environ.get('EVOLUTION_API_URL') or 'http://localhost:8080'
    EVOLUTION_API_KEY = os.environ.get('EVOLUTION_API_KEY') or 'sua-chave-evolution-api'
    
    # Configurações n8n
    N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL') or 'http://localhost:5678/webhook'
    N8N_API_KEY = os.environ.get('N8N_API_KEY') or 'sua-chave-n8n'
    
    # Configurações CORS
    CORS_ORIGINS = [
        'http://localhost:3000', 
        'http://localhost:5173',
        'https://5173-im9ilwdj0kvro4mpk0avv-e63b1b68.manusvm.computer'
    ]
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

