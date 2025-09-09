# 🏗️ SaaS Pós-Venda Madeireira Cambará

Sistema completo de pós-venda para madeireiras com automação via WhatsApp, dashboard de métricas e gestão de campanhas.

## 🚀 Funcionalidades

- ✅ **Dashboard Interativo** - Métricas em tempo real
- ✅ **Gestão de Contatos** - Importação e organização
- ✅ **Campanhas Automatizadas** - Disparos em massa
- ✅ **WhatsApp Integration** - Via Evolution API
- ✅ **Automação n8n** - Workflows personalizados
- ✅ **Multi-tenant** - Suporte a múltiplas empresas
- ✅ **Relatórios** - Analytics e insights

## 🛠️ Stack Tecnológico

### Backend
- **Flask** - API REST
- **Supabase** - Banco de dados PostgreSQL
- **JWT** - Autenticação segura
- **Evolution API** - Integração WhatsApp

### Frontend
- **React** - Interface moderna
- **Vite** - Build tool
- **Tailwind CSS** - Estilização
- **Recharts** - Gráficos interativos

### Automação
- **n8n** - Workflows visuais
- **Evolution API** - WhatsApp Business

## 🏃‍♂️ Como Executar

### Backend
```bash
cd backend/
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python src/main.py
```

### Frontend
```bash
cd frontend/
npm install
npm run dev
```

## 🌐 Deploy

### Desenvolvimento
- Backend: http://localhost:5000
- Frontend: http://localhost:5173

### Produção
- Configurar variáveis de ambiente
- Deploy via EasyPanel ou Docker

## 📋 Configuração

### Variáveis de Ambiente (Backend)
```env
SUPABASE_URL=sua-url-supabase
SUPABASE_KEY=sua-chave-supabase
EVOLUTION_API_URL=http://seu-servidor:8080
EVOLUTION_API_KEY=sua-chave-evolution
JWT_SECRET_KEY=sua-chave-jwt
```

### Variáveis de Ambiente (Frontend)
```env
VITE_API_URL=http://localhost:5000/api
VITE_SUPABASE_URL=sua-url-supabase
```

## 🔄 Fluxo de Funcionamento

1. **Usuário acessa** → Login/Dashboard
2. **Adiciona contatos** → Salva no Supabase
3. **Cria campanha** → Configura mensagens
4. **n8n dispara** → Via Evolution API
5. **Clientes respondem** → Webhook recebe
6. **Sistema processa** → Salva respostas
7. **Dashboard atualiza** → Métricas em tempo real

## 📊 Estrutura do Banco

- **empresas** - Dados das empresas clientes
- **usuarios** - Usuários do sistema
- **contatos** - Base de contatos
- **campanhas** - Campanhas de marketing
- **disparos** - Histórico de envios
- **respostas** - Respostas dos clientes
- **templates** - Templates de mensagens
- **logs** - Logs do sistema

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Eduardo** - [eduardomsxtr@gmail.com](mailto:eduardomsxtr@gmail.com)

---

⭐ **Se este projeto te ajudou, deixe uma estrela!**

