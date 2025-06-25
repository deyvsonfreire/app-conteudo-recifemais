/**
 * App Main - Controlador Principal da Aplicação
 * Gerencia o fluxo entre tela de login e dashboard
 */

class AppController {
    constructor() {
        this.loginScreen = document.getElementById('loginScreen');
        this.dashboardScreen = document.getElementById('dashboardScreen');
        this.setupAdminModal = document.getElementById('setupAdminModal');
        
        console.log('🚀 App Controller inicializado');
    }
    
    async init() {
        // Verificar se já está autenticado
        if (authManager.isAuthenticated()) {
            this.showDashboard();
        } else {
            this.showLogin();
        }
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Inicializar ícones Lucide
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }
    
    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        loginForm?.addEventListener('submit', (e) => this.handleLogin(e));
        
        // Setup admin modal
        const setupAdminLink = document.getElementById('setupAdminLink');
        setupAdminLink?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showSetupAdminModal();
        });
        
        const setupAdminForm = document.getElementById('setupAdminForm');
        setupAdminForm?.addEventListener('submit', (e) => this.handleSetupAdmin(e));
        
        const cancelSetupAdmin = document.getElementById('cancelSetupAdmin');
        cancelSetupAdmin?.addEventListener('click', () => this.hideSetupAdminModal());
        
        // CSS classes para navegação
        this.addNavigationStyles();
    }
    
    addNavigationStyles() {
        // Adicionar estilos CSS dinâmicos
        const style = document.createElement('style');
        style.textContent = `
            .nav-link {
                @apply px-3 py-2 rounded-md text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100 flex items-center transition-colors duration-200;
            }
            .nav-link.active {
                @apply text-blue-600 bg-blue-50;
            }
        `;
        document.head.appendChild(style);
    }
    
    // ==========================================
    // SCREEN MANAGEMENT
    // ==========================================
    
    showLogin() {
        this.loginScreen?.classList.remove('hidden');
        this.dashboardScreen?.classList.add('hidden');
        
        // Limpar formulário
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.reset();
        }
        
        this.hideLoginError();
        console.log('📱 Tela de login exibida');
    }
    
    showDashboard() {
        this.loginScreen?.classList.add('hidden');
        this.dashboardScreen?.classList.remove('hidden');
        
        // Inicializar dashboard
        if (window.dashboardManager) {
            dashboardManager.init();
        }
        
        console.log('📊 Dashboard exibido');
    }
    
    showSetupAdminModal() {
        this.setupAdminModal?.classList.remove('hidden');
        
        // Limpar formulário
        const form = document.getElementById('setupAdminForm');
        if (form) {
            form.reset();
        }
        
        this.hideSetupAdminError();
    }
    
    hideSetupAdminModal() {
        this.setupAdminModal?.classList.add('hidden');
    }
    
    // ==========================================
    // AUTHENTICATION HANDLERS
    // ==========================================
    
    async handleLogin(event) {
        event.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (!email || !password) {
            this.showLoginError('Por favor, preencha todos os campos');
            return;
        }
        
        this.setLoginLoading(true);
        this.hideLoginError();
        
        try {
            const result = await authManager.login(email, password);
            
            if (result.success) {
                console.log('✅ Login bem-sucedido');
                this.showDashboard();
            } else {
                this.showLoginError(result.error || 'Erro ao fazer login');
            }
        } catch (error) {
            console.error('Erro no login:', error);
            this.showLoginError('Erro de conexão com o servidor');
        } finally {
            this.setLoginLoading(false);
        }
    }
    
    async handleSetupAdmin(event) {
        event.preventDefault();
        
        const email = document.getElementById('adminEmail').value;
        const password = document.getElementById('adminPassword').value;
        
        if (!email || !password) {
            this.showSetupAdminError('Por favor, preencha todos os campos');
            return;
        }
        
        if (password.length < 6) {
            this.showSetupAdminError('A senha deve ter pelo menos 6 caracteres');
            return;
        }
        
        try {
            const result = await authManager.createInitialAdmin(email, password);
            
            if (result.success) {
                alert('Admin criado com sucesso! Faça login agora.');
                this.hideSetupAdminModal();
                
                // Preencher email no formulário de login
                document.getElementById('email').value = email;
            } else {
                this.showSetupAdminError(result.error || 'Erro ao criar admin');
            }
        } catch (error) {
            console.error('Erro ao criar admin:', error);
            this.showSetupAdminError('Erro de conexão com o servidor');
        }
    }
    
    // ==========================================
    // UI HELPERS
    // ==========================================
    
    setLoginLoading(loading) {
        const button = document.querySelector('#loginForm button[type="submit"]');
        const buttonText = document.getElementById('loginButtonText');
        const buttonSpinner = document.getElementById('loginButtonSpinner');
        
        if (loading) {
            button.disabled = true;
            buttonText.textContent = 'Entrando...';
            buttonSpinner?.classList.remove('hidden');
        } else {
            button.disabled = false;
            buttonText.textContent = 'Entrar';
            buttonSpinner?.classList.add('hidden');
        }
    }
    
    showLoginError(message) {
        const errorDiv = document.getElementById('loginError');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
    }
    
    hideLoginError() {
        const errorDiv = document.getElementById('loginError');
        if (errorDiv) {
            errorDiv.classList.add('hidden');
        }
    }
    
    showSetupAdminError(message) {
        const errorDiv = document.getElementById('setupAdminError');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
    }
    
    hideSetupAdminError() {
        const errorDiv = document.getElementById('setupAdminError');
        if (errorDiv) {
            errorDiv.classList.add('hidden');
        }
    }
    
    // ==========================================
    // GLOBAL ERROR HANDLING
    // ==========================================
    
    setupGlobalErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Erro global:', event.error);
            this.showGlobalError('Ocorreu um erro inesperado');
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Promise rejeitada:', event.reason);
            this.showGlobalError('Erro de conexão ou processamento');
        });
    }
    
    showGlobalError(message) {
        // Implementar notificação global de erro
        console.error('🚨 Erro global:', message);
        
        // Por enquanto, usar alert - depois implementar toast/notification
        if (confirm(`${message}\n\nDeseja recarregar a página?`)) {
            window.location.reload();
        }
    }
}

// ==========================================
// INITIALIZATION
// ==========================================

// Aguardar carregamento completo da página
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎯 DOM carregado, inicializando aplicação...');
    
    try {
        // Criar instância do controlador principal
        window.appController = new AppController();
        
        // Configurar tratamento global de erros
        appController.setupGlobalErrorHandling();
        
        // Inicializar aplicação
        await appController.init();
        
        console.log('✅ Aplicação inicializada com sucesso');
        
    } catch (error) {
        console.error('❌ Erro ao inicializar aplicação:', error);
        
        // Fallback em caso de erro crítico
        document.body.innerHTML = `
            <div class="min-h-screen bg-red-50 flex items-center justify-center px-4">
                <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
                    <div class="text-red-600 text-6xl mb-4">⚠️</div>
                    <h1 class="text-xl font-bold text-gray-900 mb-2">Erro de Inicialização</h1>
                    <p class="text-gray-600 mb-4">Não foi possível carregar a aplicação.</p>
                    <button 
                        onclick="window.location.reload()" 
                        class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                    >
                        Tentar Novamente
                    </button>
                </div>
            </div>
        `;
    }
});

// ==========================================
// UTILITIES
// ==========================================

// Função utilitária para debug
window.debug = {
    auth: () => console.log('Auth:', authManager),
    dashboard: () => console.log('Dashboard:', dashboardManager),
    app: () => console.log('App:', appController),
    user: () => console.log('User:', authManager.getCurrentUser()),
    logout: () => appController.handleLogout()
}; 