import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class EvolutionAPI:
    def __init__(self, base_url: str, api_key: str, instance_name: str = "cambara"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': api_key
        }
    
    def get_instance_status(self) -> Dict:
        """Verifica o status da instância"""
        try:
            url = f"{self.base_url}/instance/connectionState/{self.instance_name}"
            response = requests.get(url, headers=self.headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def send_text_message(self, number: str, message: str) -> Dict:
        """Envia mensagem de texto"""
        try:
            # Formatar número (remover caracteres especiais)
            clean_number = ''.join(filter(str.isdigit, number))
            if not clean_number.startswith('55'):
                clean_number = '55' + clean_number
            
            url = f"{self.base_url}/message/sendText/{self.instance_name}"
            payload = {
                "number": clean_number,
                "text": message
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def send_bulk_messages(self, contacts: List[Dict], message_template: str) -> List[Dict]:
        """Envia mensagens em massa"""
        results = []
        
        for contact in contacts:
            try:
                # Personalizar mensagem
                message = message_template.replace("{{nome}}", contact.get('nome', 'Cliente'))
                message = message.replace("{{telefone}}", contact.get('telefone', ''))
                
                result = self.send_text_message(contact.get('whatsapp', contact.get('telefone')), message)
                results.append({
                    "contato_id": contact.get('id'),
                    "nome": contact.get('nome'),
                    "telefone": contact.get('whatsapp', contact.get('telefone')),
                    "status": "enviado" if not result.get('error') else "erro",
                    "response": result,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "contato_id": contact.get('id'),
                    "nome": contact.get('nome'),
                    "telefone": contact.get('whatsapp', contact.get('telefone')),
                    "status": "erro",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def get_contacts(self) -> Dict:
        """Busca contatos da instância"""
        try:
            url = f"{self.base_url}/chat/findContacts/{self.instance_name}"
            response = requests.get(url, headers=self.headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_chats(self) -> Dict:
        """Busca conversas da instância"""
        try:
            url = f"{self.base_url}/chat/findChats/{self.instance_name}"
            response = requests.get(url, headers=self.headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def create_webhook(self, webhook_url: str, events: List[str] = None) -> Dict:
        """Configura webhook para receber mensagens"""
        try:
            if events is None:
                events = [
                    "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE", 
                    "SEND_MESSAGE",
                    "CONNECTION_UPDATE"
                ]
            
            url = f"{self.base_url}/webhook/set/{self.instance_name}"
            payload = {
                "url": webhook_url,
                "events": events,
                "webhook_by_events": True
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def process_webhook_message(self, webhook_data: Dict) -> Dict:
        """Processa mensagem recebida via webhook"""
        try:
            event = webhook_data.get('event')
            data = webhook_data.get('data', {})
            
            if event == 'MESSAGES_UPSERT':
                message = data.get('message', {})
                key = message.get('key', {})
                
                return {
                    "tipo": "mensagem_recebida",
                    "de": key.get('remoteJid', '').replace('@s.whatsapp.net', ''),
                    "mensagem": message.get('message', {}).get('conversation', ''),
                    "timestamp": message.get('messageTimestamp'),
                    "id_mensagem": key.get('id'),
                    "instancia": self.instance_name
                }
            
            return {"tipo": "evento_ignorado", "event": event}
        except Exception as e:
            return {"error": str(e)}

# Função para inicializar a Evolution API
def init_evolution_api(base_url: str, api_key: str, instance_name: str = "cambara") -> EvolutionAPI:
    """Inicializa e retorna instância da Evolution API"""
    return EvolutionAPI(base_url, api_key, instance_name)

