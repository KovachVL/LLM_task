const API_CONFIG = {
    baseUrl: window.location.origin, 
    chatEndpoint: '/api/chat',
    healthEndpoint: '/api/health'
};


class PSUTIShop {
    constructor() {
        this.cart = [];
        this.sessionId = this.generateSessionId();
        this.initializeEventListeners();
        this.updateCartCount();
        this.checkServerHealth();
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }

    initializeEventListeners() {
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', (e) => {
                const productId = e.target.getAttribute('data-product');
                this.addToCart(productId);
            });
        });

        const supportTrigger = document.getElementById('supportTrigger');
        const supportChat = document.getElementById('supportChat');
        const closeChat = document.getElementById('closeChat');
        const sendMessage = document.getElementById('sendMessage');
        const messageInput = document.getElementById('messageInput');

        supportTrigger.addEventListener('click', () => {
            supportChat.classList.add('active');
        });

        closeChat.addEventListener('click', () => {
            supportChat.classList.remove('active');
        });

        sendMessage.addEventListener('click', () => {
            this.sendChatMessage();
        });

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });

        document.querySelector('.cta-button').addEventListener('click', () => {
            document.getElementById('catalog').scrollIntoView({ behavior: 'smooth' });
        });
    }

    addToCart(productId) {
        this.cart.push(productId);
        this.updateCartCount();
        this.showNotification('Товар добавлен в корзину!');
    }

    updateCartCount() {
        const cartCount = document.querySelector('.cart-count');
        cartCount.textContent = this.cart.length;
    }

    showNotification(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 10000;
            font-weight: bold;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }

    async sendChatMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        this.addMessageToChat(message, 'user');
        
        messageInput.value = '';

        this.showTypingIndicator();

        try {
            const response = await this.callFlaskAPI(message);
            
            this.hideTypingIndicator();
            
            if (response.user_info) {
                this.updateUserInfo(response.user_info);
            }
            
            this.addMessageToChat(response.message, 'bot');
            
            if (response.fallback) {
                console.warn('Используется fallback ответ - LLM недоступен');
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            console.error('Ошибка при обращении к серверу:', error);
            
            if (error.message.includes('401')) {
                this.addMessageToChat(' Для использования чата необходимо войти в систему. <a href="/login">Войти</a>', 'bot');
            } else {
                this.addMessageToChat('Извините, произошла ошибка. Попробуйте позже.', 'bot');
            }
        }
    }

    async callFlaskAPI(userMessage) {
        try {
            const response = await fetch(API_CONFIG.baseUrl + API_CONFIG.chatEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Неизвестная ошибка');
            }
            
            return data;
            
        } catch (error) {
            console.error('Ошибка Flask API:', error);
            throw error;
        }
    }

    async checkServerHealth() {
        try {
            const response = await fetch(API_CONFIG.baseUrl + API_CONFIG.healthEndpoint);
            const data = await response.json();
            
            console.log('Статус сервера:', data);
            
            if (!data.llm_available) {
                console.warn('LLM Studio недоступен, будут использоваться fallback ответы');
            }
            
        } catch (error) {
            console.error('Ошибка проверки здоровья сервера:', error);
        }
    }

    updateUserInfo(userInfo) {
        const chatHeader = document.querySelector('.chat-header h4');
        if (chatHeader && userInfo.name) {
            chatHeader.textContent = `Поддержка SAMSHOP - ${userInfo.name}`;
        }
        
        if (userInfo.is_admin) {
            const adminBadge = document.createElement('span');
            adminBadge.style.cssText = `
                background: #ff4757;
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 0.7rem;
                margin-left: 5px;
            `;
            adminBadge.textContent = 'ADMIN';
            chatHeader.appendChild(adminBadge);
        }
    }

    addMessageToChat(message, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        messageContent.textContent = message;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message';
        typingDiv.id = 'typing-indicator';

        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        typingContent.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;

        typingDiv.appendChild(typingContent);
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new PSUTIShop();
});
