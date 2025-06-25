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
            const response = await authManager.apiCall('/google-data/dashboard');
            if (response.ok) {
                const data = await response.json();
                this.renderGoogleDataDashboard(data);
            } else {
                container.innerHTML = '<p class="text-gray-500">Dados do Google Analytics não disponíveis. Configure a integração primeiro.</p>';
            }
        } catch (error) {
            console.error('Erro ao carregar analytics:', error);
            container.innerHTML = '<p class="text-red-500">Erro ao carregar dados de analytics.</p>';
        }
    }
    
    async loadEmailsData() {
        // Inicializar o workflow de emails
        if (typeof emailWorkflow !== 'undefined') {
            emailWorkflow.init();
        }
        console.log('📧 Carregando dados de emails...');
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
        if (!container || !data) return;
        
        // Renderizar dados do Google Analytics e Search Console
        container.innerHTML = `
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="text-lg font-medium text-gray-900 mb-3">Search Console</h3>
                    <div class="space-y-2">
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Total de Clicks:</span>
                            <span class="text-sm font-medium">${data.gsc?.summary?.total_clicks || '--'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Total de Impressões:</span>
                            <span class="text-sm font-medium">${data.gsc?.summary?.total_impressions || '--'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">CTR Médio:</span>
                            <span class="text-sm font-medium">${data.gsc?.summary?.avg_ctr ? (data.gsc.summary.avg_ctr * 100).toFixed(2) + '%' : '--'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="bg-gray-50 p-4 rounded-lg">
                    <h3 class="text-lg font-medium text-gray-900 mb-3">Google Analytics</h3>
                    <div class="space-y-2">
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Sessões:</span>
                            <span class="text-sm font-medium">${data.ga4?.totals?.sessions || '--'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Usuários:</span>
                            <span class="text-sm font-medium">${data.ga4?.totals?.users || '--'}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Pageviews:</span>
                            <span class="text-sm font-medium">${data.ga4?.totals?.pageviews || '--'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
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