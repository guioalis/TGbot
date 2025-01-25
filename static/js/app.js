// 通知管理
const notifications = {
    show(message, type = 'info') {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type} fade-enter`;
        notification.innerHTML = `
            <div class="p-4 rounded-lg shadow-lg ${type === 'error' ? 'bg-red-500' : 'bg-green-500'} text-white">
                ${message}
            </div>
        `;
        container.appendChild(notification);
        
        // 触发动画
        setTimeout(() => notification.classList.add('fade-enter-active'), 10);
        
        // 自动关闭
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },
    
    error(message) {
        this.show(message, 'error');
    },
    
    success(message) {
        this.show(message, 'success');
    }
};

// API 请求封装
const api = {
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            notifications.error(`请求失败: ${error.message}`);
            throw error;
        }
    },
    
    async getGroups() {
        return this.request('/api/groups');
    },
    
    async updateGroup(chatId, data) {
        return this.request(`/api/groups/${chatId}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async getBannedUsers() {
        return this.request('/api/banned_users');
    },
    
    async updateAIConfig(config) {
        return this.request('/api/ai_config', {
            method: 'POST',
            body: JSON.stringify(config)
        });
    }
}; 