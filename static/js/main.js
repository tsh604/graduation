// 发送消息
async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;
    
    // 显示用户消息
    addMessage(message, 'user');
    input.value = '';
    
    // 显示加载动画
    showTypingIndicator();
    
    // 调用后端API
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: message})
        });
        const data = await response.json();
        
        // 移除加载动画
        removeTypingIndicator();
        
        // 显示机器人回复
        addMessage(data.response, 'bot');
    } catch (error) {
        removeTypingIndicator();
        addMessage('抱歉，系统出错了，请稍后再试。', 'bot');
        console.error('Error:', error);
    }
}

// 显示加载动画
function showTypingIndicator() {
    const messagesDiv = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content-wrapper">
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    `;
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 移除加载动画
function removeTypingIndicator() {
    const typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) {
        typingDiv.remove();
    }
}

// 添加消息到界面
function addMessage(content, sender) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const time = new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'});
    
    // 处理内容中的特殊格式
    let formattedContent = content;
    
    // 如果是机器人消息，尝试美化内容
    if (sender === 'bot') {
        // 直接移除所有#符号，确保它们不会显示在页面上
        formattedContent = content.replace(/#+/g, '');
        
        // 处理资源项，转换为美观的卡片形式
        formattedContent = formattedContent.replace(/(\d+)\.\s*[\[【](.*?)[\]】]\s*(.*?)\s*-\s*(https?:\/\/[^\s]+)/g, function(match, index, type, title, url) {
            return `
                <div class="resource-item">
                    <div class="resource-header">
                        <span class="resource-index">${index}</span>
                        <span class="resource-tag">${type}</span>
                        <span class="resource-title">${title.trim()}</span>
                    </div>
                    <a href="${url}" target="_blank" class="resource-url">${url}</a>
                </div>
            `;
        });
        
        // 处理换行
        formattedContent = formattedContent.replace(/\n/g, '<br>');
    } else {
        formattedContent = content.replace(/\n/g, '<br>');
    }
    
    const avatar = sender === 'bot' ? '🤖' : '👤';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content-wrapper">
            <div class="message-content">
                ${formattedContent}
            </div>
            <div class="timestamp">${time}</div>
        </div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 格式化链接为可点击状态
function formatLinks(text) {
    // 匹配URL并替换为可点击的链接
    return text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="resource-link">$1</a>');
}

// 格式化Markdown内容（用于术语解释等）
function formatMarkdownContent(content) {
    // 按行分割
    let lines = content.split('\n');
    let formatted = [];
    
    for (let line of lines) {
        // 跳过空行
        if (!line.trim()) continue;
        
        // 处理Markdown标题
        if (line.startsWith('## ')) {
            let title = line.replace('## ', '').trim();
            formatted.push(`<h3 class="explain-title">${title}</h3>`);
        } else if (line.startsWith('### ')) {
            let title = line.replace('### ', '').trim();
            formatted.push(`<h4 class="explain-subtitle">${title}</h4>`);
        } else if (line.startsWith('1. ') || line.startsWith('2. ') || line.startsWith('3. ') || line.startsWith('4. ')) {
            // 处理有序列表
            let item = line.replace(/^\d+\. /, '').trim();
            formatted.push(`<div class="explain-item">${item}</div>`);
        } else if (line.startsWith('• ')) {
            // 处理无序列表
            let item = line.replace('• ', '').trim();
            formatted.push(`<div class="explain-bullet">${item}</div>`);
        } else {
            // 普通文本
            formatted.push(`<div class="explain-text">${line}</div>`);
        }
    }
    
    return formatted.join('');
}

// 格式化学习方案
function formatLearningPlan(content) {
    // 简单的字符串替换方法，确保所有#符号都被移除
    let formatted = content
        // 移除所有Markdown标题中的#符号
        .replace(/#+/g, '')
        // 处理资源链接
        .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="resource-link">$1</a>')
        // 处理换行
        .replace(/\n/g, '<br>');
    
    return formatted;
}

// 格式化推荐资源
function formatRecommendations(content) {
    // 按行分割
    let lines = content.split('\n');
    let formatted = [];
    let inResourceList = false;
    
    for (let line of lines) {
        // 跳过空行
        if (!line.trim()) continue;
        
        // 检测是否是资源行（以数字开头，包含【】）
        if (/^\d+\./.test(line) && line.includes('【')) {
            if (!inResourceList) {
                formatted.push('<div class="resource-list">');
                inResourceList = true;
            }
            
            // 更宽松的匹配规则
            const numberMatch = line.match(/^(\d+)\./);
            const typeMatch = line.match(/【(.*?)】/);
            
            if (numberMatch && typeMatch) {
                const index = numberMatch[1];
                const type = typeMatch[1];
                
                // 提取标题和URL
                let title = '';
                let url = '#';
                
                // 去掉开头的 "1. 【视频】" 部分
                let restLine = line.replace(/^\d+\.\s*【.*?】/, '').trim();
                
                // 检查是否包含URL
                const urlMatch = restLine.match(/(https?:\/\/[^\s]+)/);
                if (urlMatch) {
                    url = urlMatch[1];
                    title = restLine.replace(url, '').trim();
                } else {
                    title = restLine;
                }
                
                // 清理标题中多余的符号
                title = title.replace(/^-\s*/, '').trim();
                
                formatted.push(`
                    <div class="resource-item">
                        <div class="resource-header">
                            <span class="resource-index">${index}</span>
                            <span class="resource-tag">${type}</span>
                            <span class="resource-title">${title || '学习资源'}</span>
                        </div>
                        <a href="${url}" target="_blank" class="resource-url">${url}</a>
                    </div>
                `);
            } else {
                // 如果解析失败，直接显示原行
                formatted.push(`<div class="resource-item">${line}</div>`);
            }
        } else {
            if (inResourceList) {
                formatted.push('</div>');
                inResourceList = false;
            }
            
            // 检测是否是建议行（包含图标）
            if (line.includes('💼') || line.includes('🛠️') || line.includes('🎯') || line.includes('📚')) {
                const icon = line.includes('💼') ? '💼' : 
                            line.includes('🛠️') ? '🛠️' : 
                            line.includes('🎯') ? '🎯' : '📚';
                const advice = line.replace(icon, '').trim();
                formatted.push(`
                    <div class="advice-card">
                        <span class="advice-icon">${icon}</span>
                        <span>${advice}</span>
                    </div>
                `);
            } else {
                formatted.push(`<div>${line}</div>`);
            }
        }
    }
    
    if (inResourceList) {
        formatted.push('</div>');
    }
    
    return formatted.join('');
}

// 清除聊天记录（新对话）
async function clearChat() {
    const messagesDiv = document.getElementById('chat-messages');
    messagesDiv.innerHTML = '';
    
    try {
        const response = await fetch('/reset', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            // 添加欢迎消息
            const welcomeDiv = document.createElement('div');
            welcomeDiv.className = 'message bot-message';
            welcomeDiv.innerHTML = `
                <div class="message-avatar">🤖</div>
                <div class="message-content-wrapper">
                    <div class="message-content">
                        你好！我是你的学习助手。请问你想学习什么技术？比如：Python、Java、前端开发等
                    </div>
                    <div class="timestamp">刚刚</div>
                </div>
            `;
            messagesDiv.appendChild(welcomeDiv);
        }
    } catch (error) {
        console.log('重置失败');
        // 出错时也显示欢迎消息
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message bot-message';
        welcomeDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content-wrapper">
                <div class="message-content">
                    你好！我是你的学习助手。请问你想学习什么技术？比如：Python、Java、前端开发等
                </div>
                <div class="timestamp">刚刚</div>
            </div>
        `;
        messagesDiv.appendChild(welcomeDiv);
    }
}

// 加载历史记录（现在默认显示欢迎消息，不加载历史记录）
async function loadHistory() {
    try {
        const messagesDiv = document.getElementById('chat-messages');
        messagesDiv.innerHTML = '';
        
        // 显示欢迎消息
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message bot-message';
        welcomeDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content-wrapper">
                <div class="message-content">
                    你好！我是你的学习助手。请问你想学习什么技术？比如：Python、Java、前端开发等
                </div>
                <div class="timestamp">刚刚</div>
            </div>
        `;
        messagesDiv.appendChild(welcomeDiv);
    } catch (error) {
        console.log('初始化聊天界面失败');
        // 出错时显示欢迎消息
        const messagesDiv = document.getElementById('chat-messages');
        messagesDiv.innerHTML = '';
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message bot-message';
        welcomeDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content-wrapper">
                <div class="message-content">
                    你好！我是你的学习助手。请问你想学习什么技术？比如：Python、Java、前端开发等
                </div>
                <div class="timestamp">刚刚</div>
            </div>
        `;
        messagesDiv.appendChild(welcomeDiv);
    }
}

// 显示资源指南
function showResourceGuide() {
    const guide = `
        📚 学习资源推荐网站：
        
        1. 菜鸟教程 (runoob.com)
           - Python、Java、C++ 基础教程
           - 适合初学者
        
        2. 官方文档 (python.org/docs)
           - 最权威的Python学习资料
           - 适合进阶学习
        
        3. LeetCode (leetcode.cn)
           - 编程练习题
           - 面试准备
        
        4. 廖雪峰的官方网站 (liaoxuefeng.com)
           - Python、Git 教程
           - 通俗易懂
        
        5. 微软文档 (learn.microsoft.com)
           - C++、C# 教程
           - 企业级开发指南
    `;
    alert(guide);
}

// 显示资源库
async function showResourceLibrary() {
    try {
        const response = await fetch('/domains');
        const data = await response.json();
        
        if (data.domains && data.domains.length > 0) {
            let domainsList = data.domains.map(domain => `
                <div class="domain-item" onclick="selectDomain('${domain}')">
                    <span class="domain-name">${domain}</span>
                    <span class="domain-arrow">→</span>
                </div>
            `).join('');
            
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>学习资源库</h2>
                        <button onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <p>请选择你感兴趣的学习领域：</p>
                        <div class="domains-list">
                            ${domainsList}
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
        } else {
            alert('暂无可用的学习领域');
        }
    } catch (error) {
        console.error('获取领域失败:', error);
        alert('获取学习领域失败，请稍后再试');
    }
}

// 选择领域
function selectDomain(domain) {
    // 关闭模态框
    document.querySelector('.modal').remove();
    
    // 显示用户消息
    addMessage(`我想学习${domain}`, 'user');
    
    // 显示加载动画
    showTypingIndicator();
    
    // 调用后端API
    fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: `我想学习${domain}`})
    })
    .then(response => response.json())
    .then(data => {
        // 移除加载动画
        removeTypingIndicator();
        
        // 显示机器人回复
        addMessage(data.response, 'bot');
    })
    .catch(error => {
        removeTypingIndicator();
        addMessage('抱歉，系统出错了，请稍后再试。', 'bot');
        console.error('Error:', error);
    });
}

// 搜索并添加资源
async function searchAndAddResource(topic, subtopic) {
    try {
        const response = await fetch('/search-resource', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({topic: topic, subtopic: subtopic})
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            return data.message;
        } else {
            return `搜索资源失败: ${data.message}`;
        }
    } catch (error) {
        console.error('搜索资源失败:', error);
        return '搜索资源失败，请稍后再试';
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 为所有现有链接添加处理
    document.querySelectorAll('.resource-link').forEach(link => {
        if (link.href.includes('example.com')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                showResourceGuide();
            });
        }
    });
    
    // 加载历史记录
    loadHistory();
    
    // 添加浏览资源库按钮
    const headerRight = document.querySelector('.header-right');
    if (headerRight) {
        const libraryButton = document.createElement('button');
        libraryButton.className = 'library-button';
        libraryButton.textContent = '浏览资源库';
        libraryButton.onclick = showResourceLibrary;
        headerRight.insertBefore(libraryButton, headerRight.firstChild);
    }
    
    // 强制刷新缓存
    console.log('Main.js loaded and executed');
});