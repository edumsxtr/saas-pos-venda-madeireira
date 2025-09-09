import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.config import config
from src.database import init_supabase

# Importar blueprints
from src.routes.auth import auth_bp
from src.routes.contatos import contatos_bp
from src.routes.campanhas import campanhas_bp
from src.routes.dashboard import dashboard_bp
from src.routes.whatsapp import whatsapp_bp

def create_app(config_name='default'):
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configurações
    app.config.from_object(config[config_name])
    
    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Inicializar Supabase
    try:
        init_supabase(app.config.get('SUPABASE_URL'), app.config.get('SUPABASE_KEY'))
    except Exception as e:
        print(f"Aviso: Erro ao inicializar Supabase: {e}")
        print("Configure as variáveis SUPABASE_URL e SUPABASE_KEY")
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contatos_bp, url_prefix='/api/contatos')
    app.register_blueprint(campanhas_bp, url_prefix='/api/campanhas')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(whatsapp_bp, url_prefix='/api/whatsapp')
    
    # Rota de health check
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'SaaS Pós-Venda API está funcionando',
            'version': '1.0.0'
        })
    
    # Servir frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return jsonify({
                    'message': 'Frontend não encontrado. Deploy o frontend React na pasta static.',
                    'api_status': 'ok'
                }), 200
    
    return app

app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
