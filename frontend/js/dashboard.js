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

/**
 * 🔍 GERADOR DE DIAGNÓSTICO COMPLETO
 * Coleta dados do sistema e gera log detalhado
 */
async function generateSystemDiagnostic() {
    try {
        showNotification('🔍 Gerando diagnóstico completo...', 'info');
        
        const response = await fetch('/admin/system-diagnostic');
        const data = await response.json();
        
        if (data.status === 'success') {
            // Criar modal ou nova página com o diagnóstico
            displayDiagnosticModal(data.diagnostic, data.summary);
            showNotification('✅ Diagnóstico gerado com sucesso!', 'success');
        } else {
            throw new Error('Falha ao gerar diagnóstico');
        }
    } catch (error) {
        console.error('Erro ao gerar diagnóstico:', error);
        showNotification('❌ Erro ao gerar diagnóstico: ' + error.message, 'error');
    }
}

/**
 * 📋 EXIBIR DIAGNÓSTICO EM MODAL
 */
function displayDiagnosticModal(diagnostic, summary) {
    const modal = document.createElement('div');
    modal.className = 'diagnostic-modal';
    modal.innerHTML = `
        <div class="diagnostic-modal-content">
            <div class="diagnostic-header">
                <h2>🔍 DIAGNÓSTICO COMPLETO DO SISTEMA</h2>
                <button class="close-diagnostic" onclick="closeDiagnosticModal()">&times;</button>
            </div>
            
            <div class="diagnostic-summary">
                <div class="health-score ${getHealthScoreClass(summary.health_score.score)}">
                    <h3>${summary.health_score.status}</h3>
                    <div class="score">${summary.health_score.score}</div>
                </div>
                <div class="summary-stats">
                    <div class="stat">
                        <span class="label">Timestamp:</span>
                        <span class="value">${new Date(summary.timestamp).toLocaleString('pt-BR')}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Erros:</span>
                        <span class="value error-count">${summary.total_errors}</span>
                    </div>
                    <div class="stat">
                        <span class="label">Recomendações:</span>
                        <span class="value rec-count">${summary.total_recommendations}</span>
                    </div>
                </div>
            </div>
            
            <div class="diagnostic-content">
                <div class="diagnostic-tabs">
                    <button class="tab-btn active" onclick="showDiagnosticTab('overview')">📊 Visão Geral</button>
                    <button class="tab-btn" onclick="showDiagnosticTab('services')">🚀 Serviços</button>
                    <button class="tab-btn" onclick="showDiagnosticTab('database')">🗄️ Banco</button>
                    <button class="tab-btn" onclick="showDiagnosticTab('raw')">📝 Log Completo</button>
                </div>
                
                <div id="diagnostic-overview" class="diagnostic-tab-content active">
                    ${generateOverviewContent(diagnostic)}
                </div>
                
                <div id="diagnostic-services" class="diagnostic-tab-content">
                    ${generateServicesContent(diagnostic)}
                </div>
                
                <div id="diagnostic-database" class="diagnostic-tab-content">
                    ${generateDatabaseContent(diagnostic)}
                </div>
                
                <div id="diagnostic-raw" class="diagnostic-tab-content">
                    <div class="raw-log-container">
                        <div class="raw-log-header">
                            <h4>📋 LOG COMPLETO PARA COPIAR</h4>
                            <button onclick="copyDiagnosticToClipboard()" class="copy-btn">📋 Copiar Tudo</button>
                        </div>
                        <textarea id="diagnostic-raw-text" readonly>${JSON.stringify({diagnostic, summary}, null, 2)}</textarea>
                    </div>
                </div>
            </div>
            
            ${diagnostic.recommendations.length > 0 ? `
                <div class="diagnostic-recommendations">
                    <h4>💡 Recomendações</h4>
                    <ul>
                        ${diagnostic.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${diagnostic.errors.length > 0 ? `
                <div class="diagnostic-errors">
                    <h4>⚠️ Erros Encontrados</h4>
                    <ul>
                        ${diagnostic.errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Adicionar estilos
    addDiagnosticStyles();
}

/**
 * 📊 GERAR CONTEÚDO DA VISÃO GERAL
 */
function generateOverviewContent(diagnostic) {
    return `
        <div class="overview-grid">
            <div class="overview-card">
                <h4>🖥️ Sistema</h4>
                <p><strong>Versão:</strong> ${diagnostic.system_info.app_version}</p>
                <p><strong>Ambiente:</strong> ${diagnostic.system_info.environment_type}</p>
                <p><strong>Debug:</strong> ${diagnostic.system_info.debug_mode ? 'Ativo' : 'Inativo'}</p>
            </div>
            
            <div class="overview-card">
                <h4>🗄️ Banco de Dados</h4>
                <p><strong>Status:</strong> ${diagnostic.database.connection}</p>
                <p><strong>Credenciais:</strong> ${Array.isArray(diagnostic.database.stored_credentials) ? diagnostic.database.stored_credentials.length : 0} configuradas</p>
            </div>
            
            <div class="overview-card">
                <h4>🚀 Serviços</h4>
                <p><strong>WordPress:</strong> ${diagnostic.services.wordpress?.status || 'N/A'}</p>
                <p><strong>Google AI:</strong> ${diagnostic.services.google_ai?.status || 'N/A'}</p>
                <p><strong>Gmail:</strong> ${diagnostic.services.gmail_oauth?.status || 'N/A'}</p>
            </div>
            
            <div class="overview-card">
                <h4>🔐 Credenciais</h4>
                ${Object.entries(diagnostic.credentials).map(([key, status]) => 
                    `<p><strong>${key}:</strong> ${status}</p>`
                ).join('')}
            </div>
        </div>
    `;
}

/**
 * 🚀 GERAR CONTEÚDO DOS SERVIÇOS
 */
function generateServicesContent(diagnostic) {
    return `
        <div class="services-grid">
            ${Object.entries(diagnostic.services).map(([service, data]) => `
                <div class="service-card">
                    <h4>${getServiceIcon(service)} ${service.toUpperCase()}</h4>
                    <p><strong>Status:</strong> ${data.status}</p>
                    ${data.url ? `<p><strong>URL:</strong> ${data.url}</p>` : ''}
                    ${data.response_time ? `<p><strong>Tempo:</strong> ${data.response_time}</p>` : ''}
                    ${data.ga4_property ? `<p><strong>GA4:</strong> ${data.ga4_property}</p>` : ''}
                    ${data.search_console ? `<p><strong>GSC:</strong> ${data.search_console}</p>` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * 🗄️ GERAR CONTEÚDO DO BANCO
 */
function generateDatabaseContent(diagnostic) {
    return `
        <div class="database-info">
            <div class="db-connection">
                <h4>🔗 Conexão</h4>
                <p>${diagnostic.database.connection}</p>
            </div>
            
            <div class="db-tables">
                <h4>📋 Tabelas</h4>
                ${Object.entries(diagnostic.database.tables || {}).map(([table, info]) => `
                    <div class="table-info">
                        <strong>${table}:</strong> ${info.status}
                        ${info.row_count !== undefined ? ` (${info.row_count} registros)` : ''}
                        ${info.error ? `<br><small>Erro: ${info.error}</small>` : ''}
                    </div>
                `).join('')}
            </div>
            
            <div class="db-credentials">
                <h4>🔐 Credenciais Armazenadas</h4>
                ${Array.isArray(diagnostic.database.stored_credentials) ? 
                    diagnostic.database.stored_credentials.map(key => `<span class="credential-tag">${key}</span>`).join('') :
                    `<p>${diagnostic.database.stored_credentials}</p>`
                }
            </div>
        </div>
    `;
}

/**
 * 🎨 HELPERS
 */
function getHealthScoreClass(score) {
    const numScore = parseFloat(score);
    if (numScore >= 80) return 'excellent';
    if (numScore >= 60) return 'good';
    if (numScore >= 40) return 'warning';
    return 'critical';
}

function getServiceIcon(service) {
    const icons = {
        wordpress: '🌐',
        google_ai: '🤖',
        gmail_oauth: '📧',
        google_analytics: '📊'
    };
    return icons[service] || '🔧';
}

function showDiagnosticTab(tabName) {
    // Remover active de todos os tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.diagnostic-tab-content').forEach(content => content.classList.remove('active'));
    
    // Ativar tab selecionado
    document.querySelector(`[onclick="showDiagnosticTab('${tabName}')"]`).classList.add('active');
    document.getElementById(`diagnostic-${tabName}`).classList.add('active');
}

function closeDiagnosticModal() {
    document.querySelector('.diagnostic-modal')?.remove();
}

function copyDiagnosticToClipboard() {
    const textarea = document.getElementById('diagnostic-raw-text');
    textarea.select();
    document.execCommand('copy');
    showNotification('📋 Diagnóstico copiado para a área de transferência!', 'success');
}

/**
 * 🎨 ESTILOS DO DIAGNÓSTICO
 */
function addDiagnosticStyles() {
    if (document.getElementById('diagnostic-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'diagnostic-styles';
    styles.textContent = `
        .diagnostic-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .diagnostic-modal-content {
            background: white;
            border-radius: 12px;
            width: 90%;
            max-width: 1200px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        
        .diagnostic-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 2px solid #f0f0f0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px 12px 0 0;
        }
        
        .close-diagnostic {
            background: none;
            border: none;
            color: white;
            font-size: 30px;
            cursor: pointer;
            padding: 0;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            transition: background 0.3s;
        }
        
        .close-diagnostic:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .diagnostic-summary {
            display: flex;
            padding: 20px;
            gap: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        .health-score {
            text-align: center;
            padding: 20px;
            border-radius: 12px;
            color: white;
            min-width: 150px;
        }
        
        .health-score.excellent { background: linear-gradient(135deg, #4CAF50, #45a049); }
        .health-score.good { background: linear-gradient(135deg, #2196F3, #1976D2); }
        .health-score.warning { background: linear-gradient(135deg, #FF9800, #F57C00); }
        .health-score.critical { background: linear-gradient(135deg, #f44336, #d32f2f); }
        
        .health-score .score {
            font-size: 2em;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .summary-stats {
            flex: 1;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .stat {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stat .label {
            display: block;
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
        }
        
        .stat .value {
            font-size: 1.2em;
            color: #333;
        }
        
        .diagnostic-tabs {
            display: flex;
            border-bottom: 2px solid #f0f0f0;
            background: #fafafa;
        }
        
        .tab-btn {
            padding: 15px 25px;
            border: none;
            background: none;
            cursor: pointer;
            font-weight: bold;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        
        .tab-btn:hover {
            background: #f0f0f0;
            color: #333;
        }
        
        .tab-btn.active {
            color: #667eea;
            border-bottom-color: #667eea;
            background: white;
        }
        
        .diagnostic-tab-content {
            display: none;
            padding: 20px;
        }
        
        .diagnostic-tab-content.active {
            display: block;
        }
        
        .overview-grid, .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .overview-card, .service-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        .raw-log-container {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
        }
        
        .raw-log-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .copy-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        
        .copy-btn:hover {
            background: #5a67d8;
        }
        
        #diagnostic-raw-text {
            width: 100%;
            height: 400px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            background: #2d3748;
            color: #e2e8f0;
            border: none;
            border-radius: 6px;
            padding: 15px;
            resize: vertical;
        }
        
        .diagnostic-recommendations, .diagnostic-errors {
            margin: 20px;
            padding: 20px;
            border-radius: 8px;
        }
        
        .diagnostic-recommendations {
            background: #e8f5e8;
            border-left: 4px solid #4CAF50;
        }
        
        .diagnostic-errors {
            background: #ffeaea;
            border-left: 4px solid #f44336;
        }
        
        .credential-tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            margin: 2px;
            font-size: 0.9em;
        }
        
        .database-info > div {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .table-info {
            margin-bottom: 10px;
            padding: 10px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #667eea;
        }
    `;
    
    document.head.appendChild(styles);
} 