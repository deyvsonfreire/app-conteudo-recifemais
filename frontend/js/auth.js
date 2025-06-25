/**
 * Auth Module - Sistema de Autenticação Frontend
 * Gerencia login, logout, tokens e estado de autenticação
 */

class AuthManager {
    constructor() {
        this.baseUrl = this.getBaseUrl();
        this.token = localStorage.getItem('auth_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        
        // Auto-refresh token antes de expirar
        this.setupTokenRefresh();
        
        console.log('🔐 Auth Manager inicializado');
    }
    
    getBaseUrl() {
        // Detectar se estamos em desenvolvimento ou produção
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        } else {
            return 'https://redacao.admin.recifemais.com.br';
        }
    }
    
    // ==========================================
    // AUTHENTICATION METHODS
    // ==========================================
    
    async login(email, password) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Salvar tokens e dados do usuário
                this.token = data.access_token;
                this.refreshToken = data.refresh_token;
                this.user = data.user;
                
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);
                localStorage.setItem('user', JSON.stringify(this.user));
                
                // Configurar auto-refresh
                this.setupTokenRefresh();
                
                console.log('✅ Login realizado:', this.user.email);
                return { success: true, user: this.user };
            } else {
                console.error('❌ Erro no login:', data.message);
                return { success: false, error: data.message || 'Erro de autenticação' };
            }
        } catch (error) {
            console.error('❌ Erro de rede no login:', error);
            return { success: false, error: 'Erro de conexão com o servidor' };
        }
    }
    
    async logout() {
        try {
            if (this.token) {
                await fetch(`${this.baseUrl}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json',
                    }
                });
            }
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
        } finally {
            // Limpar dados locais
            this.clearAuthData();
            console.log('🔒 Logout realizado');
        }
    }
    
    async refreshAccessToken() {
        if (!this.refreshToken) {
            this.clearAuthData();
            return false;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh_token: this.refreshToken })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.token = data.access_token;
                this.refreshToken = data.refresh_token;
                
                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('refresh_token', this.refreshToken);
                
                console.log('🔄 Token renovado');
                return true;
            } else {
                console.error('❌ Erro ao renovar token');
                this.clearAuthData();
                return false;
            }
        } catch (error) {
            console.error('❌ Erro de rede ao renovar token:', error);
            this.clearAuthData();
            return false;
        }
    }
    
    clearAuthData() {
        this.token = null;
        this.refreshToken = null;
        this.user = null;
        
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
        }
    }
    
    // ==========================================
    // TOKEN MANAGEMENT
    // ==========================================
    
    setupTokenRefresh() {
        if (!this.token) return;
        
        try {
            // Decodificar token JWT para obter tempo de expiração
            const tokenParts = this.token.split('.');
            if (tokenParts.length !== 3) return;
            
            const payload = JSON.parse(atob(tokenParts[1]));
            const expirationTime = payload.exp * 1000; // Converter para milliseconds
            const currentTime = Date.now();
            const timeUntilExpiry = expirationTime - currentTime;
            
            // Renovar token 5 minutos antes de expirar
            const refreshTime = Math.max(timeUntilExpiry - (5 * 60 * 1000), 60000);
            
            if (refreshTime > 0) {
                this.refreshTimer = setTimeout(() => {
                    this.refreshAccessToken();
                }, refreshTime);
                
                console.log(`⏰ Token será renovado em ${Math.round(refreshTime / 60000)} minutos`);
            }
        } catch (error) {
            console.error('Erro ao configurar renovação de token:', error);
        }
    }
    
    // ==========================================
    // API HELPERS
    // ==========================================
    
    async apiCall(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            // Se token expirou, tentar renovar
            if (response.status === 401 && this.refreshToken) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Repetir requisição com novo token
                    headers['Authorization'] = `Bearer ${this.token}`;
                    return await fetch(url, { ...options, headers });
                }
            }
            
            return response;
        } catch (error) {
            console.error('Erro na requisição API:', error);
            throw error;
        }
    }
    
    // ==========================================
    // USER MANAGEMENT
    // ==========================================
    
    async createInitialAdmin(email, password) {
        try {
            const response = await fetch(`${this.baseUrl}/admin/setup/initial-admin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email, 
                    password,
                    role: 'admin'
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                console.log('👑 Admin inicial criado');
                return { success: true };
            } else {
                console.error('❌ Erro ao criar admin:', data.message);
                return { success: false, error: data.message || 'Erro ao criar admin' };
            }
        } catch (error) {
            console.error('❌ Erro de rede ao criar admin:', error);
            return { success: false, error: 'Erro de conexão com o servidor' };
        }
    }
    
    async getUsers() {
        try {
            const response = await this.apiCall('/admin/users');
            
            if (response.ok) {
                const data = await response.json();
                return { success: true, users: data.users };
            } else {
                const data = await response.json();
                return { success: false, error: data.detail || 'Erro ao listar usuários' };
            }
        } catch (error) {
            console.error('Erro ao listar usuários:', error);
            return { success: false, error: 'Erro de conexão' };
        }
    }
    
    async createUser(email, password, role, metadata = {}) {
        try {
            const response = await this.apiCall('/admin/users', {
                method: 'POST',
                body: JSON.stringify({ email, password, role, metadata })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true, user: data };
            } else {
                return { success: false, error: data.message || data.detail || 'Erro ao criar usuário' };
            }
        } catch (error) {
            console.error('Erro ao criar usuário:', error);
            return { success: false, error: 'Erro de conexão' };
        }
    }
    
    async updateUserRole(userId, newRole) {
        try {
            const response = await this.apiCall('/admin/users/role', {
                method: 'PUT',
                body: JSON.stringify({ user_id: userId, new_role: newRole })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true };
            } else {
                return { success: false, error: data.error || data.detail || 'Erro ao atualizar role' };
            }
        } catch (error) {
            console.error('Erro ao atualizar role:', error);
            return { success: false, error: 'Erro de conexão' };
        }
    }
    
    async deleteUser(userId) {
        try {
            const response = await this.apiCall(`/admin/users/${userId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                return { success: true };
            } else {
                return { success: false, error: data.error || data.detail || 'Erro ao remover usuário' };
            }
        } catch (error) {
            console.error('Erro ao remover usuário:', error);
            return { success: false, error: 'Erro de conexão' };
        }
    }
    
    // ==========================================
    // STATE MANAGEMENT
    // ==========================================
    
    isAuthenticated() {
        return !!(this.token && this.user);
    }
    
    hasPermission(permission) {
        if (!this.user) return false;
        
        const permissions = this.user.permissions || [];
        return permissions.includes('*') || permissions.includes(permission);
    }
    
    isAdmin() {
        return this.user && this.user.role === 'admin';
    }
    
    getCurrentUser() {
        return this.user;
    }
    
    getUserRole() {
        return this.user ? this.user.role : null;
    }
}

// Instância global
window.authManager = new AuthManager(); 