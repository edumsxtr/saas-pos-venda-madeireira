from flask import Blueprint, request, jsonify
from src.auth import token_required
from src.database import get_supabase
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/metrics', methods=['GET'])
@token_required
def get_dashboard_metrics():
    """Retorna métricas principais do dashboard"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        # Buscar métricas básicas
        metrics = db.get_metricas_dashboard(empresa_id)
        
        # Buscar dados adicionais
        client = db.get_client()
        
        # Campanhas por status
        campanhas_response = client.table('campanhas').select('status').eq('empresa_id', empresa_id).execute()
        campanhas_por_status = {}
        for campanha in campanhas_response.data:
            status = campanha['status']
            campanhas_por_status[status] = campanhas_por_status.get(status, 0) + 1
        
        # Disparos dos últimos 7 dias
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        disparos_response = client.rpc('get_disparos_last_days', {
            'empresa_id_param': empresa_id,
            'days_param': 7
        }).execute()
        
        disparos_ultimos_dias = disparos_response.data or []
        
        # Respostas por sentimento
        sentimentos_response = client.table('vw_analise_sentimentos').select('*').execute()
        sentimentos_data = sentimentos_response.data or []
        
        # Calcular média de sentimento
        total_positivas = sum(s.get('positivas', 0) for s in sentimentos_data)
        total_negativas = sum(s.get('negativas', 0) for s in sentimentos_data)
        total_respostas_sentimento = total_positivas + total_negativas
        
        percentual_satisfacao = 0
        if total_respostas_sentimento > 0:
            percentual_satisfacao = round((total_positivas / total_respostas_sentimento) * 100, 2)
        
        return jsonify({
            'metrics': {
                **metrics,
                'percentual_satisfacao': percentual_satisfacao
            },
            'campanhas_por_status': campanhas_por_status,
            'disparos_ultimos_dias': disparos_ultimos_dias,
            'analise_sentimentos': {
                'total_positivas': total_positivas,
                'total_negativas': total_negativas,
                'percentual_satisfacao': percentual_satisfacao
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar métricas do dashboard: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@dashboard_bp.route('/recent-activity', methods=['GET'])
@token_required
def get_recent_activity():
    """Retorna atividades recentes"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        client = db.get_client()
        
        # Buscar logs recentes
        logs_response = client.table('logs_sistema').select('*').eq('empresa_id', empresa_id).order('created_at', desc=True).limit(20).execute()
        
        activities = []
        for log in logs_response.data:
            activity = {
                'id': log['id'],
                'acao': log['acao'],
                'entidade': log['entidade'],
                'created_at': log['created_at'],
                'usuario_id': log.get('usuario_id')
            }
            activities.append(activity)
        
        return jsonify({
            'activities': activities
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar atividades recentes: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@dashboard_bp.route('/charts/disparos-por-dia', methods=['GET'])
@token_required
def get_disparos_por_dia():
    """Retorna dados para gráfico de disparos por dia"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        # Parâmetros de período
        days = int(request.args.get('days', 30))
        
        client = db.get_client()
        
        # Buscar disparos agrupados por dia
        response = client.rpc('get_disparos_chart_data', {
            'empresa_id_param': empresa_id,
            'days_param': days
        }).execute()
        
        chart_data = response.data or []
        
        return jsonify({
            'chart_data': chart_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados do gráfico: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@dashboard_bp.route('/charts/respostas-por-sentimento', methods=['GET'])
@token_required
def get_respostas_por_sentimento():
    """Retorna dados para gráfico de respostas por sentimento"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        client = db.get_client()
        
        # Buscar análise de sentimentos
        response = client.table('vw_analise_sentimentos').select('*').execute()
        
        sentimentos_data = response.data or []
        
        # Agregar dados
        total_positivas = sum(s.get('positivas', 0) for s in sentimentos_data)
        total_neutras = sum(s.get('neutras', 0) for s in sentimentos_data)
        total_negativas = sum(s.get('negativas', 0) for s in sentimentos_data)
        
        chart_data = [
            {'sentimento': 'Positivo', 'quantidade': total_positivas},
            {'sentimento': 'Neutro', 'quantidade': total_neutras},
            {'sentimento': 'Negativo', 'quantidade': total_negativas}
        ]
        
        return jsonify({
            'chart_data': chart_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados de sentimento: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@dashboard_bp.route('/charts/campanhas-performance', methods=['GET'])
@token_required
def get_campanhas_performance():
    """Retorna dados de performance das campanhas"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        client = db.get_client()
        
        # Buscar métricas das campanhas
        response = client.table('vw_metricas_campanhas').select('*').execute()
        
        campanhas_data = response.data or []
        
        # Filtrar apenas campanhas da empresa (se necessário)
        # Nota: isso deveria ser feito no banco com RLS
        
        chart_data = []
        for campanha in campanhas_data:
            chart_data.append({
                'nome': campanha['nome'],
                'taxa_entrega': campanha.get('taxa_entrega', 0),
                'taxa_leitura': campanha.get('taxa_leitura', 0),
                'taxa_resposta': campanha.get('taxa_resposta', 0),
                'total_enviados': campanha.get('total_enviados', 0)
            })
        
        return jsonify({
            'chart_data': chart_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar performance das campanhas: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@dashboard_bp.route('/export/report', methods=['GET'])
@token_required
def export_report():
    """Exporta relatório completo"""
    try:
        db = get_supabase()
        empresa_id = request.current_user['empresa_id']
        
        # Buscar todos os dados necessários
        metrics = db.get_metricas_dashboard(empresa_id)
        campanhas = db.get_campanhas(empresa_id)
        contatos = db.get_contatos(empresa_id, 10000, 0)
        
        client = db.get_client()
        
        # Buscar respostas recentes
        respostas_response = client.table('respostas').select('*').order('created_at', desc=True).limit(100).execute()
        respostas = respostas_response.data or []
        
        # Gerar relatório
        report_data = {
            'empresa': request.current_user.get('empresa', {}),
            'periodo': datetime.now().isoformat(),
            'metricas_gerais': metrics,
            'total_campanhas': len(campanhas),
            'total_contatos': len(contatos),
            'campanhas_ativas': len([c for c in campanhas if c['status'] == 'executando']),
            'contatos_ativos': len([c for c in contatos if c['status'] == 'ativo']),
            'respostas_recentes': len(respostas)
        }
        
        return jsonify({
            'report': report_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

