/**
 * SafetyAgent AI - Frontend Application
 * Handles chat interface, document upload, and API communication
 */

class SafetyAgentApp {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        this.websocket = null;
        
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeWebSocket();
        this.loadExistingDocuments();
        
        console.log('SafetyAgent AI initialized');
    }

    initializeElements() {
        // Chat elements
        this.chatWidget = document.getElementById('chat-widget');
        this.chatToggle = document.getElementById('chat-toggle');
        this.chatWindow = document.getElementById('chat-window');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.chatSend = document.getElementById('chat-send');
        this.chatBadge = document.getElementById('chat-badge');
        this.chatMinimize = document.getElementById('chat-minimize');
        this.chatClose = document.getElementById('chat-close');

        // Modal elements
        this.uploadModal = document.getElementById('upload-modal');
        this.statsModal = document.getElementById('stats-modal');
        this.uploadClose = document.getElementById('upload-close');
        this.statsClose = document.getElementById('stats-close');

        // Upload elements
        this.uploadBtn = document.getElementById('upload-btn');
        this.statsBtn = document.getElementById('stats-btn');
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.browseFiles = document.getElementById('browse-files');
        this.uploadProgress = document.getElementById('upload-progress');
        this.fileList = document.getElementById('file-list');
        this.categorySelect = document.getElementById('category-select');

        // Other elements
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.statsContent = document.getElementById('stats-content');
    }

    initializeEventListeners() {
        // Chat toggle
        this.chatToggle.addEventListener('click', () => this.toggleChat());
        this.chatMinimize.addEventListener('click', () => this.minimizeChat());
        this.chatClose.addEventListener('click', () => this.closeChat());

        // Chat input
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.chatSend.addEventListener('click', () => this.sendMessage());

        // Suggestion buttons
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const query = e.target.dataset.query;
                this.chatInput.value = query;
                this.sendMessage();
            });
        });

        // Modal controls
        this.uploadBtn.addEventListener('click', () => this.openModal('upload'));
        this.statsBtn.addEventListener('click', () => this.openModal('stats'));
        this.uploadClose.addEventListener('click', () => this.closeModal('upload'));
        this.statsClose.addEventListener('click', () => this.closeModal('stats'));

        // Upload functionality
        this.browseFiles.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files));
        
        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });
        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });
        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFileUpload(e.dataTransfer.files);
        });

        // Close modals on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id.replace('-modal', ''));
            }
        });
    }

    initializeWebSocket() {
        try {
            const wsUrl = this.apiBaseUrl.replace('http', 'ws') + '/ws/chat';
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                this.isConnected = true;
                console.log('WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                const response = JSON.parse(event.data);
                this.displayMessage(response.answer, 'ai', response.sources);
            };
            
            this.websocket.onclose = () => {
                this.isConnected = false;
                console.log('WebSocket disconnected');
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.initializeWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Chat functionality
    toggleChat() {
        this.chatWindow.classList.toggle('open');
        if (this.chatWindow.classList.contains('open')) {
            this.chatInput.focus();
            this.hideBadge();
        }
    }

    minimizeChat() {
        this.chatWindow.classList.remove('open');
    }

    closeChat() {
        this.chatWindow.classList.remove('open');
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Display user message
        this.displayMessage(message, 'user');
        this.chatInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            if (this.isConnected && this.websocket) {
                // Use WebSocket for real-time response
                this.websocket.send(JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                }));
            } else {
                // Fallback to REST API
                const response = await this.sendChatRequest(message);
                this.hideTypingIndicator();
                this.displayMessage(response.answer, 'ai', response.sources);
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.displayMessage('Sorry, I encountered an error. Please try again.', 'ai');
            console.error('Chat error:', error);
        }
    }

    async sendChatRequest(message) {
        const response = await fetch(`${this.apiBaseUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    displayMessage(content, sender, sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const avatar = sender === 'user' ? '👤' : '🛡️';
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="message-sources">
                    <details>
                        <summary>Sources (${sources.length})</summary>
                        <div class="sources-list">
                            ${sources.map(source => `
                                <div class="source-item">
                                    <strong>${source.source_file}</strong>
                                    <p>${source.content}</p>
                                </div>
                            `).join('')}
                        </div>
                    </details>
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(content)}${sourcesHtml}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;

        // Show badge for new AI messages
        if (sender === 'ai' && !this.chatWindow.classList.contains('open')) {
            this.showBadge();
        }
    }

    formatMessage(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">🛡️</div>
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        `;
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    showBadge() {
        this.chatBadge.style.display = 'flex';
    }

    hideBadge() {
        this.chatBadge.style.display = 'none';
    }

    // Modal functionality
    openModal(type) {
        const modal = document.getElementById(`${type}-modal`);
        if (modal) {
            modal.classList.add('open');
            if (type === 'stats') {
                this.loadStats();
            }
        }
    }

    closeModal(type) {
        const modal = document.getElementById(`${type}-modal`);
        if (modal) {
            modal.classList.remove('open');
        }
    }

    // File upload functionality
    async handleFileUpload(files) {
        if (!files || files.length === 0) return;

        for (let file of files) {
            if (!this.isValidFileType(file)) {
                this.showNotification(`File "${file.name}" is not supported. Please upload .docx, .doc, .pdf, .txt, or .md files.`, 'error');
                continue;
            }

            await this.uploadFile(file);
        }
    }

    isValidFileType(file) {
        const validTypes = ['.docx', '.doc', '.pdf', '.txt', '.md'];
        const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        return validTypes.includes(fileExt);
    }

    async uploadFile(file) {
        this.showLoading();
        this.showUploadProgress();

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('category', this.categorySelect.value);

            const response = await fetch(`${this.apiBaseUrl}/api/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status}`);
            }

            const result = await response.json();
            this.hideUploadProgress();
            this.hideLoading();
            this.showNotification(`Document "${file.name}" uploaded successfully!`, 'success');
            this.loadExistingDocuments();
            
        } catch (error) {
            this.hideUploadProgress();
            this.hideLoading();
            this.showNotification(`Failed to upload "${file.name}": ${error.message}`, 'error');
            console.error('Upload error:', error);
        }
    }

    showUploadProgress() {
        this.uploadProgress.style.display = 'block';
    }

    hideUploadProgress() {
        this.uploadProgress.style.display = 'none';
    }

    async loadExistingDocuments() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/documents`);
            if (!response.ok) return;

            const data = await response.json();
            this.displayDocuments(data.documents);
        } catch (error) {
            console.error('Error loading documents:', error);
        }
    }

    displayDocuments(documents) {
        this.fileList.innerHTML = '';

        if (documents.length === 0) {
            this.fileList.innerHTML = '<p style="text-align: center; color: #7f8c8d;">No documents uploaded yet.</p>';
            return;
        }

        documents.forEach(doc => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <div class="file-icon">📄</div>
                    <div class="file-details">
                        <h4>${doc.filename}</h4>
                        <p>${this.formatFileSize(doc.file_size)} • ${doc.chunks_count} chunks • ${new Date(doc.loaded_at).toLocaleDateString()}</p>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn-danger" onclick="app.deleteDocument('${doc.id}')">Delete</button>
                </div>
            `;
            this.fileList.appendChild(fileItem);
        });
    }

    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/documents/${docId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`Delete failed: ${response.status}`);
            }

            this.showNotification('Document deleted successfully!', 'success');
            this.loadExistingDocuments();
        } catch (error) {
            this.showNotification(`Failed to delete document: ${error.message}`, 'error');
            console.error('Delete error:', error);
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/stats`);
            if (!response.ok) return;

            const stats = await response.json();
            this.displayStats(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
            this.statsContent.innerHTML = '<div class="loading">Error loading statistics</div>';
        }
    }

    displayStats(stats) {
        this.statsContent.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">${stats.total_documents}</div>
                    <div class="stat-label">Documents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats.total_chunks}</div>
                    <div class="stat-label">Chunks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${Object.keys(stats.file_types).length}</div>
                    <div class="stat-label">File Types</div>
                </div>
            </div>
            <div class="stats-details">
                <h3>File Types</h3>
                <ul>
                    ${Object.entries(stats.file_types).map(([type, count]) => 
                        `<li>${type}: ${count} files</li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }

    // Utility functions
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 4000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SafetyAgentApp();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        background: #95a5a6;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    .message-sources {
        margin-top: 0.5rem;
        font-size: 0.8rem;
    }
    
    .message-sources details {
        cursor: pointer;
    }
    
    .message-sources summary {
        color: #3498db;
        font-weight: 600;
    }
    
    .sources-list {
        margin-top: 0.5rem;
        padding-left: 1rem;
    }
    
    .source-item {
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        background: rgba(52, 152, 219, 0.1);
        border-radius: 4px;
    }
    
    .source-item strong {
        color: #2c3e50;
    }
    
    .source-item p {
        margin: 0.25rem 0 0 0;
        color: #7f8c8d;
        font-size: 0.75rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stats-details {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
    }
    
    .stats-details h3 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .stats-details ul {
        list-style: none;
        padding: 0;
    }
    
    .stats-details li {
        padding: 0.25rem 0;
        color: #7f8c8d;
    }
`;
document.head.appendChild(style);
