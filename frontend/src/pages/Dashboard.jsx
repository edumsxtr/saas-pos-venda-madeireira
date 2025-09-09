import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  MessageSquare, 
  TrendingUp, 
  Activity,
  Download,
  RefreshCw
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { dashboardAPI } from '@/lib/api';
import { useAppStore, useNotifications } from '@/lib/store';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [chartData, setChartData] = useState({
    disparos: [],
    sentimentos: [],
    campanhas: []
  });
  const [loading, setLoading] = useState(true);
  
  const { showError, showSuccess } = useNotifications();

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Carregar métricas principais
      const metricsResponse = await dashboardAPI.getMetrics();
      setMetrics(metricsResponse.data.metrics);

      // Carregar dados dos gráficos
      const [disparosRes, sentimentosRes, campanhasRes] = await Promise.all([
        dashboardAPI.getDisparosPorDia(30),
        dashboardAPI.getRespostasPorSentimento(),
        dashboardAPI.getCampanhasPerformance()
      ]);

      setChartData({
        disparos: disparosRes.data.chart_data || [],
        sentimentos: sentimentosRes.data.chart_data || [],
        campanhas: campanhasRes.data.chart_data || []
      });

    } catch (error) {
      showError('Erro ao carregar dados do dashboard');
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleRefresh = () => {
    loadDashboardData();
    showSuccess('Dados atualizados!');
  };

  const handleExportReport = async () => {
    try {
      const response = await dashboardAPI.exportReport();
      showSuccess('Relatório exportado com sucesso!');
      // Aqui você pode implementar o download do relatório
    } catch (error) {
      showError('Erro ao exportar relatório');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Visão geral das suas campanhas de pós-venda</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button onClick={handleExportReport}>
            <Download className="h-4 w-4 mr-2" />
            Exportar Relatório
          </Button>
        </div>
      </div>

      {/* Métricas principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Contatos</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.total_contatos || 0}</div>
            <p className="text-xs text-muted-foreground">
              Base de clientes cadastrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Campanhas Ativas</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.total_campanhas || 0}</div>
            <p className="text-xs text-muted-foreground">
              Campanhas em execução
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Disparos</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.total_disparos || 0}</div>
            <p className="text-xs text-muted-foreground">
              Mensagens enviadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Taxa de Resposta</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.taxa_resposta || 0}%</div>
            <p className="text-xs text-muted-foreground">
              Clientes que responderam
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de disparos por dia */}
        <Card>
          <CardHeader>
            <CardTitle>Disparos por Dia</CardTitle>
            <CardDescription>
              Últimos 30 dias
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData.disparos}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="data" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="quantidade" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de sentimentos */}
        <Card>
          <CardHeader>
            <CardTitle>Análise de Sentimentos</CardTitle>
            <CardDescription>
              Distribuição das respostas recebidas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={chartData.sentimentos}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="quantidade"
                >
                  {chartData.sentimentos.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Performance das campanhas */}
      <Card>
        <CardHeader>
          <CardTitle>Performance das Campanhas</CardTitle>
          <CardDescription>
            Taxa de entrega, leitura e resposta por campanha
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData.campanhas}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="nome" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="taxa_entrega" fill="#8884d8" name="Taxa de Entrega" />
              <Bar dataKey="taxa_leitura" fill="#82ca9d" name="Taxa de Leitura" />
              <Bar dataKey="taxa_resposta" fill="#ffc658" name="Taxa de Resposta" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Resumo de satisfação */}
      {metrics?.percentual_satisfacao !== undefined && (
        <Card>
          <CardHeader>
            <CardTitle>Índice de Satisfação</CardTitle>
            <CardDescription>
              Baseado nas respostas dos clientes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <div className="text-4xl font-bold text-green-600">
                {metrics.percentual_satisfacao}%
              </div>
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${metrics.percentual_satisfacao}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {metrics.percentual_satisfacao >= 80 ? 'Excelente!' : 
                   metrics.percentual_satisfacao >= 60 ? 'Bom' : 
                   'Precisa melhorar'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

