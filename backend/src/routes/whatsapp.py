from flask import Blueprint, request, jsonify
from src.evolution_api import init_evolution_api
from src.database import get_supabase
from src.auth import token_required
import os
from datetime import datetime

whatsapp_bp = Blueprint('whatsapp', __name__)

# Configurações da Evolution API
EVOLUTION_API_URL = os.environ.get('EVOLUTION_API_URL', 'http://31.97.95.124:8080')
EVOLUTION_API_KEY = os.environ.get('EVOLUTION_API_KEY', 'B6DDUF2BF4-4D81-4B5C-9618-E5DDCE9C4C26')
INSTANCE_NAME = "cambara"

@whatsapp_bp.route('/status', methods=['GET'])
@token_required
def get_whatsapp_status(current_user):
    """Verifica status da instância WhatsApp"""
    try:
        evolution = init_evolution_api(EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME)
        status = evolution.get_instance_status()
        
        return jsonify({
            "success": True,
            "status": status,
            "instance": INSTANCE_NAME
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@whatsapp_bp.route('/send-message', methods=['POST'])
@token_required
def send_whatsapp_message(current_user):
    """Envia mensagem individual via WhatsApp"""
    try:
        data = request.get_json()
        number = data.get('number')
        message = data.get('message')
        
        if not number or not message:
            return jsonify({"success": False, "error": "Número e mensagem são obrigatórios"}), 400
        
        evolution = init_evolution_api(EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME)
        result = evolution.send_text_message(number, message)
        
        # Salvar disparo no banco
        supabase = get_supabase()
        disparo_data = {
            "empresa_id": current_user['empresa_id'],
            "canal": "whatsapp",
            "mensagem": message,
            "status": "enviado" if not result.get('error') else "erro",
            "external_id": result.get('key', {}).get('id') if result.get('key') else None,
            "erro_mensagem": result.get('error') if result.get('error') else None
        }
        
        supabase.table('disparos').insert(disparo_data).execute()
        
        return jsonify({
            "success": True,
            "result": result,
            "disparo": disparo_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@whatsapp_bp.route('/send-bulk', methods=['POST'])
@token_required
def send_bulk_whatsapp(current_user):
    """Envia mensagens em massa via WhatsApp"""
    try:
        data = request.get_json()
        contatos_ids = data.get('contatos_ids', [])
        template_mensagem = data.get('template_mensagem')
        campanha_id = data.get('campanha_id')
        
        if not contatos_ids or not template_mensagem:
            return jsonify({"success": False, "error": "Contatos e template são obrigatórios"}), 400
        
        # Buscar contatos no banco
        supabase = get_supabase()
        contatos_response = supabase.table('contatos').select('*').in_('id', contatos_ids).eq('empresa_id', current_user['empresa_id']).execute()
        contatos = contatos_response.data
        
        if not contatos:
            return jsonify({"success": False, "error": "Nenhum contato encontrado"}), 404
        
        # Enviar mensagens
        evolution = init_evolution_api(EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME)
        results = evolution.send_bulk_messages(contatos, template_mensagem)
        
        # Salvar disparos no banco
        disparos_data = []
        for result in results:
            disparo = {
                "empresa_id": current_user['empresa_id'],
                "campanha_id": campanha_id,
                "contato_id": result['contato_id'],
                "canal": "whatsapp",
                "mensagem": template_mensagem.replace("{{nome}}", result['nome']),
                "status": result['status'],
                "external_id": result.get('response', {}).get('key', {}).get('id') if result.get('response', {}).get('key') else None,
                "erro_mensagem": result.get('error') if result.get('error') else None
            }
            disparos_data.append(disparo)
        
        if disparos_data:
            supabase.table('disparos').insert(disparos_data).execute()
        
        return jsonify({
            "success": True,
            "total_enviados": len([r for r in results if r['status'] == 'enviado']),
            "total_erros": len([r for r in results if r['status'] == 'erro']),
            "results": results
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@whatsapp_bp.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Recebe webhooks da Evolution API"""
    try:
        data = request.get_json()
        
        evolution = init_evolution_api(EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME)
        processed = evolution.process_webhook_message(data)
        
        if processed.get('tipo') == 'mensagem_recebida':
            # Salvar resposta no banco
            supabase = get_supabase()
            
            # Buscar disparo relacionado pelo número
            numero = processed['de']
            disparo_response = supabase.table('disparos').select('*').eq('canal', 'whatsapp').like('mensagem', f'%{numero}%').order('created_at', desc=True).limit(1).execute()
            
            resposta_data = {
                "canal": "whatsapp",
                "conteudo": processed['mensagem'],
                "tipo_resposta": "texto",
                "created_at": datetime.now().isoformat()
            }
            
            if disparo_response.data:
                disparo = disparo_response.data[0]
                resposta_data.update({
                    "empresa_id": disparo['empresa_id'],
                    "disparo_id": disparo['id'],
                    "contato_id": disparo['contato_id'],
                    "campanha_id": disparo['campanha_id']
                })
            
            supabase.table('respostas').insert(resposta_data).execute()
        
        return jsonify({"success": True, "processed": processed})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@whatsapp_bp.route('/contacts', methods=['GET'])
@token_required
def get_whatsapp_contacts(current_user):
    """Busca contatos da instância WhatsApp"""
    try:
        evolution = init_evolution_api(EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME)
        contacts = evolution.get_contacts()
        
        return jsonify({
            "success": True,
            "contacts": contacts
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@whatsapp_bp.route('/setup-webhook', methods=['POST'])
@token_required
def setup_webhook(current_user):
    """Configura webhook da Evolution API"""
    try:
        data = request.get_json()
        webhook_url = data.get('webhook_url', f'http://31.97.95.124:5000/api/whatsapp/webhook')
        
        evolution = init_evolution_api(EVOLUTION_API_URL, EVOLUTION_API_KEY, INSTANCE_NAME)
        result = evolution.create_webhook(webhook_url)
        
        return jsonify({
            "success": True,
            "webhook_configured": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

