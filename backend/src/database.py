import os
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    def __init__(self, url: str = None, key: str = None):
        self.url = url or os.environ.get('SUPABASE_URL')
        self.key = key or os.environ.get('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios")
        
        self.client: Client = create_client(self.url, self.key)
    
    def get_client(self) -> Client:
        """Retorna o cliente Supabase"""
        return self.client
    
    # =====================================================
    # MÉTODOS PARA EMPRESAS
    # =====================================================
    
    def get_empresa_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Busca empresa por slug"""
        try:
            response = self.client.table('empresas').select('*').eq('slug', slug).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar empresa por slug {slug}: {e}")
            return None
    
    def create_empresa(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria nova empresa"""
        try:
            response = self.client.table('empresas').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar empresa: {e}")
            return None
    
    # =====================================================
    # MÉTODOS PARA USUÁRIOS
    # =====================================================
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca usuário por email"""
        try:
            response = self.client.table('usuarios').select('*').eq('email', email).eq('ativo', True).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email {email}: {e}")
            return None
    
    def create_user(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria novo usuário"""
        try:
            response = self.client.table('usuarios').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return None
    
    def update_user_last_login(self, user_id: str) -> bool:
        """Atualiza último login do usuário"""
        try:
            self.client.table('usuarios').update({'ultimo_login': 'now()'}).eq('id', user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar último login: {e}")
            return False
    
    # =====================================================
    # MÉTODOS PARA CONTATOS
    # =====================================================
    
    def get_contatos(self, empresa_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Lista contatos da empresa"""
        try:
            response = self.client.table('contatos').select('*').eq('empresa_id', empresa_id).range(offset, offset + limit - 1).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Erro ao buscar contatos: {e}")
            return []
    
    def create_contato(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria novo contato"""
        try:
            response = self.client.table('contatos').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar contato: {e}")
            return None
    
    def bulk_create_contatos(self, contatos: List[Dict[str, Any]]) -> bool:
        """Cria múltiplos contatos de uma vez"""
        try:
            self.client.table('contatos').insert(contatos).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao criar contatos em lote: {e}")
            return False
    
    def update_contato(self, contato_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza contato"""
        try:
            response = self.client.table('contatos').update(data).eq('id', contato_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao atualizar contato: {e}")
            return None
    
    def delete_contato(self, contato_id: str) -> bool:
        """Deleta contato"""
        try:
            self.client.table('contatos').delete().eq('id', contato_id).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar contato: {e}")
            return False
    
    # =====================================================
    # MÉTODOS PARA CAMPANHAS
    # =====================================================
    
    def get_campanhas(self, empresa_id: str) -> List[Dict[str, Any]]:
        """Lista campanhas da empresa"""
        try:
            response = self.client.table('campanhas').select('*').eq('empresa_id', empresa_id).order('created_at', desc=True).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Erro ao buscar campanhas: {e}")
            return []
    
    def create_campanha(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria nova campanha"""
        try:
            response = self.client.table('campanhas').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar campanha: {e}")
            return None
    
    def update_campanha(self, campanha_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza campanha"""
        try:
            response = self.client.table('campanhas').update(data).eq('id', campanha_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao atualizar campanha: {e}")
            return None
    
    # =====================================================
    # MÉTODOS PARA DISPAROS
    # =====================================================
    
    def create_disparo(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria novo disparo"""
        try:
            response = self.client.table('disparos').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar disparo: {e}")
            return None
    
    def update_disparo_status(self, disparo_id: str, status: str, detalhes: Dict[str, Any] = None) -> bool:
        """Atualiza status do disparo"""
        try:
            update_data = {'status': status}
            if detalhes:
                update_data.update(detalhes)
            
            self.client.table('disparos').update(update_data).eq('id', disparo_id).execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar status do disparo: {e}")
            return False
    
    # =====================================================
    # MÉTODOS PARA RESPOSTAS
    # =====================================================
    
    def create_resposta(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria nova resposta"""
        try:
            response = self.client.table('respostas').insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erro ao criar resposta: {e}")
            return None
    
    # =====================================================
    # MÉTODOS PARA MÉTRICAS
    # =====================================================
    
    def get_metricas_dashboard(self, empresa_id: str) -> Dict[str, Any]:
        """Busca métricas para o dashboard"""
        try:
            # Total de contatos
            contatos_response = self.client.table('contatos').select('id', count='exact').eq('empresa_id', empresa_id).execute()
            total_contatos = contatos_response.count or 0
            
            # Total de campanhas
            campanhas_response = self.client.table('campanhas').select('id', count='exact').eq('empresa_id', empresa_id).execute()
            total_campanhas = campanhas_response.count or 0
            
            # Total de disparos
            disparos_response = self.client.rpc('get_disparos_count_by_empresa', {'empresa_id_param': empresa_id}).execute()
            total_disparos = disparos_response.data or 0
            
            # Total de respostas
            respostas_response = self.client.rpc('get_respostas_count_by_empresa', {'empresa_id_param': empresa_id}).execute()
            total_respostas = respostas_response.data or 0
            
            # Taxa de resposta
            taxa_resposta = (total_respostas / total_disparos * 100) if total_disparos > 0 else 0
            
            return {
                'total_contatos': total_contatos,
                'total_campanhas': total_campanhas,
                'total_disparos': total_disparos,
                'total_respostas': total_respostas,
                'taxa_resposta': round(taxa_resposta, 2)
            }
        except Exception as e:
            logger.error(f"Erro ao buscar métricas: {e}")
            return {
                'total_contatos': 0,
                'total_campanhas': 0,
                'total_disparos': 0,
                'total_respostas': 0,
                'taxa_resposta': 0
            }

# Instância global do cliente Supabase
supabase_client = None

def init_supabase(url: str = None, key: str = None):
    """Inicializa o cliente Supabase"""
    global supabase_client
    supabase_client = SupabaseClient(url, key)
    return supabase_client

def get_supabase() -> SupabaseClient:
    """Retorna a instância do cliente Supabase"""
    if supabase_client is None:
        raise RuntimeError("Supabase não foi inicializado. Chame init_supabase() primeiro.")
    return supabase_client

