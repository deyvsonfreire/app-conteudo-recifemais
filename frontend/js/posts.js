/**
 * Gerenciador de Posts
 * Responsável por carregar e exibir posts publicados no WordPress
 */
class PostsManager {
    constructor() {
        this.posts = [];
        this.filteredPosts = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadPosts();
    }

    bindEvents() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshPostsButton');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadPosts());
        }

        // Filters
        const statusFilter = document.getElementById('postStatusFilter');
        const categoryFilter = document.getElementById('postCategoryFilter');
        const dateFilter = document.getElementById('postDateFilter');

        if (statusFilter) statusFilter.addEventListener('change', () => this.applyFilters());
        if (categoryFilter) categoryFilter.addEventListener('change', () => this.applyFilters());
        if (dateFilter) dateFilter.addEventListener('change', () => this.applyFilters());
    }

    async loadPosts() {
        try {
            showLoading('Carregando posts...');
            
            const response = await fetch('/api/posts', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao carregar posts');
            }

            const data = await response.json();
            this.posts = data.posts || [];
            this.updateStats(data.stats || {});
            this.applyFilters();
            
        } catch (error) {
            console.error('Erro ao carregar posts:', error);
            showAlert('Erro ao carregar posts: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    updateStats(stats) {
        // Atualizar estatísticas
        document.getElementById('totalPosts').textContent = stats.total || 0;
        document.getElementById('postsThisWeek').textContent = stats.thisWeek || 0;
        document.getElementById('totalViews').textContent = this.formatNumber(stats.totalViews || 0);
        document.getElementById('avgEngagement').textContent = stats.avgEngagement || '0%';
    }

    applyFilters() {
        const statusFilter = document.getElementById('postStatusFilter')?.value || '';
        const categoryFilter = document.getElementById('postCategoryFilter')?.value || '';
        const dateFilter = document.getElementById('postDateFilter')?.value || '';

        this.filteredPosts = this.posts.filter(post => {
            let matches = true;

            if (statusFilter && post.status !== statusFilter) {
                matches = false;
            }

            if (categoryFilter && !post.categories.includes(categoryFilter)) {
                matches = false;
            }

            if (dateFilter) {
                const postDate = new Date(post.date);
                const now = new Date();
                
                switch (dateFilter) {
                    case 'today':
                        matches = matches && this.isSameDay(postDate, now);
                        break;
                    case 'week':
                        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                        matches = matches && postDate >= weekAgo;
                        break;
                    case 'month':
                        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                        matches = matches && postDate >= monthAgo;
                        break;
                }
            }

            return matches;
        });

        this.renderPosts();
    }

    renderPosts() {
        const container = document.getElementById('postsTable');
        if (!container) return;

        if (this.filteredPosts.length === 0) {
            container.innerHTML = `
                <div class="p-8 text-center">
                    <i data-lucide="file-text" class="h-12 w-12 text-gray-400 mx-auto mb-4"></i>
                    <p class="text-gray-500">Nenhum post encontrado</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const paginatedPosts = this.filteredPosts.slice(startIndex, endIndex);

        const tableHTML = `
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Post
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Data
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Visualizações
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Ações
                        </th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    ${paginatedPosts.map(post => this.renderPostRow(post)).join('')}
                </tbody>
            </table>
            ${this.renderPagination()}
        `;

        container.innerHTML = tableHTML;
        lucide.createIcons();
        this.bindPostActions();
    }

    renderPostRow(post) {
        const statusBadge = this.getStatusBadge(post.status);
        const excerpt = post.excerpt ? post.excerpt.substring(0, 100) + '...' : '';
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4">
                    <div class="flex items-start">
                        <div class="flex-1">
                            <div class="text-sm font-medium text-gray-900">
                                ${post.title}
                            </div>
                            <div class="text-sm text-gray-500 mt-1">
                                ${excerpt}
                            </div>
                            <div class="text-xs text-gray-400 mt-1">
                                ID: ${post.id} | Email: ${post.email_id || 'N/A'}
                            </div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    ${statusBadge}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${this.formatDate(post.date)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${this.formatNumber(post.views || 0)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-2">
                        <button onclick="postsManager.viewPost(${post.id})" 
                                class="text-blue-600 hover:text-blue-900">
                            <i data-lucide="eye" class="h-4 w-4"></i>
                        </button>
                        <button onclick="postsManager.editPost(${post.id})" 
                                class="text-indigo-600 hover:text-indigo-900">
                            <i data-lucide="edit" class="h-4 w-4"></i>
                        </button>
                        <a href="${post.url}" target="_blank" 
                           class="text-green-600 hover:text-green-900">
                            <i data-lucide="external-link" class="h-4 w-4"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `;
    }

    getStatusBadge(status) {
        const badges = {
            'publish': 'bg-green-100 text-green-800',
            'draft': 'bg-yellow-100 text-yellow-800',
            'private': 'bg-gray-100 text-gray-800',
            'pending': 'bg-orange-100 text-orange-800'
        };

        const labels = {
            'publish': 'Publicado',
            'draft': 'Rascunho',
            'private': 'Privado',
            'pending': 'Pendente'
        };

        const badgeClass = badges[status] || 'bg-gray-100 text-gray-800';
        const label = labels[status] || status;

        return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badgeClass}">${label}</span>`;
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredPosts.length / this.itemsPerPage);
        
        if (totalPages <= 1) return '';

        let paginationHTML = '<div class="px-6 py-3 border-t border-gray-200 flex items-center justify-between">';
        
        // Info
        paginationHTML += `
            <div class="text-sm text-gray-700">
                Mostrando ${(this.currentPage - 1) * this.itemsPerPage + 1} a 
                ${Math.min(this.currentPage * this.itemsPerPage, this.filteredPosts.length)} 
                de ${this.filteredPosts.length} posts
            </div>
        `;

        // Navigation
        paginationHTML += '<div class="flex space-x-2">';
        
        // Previous
        if (this.currentPage > 1) {
            paginationHTML += `
                <button onclick="postsManager.goToPage(${this.currentPage - 1})" 
                        class="px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                    Anterior
                </button>
            `;
        }

        // Page numbers
        for (let i = Math.max(1, this.currentPage - 2); i <= Math.min(totalPages, this.currentPage + 2); i++) {
            const isActive = i === this.currentPage;
            paginationHTML += `
                <button onclick="postsManager.goToPage(${i})" 
                        class="px-3 py-1 border rounded-md text-sm ${isActive ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 hover:bg-gray-50'}">
                    ${i}
                </button>
            `;
        }

        // Next
        if (this.currentPage < totalPages) {
            paginationHTML += `
                <button onclick="postsManager.goToPage(${this.currentPage + 1})" 
                        class="px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                    Próximo
                </button>
            `;
        }

        paginationHTML += '</div></div>';
        return paginationHTML;
    }

    goToPage(page) {
        this.currentPage = page;
        this.renderPosts();
    }

    bindPostActions() {
        // Actions are bound via onclick in the HTML
    }

    async viewPost(postId) {
        try {
            const response = await fetch(`/api/posts/${postId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao carregar detalhes do post');
            }

            const post = await response.json();
            this.showPostModal(post);
            
        } catch (error) {
            console.error('Erro ao carregar post:', error);
            showAlert('Erro ao carregar post: ' + error.message, 'error');
        }
    }

    showPostModal(post) {
        const modal = document.getElementById('emailDetailsModal');
        const content = document.getElementById('emailDetailsContent');
        
        if (!modal || !content) return;

        content.innerHTML = `
            <div class="space-y-6">
                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Informações do Post</h3>
                    <div class="bg-gray-50 rounded-lg p-4 space-y-2">
                        <div class="flex justify-between">
                            <span class="font-medium">ID:</span>
                            <span>${post.id}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="font-medium">Status:</span>
                            <span>${this.getStatusBadge(post.status)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="font-medium">Data:</span>
                            <span>${this.formatDate(post.date)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="font-medium">Visualizações:</span>
                            <span>${this.formatNumber(post.views || 0)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="font-medium">URL:</span>
                            <a href="${post.url}" target="_blank" class="text-blue-600 hover:underline">
                                Ver no site
                            </a>
                        </div>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Título</h3>
                    <div class="bg-gray-50 rounded-lg p-4">
                        <p class="text-gray-900">${post.title}</p>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Resumo</h3>
                    <div class="bg-gray-50 rounded-lg p-4">
                        <p class="text-gray-700">${post.excerpt || 'Sem resumo disponível'}</p>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Conteúdo</h3>
                    <div class="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <div class="prose max-w-none">
                            ${post.content}
                        </div>
                    </div>
                </div>

                ${post.email_id ? `
                <div>
                    <h3 class="text-lg font-medium text-gray-900 mb-2">Email Original</h3>
                    <div class="bg-blue-50 rounded-lg p-4">
                        <p class="text-sm text-blue-800">
                            Este post foi gerado a partir do email ID: ${post.email_id}
                        </p>
                        <button onclick="emailWorkflowManager.viewEmailDetails(${post.email_id})" 
                                class="mt-2 text-blue-600 hover:text-blue-800 text-sm underline">
                            Ver email original
                        </button>
                    </div>
                </div>
                ` : ''}
            </div>
        `;

        modal.classList.remove('hidden');
        lucide.createIcons();
    }

    editPost(postId) {
        const post = this.posts.find(p => p.id === postId);
        if (post && post.url) {
            // Abrir o editor do WordPress
            const editUrl = post.url.replace(/\/$/, '') + '/wp-admin/post.php?post=' + postId + '&action=edit';
            window.open(editUrl, '_blank');
        } else {
            showAlert('URL de edição não disponível', 'warning');
        }
    }

    // Utility methods
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    isSameDay(date1, date2) {
        return date1.getDate() === date2.getDate() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getFullYear() === date2.getFullYear();
    }
}

// Instância global
let postsManager;

// Inicializar quando a seção de posts for carregada
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que todos os elementos estejam carregados
    setTimeout(() => {
        if (document.getElementById('postsSection')) {
            postsManager = new PostsManager();
        }
    }, 100);
}); 