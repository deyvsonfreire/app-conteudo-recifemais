/**
 * Dashboard Module - Interface do Painel de Controle
 * Gerencia visualização de dados, navegação e interações
 */

class DashboardManager {
    constructor() {
        this.currentSection = 'overview';
        this.refreshInterval = null;
        this.charts = {};
        
        console.log('📊 Dashboard Manager inicializado');
    }
    
    // ==========================================
    // INITIALIZATION
    // ==========================================
    
    init() {
        this.setupNavigation();
        this.setupUserInterface();
        this.loadDashboardData();
        this.startAutoRefresh();
        
        // Mostrar/ocultar seções baseado em permissões
        this.updateUIBasedOnPermissions();
    }
    
    setupNavigation() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.showSection(section);
            });
        });
        
        // User menu
        const userMenuButton = document.getElementById('userMenuButton');
        const userMenu = document.getElementById('userMenu');
        
        userMenuButton?.addEventListener('click', () => {
            userMenu.classList.toggle('hidden');
        });
        
        // Fechar menu quando clicar fora
        document.addEventListener('click', (e) => {
            if (!userMenuButton?.contains(e.target) && !userMenu?.contains(e.target)) {
                userMenu?.classList.add('hidden');
            }
        });
        
        // Logout
        document.getElementById('logoutButton')?.addEventListener('click', async (e) => {
            e.preventDefault();
            await this.handleLogout();
        });
    }
    
    setupUserInterface() {
        const user = authManager.getCurrentUser();
        if (user) {
            document.getElementById('userEmail').textContent = user.email;
        }
        
        // Setup user management se for admin
        if (authManager.isAdmin()) {
            this.setupUserManagement();
        }
    }
    
    updateUIBasedOnPermissions() {
        const user = authManager.getCurrentUser();
        if (!user) return;
        
        // Mostrar seção de usuários apenas para admins
        const usersNavLink = document.getElementById('usersNavLink');
        if (authManager.isAdmin()) {
            usersNavLink.style.display = 'flex';
        } else {
            usersNavLink.style.display = 'none';
        }
        
        // Outras permissões podem ser verificadas aqui
        console.log(`👤 UI configurada para role: ${user.role}`);
    }
    
    // ==========================================
    // NAVIGATION
    // ==========================================
    
    showSection(sectionName) {
        // Ocultar todas as seções
        document.querySelectorAll('.dashboard-section').forEach(section => {
            section.classList.add('hidden');
        });
        
        // Remover classe active de todos os links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Mostrar seção selecionada
        const targetSection = document.getElementById(`${sectionName}Section`);
        if (targetSection) {
            targetSection.classList.remove('hidden');
            targetSection.classList.add('fade-in');
        }
        
        // Adicionar classe active ao link
        const activeLink = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        this.currentSection = sectionName;
        
        // Carregar dados específicos da seção
        this.loadSectionData(sectionName);
        
        console.log(`📄 Seção ativa: ${sectionName}`);
    }
    
    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'overview':
                await this.loadOverviewData();
                break;
            case 'analytics':
                await this.loadAnalyticsData();
                break;
            case 'emails':
                await this.loadEmailsData();
                break;
            case 'posts':
                await this.loadPostsData();
                break;
            case 'workflow':
                await this.loadWorkflowData();
                break;
            case 'config':
                await this.loadConfigData();
                break;
            case 'content':
                await this.loadContentData();
                break;
            case 'users':
                if (authManager.isAdmin()) {
                    await this.loadUsersData();
                }
                break;
        }
    }
    
    // ==========================================
    // DATA LOADING
    // ==========================================
    
    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadSystemHealth(),
                this.loadOverviewStats(),
                this.loadRecentActivity()
            ]);
        } catch (error) {
            console.error('Erro ao carregar dados do dashboard:', error);
            this.showError('Erro ao carregar dados do sistema');
        }
    }
    
    async loadSystemHealth() {
        try {
            const response = await authManager.apiCall('/health');
            if (response.ok) {
                const health = await response.json();
                this.updateSystemHealthUI(health);
            }
        } catch (error) {
            console.error('Erro ao carregar health check:', error);
        }
    }
    
    async loadOverviewStats() {
        try {
            // Simular dados por enquanto - substituir por APIs reais
            const stats = {
                emailsProcessed: 127,
                postsPublished: 45,
                organicClicks: 12543,
                activeUsers: authManager.isAdmin() ? 3 : '--'
            };
            
            document.getElementById('emailsProcessed').textContent = stats.emailsProcessed;
            document.getElementById('postsPublished').textContent = stats.postsPublished;
            document.getElementById('organicClicks').textContent = stats.organicClicks.toLocaleString();
            document.getElementById('activeUsers').textContent = stats.activeUsers;
            
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    }
    
    async loadRecentActivity() {
        const recentActivityContainer = document.getElementById('recentActivity');
        if (!recentActivityContainer) return;
        
        // Simular atividade recente
        const activities = [
            { type: 'email', message: 'Novo email processado sobre "Carnaval 2024"', time: '5 min atrás' },
            { type: 'post', message: 'Post publicado: "Agenda Cultural do Recife"', time: '15 min atrás' },
            { type: 'analytics', message: 'Relatório Google Analytics atualizado', time: '1 hora atrás' }
        ];
        
        recentActivityContainer.innerHTML = activities.map(activity => `
            <div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div class="flex-shrink-0">
                    <div class="h-2 w-2 bg-blue-400 rounded-full"></div>
                </div>
                <div class="flex-1">
                    <p class="text-sm text-gray-900">${activity.message}</p>
                    <p class="text-xs text-gray-500">${activity.time}</p>
                </div>
            </div>
        `).join('');
    }
    
    async loadOverviewData() {
        // Já carregado no loadDashboardData
    }
    
    async loadAnalyticsData() {
        const container = document.getElementById('googleDataDashboard');
        if (!container) return;
        
        try {
            showLoading('Carregando dados do Google Analytics...');
            
            // Carregar dados de analytics
            const response = await authManager.apiCall('/google-data/dashboard');
            
            if (response.ok) {
                const data = await response.json();
                this.renderGoogleDataDashboard(data);
            } else {
                // Verificar se é erro de autenticação
                if (response.status === 401 || response.status === 403) {
                    container.innerHTML = `
                        <div class="text-center py-8">
                            <div class="text-gray-400 text-6xl mb-4">📊</div>
                            <h3 class="text-lg font-medium text-gray-900 mb-2">Google Analytics não conectado</h3>
                            <p class="text-gray-500 mb-4">Configure a integração com Google Analytics para ver os dados aqui.</p>
                            <button onclick="appController.showSection('config')" 
                                    class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                                Configurar Agora
                            </button>
                        </div>
                    `;
                } else {
                    throw new Error('Erro ao carregar dados de analytics');
                }
            }
        } catch (error) {
            console.error('Erro ao carregar analytics:', error);
            container.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-red-400 text-6xl mb-4">⚠️</div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Erro ao carregar dados</h3>
                    <p class="text-red-500 mb-4">${error.message}</p>
                    <button onclick="dashboardManager.loadAnalyticsData()" 
                            class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700">
                        Tentar Novamente
                    </button>
                </div>
            `;
        } finally {
            hideLoading();
        }
    }
    
    async loadEmailsData() {
        // Inicializar o workflow de emails
        if (typeof emailWorkflow !== 'undefined') {
            await emailWorkflow.loadWorkflowStats();
            await emailWorkflow.loadEmailsList();
        }
        console.log('📧 Dados de emails carregados');
    }

    async loadPostsData() {
        // Carregar dados de posts
        if (typeof postsManager !== 'undefined') {
            await postsManager.loadPosts();
        }
        console.log('📝 Dados de posts carregados');
    }

    async loadConfigData() {
        // Carregar configurações
        if (typeof configManager !== 'undefined') {
            await configManager.loadConfigurations();
            await configManager.checkServiceStatus();
        }
        console.log('⚙️ Configurações carregadas');
    }
    
    async loadWorkflowData() {
        // Carregar dados do workflow
        if (typeof emailWorkflow !== 'undefined') {
            await emailWorkflow.loadWorkflowStats();
            await emailWorkflow.loadEmailsList('workflow');
        }
        console.log('📋 Dados do workflow carregados');
    }
    
    async loadWorkflowData() {
        // Carregar dados do workflow
        if (typeof emailWorkflow !== 'undefined') {
            await emailWorkflow.loadWorkflowStats();
            await emailWorkflow.loadEmailsList('workflow');
        }
        console.log('📋 Dados do workflow carregados');
    }
    
    async loadContentData() {
        // Implementar carregamento de dados de conteúdo
        console.log('Carregando dados de conteúdo...');
    }
    
    async loadUsersData() {
        if (!authManager.isAdmin()) return;
        
        try {
            const result = await authManager.getUsers();
            if (result.success) {
                this.renderUsersTable(result.users);
            } else {
                this.showError('Erro ao carregar usuários: ' + result.error);
            }
        } catch (error) {
            console.error('Erro ao carregar usuários:', error);
            this.showError('Erro ao carregar lista de usuários');
        }
    }
    
    // ==========================================
    // UI RENDERING
    // ==========================================
    
    updateSystemHealthUI(health) {
        const container = document.getElementById('systemHealthStatus');
        if (!container) return;
        
        const checks = health.checks || {};
        const status = health.status || 'unknown';
        
        // Atualizar status geral
        const statusElement = document.getElementById('systemStatus');
        if (statusElement) {
            statusElement.textContent = status === 'healthy' ? 'Sistema Ativo' : 'Sistema com Problemas';
            statusElement.className = status === 'healthy' ? 'text-sm text-green-600' : 'text-sm text-red-600';
        }
        
        // Renderizar checks individuais
        const checkItems = Object.entries(checks).map(([service, isHealthy]) => {
            const icon = isHealthy ? 'check-circle' : 'x-circle';
            const color = isHealthy ? 'text-green-600' : 'text-red-600';
            const statusText = isHealthy ? 'Ativo' : 'Inativo';
            
            return `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center space-x-3">
                        <i data-lucide="${icon}" class="h-5 w-5 ${color}"></i>
                        <span class="text-sm font-medium text-gray-900">${this.getServiceName(service)}</span>
                    </div>
                    <span class="text-sm ${color}">${statusText}</span>
                </div>
            `;
        }).join('');
        
        container.innerHTML = checkItems;
        
        // Re-inicializar ícones Lucide
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }
    
    getServiceName(service) {
        const names = {
            'database': 'Banco de Dados',
            'supabase': 'Supabase',
            'gmail': 'Gmail',
            'wordpress': 'WordPress',
            'ai': 'IA (Gemini)',
            'google_data': 'Google Data',
            'auth': 'Autenticação'
        };
        return names[service] || service;
    }
    
    renderGoogleDataDashboard(data) {
        const container = document.getElementById('googleDataDashboard');
        if (!container) return;

        // Verificar se há dados
        if (!data || (!data.analytics && !data.search_console)) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <div class="text-yellow-400 text-6xl mb-4">📈</div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Dados sendo coletados</h3>
                    <p class="text-gray-500 mb-4">Os dados do Google Analytics estão sendo processados. Tente novamente em alguns minutos.</p>
                    <button onclick="dashboardManager.loadAnalyticsData()" 
                            class="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700">
                        Atualizar
                    </button>
                </div>
            `;
            return;
        }

        // Renderizar dashboard com dados
        container.innerHTML = `
            <div class="space-y-6">
                <!-- Métricas Principais -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    ${this.renderAnalyticsCards(data.analytics)}
                </div>

                <!-- Gráficos -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Gráfico de Visitantes -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Visitantes (Últimos 30 dias)</h3>
                        <div id="visitorsChart" class="h-64"></div>
                    </div>

                    <!-- Gráfico de Páginas Mais Visitadas -->
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="text-lg font-medium text-gray-900 mb-4">Páginas Mais Visitadas</h3>
                        <div id="pagesChart" class="h-64"></div>
                    </div>
                </div>

                <!-- Search Console Data -->
                ${data.search_console ? this.renderSearchConsoleData(data.search_console) : ''}

                <!-- Tabela de Conteúdo Recente -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-medium text-gray-900">Performance de Conteúdo Recente</h3>
                    </div>
                    <div class="overflow-x-auto">
                        ${this.renderContentPerformanceTable(data)}
                    </div>
                </div>
            </div>
        `;

        // Renderizar gráficos
        this.renderCharts(data);
    }

    renderAnalyticsCards(analytics) {
        if (!analytics) return '';

        const cards = [
            {
                title: 'Visitantes Únicos',
                value: analytics.unique_visitors || 0,
                change: analytics.visitors_change || 0,
                icon: '👥'
            },
            {
                title: 'Visualizações',
                value: analytics.page_views || 0,
                change: analytics.views_change || 0,
                icon: '👁️'
            },
            {
                title: 'Sessões',
                value: analytics.sessions || 0,
                change: analytics.sessions_change || 0,
                icon: '🔄'
            },
            {
                title: 'Taxa de Rejeição',
                value: `${analytics.bounce_rate || 0}%`,
                change: analytics.bounce_change || 0,
                icon: '📊',
                inverse: true // Para taxa de rejeição, menor é melhor
            }
        ];

        return cards.map(card => `
            <div class="bg-white rounded-lg shadow p-6">
                <div class="flex items-center">
                    <div class="text-2xl mr-3">${card.icon}</div>
                    <div class="flex-1">
                        <p class="text-sm font-medium text-gray-600">${card.title}</p>
                        <p class="text-2xl font-bold text-gray-900">${typeof card.value === 'number' ? card.value.toLocaleString() : card.value}</p>
                        ${card.change !== 0 ? `
                            <p class="text-sm ${
                                (card.inverse ? card.change < 0 : card.change > 0) ? 'text-green-600' : 'text-red-600'
                            }">
                                ${card.change > 0 ? '+' : ''}${card.change}% vs mês anterior
                            </p>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderSearchConsoleData(searchConsole) {
        return `
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Google Search Console</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="text-center">
                        <div class="text-2xl font-bold text-blue-600">${(searchConsole.total_clicks || 0).toLocaleString()}</div>
                        <div class="text-sm text-gray-600">Cliques Totais</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-green-600">${(searchConsole.total_impressions || 0).toLocaleString()}</div>
                        <div class="text-sm text-gray-600">Impressões</div>
                    </div>
                    <div class="text-center">
                        <div class="text-2xl font-bold text-purple-600">${(searchConsole.average_ctr || 0).toFixed(2)}%</div>
                        <div class="text-sm text-gray-600">CTR Médio</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderContentPerformanceTable(data) {
        const content = data.content_performance || [];
        
        if (content.length === 0) {
            return `
                <div class="text-center py-8">
                    <p class="text-gray-500">Nenhum dado de performance disponível</p>
                </div>
            `;
        }

        return `
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Página</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Visualizações</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliques</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CTR</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Posição Média</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    ${content.map(item => `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm font-medium text-gray-900">${item.title || 'Sem título'}</div>
                                <div class="text-sm text-gray-500">${item.url}</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${(item.page_views || 0).toLocaleString()}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${(item.clicks || 0).toLocaleString()}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${(item.ctr || 0).toFixed(2)}%
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${(item.position || 0).toFixed(1)}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    renderCharts(data) {
        // Renderizar gráfico de visitantes
        this.renderVisitorsChart(data.analytics?.visitors_timeline || []);
        
        // Renderizar gráfico de páginas
        this.renderPagesChart(data.analytics?.top_pages || []);
    }

    renderVisitorsChart(visitorsData) {
        const container = document.getElementById('visitorsChart');
        if (!container || !visitorsData.length) {
            container.innerHTML = '<div class="flex items-center justify-center h-full text-gray-500">Dados não disponíveis</div>';
            return;
        }

        // Usar Chart.js simples com Canvas
        container.innerHTML = `
            <canvas id="visitorsCanvas" width="400" height="200"></canvas>
        `;

        const canvas = document.getElementById('visitorsCanvas');
        const ctx = canvas.getContext('2d');
        
        // Dados para o gráfico
        const labels = visitorsData.map(d => new Date(d.date).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }));
        const values = visitorsData.map(d => d.visitors);
        
        // Desenhar gráfico simples
        this.drawLineChart(ctx, labels, values, '#3B82F6');
    }

    renderPagesChart(pagesData) {
        const container = document.getElementById('pagesChart');
        if (!container || !pagesData.length) {
            container.innerHTML = '<div class="flex items-center justify-center h-full text-gray-500">Dados não disponíveis</div>';
            return;
        }

        // Renderizar como lista estilizada
        const topPages = pagesData.slice(0, 5);
        const maxViews = Math.max(...topPages.map(p => p.views));

        container.innerHTML = `
            <div class="space-y-3">
                ${topPages.map(page => `
                    <div class="flex items-center">
                        <div class="flex-1">
                            <div class="text-sm font-medium text-gray-900 truncate">${page.title || 'Sem título'}</div>
                            <div class="text-xs text-gray-500 truncate">${page.path}</div>
                        </div>
                        <div class="ml-4 flex items-center">
                            <div class="w-20 bg-gray-200 rounded-full h-2 mr-2">
                                <div class="bg-blue-600 h-2 rounded-full" style="width: ${(page.views / maxViews) * 100}%"></div>
                            </div>
                            <span class="text-sm font-medium text-gray-900 w-12 text-right">${page.views.toLocaleString()}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    drawLineChart(ctx, labels, values, color) {
        const canvas = ctx.canvas;
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        
        // Limpar canvas
        ctx.clearRect(0, 0, width, height);
        
        if (values.length === 0) return;
        
        // Calcular escalas
        const maxValue = Math.max(...values);
        const minValue = Math.min(...values);
        const valueRange = maxValue - minValue || 1;
        
        const stepX = (width - 2 * padding) / (labels.length - 1);
        const stepY = (height - 2 * padding) / valueRange;
        
        // Desenhar eixos
        ctx.strokeStyle = '#E5E7EB';
        ctx.lineWidth = 1;
        
        // Eixo X
        ctx.beginPath();
        ctx.moveTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();
        
        // Eixo Y
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.stroke();
        
        // Desenhar linha
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        values.forEach((value, index) => {
            const x = padding + index * stepX;
            const y = height - padding - (value - minValue) * stepY;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Desenhar pontos
        ctx.fillStyle = color;
        values.forEach((value, index) => {
            const x = padding + index * stepX;
            const y = height - padding - (value - minValue) * stepY;
            
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, 2 * Math.PI);
            ctx.fill();
        });
        
        // Labels do eixo X (apenas alguns)
        ctx.fillStyle = '#6B7280';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        
        const labelStep = Math.ceil(labels.length / 5);
        labels.forEach((label, index) => {
            if (index % labelStep === 0) {
                const x = padding + index * stepX;
                ctx.fillText(label, x, height - padding + 15);
            }
        });
    }
    
    renderUsersTable(users) {
        const container = document.getElementById('usersTable');
        if (!container) return;
        
        if (!users || users.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">Nenhum usuário encontrado.</p>';
            return;
        }
        
        const tableHTML = `
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuário</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Último Login</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${users.map(user => `
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <div class="flex items-center">
                                        <div class="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                                            <i data-lucide="user" class="h-4 w-4 text-gray-600"></i>
                                        </div>
                                        <div class="ml-3">
                                            <div class="text-sm font-medium text-gray-900">${user.email}</div>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${this.getRoleBadgeClass(user.role)}">
                                        ${this.getRoleDisplayName(user.role)}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                        ${user.is_active ? 'Ativo' : 'Inativo'}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    ${user.last_sign_in ? new Date(user.last_sign_in).toLocaleDateString('pt-BR') : 'Nunca'}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <button onclick="dashboardManager.editUser('${user.id}')" class="text-blue-600 hover:text-blue-900 mr-3">
                                        Editar
                                    </button>
                                    ${user.id !== authManager.getCurrentUser().user_id ? `
                                        <button onclick="dashboardManager.deleteUser('${user.id}', '${user.email}')" class="text-red-600 hover:text-red-900">
                                            Remover
                                        </button>
                                    ` : ''}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = tableHTML;
        
        // Re-inicializar ícones Lucide
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }
    
    getRoleBadgeClass(role) {
        const classes = {
            'admin': 'bg-red-100 text-red-800',
            'editor': 'bg-blue-100 text-blue-800',
            'viewer': 'bg-gray-100 text-gray-800'
        };
        return classes[role] || 'bg-gray-100 text-gray-800';
    }
    
    getRoleDisplayName(role) {
        const names = {
            'admin': 'Administrador',
            'editor': 'Editor',
            'viewer': 'Visualizador'
        };
        return names[role] || role;
    }
    
    // ==========================================
    // USER MANAGEMENT
    // ==========================================
    
    setupUserManagement() {
        const addUserButton = document.getElementById('addUserButton');
        addUserButton?.addEventListener('click', () => {
            this.showAddUserModal();
        });
    }
    
    showAddUserModal() {
        // Implementar modal de adicionar usuário
        const email = prompt('Email do novo usuário:');
        if (!email) return;
        
        const password = prompt('Senha inicial:');
        if (!password) return;
        
        const role = prompt('Role (admin, editor, viewer):', 'viewer');
        if (!role) return;
        
        this.createUser(email, password, role);
    }
    
    async createUser(email, password, role) {
        try {
            const result = await authManager.createUser(email, password, role);
            if (result.success) {
                this.showSuccess('Usuário criado com sucesso!');
                await this.loadUsersData();
            } else {
                this.showError('Erro ao criar usuário: ' + result.error);
            }
        } catch (error) {
            console.error('Erro ao criar usuário:', error);
            this.showError('Erro interno ao criar usuário');
        }
    }
    
    async editUser(userId) {
        const newRole = prompt('Novo role (admin, editor, viewer):');
        if (!newRole) return;
        
        try {
            const result = await authManager.updateUserRole(userId, newRole);
            if (result.success) {
                this.showSuccess('Role atualizado com sucesso!');
                await this.loadUsersData();
            } else {
                this.showError('Erro ao atualizar role: ' + result.error);
            }
        } catch (error) {
            console.error('Erro ao atualizar role:', error);
            this.showError('Erro interno ao atualizar role');
        }
    }
    
    async deleteUser(userId, userEmail) {
        if (!confirm(`Tem certeza que deseja remover o usuário ${userEmail}?`)) {
            return;
        }
        
        try {
            const result = await authManager.deleteUser(userId);
            if (result.success) {
                this.showSuccess('Usuário removido com sucesso!');
                await this.loadUsersData();
            } else {
                this.showError('Erro ao remover usuário: ' + result.error);
            }
        } catch (error) {
            console.error('Erro ao remover usuário:', error);
            this.showError('Erro interno ao remover usuário');
        }
    }
    
    // ==========================================
    // UTILITIES
    // ==========================================
    
    startAutoRefresh() {
        // Atualizar dados a cada 5 minutos
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    async handleLogout() {
        this.stopAutoRefresh();
        await authManager.logout();
        window.location.reload();
    }
    
    showSuccess(message) {
        // Implementar notificação de sucesso
        console.log('✅ Sucesso:', message);
        alert(message); // Temporário - substituir por toast
    }
    
    showError(message) {
        // Implementar notificação de erro
        console.error('❌ Erro:', message);
        alert(message); // Temporário - substituir por toast
    }
    
    showLoading(show = true) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }
}

// Instância global
window.dashboardManager = new DashboardManager(); 