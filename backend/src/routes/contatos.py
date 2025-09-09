from flask import Blueprint, request, jsonify
from src.auth import token_required
from src.database import get_supabase
import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)

contatos_bp = Blueprint('contatos', __name__)

@contatos_bp.route('/', methods=['GET'])
@token_required
def get_contatos():
    """Lista contatos da empresa"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '')
        
        offset = (page - 1) * per_page
        
        contatos = db.get_contatos(empresa_id, per_page, offset)
        
        # Se houver busca, filtrar localmente (idealmente seria no banco)
        if search:
            contatos = [c for c in contatos if search.lower() in c['nome'].lower() or 
                       (c['telefone'] and search in c['telefone']) or
                       (c['email'] and search.lower() in c['email'].lower())]
        
        return jsonify({
            'contatos': contatos,
            'page': page,
            'per_page': per_page,
            'total': len(contatos)
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar contatos: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@contatos_bp.route('/', methods=['POST'])
@token_required
def create_contato():
    """Cria novo contato"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        nome = data.get('nome')
        telefone = data.get('telefone')
        email = data.get('email')
        
        if not nome:
            return jsonify({'message': 'Nome é obrigatório'}), 400
        
        if not telefone and not email:
            return jsonify({'message': 'Telefone ou email é obrigatório'}), 400
        
        db = get_supabase()
        
        contato_data = {
            'empresa_id': request.current_user['empresa_id'],
            'nome': nome,
            'telefone': telefone,
            'email': email,
            'documento': data.get('documento'),
            'endereco': data.get('endereco'),
            'campos_customizados': data.get('campos_customizados', {}),
            'tags': data.get('tags', []),
            'origem': 'manual'
        }
        
        contato = db.create_contato(contato_data)
        
        if contato:
            return jsonify({
                'message': 'Contato criado com sucesso',
                'contato': contato
            }), 201
        else:
            return jsonify({'message': 'Erro ao criar contato'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao criar contato: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@contatos_bp.route('/<contato_id>', methods=['PUT'])
@token_required
def update_contato(contato_id):
    """Atualiza contato"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        db = get_supabase()
        
        # Remover campos que não devem ser atualizados
        update_data = {k: v for k, v in data.items() 
                      if k not in ['id', 'empresa_id', 'created_at', 'updated_at']}
        
        contato = db.update_contato(contato_id, update_data)
        
        if contato:
            return jsonify({
                'message': 'Contato atualizado com sucesso',
                'contato': contato
            }), 200
        else:
            return jsonify({'message': 'Contato não encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao atualizar contato: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@contatos_bp.route('/<contato_id>', methods=['DELETE'])
@token_required
def delete_contato(contato_id):
    """Deleta contato"""
    try:
        db = get_supabase()
        
        success = db.delete_contato(contato_id)
        
        if success:
            return jsonify({'message': 'Contato deletado com sucesso'}), 200
        else:
            return jsonify({'message': 'Contato não encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao deletar contato: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@contatos_bp.route('/import', methods=['POST'])
@token_required
def import_contatos():
    """Importa contatos de arquivo CSV/Excel"""
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'Arquivo não fornecido'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar extensão do arquivo
        allowed_extensions = {'csv', 'xlsx', 'xls'}
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({'message': 'Formato de arquivo não suportado. Use CSV ou Excel'}), 400
        
        # Ler arquivo
        try:
            if file_extension == 'csv':
                df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'message': f'Erro ao ler arquivo: {str(e)}'}), 400
        
        # Validar colunas obrigatórias
        required_columns = ['nome']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                'message': f'Colunas obrigatórias não encontradas: {", ".join(missing_columns)}'
            }), 400
        
        # Preparar dados para inserção
        contatos_data = []
        empresa_id = request.current_user['empresa_id']
        
        for _, row in df.iterrows():
            # Pular linhas com nome vazio
            if pd.isna(row['nome']) or str(row['nome']).strip() == '':
                continue
            
            contato_data = {
                'empresa_id': empresa_id,
                'nome': str(row['nome']).strip(),
                'telefone': str(row.get('telefone', '')).strip() if not pd.isna(row.get('telefone')) else None,
                'email': str(row.get('email', '')).strip() if not pd.isna(row.get('email')) else None,
                'documento': str(row.get('documento', '')).strip() if not pd.isna(row.get('documento')) else None,
                'endereco': str(row.get('endereco', '')).strip() if not pd.isna(row.get('endereco')) else None,
                'origem': 'importacao'
            }
            
            # Validar se tem pelo menos telefone ou email
            if not contato_data['telefone'] and not contato_data['email']:
                continue
            
            contatos_data.append(contato_data)
        
        if not contatos_data:
            return jsonify({'message': 'Nenhum contato válido encontrado no arquivo'}), 400
        
        # Inserir contatos no banco
        db = get_supabase()
        success = db.bulk_create_contatos(contatos_data)
        
        if success:
            return jsonify({
                'message': f'{len(contatos_data)} contatos importados com sucesso',
                'total_importados': len(contatos_data)
            }), 201
        else:
            return jsonify({'message': 'Erro ao importar contatos'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao importar contatos: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@contatos_bp.route('/export', methods=['GET'])
@token_required
def export_contatos():
    """Exporta contatos para CSV"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        # Buscar todos os contatos
        contatos = db.get_contatos(empresa_id, 10000, 0)  # Limite alto para pegar todos
        
        if not contatos:
            return jsonify({'message': 'Nenhum contato encontrado'}), 404
        
        # Converter para DataFrame
        df = pd.DataFrame(contatos)
        
        # Selecionar apenas colunas relevantes
        columns_to_export = ['nome', 'telefone', 'email', 'documento', 'endereco', 'status', 'created_at']
        df = df[columns_to_export]
        
        # Converter para CSV
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        csv_data = output.getvalue()
        
        from flask import Response
        
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=contatos.csv'}
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar contatos: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@contatos_bp.route('/stats', methods=['GET'])
@token_required
def get_contatos_stats():
    """Retorna estatísticas dos contatos"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        # Buscar todos os contatos para calcular estatísticas
        contatos = db.get_contatos(empresa_id, 10000, 0)
        
        total = len(contatos)
        ativos = len([c for c in contatos if c['status'] == 'ativo'])
        com_telefone = len([c for c in contatos if c['telefone']])
        com_email = len([c for c in contatos if c['email']])
        
        return jsonify({
            'total': total,
            'ativos': ativos,
            'inativos': total - ativos,
            'com_telefone': com_telefone,
            'com_email': com_email,
            'sem_contato': total - com_telefone - com_email
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

