/**
 * Email Workflow Module - Gerencia o fluxo de aprovação de emails
 * Integra com o backend para controlar as etapas do workflow
 */

class EmailWorkflowManager {
    constructor() {
        this.currentEmails = [];
        this.currentFilters = {};
        this.selectedEmail = null;
        
        console.log('📧 Email Workflow Manager inicializado');
    }
    
    // ==========================================
    // INITIALIZATION
    // ==========================================
    
    init() {
        this.setupEventListeners();
        this.loadWorkflowStats();
        this.loadEmailsList();
    }
    
    setupEventListeners() {
        // Filtros
        document.getElementById('emailStatusFilter')?.addEventListener('change', () => {
            this.applyFilters();
        });
        
        document.getElementById('emailPriorityFilter')?.addEventListener('change', () => {
            this.applyFilters();
        });
        
        document.getElementById('emailTypeFilter')?.addEventListener('change', () => {
            this.applyFilters();
        });
        
        // Botão de atualizar
        document.getElementById('refreshEmailsButton')?.addEventListener('click', () => {
            this.refreshData();
        });
    }
    
    // ==========================================
    // DATA LOADING
    // ==========================================
    
    async loadWorkflowStats() {
        try {
            const response = await authManager.apiCall('/workflow/dashboard');
            if (response.ok) {
                const data = await response.json();
                this.updateStatsUI(data.stats);
            }
        } catch (error) {
            console.error('Erro ao carregar estatísticas do workflow:', error);
        }
    }
    
    async loadEmailsList(filters = {}) {
        try {
            const params = new URLSearchParams({
                limit: '50',
                offset: '0',
                ...filters
            });
            
            const response = await authManager.apiCall(`/workflow/emails?${params}`);
            if (response.ok) {
                const data = await response.json();
                this.currentEmails = data.emails;
                this.renderEmailsTable(data.emails);
            }
        } catch (error) {
            console.error('Erro ao carregar lista de emails:', error);
            this.showError('Erro ao carregar emails');
        }
    }
    
    async loadEmailDetails(emailId) {
        try {
            const response = await authManager.apiCall(`/workflow/emails/${emailId}`);
            if (response.ok) {
                const data = await response.json();
                return data.email;
            }
        } catch (error) {
            console.error('Erro ao carregar detalhes do email:', error);
            return null;
        }
    }
    
    // ==========================================
    // UI UPDATES
    // ==========================================
    
    updateStatsUI(stats) {
        document.getElementById('pendingReview').textContent = stats.pending_review || 0;
        document.getElementById('readyToPublish').textContent = stats.ready_to_publish || 0;
        document.getElementById('publishedToday').textContent = stats.published_today || 0;
        document.getElementById('totalEmails').textContent = stats.total_emails || 0;
    }
    
    renderEmailsTable(emails) {
        const tableContainer = document.getElementById('emailsTable');
        if (!tableContainer) return;
        
        if (emails.length === 0) {
            tableContainer.innerHTML = `
                <div class="p-8 text-center text-gray-500">
                    <i data-lucide="inbox" class="h-12 w-12 mx-auto mb-4 text-gray-300"></i>
                    <p>Nenhum email encontrado</p>
                </div>
            `;
            return;
        }
        
        const table = `
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Email
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Prioridade
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Recebido
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Ações
                        </th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    ${emails.map(email => this.renderEmailRow(email)).join('')}
                </tbody>
            </table>
        `;
        
        tableContainer.innerHTML = table;
        
        // Reprocessar ícones do Lucide
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Adicionar event listeners para ações
        this.setupEmailActions();
    }
    
    renderEmailRow(email) {
        const priorityClass = this.getPriorityClass(email.priority);
        const statusBadge = this.getStatusBadge(email.workflow_stage);
        const receivedDate = new Date(email.received_at).toLocaleDateString('pt-BR');
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <div class="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
                                <i data-lucide="mail" class="h-5 w-5 text-gray-600"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900 truncate max-w-xs">
                                ${email.subject}
                            </div>
                            <div class="text-sm text-gray-500">
                                De: ${email.sender}
                            </div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    ${statusBadge}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityClass}">
                        ${this.getPriorityText(email.priority)}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${receivedDate}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-2">
                        <button 
                            onclick="emailWorkflow.viewEmail('${email.id}')" 
                            class="text-blue-600 hover:text-blue-900"
                            title="Ver detalhes"
                        >
                            <i data-lucide="eye" class="h-4 w-4"></i>
                        </button>
                        ${this.getEmailActionButtons(email)}
                    </div>
                </td>
            </tr>
        `;
    }
    
    getStatusBadge(stage) {
        const badges = {
            'received': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Recebido</span>',
            'analyzed': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Analisado</span>',
            'approved_content': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Aprovado</span>',
            'ready_publish': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">Pronto</span>',
            'published': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Publicado</span>',
            'rejected': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Rejeitado</span>',
            'archived': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Arquivado</span>'
        };
        
        return badges[stage] || badges['received'];
    }
    
    getPriorityClass(priority) {
        const classes = {
            1: 'bg-red-100 text-red-800',
            2: 'bg-yellow-100 text-yellow-800',
            3: 'bg-green-100 text-green-800'
        };
        return classes[priority] || classes[3];
    }
    
    getPriorityText(priority) {
        const texts = {
            1: 'Alta',
            2: 'Média',
            3: 'Baixa'
        };
        return texts[priority] || 'Baixa';
    }
    
    getEmailActionButtons(email) {
        const stage = email.workflow_stage;
        let buttons = '';
        
        switch (stage) {
            case 'received':
                buttons = `
                    <button 
                        onclick="emailWorkflow.analyzeEmail('${email.id}')" 
                        class="text-green-600 hover:text-green-900"
                        title="Analisar com IA"
                    >
                        <i data-lucide="brain" class="h-4 w-4"></i>
                    </button>
                `;
                break;
                
            case 'analyzed':
                buttons = `
                    <button 
                        onclick="emailWorkflow.approveContent('${email.id}')" 
                        class="text-green-600 hover:text-green-900"
                        title="Aprovar conteúdo"
                    >
                        <i data-lucide="check" class="h-4 w-4"></i>
                    </button>
                `;
                break;
                
            case 'approved_content':
                buttons = `
                    <button 
                        onclick="emailWorkflow.preparePublish('${email.id}')" 
                        class="text-blue-600 hover:text-blue-900"
                        title="Preparar publicação"
                    >
                        <i data-lucide="edit" class="h-4 w-4"></i>
                    </button>
                `;
                break;
                
            case 'ready_publish':
                buttons = `
                    <button 
                        onclick="emailWorkflow.publishEmail('${email.id}')" 
                        class="text-purple-600 hover:text-purple-900"
                        title="Publicar no WordPress"
                    >
                        <i data-lucide="send" class="h-4 w-4"></i>
                    </button>
                `;
                break;
        }
        
        // Botão de rejeitar (disponível em qualquer etapa exceto publicado)
        if (!['published', 'rejected', 'archived'].includes(stage)) {
            buttons += `
                <button 
                    onclick="emailWorkflow.rejectEmail('${email.id}')" 
                    class="text-red-600 hover:text-red-900"
                    title="Rejeitar email"
                >
                    <i data-lucide="x" class="h-4 w-4"></i>
                </button>
            `;
        }
        
        return buttons;
    }
    
    setupEmailActions() {
        // Event listeners já são configurados via onclick nos botões
        // Mas podemos adicionar outros eventos aqui se necessário
    }
    
    // ==========================================
    // WORKFLOW ACTIONS
    // ==========================================
    
    async analyzeEmail(emailId) {
        try {
            this.showLoading(true);
            
            const response = await authManager.apiCall(`/workflow/emails/${emailId}/analyze`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showSuccess('Email analisado com sucesso!');
                this.refreshData();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Erro ao analisar email');
            }
        } catch (error) {
            console.error('Erro ao analisar email:', error);
            this.showError('Erro ao analisar email');
        } finally {
            this.showLoading(false);
        }
    }
    
    async approveContent(emailId) {
        // Aqui poderia abrir um modal para feedback detalhado
        // Por simplicidade, vamos aprovar diretamente
        try {
            this.showLoading(true);
            
            const response = await authManager.apiCall(`/workflow/emails/${emailId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    rating: 5,
                    notes: 'Conteúdo aprovado via interface'
                })
            });
            
            if (response.ok) {
                this.showSuccess('Conteúdo aprovado com sucesso!');
                this.refreshData();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Erro ao aprovar conteúdo');
            }
        } catch (error) {
            console.error('Erro ao aprovar conteúdo:', error);
            this.showError('Erro ao aprovar conteúdo');
        } finally {
            this.showLoading(false);
        }
    }
    
    async preparePublish(emailId) {
        // Aqui deveria abrir um modal para editar o conteúdo final
        // Por simplicidade, vamos usar dados básicos
        try {
            const email = await this.loadEmailDetails(emailId);
            if (!email) return;
            
            const aiAnalysis = email.ai_analysis || {};
            const generatedContent = aiAnalysis.generated_content || {};
            
            this.showLoading(true);
            
            const response = await authManager.apiCall(`/workflow/emails/${emailId}/prepare`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    titulo: generatedContent.titulo || email.subject,
                    conteudo: generatedContent.conteudo || 'Conteúdo a ser definido',
                    categoria: generatedContent.categoria || 'geral',
                    tags: generatedContent.tags || [],
                    meta_descricao: generatedContent.meta_descricao || ''
                })
            });
            
            if (response.ok) {
                this.showSuccess('Email preparado para publicação!');
                this.refreshData();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Erro ao preparar publicação');
            }
        } catch (error) {
            console.error('Erro ao preparar publicação:', error);
            this.showError('Erro ao preparar publicação');
        } finally {
            this.showLoading(false);
        }
    }
    
    async publishEmail(emailId) {
        if (!confirm('Tem certeza que deseja publicar este email no WordPress?')) {
            return;
        }
        
        try {
            this.showLoading(true);
            
            const response = await authManager.apiCall(`/workflow/emails/${emailId}/publish`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showSuccess(`Email publicado com sucesso! Post ID: ${result.wordpress_post_id}`);
                this.refreshData();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Erro ao publicar email');
            }
        } catch (error) {
            console.error('Erro ao publicar email:', error);
            this.showError('Erro ao publicar email');
        } finally {
            this.showLoading(false);
        }
    }
    
    async rejectEmail(emailId) {
        const reason = prompt('Motivo da rejeição:');
        if (!reason) return;
        
        try {
            this.showLoading(true);
            
            const response = await authManager.apiCall(`/workflow/emails/${emailId}/reject`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    reason: reason
                })
            });
            
            if (response.ok) {
                this.showSuccess('Email rejeitado');
                this.refreshData();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Erro ao rejeitar email');
            }
        } catch (error) {
            console.error('Erro ao rejeitar email:', error);
            this.showError('Erro ao rejeitar email');
        } finally {
            this.showLoading(false);
        }
    }
    
    async viewEmail(emailId) {
        try {
            const email = await this.loadEmailDetails(emailId);
            if (email) {
                this.showEmailDetails(email);
            }
        } catch (error) {
            console.error('Erro ao visualizar email:', error);
            this.showError('Erro ao carregar detalhes do email');
        }
    }
    
    // ==========================================
    // FILTERS & REFRESH
    // ==========================================
    
    applyFilters() {
        const statusFilter = document.getElementById('emailStatusFilter').value;
        const priorityFilter = document.getElementById('emailPriorityFilter').value;
        const typeFilter = document.getElementById('emailTypeFilter').value;
        
        const filters = {};
        
        if (statusFilter) filters.stage = statusFilter;
        if (priorityFilter) filters.priority = priorityFilter;
        if (typeFilter) filters.is_auto_process = typeFilter;
        
        this.currentFilters = filters;
        this.loadEmailsList(filters);
    }
    
    async refreshData() {
        await Promise.all([
            this.loadWorkflowStats(),
            this.loadEmailsList(this.currentFilters)
        ]);
    }
    
    // ==========================================
    // MODALS & UI HELPERS
    // ==========================================
    
    showEmailDetails(email) {
        const modal = document.getElementById('emailDetailsModal');
        const content = document.getElementById('emailDetailsContent');
        
        if (!modal || !content) return;

        // Formatar dados de análise IA se existir
        let aiAnalysisHtml = '';
        if (email.ai_analysis) {
            try {
                const analysis = typeof email.ai_analysis === 'string' ? 
                    JSON.parse(email.ai_analysis) : email.ai_analysis;
                
                aiAnalysisHtml = `
                    <div>
                        <h3 class="text-lg font-medium text-gray-900 mb-2">Análise da IA</h3>
                        <div class="bg-blue-50 rounded-lg p-4 space-y-3">
                            ${analysis.title ? `<div><span class="font-medium">Título Sugerido:</span> ${analysis.title}</div>` : ''}
                            ${analysis.summary ? `<div><span class="font-medium">Resumo:</span> ${analysis.summary}</div>` : ''}
                            ${analysis.category ? `<div><span class="font-medium">Categoria:</span> ${analysis.category}</div>` : ''}
                            ${analysis.tags ? `<div><span class="font-medium">Tags:</span> ${analysis.tags}</div>` : ''}
                            ${analysis.content ? `
                                <div>
                                    <span class="font-medium">Conteúdo Processado:</span>
                                    <div class="mt-2 bg-white rounded p-3 max-h-48 overflow-y-auto">
                                        ${analysis.content}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            } catch (e) {
                aiAnalysisHtml = `
                    <div>
                        <h3 class="text-lg font-medium text-gray-900 mb-2">Análise da IA</h3>
                        <div class="bg-blue-50 rounded-lg p-4">
                            <pre class="text-sm">${email.ai_analysis}</pre>
                        </div>
                    </div>
                `;
            }
        }

        content.innerHTML = `
            <div class="space-y-6">
                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Informações do Email</h3>
                    <div class="bg-gray-50 rounded-lg p-4 space-y-2">
                        <div class="flex justify-between">
                            <span class="font-medium">ID:</span>
                            <span>${email.id}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="font-medium">Status:</span>
                            <span>${this.getStatusBadge(email.workflow_stage)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="font-medium">Prioridade:</span>
                            <span>${this.getPriorityBadge(email.priority)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="font-medium">Data de Recebimento:</span>
                            <span>${this.formatDate(email.received_at)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="font-medium">Tipo:</span>
                            <span>${email.is_auto_process ? 'Processamento Automático' : 'Email Antigo'}</span>
                        </div>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Remetente</h3>
                    <div class="bg-gray-50 rounded-lg p-4">
                        <p class="text-gray-900">${email.sender_name || 'Nome não disponível'}</p>
                        <p class="text-gray-600">${email.sender_email}</p>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Assunto</h3>
                    <div class="bg-gray-50 rounded-lg p-4">
                        <p class="text-gray-900">${email.subject}</p>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Conteúdo Original</h3>
                    <div class="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <div class="prose max-w-none">
                            ${email.body || 'Conteúdo não disponível'}
                        </div>
                    </div>
                </div>

                ${aiAnalysisHtml}

                <div class="flex justify-center space-x-3 pt-4 border-t">
                    ${this.getModalActionButtons(email)}
                </div>
            </div>
        `;

        modal.classList.remove('hidden');
        lucide.createIcons();

        // Bind modal close events
        const closeBtn = document.getElementById('closeEmailModal');
        const closeModalBtn = document.getElementById('closeEmailModalBtn');
        
        const closeModal = () => {
            modal.classList.add('hidden');
        };

        if (closeBtn) closeBtn.onclick = closeModal;
        if (closeModalBtn) closeModalBtn.onclick = closeModal;
        
        // Close on outside click
        modal.onclick = (e) => {
            if (e.target === modal) closeModal();
        };
    }

    getModalActionButtons(email) {
        const stage = email.workflow_stage;
        let buttons = [];

        switch (stage) {
            case 'received':
                buttons.push(`
                    <button onclick="emailWorkflow.analyzeEmail(${email.id}); document.getElementById('emailDetailsModal').classList.add('hidden');" 
                            class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                        <i data-lucide="brain" class="h-4 w-4 mr-1 inline"></i>
                        Analisar com IA
                    </button>
                `);
                break;
            case 'analyzed':
                buttons.push(`
                    <button onclick="emailWorkflow.approveContent(${email.id}); document.getElementById('emailDetailsModal').classList.add('hidden');" 
                            class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
                        <i data-lucide="check" class="h-4 w-4 mr-1 inline"></i>
                        Aprovar Conteúdo
                    </button>
                `);
                break;
            case 'approved_content':
                buttons.push(`
                    <button onclick="emailWorkflow.preparePublish(${email.id}); document.getElementById('emailDetailsModal').classList.add('hidden');" 
                            class="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700">
                        <i data-lucide="edit" class="h-4 w-4 mr-1 inline"></i>
                        Preparar Publicação
                    </button>
                `);
                break;
            case 'ready_publish':
                buttons.push(`
                    <button onclick="emailWorkflow.publishEmail(${email.id}); document.getElementById('emailDetailsModal').classList.add('hidden');" 
                            class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">
                        <i data-lucide="send" class="h-4 w-4 mr-1 inline"></i>
                        Publicar no WordPress
                    </button>
                `);
                break;
        }

        // Botão de rejeição (exceto para emails publicados)
        if (stage !== 'published') {
            buttons.push(`
                <button onclick="emailWorkflow.rejectEmail(${email.id}); document.getElementById('emailDetailsModal').classList.add('hidden');" 
                        class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700">
                    <i data-lucide="x" class="h-4 w-4 mr-1 inline"></i>
                    Rejeitar
                </button>
            `);
        }

        return buttons.join('');
    }

    getPriorityBadge(priority) {
        const badges = {
            1: 'bg-red-100 text-red-800',
            2: 'bg-yellow-100 text-yellow-800',
            3: 'bg-green-100 text-green-800'
        };

        const labels = {
            1: 'Alta',
            2: 'Média', 
            3: 'Baixa'
        };

        const badgeClass = badges[priority] || 'bg-gray-100 text-gray-800';
        const label = labels[priority] || 'N/A';

        return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badgeClass}">${label}</span>`;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    showSuccess(message) {
        // Implementar notificação de sucesso
        alert(`✅ ${message}`);
    }
    
    showError(message) {
        // Implementar notificação de erro
        alert(`❌ ${message}`);
    }
    
    showLoading(show = true) {
        // Implementar indicador de loading
        const button = document.getElementById('refreshEmailsButton');
        if (button) {
            button.disabled = show;
            if (show) {
                button.innerHTML = '<i data-lucide="loader-2" class="h-4 w-4 mr-1 inline animate-spin"></i> Carregando...';
            } else {
                button.innerHTML = '<i data-lucide="refresh-cw" class="h-4 w-4 mr-1 inline"></i> Atualizar';
            }
        }
    }
}

// Instância global
const emailWorkflow = new EmailWorkflowManager(); 