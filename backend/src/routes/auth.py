from flask import Blueprint, request, jsonify
from src.auth import AuthService
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email e senha são obrigatórios'}), 400
        
        result = AuthService.login(email, password)
        
        if result['success']:
            return jsonify({
                'message': 'Login realizado com sucesso',
                'user': result['user'],
                'tokens': result['tokens']
            }), 200
        else:
            return jsonify({'message': result['message']}), 401
            
    except Exception as e:
        logger.error(f"Erro no endpoint de login: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint de registro"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        nome = data.get('nome')
        email = data.get('email')
        password = data.get('password')
        empresa_nome = data.get('empresa_nome')
        empresa_slug = data.get('empresa_slug')
        
        # Validações
        if not all([nome, email, password, empresa_nome, empresa_slug]):
            return jsonify({'message': 'Todos os campos são obrigatórios'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        # Validar formato do slug (apenas letras, números e hífens)
        import re
        if not re.match(r'^[a-z0-9-]+$', empresa_slug):
            return jsonify({'message': 'Slug da empresa deve conter apenas letras minúsculas, números e hífens'}), 400
        
        result = AuthService.register(nome, email, password, empresa_nome, empresa_slug)
        
        if result['success']:
            return jsonify({
                'message': 'Registro realizado com sucesso',
                'user': result['user'],
                'tokens': result['tokens']
            }), 201
        else:
            return jsonify({'message': result['message']}), 400
            
    except Exception as e:
        logger.error(f"Erro no endpoint de registro: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Endpoint para renovar token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'message': 'Refresh token é obrigatório'}), 400
        
        result = AuthService.refresh_token(refresh_token)
        
        if result['success']:
            return jsonify({
                'message': 'Token renovado com sucesso',
                'tokens': result['tokens']
            }), 200
        else:
            return jsonify({'message': result['message']}), 401
            
    except Exception as e:
        logger.error(f"Erro no endpoint de refresh: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/me', methods=['GET'])
def me():
    """Endpoint para obter dados do usuário atual"""
    from src.auth import token_required
    
    @token_required
    def get_current_user():
        try:
            from src.database import get_supabase
            
            db = get_supabase()
            user = db.get_user_by_email(request.current_user['email'])
            
            if not user:
                return jsonify({'message': 'Usuário não encontrado'}), 404
            
            # Buscar dados da empresa
            empresa = db.get_empresa_by_slug(user['empresa_id'])
            
            return jsonify({
                'user': {
                    'id': user['id'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'perfil': user['perfil'],
                    'ultimo_login': user.get('ultimo_login'),
                    'empresa': empresa
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erro no endpoint /me: {e}")
            return jsonify({'message': 'Erro interno do servidor'}), 500
    
    return get_current_user()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint de logout (apenas retorna sucesso, pois JWT é stateless)"""
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

