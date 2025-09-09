import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from src.database import get_supabase
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash da senha"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifica se a senha está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_tokens(user_data: dict) -> dict:
        """Gera tokens JWT de acesso e refresh"""
        now = datetime.utcnow()
        
        # Payload comum
        payload = {
            'user_id': user_data['id'],
            'empresa_id': user_data['empresa_id'],
            'email': user_data['email'],
            'perfil': user_data['perfil']
        }
        
        # Token de acesso (1 hora)
        access_payload = {
            **payload,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(hours=1)
        }
        
        # Token de refresh (30 dias)
        refresh_payload = {
            **payload,
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=30)
        }
        
        access_token = jwt.encode(access_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600  # 1 hora em segundos
        }
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('Token expirado')
        except jwt.InvalidTokenError:
            raise Exception('Token inválido')
    
    @staticmethod
    def login(email: str, password: str) -> dict:
        """Realiza login do usuário"""
        try:
            db = get_supabase()
            
            # Buscar usuário por email
            user = db.get_user_by_email(email)
            if not user:
                raise Exception('Email ou senha incorretos')
            
            # Verificar senha
            if not AuthService.verify_password(password, user['senha_hash']):
                raise Exception('Email ou senha incorretos')
            
            # Atualizar último login
            db.update_user_last_login(user['id'])
            
            # Gerar tokens
            tokens = AuthService.generate_tokens(user)
            
            # Buscar dados da empresa
            empresa = db.get_empresa_by_slug(user['empresa_id'])
            
            return {
                'success': True,
                'user': {
                    'id': user['id'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'perfil': user['perfil'],
                    'empresa': empresa
                },
                'tokens': tokens
            }
            
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def register(nome: str, email: str, password: str, empresa_nome: str, empresa_slug: str) -> dict:
        """Registra novo usuário e empresa"""
        try:
            db = get_supabase()
            
            # Verificar se email já existe
            existing_user = db.get_user_by_email(email)
            if existing_user:
                raise Exception('Email já está em uso')
            
            # Verificar se slug da empresa já existe
            existing_empresa = db.get_empresa_by_slug(empresa_slug)
            if existing_empresa:
                raise Exception('Nome da empresa já está em uso')
            
            # Criar empresa
            empresa_data = {
                'nome': empresa_nome,
                'slug': empresa_slug,
                'email': email,
                'status': 'ativo'
            }
            
            empresa = db.create_empresa(empresa_data)
            if not empresa:
                raise Exception('Erro ao criar empresa')
            
            # Criar usuário admin
            user_data = {
                'empresa_id': empresa['id'],
                'nome': nome,
                'email': email,
                'senha_hash': AuthService.hash_password(password),
                'perfil': 'admin',
                'ativo': True
            }
            
            user = db.create_user(user_data)
            if not user:
                raise Exception('Erro ao criar usuário')
            
            # Gerar tokens
            user_with_empresa = {**user, 'empresa_id': empresa['id']}
            tokens = AuthService.generate_tokens(user_with_empresa)
            
            return {
                'success': True,
                'user': {
                    'id': user['id'],
                    'nome': user['nome'],
                    'email': user['email'],
                    'perfil': user['perfil'],
                    'empresa': empresa
                },
                'tokens': tokens
            }
            
        except Exception as e:
            logger.error(f"Erro no registro: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        """Renova token de acesso usando refresh token"""
        try:
            # Verificar refresh token
            payload = AuthService.verify_token(refresh_token)
            
            if payload.get('type') != 'refresh':
                raise Exception('Token de refresh inválido')
            
            # Buscar usuário atualizado
            db = get_supabase()
            user = db.get_user_by_email(payload['email'])
            
            if not user or not user['ativo']:
                raise Exception('Usuário inativo ou não encontrado')
            
            # Gerar novo token de acesso
            tokens = AuthService.generate_tokens(user)
            
            return {
                'success': True,
                'tokens': tokens
            }
            
        except Exception as e:
            logger.error(f"Erro ao renovar token: {e}")
            return {
                'success': False,
                'message': str(e)
            }

def token_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token no header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token malformado'}), 401
        
        if not token:
            return jsonify({'message': 'Token de acesso requerido'}), 401
        
        try:
            # Verificar token
            payload = AuthService.verify_token(token)
            
            if payload.get('type') != 'access':
                return jsonify({'message': 'Tipo de token inválido'}), 401
            
            # Adicionar dados do usuário ao request
            request.current_user = {
                'id': payload['user_id'],
                'empresa_id': payload['empresa_id'],
                'email': payload['email'],
                'perfil': payload['perfil']
            }
            
        except Exception as e:
            return jsonify({'message': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator para rotas que requerem perfil admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'message': 'Usuário não autenticado'}), 401
        
        if request.current_user['perfil'] != 'admin':
            return jsonify({'message': 'Acesso negado. Requer perfil de administrador'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

