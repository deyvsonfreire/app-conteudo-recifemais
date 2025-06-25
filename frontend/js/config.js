/**
 * Gerenciador de Configurações
 * Responsável por gerenciar todas as configurações do sistema
 */
class ConfigManager {
    constructor() {
        this.configs = {};
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadConfigurations();
        this.checkServiceStatus();
    }

    bindEvents() {
        // WordPress Configuration
        const wpForm = document.getElementById('wpConfigForm');
        if (wpForm) {
            wpForm.addEventListener('submit', (e) => this.saveWordPressConfig(e));
        }

        const testWpBtn = document.getElementById('testWpConnection');
        if (testWpBtn) {
            testWpBtn.addEventListener('click', () => this.testWordPressConnection());
        }

        // Gmail Configuration
        const gmailForm = document.getElementById('gmailConfigForm');
        if (gmailForm) {
            gmailForm.addEventListener('submit', (e) => this.saveGmailConfig(e));
        }

        const authGmailBtn = document.getElementById('authenticateGmail');
        if (authGmailBtn) {
            authGmailBtn.addEventListener('click', () => this.authenticateGmail());
        }

        // Gemini Configuration
        const geminiForm = document.getElementById('geminiConfigForm');
        if (geminiForm) {
            geminiForm.addEventListener('submit', (e) => this.saveGeminiConfig(e));
        }

        const testGeminiBtn = document.getElementById('testGeminiConnection');
        if (testGeminiBtn) {
            testGeminiBtn.addEventListener('click', () => this.testGeminiConnection());
        }

        // Google Data Configuration
        const saveGoogleDataBtn = document.getElementById('saveGoogleDataConfig');
        if (saveGoogleDataBtn) {
            saveGoogleDataBtn.addEventListener('click', () => this.saveGoogleDataConfig());
        }

        const authGoogleDataBtn = document.getElementById('authenticateGoogleData');
        if (authGoogleDataBtn) {
            authGoogleDataBtn.addEventListener('click', () => this.authenticateGoogleData());
        }
    }

    async loadConfigurations() {
        try {
            showLoading('Carregando configurações...');
            
            const response = await fetch('/api/config', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao carregar configurações');
            }

            this.configs = await response.json();
            this.populateConfigForms();
            
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
            showAlert('Erro ao carregar configurações: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    populateConfigForms() {
        // WordPress
        if (this.configs.wordpress) {
            const wp = this.configs.wordpress;
            if (document.getElementById('wpUrl')) document.getElementById('wpUrl').value = wp.url || '';
            if (document.getElementById('wpUsername')) document.getElementById('wpUsername').value = wp.username || '';
        }

        // Gmail
        if (this.configs.gmail) {
            const gmail = this.configs.gmail;
            if (document.getElementById('gmailClientId')) document.getElementById('gmailClientId').value = gmail.client_id || '';
        }

        // Gemini
        if (this.configs.gemini) {
            const gemini = this.configs.gemini;
            if (document.getElementById('geminiModel')) document.getElementById('geminiModel').value = gemini.model || 'gemini-pro';
        }

        // Google Data
        if (this.configs.google_data) {
            const gd = this.configs.google_data;
            if (document.getElementById('ga4PropertyId')) document.getElementById('ga4PropertyId').value = gd.ga4_property_id || '';
            if (document.getElementById('gscSiteUrl')) document.getElementById('gscSiteUrl').value = gd.gsc_site_url || '';
        }
    }

    async checkServiceStatus() {
        try {
            const response = await fetch('/api/config/status', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao verificar status dos serviços');
            }

            const status = await response.json();
            this.updateStatusBadges(status);
            
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            // Manter status como "Verificando..." em caso de erro
        }
    }

    updateStatusBadges(status) {
        // WordPress Status
        const wpStatus = document.getElementById('wpStatus');
        if (wpStatus) {
            const wp = status.wordpress || {};
            if (wp.connected) {
                wpStatus.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
                wpStatus.textContent = 'Conectado';
            } else {
                wpStatus.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800';
                wpStatus.textContent = wp.error || 'Não configurado';
            }
        }

        // Gmail Status
        const gmailStatus = document.getElementById('gmailStatus');
        if (gmailStatus) {
            const gmail = status.gmail || {};
            if (gmail.authenticated) {
                gmailStatus.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
                gmailStatus.textContent = 'Autenticado';
            } else {
                gmailStatus.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800';
                gmailStatus.textContent = gmail.error || 'Não autenticado';
            }
        }

        // Gemini Status
        const geminiStatus = document.getElementById('geminiStatus');
        if (geminiStatus) {
            const gemini = status.gemini || {};
            if (gemini.configured) {
                geminiStatus.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
                geminiStatus.textContent = 'Configurado';
            } else {
                geminiStatus.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800';
                geminiStatus.textContent = gemini.error || 'Não configurado';
            }
        }

        // Google Data Status
        const googleDataStatus = document.getElementById('googleDataStatus');
        if (googleDataStatus) {
            const gd = status.google_data || {};
            if (gd.authenticated) {
                googleDataStatus.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800';
                googleDataStatus.textContent = 'Autenticado';
            } else {
                googleDataStatus.className = 'ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800';
                googleDataStatus.textContent = gd.error || 'Não autenticado';
            }
        }
    }

    // WordPress Configuration
    async saveWordPressConfig(event) {
        event.preventDefault();
        
        const wpConfig = {
            url: document.getElementById('wpUrl').value,
            username: document.getElementById('wpUsername').value,
            password: document.getElementById('wpPassword').value
        };

        if (!wpConfig.url || !wpConfig.username || !wpConfig.password) {
            showAlert('Todos os campos do WordPress são obrigatórios', 'error');
            return;
        }

        try {
            showLoading('Salvando configuração do WordPress...');
            
            const response = await fetch('/api/config/wordpress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(wpConfig)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao salvar configuração');
            }

            showAlert('Configuração do WordPress salva com sucesso!', 'success');
            document.getElementById('wpPassword').value = ''; // Limpar senha
            this.checkServiceStatus();
            
        } catch (error) {
            console.error('Erro ao salvar WordPress config:', error);
            showAlert('Erro ao salvar configuração: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    async testWordPressConnection() {
        try {
            showLoading('Testando conexão com WordPress...');
            
            const response = await fetch('/api/config/wordpress/test', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro na conexão');
            }

            const result = await response.json();
            showAlert('Conexão com WordPress testada com sucesso! Site: ' + result.site_name, 'success');
            
        } catch (error) {
            console.error('Erro ao testar WordPress:', error);
            showAlert('Erro na conexão: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    // Gmail Configuration
    async saveGmailConfig(event) {
        event.preventDefault();
        
        const gmailConfig = {
            client_id: document.getElementById('gmailClientId').value,
            client_secret: document.getElementById('gmailClientSecret').value
        };

        if (!gmailConfig.client_id || !gmailConfig.client_secret) {
            showAlert('Client ID e Client Secret são obrigatórios', 'error');
            return;
        }

        try {
            showLoading('Salvando configuração do Gmail...');
            
            const response = await fetch('/api/config/gmail', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(gmailConfig)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao salvar configuração');
            }

            showAlert('Configuração do Gmail salva com sucesso!', 'success');
            document.getElementById('gmailClientSecret').value = ''; // Limpar secret
            this.checkServiceStatus();
            
        } catch (error) {
            console.error('Erro ao salvar Gmail config:', error);
            showAlert('Erro ao salvar configuração: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    async authenticateGmail() {
        try {
            showLoading('Iniciando autenticação do Gmail...');
            
            const response = await fetch('/api/config/gmail/auth', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro na autenticação');
            }

            const result = await response.json();
            
            if (result.auth_url) {
                // Abrir URL de autenticação em nova janela
                window.open(result.auth_url, '_blank', 'width=600,height=600');
                showAlert('Janela de autenticação aberta. Complete o processo e retorne aqui.', 'info');
                
                // Verificar status periodicamente
                this.checkGmailAuthStatus();
            } else {
                showAlert('Gmail já está autenticado!', 'success');
            }
            
        } catch (error) {
            console.error('Erro na autenticação Gmail:', error);
            showAlert('Erro na autenticação: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    checkGmailAuthStatus() {
        const checkInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/config/gmail/status', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (response.ok) {
                    const status = await response.json();
                    if (status.authenticated) {
                        clearInterval(checkInterval);
                        showAlert('Gmail autenticado com sucesso!', 'success');
                        this.checkServiceStatus();
                    }
                }
            } catch (error) {
                // Ignorar erros durante verificação
            }
        }, 3000); // Verificar a cada 3 segundos

        // Parar verificação após 2 minutos
        setTimeout(() => clearInterval(checkInterval), 120000);
    }

    // Gemini Configuration
    async saveGeminiConfig(event) {
        event.preventDefault();
        
        const geminiConfig = {
            api_key: document.getElementById('geminiApiKey').value,
            model: document.getElementById('geminiModel').value
        };

        if (!geminiConfig.api_key) {
            showAlert('API Key do Gemini é obrigatória', 'error');
            return;
        }

        try {
            showLoading('Salvando configuração do Gemini...');
            
            const response = await fetch('/api/config/gemini', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(geminiConfig)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao salvar configuração');
            }

            showAlert('Configuração do Gemini salva com sucesso!', 'success');
            document.getElementById('geminiApiKey').value = ''; // Limpar API key
            this.checkServiceStatus();
            
        } catch (error) {
            console.error('Erro ao salvar Gemini config:', error);
            showAlert('Erro ao salvar configuração: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    async testGeminiConnection() {
        try {
            showLoading('Testando conexão com Gemini AI...');
            
            const response = await fetch('/api/config/gemini/test', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro na conexão');
            }

            const result = await response.json();
            showAlert('Gemini AI testado com sucesso! Resposta: ' + result.response, 'success');
            
        } catch (error) {
            console.error('Erro ao testar Gemini:', error);
            showAlert('Erro na conexão: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    // Google Data Configuration
    async saveGoogleDataConfig() {
        const googleDataConfig = {
            ga4_property_id: document.getElementById('ga4PropertyId').value,
            gsc_site_url: document.getElementById('gscSiteUrl').value
        };

        if (!googleDataConfig.ga4_property_id && !googleDataConfig.gsc_site_url) {
            showAlert('Pelo menos um campo do Google Data deve ser preenchido', 'error');
            return;
        }

        try {
            showLoading('Salvando configuração do Google Data...');
            
            const response = await fetch('/api/config/google-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(googleDataConfig)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao salvar configuração');
            }

            showAlert('Configuração do Google Data salva com sucesso!', 'success');
            this.checkServiceStatus();
            
        } catch (error) {
            console.error('Erro ao salvar Google Data config:', error);
            showAlert('Erro ao salvar configuração: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    async authenticateGoogleData() {
        try {
            showLoading('Iniciando autenticação do Google Data...');
            
            const response = await fetch('/api/config/google-data/auth', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro na autenticação');
            }

            const result = await response.json();
            
            if (result.auth_url) {
                // Abrir URL de autenticação em nova janela
                window.open(result.auth_url, '_blank', 'width=600,height=600');
                showAlert('Janela de autenticação aberta. Complete o processo e retorne aqui.', 'info');
                
                // Verificar status periodicamente
                this.checkGoogleDataAuthStatus();
            } else {
                showAlert('Google Data já está autenticado!', 'success');
            }
            
        } catch (error) {
            console.error('Erro na autenticação Google Data:', error);
            showAlert('Erro na autenticação: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    checkGoogleDataAuthStatus() {
        const checkInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/config/google-data/status', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (response.ok) {
                    const status = await response.json();
                    if (status.authenticated) {
                        clearInterval(checkInterval);
                        showAlert('Google Data autenticado com sucesso!', 'success');
                        this.checkServiceStatus();
                    }
                }
            } catch (error) {
                // Ignorar erros durante verificação
            }
        }, 3000); // Verificar a cada 3 segundos

        // Parar verificação após 2 minutos
        setTimeout(() => clearInterval(checkInterval), 120000);
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