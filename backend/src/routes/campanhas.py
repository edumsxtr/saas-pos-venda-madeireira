from flask import Blueprint, request, jsonify
from src.auth import token_required
from src.database import get_supabase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

campanhas_bp = Blueprint('campanhas', __name__)

@campanhas_bp.route('/', methods=['GET'])
@token_required
def get_campanhas():
    """Lista campanhas da empresa"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        campanhas = db.get_campanhas(empresa_id)
        
        return jsonify({
            'campanhas': campanhas
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar campanhas: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campanhas_bp.route('/', methods=['POST'])
@token_required
def create_campanha():
    """Cria nova campanha"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        nome = data.get('nome')
        tipo = data.get('tipo')
        canal = data.get('canal')
        template_mensagem = data.get('template_mensagem')
        
        # Validações
        if not all([nome, tipo, canal, template_mensagem]):
            return jsonify({'message': 'Nome, tipo, canal e template da mensagem são obrigatórios'}), 400
        
        tipos_validos = ['saudacao', 'pesquisa', 'follow_up', 'promocional']
        if tipo not in tipos_validos:
            return jsonify({'message': f'Tipo deve ser um dos: {", ".join(tipos_validos)}'}), 400
        
        canais_validos = ['whatsapp', 'sms', 'email']
        if canal not in canais_validos:
            return jsonify({'message': f'Canal deve ser um dos: {", ".join(canais_validos)}'}), 400
        
        db = get_supabase()
        
        campanha_data = {
            'empresa_id': request.current_user['empresa_id'],
            'nome': nome,
            'descricao': data.get('descricao'),
            'tipo': tipo,
            'canal': canal,
            'template_mensagem': template_mensagem,
            'configuracoes': data.get('configuracoes', {}),
            'status': 'rascunho'
        }
        
        # Se houver agendamento
        agendamento = data.get('agendamento')
        if agendamento:
            try:
                campanha_data['agendamento'] = datetime.fromisoformat(agendamento.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Formato de data inválido para agendamento'}), 400
        
        campanha = db.create_campanha(campanha_data)
        
        if campanha:
            return jsonify({
                'message': 'Campanha criada com sucesso',
                'campanha': campanha
            }), 201
        else:
            return jsonify({'message': 'Erro ao criar campanha'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao criar campanha: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campanhas_bp.route('/<campanha_id>', methods=['PUT'])
@token_required
def update_campanha(campanha_id):
    """Atualiza campanha"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Dados não fornecidos'}), 400
        
        db = get_supabase()
        
        # Remover campos que não devem ser atualizados
        update_data = {k: v for k, v in data.items() 
                      if k not in ['id', 'empresa_id', 'created_at', 'updated_at']}
        
        # Validar agendamento se fornecido
        if 'agendamento' in update_data and update_data['agendamento']:
            try:
                update_data['agendamento'] = datetime.fromisoformat(update_data['agendamento'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Formato de data inválido para agendamento'}), 400
        
        campanha = db.update_campanha(campanha_id, update_data)
        
        if campanha:
            return jsonify({
                'message': 'Campanha atualizada com sucesso',
                'campanha': campanha
            }), 200
        else:
            return jsonify({'message': 'Campanha não encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao atualizar campanha: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campanhas_bp.route('/<campanha_id>/execute', methods=['POST'])
@token_required
def execute_campanha(campanha_id):
    """Executa campanha (dispara mensagens)"""
    try:
        data = request.get_json() or {}
        
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        # Buscar campanha
        campanhas = db.get_campanhas(empresa_id)
        campanha = next((c for c in campanhas if c['id'] == campanha_id), None)
        
        if not campanha:
            return jsonify({'message': 'Campanha não encontrada'}), 404
        
        if campanha['status'] not in ['rascunho', 'pausada']:
            return jsonify({'message': 'Campanha não pode ser executada no status atual'}), 400
        
        # Buscar contatos para a campanha
        contatos_ids = data.get('contatos_ids', [])
        
        if not contatos_ids:
            # Se não especificou contatos, usar todos os contatos ativos
            contatos = db.get_contatos(empresa_id, 10000, 0)
            contatos_ids = [c['id'] for c in contatos if c['status'] == 'ativo']
        
        if not contatos_ids:
            return jsonify({'message': 'Nenhum contato encontrado para a campanha'}), 400
        
        # Criar disparos para cada contato
        disparos_criados = 0
        
        for contato_id in contatos_ids:
            disparo_data = {
                'campanha_id': campanha_id,
                'contato_id': contato_id,
                'canal': campanha['canal'],
                'mensagem': campanha['template_mensagem'],
                'status': 'pendente'
            }
            
            disparo = db.create_disparo(disparo_data)
            if disparo:
                disparos_criados += 1
        
        # Atualizar status da campanha
        db.update_campanha(campanha_id, {
            'status': 'executando',
            'total_contatos': len(contatos_ids)
        })
        
        # Aqui você integraria com n8n para processar os disparos
        # Por enquanto, vamos simular o envio
        
        return jsonify({
            'message': f'Campanha executada com sucesso. {disparos_criados} disparos criados.',
            'disparos_criados': disparos_criados
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao executar campanha: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campanhas_bp.route('/<campanha_id>/pause', methods=['POST'])
@token_required
def pause_campanha(campanha_id):
    """Pausa campanha"""
    try:
        db = get_supabase()
        
        campanha = db.update_campanha(campanha_id, {'status': 'pausada'})
        
        if campanha:
            return jsonify({
                'message': 'Campanha pausada com sucesso',
                'campanha': campanha
            }), 200
        else:
            return jsonify({'message': 'Campanha não encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao pausar campanha: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campanhas_bp.route('/<campanha_id>/resume', methods=['POST'])
@token_required
def resume_campanha(campanha_id):
    """Retoma campanha pausada"""
    try:
        db = get_supabase()
        
        campanha = db.update_campanha(campanha_id, {'status': 'executando'})
        
        if campanha:
            return jsonify({
                'message': 'Campanha retomada com sucesso',
                'campanha': campanha
            }), 200
        else:
            return jsonify({'message': 'Campanha não encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao retomar campanha: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campanhas_bp.route('/<campanha_id>/cancel', methods=['POST'])
@token_required
def cancel_campanha(campanha_id):
    """Cancela campanha"""
    try:
        db = get_supabase()
        
        campanha = db.update_campanha(campanha_id, {'status': 'cancelada'})
        
        if campanha:
            return jsonify({
                'message': 'Campanha cancelada com sucesso',
                'campanha': campanha
            }), 200
        else:
            return jsonify({'message': 'Campanha não encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao cancelar campanha: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campanhas_bp.route('/<campanha_id>/stats', methods=['GET'])
@token_required
def get_campanha_stats(campanha_id):
    """Retorna estatísticas da campanha"""
    try:
        db = get_supabase()
        
        # Buscar métricas da campanha usando a view
        client = db.get_client()
        response = client.table('vw_metricas_campanhas').select('*').eq('id', campanha_id).execute()
        
        if response.data:
            return jsonify({
                'stats': response.data[0]
            }), 200
        else:
            return jsonify({'message': 'Campanha não encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas da campanha: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@campanhas_bp.route('/templates', methods=['GET'])
@token_required
def get_templates():
    """Retorna templates de mensagem pré-definidos"""
    templates = {
        'saudacao': [
            {
                'nome': 'Saudação Padrão',
                'template': 'Olá {nome}! Obrigado por escolher a Madeireira Cambará. Como foi sua experiência conosco?'
            },
            {
                'nome': 'Saudação Formal',
                'template': 'Prezado(a) {nome}, agradecemos pela confiança em nossos produtos. Gostaríamos de saber sua opinião sobre nosso atendimento.'
            }
        ],
        'pesquisa': [
            {
                'nome': 'Pesquisa de Satisfação',
                'template': 'Olá {nome}! Em uma escala de 1 a 10, como você avalia nosso atendimento? Sua opinião é muito importante para nós!'
            },
            {
                'nome': 'NPS Simples',
                'template': 'Oi {nome}! Você recomendaria a Madeireira Cambará para um amigo? Responda de 0 a 10.'
            }
        ],
        'follow_up': [
            {
                'nome': 'Follow-up Padrão',
                'template': 'Olá {nome}! Tudo certo com sua compra? Se precisar de algo, estamos aqui para ajudar!'
            }
        ]
    }
    
    return jsonify({'templates': templates}), 200

