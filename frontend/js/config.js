/**
 * Gerenciador de Configurações
 * Responsável por gerenciar todas as configurações do sistema
 */
class ConfigManager {
    constructor() {
        this.configs = {};
        this.serviceStatus = {};
        this.setupEventListeners();
        this.loadConfigurations();
        this.checkServiceStatus();
    }

    setupEventListeners() {
        // WordPress
        const wpForm = document.getElementById('wpConfigForm');
        if (wpForm) {
            wpForm.addEventListener('submit', (e) => this.saveWordPressConfig(e));
        }

        const testWpBtn = document.getElementById('testWpConnection');
        if (testWpBtn) {
            testWpBtn.addEventListener('click', () => this.testWordPressConnection());
        }

        // Gemini
        const geminiForm = document.getElementById('geminiConfigForm');
        if (geminiForm) {
            geminiForm.addEventListener('submit', (e) => this.saveGeminiConfig(e));
        }

        const testGeminiBtn = document.getElementById('testGeminiConnection');
        if (testGeminiBtn) {
            testGeminiBtn.addEventListener('click', () => this.testGeminiConnection());
        }

        // Gmail
        const authenticateGmailBtn = document.getElementById('authenticateGmail');
        if (authenticateGmailBtn) {
            authenticateGmailBtn.addEventListener('click', () => this.authenticateGmail());
        }

        // Google Data
        const googleDataForm = document.getElementById('googleDataConfigForm');
        if (googleDataForm) {
            googleDataForm.addEventListener('submit', (e) => this.saveGoogleDataConfig(e));
        }

        const authenticateGoogleDataBtn = document.getElementById('authenticateGoogleData');
        if (authenticateGoogleDataBtn) {
            authenticateGoogleDataBtn.addEventListener('click', () => this.authenticateGoogleData());
        }
    }

    async loadConfigurations() {
        try {
            showLoading('Carregando configurações...');
            
            // Carregar configurações do backend
            const response = await authManager.apiCall('/admin/secure-config');
            
            if (response.ok) {
                const data = await response.json();
                this.configs = data.configs || {};
                this.populateConfigForms();
                this.updateServiceStatusIndicators();
            } else {
                throw new Error('Erro ao carregar configurações');
            }
            
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
            appController.showToastNotification('Erro ao carregar configurações: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    populateConfigForms() {
        // WordPress - carregar dados existentes
        const wpUrlField = document.getElementById('wpUrl');
        const wpUsernameField = document.getElementById('wpUsername');
        
        if (wpUrlField) {
            wpUrlField.value = this.getConfigValue('wordpress_url') || 'https://recifemais.com.br';
        }
        
        if (wpUsernameField) {
            wpUsernameField.value = this.getConfigValue('wordpress_username') || '';
        }
        
        // Gemini AI
        const geminiKeyField = document.getElementById('geminiApiKey');
        if (geminiKeyField && this.getConfigValue('google_ai_api_key')) {
            geminiKeyField.value = '••••••••••••••••'; // Mascarar chave existente
            geminiKeyField.placeholder = 'Chave configurada (digite nova para alterar)';
        }
        
        // Google Data
        const ga4PropertyField = document.getElementById('ga4PropertyId');
        const gscSiteField = document.getElementById('gscSiteUrl');
        
        if (ga4PropertyField) {
            ga4PropertyField.value = this.getConfigValue('ga4_property_id') || '';
        }
        
        if (gscSiteField) {
            gscSiteField.value = this.getConfigValue('gsc_site_url') || 'https://recifemais.com.br/';
        }
    }

    getConfigValue(key) {
        const config = this.configs.find(c => c.key === key);
        return config ? config.value : null;
    }

    async checkServiceStatus() {
        try {
            const response = await authManager.apiCall('/health');
            
            if (response.ok) {
                const healthData = await response.json();
                this.serviceStatus = healthData.checks;
                this.updateServiceStatusIndicators();
            }
        } catch (error) {
            console.error('Erro ao verificar status dos serviços:', error);
        }
    }

    updateServiceStatusIndicators() {
        // WordPress Status
        this.updateStatusIndicator('wpStatus', this.serviceStatus.wordpress, {
            connected: 'WordPress conectado ✅',
            disconnected: 'WordPress desconectado ❌',
            action: 'Configure as credenciais abaixo'
        });

        // Gemini Status  
        this.updateStatusIndicator('geminiStatus', this.serviceStatus.gemini, {
            connected: 'Gemini AI conectado ✅',
            disconnected: 'Gemini AI desconectado ❌',
            action: 'Configure a API Key abaixo'
        });

        // Gmail Status
        this.updateStatusIndicator('gmailStatus', this.serviceStatus.gmail, {
            connected: 'Gmail conectado ✅',
            disconnected: 'Gmail desconectado ❌',
            action: 'Clique em "Conectar Gmail" abaixo'
        });

        // Google Data Status
        this.updateStatusIndicator('googleDataStatus', this.serviceStatus.google_data, {
            connected: 'Google Analytics conectado ✅',
            disconnected: 'Google Analytics desconectado ❌',
            action: 'Clique em "Conectar Google Analytics" abaixo'
        });
    }

    updateStatusIndicator(elementId, isConnected, messages) {
        const element = document.getElementById(elementId);
        if (!element) return;

        if (isConnected) {
            element.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
            element.textContent = messages.connected;
        } else {
            element.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800';
            element.textContent = messages.disconnected;
            
            // Adicionar dica de ação
            const parentCard = element.closest('.bg-white');
            if (parentCard) {
                let actionHint = parentCard.querySelector('.action-hint');
                if (!actionHint) {
                    actionHint = document.createElement('div');
                    actionHint.className = 'action-hint mt-2 text-sm text-blue-600 bg-blue-50 p-2 rounded';
                    actionHint.textContent = `💡 ${messages.action}`;
                    parentCard.appendChild(actionHint);
                }
            }
        }
    }

    // WordPress Configuration
    async saveWordPressConfig(event) {
        event.preventDefault();
        
        const wpConfig = {
            wordpress_url: document.getElementById('wpUrl').value,
            wordpress_username: document.getElementById('wpUsername').value,
            wordpress_password: document.getElementById('wpPassword').value
        };

        if (!wpConfig.wordpress_url || !wpConfig.wordpress_username || !wpConfig.wordpress_password) {
            appController.showToastNotification('Todos os campos do WordPress são obrigatórios', 'error');
            return;
        }

        try {
            showLoading('Salvando configuração do WordPress...');
            
            // Salvar cada configuração individualmente
            for (const [key, value] of Object.entries(wpConfig)) {
                const response = await authManager.apiCall(`/admin/secure-config/${key}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `value=${encodeURIComponent(value)}&description=Configurado via interface admin`
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || `Erro ao salvar ${key}`);
                }
            }

            appController.showToastNotification('Configuração do WordPress salva com sucesso!', 'success');
            document.getElementById('wpPassword').value = ''; // Limpar senha
            this.checkServiceStatus();
            
        } catch (error) {
            console.error('Erro ao salvar WordPress config:', error);
            appController.showToastNotification('Erro ao salvar configuração: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    async testWordPressConnection() {
        try {
            showLoading('Testando conexão com WordPress...');
            
            const response = await authManager.apiCall('/wordpress/posts', {
                method: 'GET'
            });

            if (response.ok) {
                const result = await response.json();
                appController.showToastNotification(`WordPress conectado com sucesso! ${result.posts?.length || 0} posts encontrados.`, 'success');
            } else {
                throw new Error('Erro na conexão com WordPress');
            }
            
        } catch (error) {
            console.error('Erro ao testar WordPress:', error);
            appController.showToastNotification('Erro na conexão: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    // Gemini Configuration
    async saveGeminiConfig(event) {
        event.preventDefault();
        
        const apiKey = document.getElementById('geminiApiKey').value;
        
        if (!apiKey || apiKey === '••••••••••••••••') {
            appController.showToastNotification('Digite uma API Key válida do Google AI', 'error');
            return;
        }

        try {
            showLoading('Salvando configuração do Gemini AI...');
            
            const response = await authManager.apiCall('/admin/secure-config/google_ai_api_key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `value=${encodeURIComponent(apiKey)}&description=API Key Gemini configurada via interface admin`
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao salvar API Key');
            }

            appController.showToastNotification('API Key do Gemini salva com sucesso!', 'success');
            document.getElementById('geminiApiKey').value = '••••••••••••••••';
            this.checkServiceStatus();
            
        } catch (error) {
            console.error('Erro ao salvar Gemini config:', error);
            appController.showToastNotification('Erro ao salvar configuração: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    async testGeminiConnection() {
        try {
            showLoading('Testando conexão com Gemini AI...');
            
            const response = await authManager.apiCall('/suggest-topics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ seed_topics: ['teste'] })
            });

            if (response.ok) {
                const result = await response.json();
                appController.showToastNotification('Gemini AI conectado e funcionando!', 'success');
            } else {
                throw new Error('Erro na conexão com Gemini');
            }
            
        } catch (error) {
            console.error('Erro ao testar Gemini:', error);
            appController.showToastNotification('Erro na conexão: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    // Gmail Authentication - Um clique
    async authenticateGmail() {
        try {
            showLoading('Iniciando autenticação do Gmail...');
            
            const response = await authManager.apiCall('/auth/gmail');
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.auth_url) {
                    // Abrir URL de autenticação em nova janela
                    const authWindow = window.open(result.auth_url, 'gmail_auth', 'width=600,height=600,scrollbars=yes,resizable=yes');
                    
                    appController.showToastNotification('Janela de autenticação aberta. Complete o processo e retorne aqui.', 'info');
                    
                    // Verificar status periodicamente
                    this.checkGmailAuthStatus(authWindow);
                } else {
                    appController.showToastNotification('Gmail já está autenticado!', 'success');
                }
            } else {
                throw new Error('Erro ao iniciar autenticação');
            }
            
        } catch (error) {
            console.error('Erro na autenticação Gmail:', error);
            appController.showToastNotification('Erro na autenticação: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    checkGmailAuthStatus(authWindow) {
        const checkInterval = setInterval(async () => {
            try {
                // Verificar se a janela foi fechada
                if (authWindow.closed) {
                    clearInterval(checkInterval);
                    
                    // Aguardar um pouco e verificar status
                    setTimeout(async () => {
                        const response = await authManager.apiCall('/gmail/status');
                        if (response.ok) {
                            const status = await response.json();
                            if (status.authenticated) {
                                appController.showToastNotification('Gmail autenticado com sucesso!', 'success');
                                this.checkServiceStatus();
                            } else {
                                appController.showToastNotification('Autenticação cancelada ou falhou.', 'warning');
                            }
                        }
                    }, 2000);
                }
            } catch (error) {
                clearInterval(checkInterval);
                console.error('Erro ao verificar status de autenticação:', error);
            }
        }, 1000);
        
        // Timeout após 5 minutos
        setTimeout(() => {
            clearInterval(checkInterval);
            if (!authWindow.closed) {
                authWindow.close();
                appController.showToastNotification('Timeout de autenticação. Tente novamente.', 'warning');
            }
        }, 300000);
    }

    // Google Data Configuration e Authentication
    async saveGoogleDataConfig(event) {
        event.preventDefault();
        
        const googleDataConfig = {
            ga4_property_id: document.getElementById('ga4PropertyId').value,
            gsc_site_url: document.getElementById('gscSiteUrl').value
        };

        try {
            showLoading('Salvando configuração do Google Data...');
            
            // Salvar cada configuração
            for (const [key, value] of Object.entries(googleDataConfig)) {
                if (value) {
                    const response = await authManager.apiCall(`/admin/secure-config/${key}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `value=${encodeURIComponent(value)}&description=Configurado via interface admin`
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || `Erro ao salvar ${key}`);
                    }
                }
            }

            appController.showToastNotification('Configuração do Google Data salva com sucesso!', 'success');
            this.checkServiceStatus();
            
        } catch (error) {
            console.error('Erro ao salvar Google Data config:', error);
            appController.showToastNotification('Erro ao salvar configuração: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    async authenticateGoogleData() {
        try {
            showLoading('Iniciando autenticação do Google Data...');
            
            const response = await authManager.apiCall('/auth/google');
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.auth_url) {
                    // Abrir URL de autenticação em nova janela
                    const authWindow = window.open(result.auth_url, 'google_data_auth', 'width=600,height=600,scrollbars=yes,resizable=yes');
                    
                    appController.showToastNotification('Janela de autenticação aberta. Complete o processo e retorne aqui.', 'info');
                    
                    // Verificar status periodicamente
                    this.checkGoogleDataAuthStatus(authWindow);
                } else {
                    appController.showToastNotification('Google Data já está autenticado!', 'success');
                }
            } else {
                throw new Error('Erro ao iniciar autenticação');
            }
            
        } catch (error) {
            console.error('Erro na autenticação Google Data:', error);
            appController.showToastNotification('Erro na autenticação: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    checkGoogleDataAuthStatus(authWindow) {
        const checkInterval = setInterval(async () => {
            try {
                // Verificar se a janela foi fechada
                if (authWindow.closed) {
                    clearInterval(checkInterval);
                    
                    // Aguardar um pouco e verificar status
                    setTimeout(async () => {
                        const response = await authManager.apiCall('/google-data/status');
                        if (response.ok) {
                            const status = await response.json();
                            if (status.authenticated) {
                                appController.showToastNotification('Google Analytics conectado com sucesso!', 'success');
                                this.checkServiceStatus();
                            } else {
                                appController.showToastNotification('Autenticação cancelada ou falhou.', 'warning');
                            }
                        }
                    }, 2000);
                }
            } catch (error) {
                clearInterval(checkInterval);
                console.error('Erro ao verificar status de autenticação:', error);
            }
        }, 1000);
        
        // Timeout após 5 minutos
        setTimeout(() => {
            clearInterval(checkInterval);
            if (!authWindow.closed) {
                authWindow.close();
                appController.showToastNotification('Timeout de autenticação. Tente novamente.', 'warning');
            }
        }, 300000);
    }
}

// Instância global
let configManager;

// Inicializar quando a seção de configurações for carregada
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que todos os elementos estejam carregados
    setTimeout(() => {
        if (document.getElementById('configSection')) {
            configManager = new ConfigManager();
        }
    }, 100);
}); 