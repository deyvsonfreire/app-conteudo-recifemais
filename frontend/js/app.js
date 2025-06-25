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
        // Contador para evitar spam de notificações
        this.errorCount = 0;
        this.lastErrorTime = 0;
        
        window.addEventListener('error', (event) => {
            console.error('Erro global:', event.error);
            this.handleGlobalError('Ocorreu um erro inesperado', event.error);
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Promise rejeitada:', event.reason);
            this.handleGlobalError('Erro de conexão ou processamento', event.reason);
        });
    }
    
    handleGlobalError(message, error) {
        const now = Date.now();
        
        // Evitar spam de alertas (máximo 1 por 10 segundos)
        if (now - this.lastErrorTime < 10000) {
            console.warn('Erro ignorado para evitar spam:', message);
            return;
        }
        
        this.lastErrorTime = now;
        this.errorCount++;
        
        // Mostrar notificação toast em vez de alert
        this.showToastNotification(message, 'error');
        
        // Após 3 erros, sugerir recarregar página
        if (this.errorCount >= 3) {
            this.showReloadSuggestion();
        }
    }
    
    showToastNotification(message, type = 'info') {
        // Remover notificação anterior se existir
        const existingToast = document.getElementById('globalToast');
        if (existingToast) {
            existingToast.remove();
        }
        
        // Criar notificação toast
        const toast = document.createElement('div');
        toast.id = 'globalToast';
        toast.className = `fixed top-4 right-4 z-50 max-w-sm p-4 rounded-lg shadow-lg transform transition-all duration-300 ${
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'warning' ? 'bg-yellow-500 text-white' :
            type === 'success' ? 'bg-green-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        
        toast.innerHTML = `
            <div class="flex items-center">
                <span class="mr-3">${
                    type === 'error' ? '⚠️' : 
                    type === 'warning' ? '⚠️' : 
                    type === 'success' ? '✅' : 
                    'ℹ️'
                }</span>
                <span class="flex-1">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-3 text-white hover:text-gray-200">
                    ✕
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }
    
    showReloadSuggestion() {
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 z-50 max-w-sm p-4 bg-orange-500 text-white rounded-lg shadow-lg';
        
        toast.innerHTML = `
            <div class="space-y-3">
                <div class="flex items-center">
                    <span class="mr-3">🔄</span>
                    <span class="flex-1">Múltiplos erros detectados</span>
                </div>
                <div class="text-sm opacity-90">
                    Recomendamos recarregar a página para resolver problemas de conexão.
                </div>
                <div class="flex space-x-2">
                    <button onclick="window.location.reload()" 
                            class="bg-white text-orange-500 px-3 py-1 rounded text-sm font-medium hover:bg-gray-100">
                        Recarregar
                    </button>
                    <button onclick="this.parentElement.parentElement.parentElement.remove(); appController.errorCount = 0;" 
                            class="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700">
                        Ignorar
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(toast);
    }
    
    showGlobalError(message) {
        // Método mantido para compatibilidade, mas agora usa toast
        this.showToastNotification(message, 'error');
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