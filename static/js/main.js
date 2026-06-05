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
        
        // 将HTML换行符转换为普通换行符
        formattedContent = formattedContent.replace(/<br\s*\/?>/gi, '\n');
        
        // 处理阶段信息，转换为美观的卡片形式
        // 使用更精确的正则表达式，支持中英文冒号，只匹配阶段标题和基本信息
        const stageRegex = /阶段\s*(\d+)\s*[:：]\s*([^(]+?)\s*\(\s*([^)]+?)\s*\)\s*[\n\r]+((?:-\s*(?!推荐资源)[^\n\r]*[\n\r]*?)+?)(?=\n阶段|\n- 推荐资源[:：]|\Z)/gi;
        formattedContent = formattedContent.replace(stageRegex, function(match, stageNum, topic, level, details) {
            // 清理topic末尾的空格
            topic = topic.trim();
            level = level.trim();
            
            // 解析详细信息
            let learningTime = '';
            let weeks = '';
            let description = '';
            
            // 从details中提取学习时间（处理重复字段，支持中英文冒号）
            const timeMatches = details.match(/学习时间[\uff1a:]\s*([^\n\r]+)/g);
            if (timeMatches && timeMatches.length > 0) {
                const lastTimeMatch = timeMatches[timeMatches.length - 1].match(/学习时间[\uff1a:]\s*([^\n\r]+)/);
                if (lastTimeMatch) {
                    learningTime = lastTimeMatch[1].trim();
                    if (!learningTime.includes('小时')) {
                        learningTime += ' 小时';
                    }
                }
            }
            
            // 从details中提取预计周数（处理重复字段，优先选择包含"周"的）
            const weekMatches = details.match(/预计周数[\uff1a:]\s*([^\n\r]+)/g);
            if (weekMatches) {
                for (let wm of weekMatches) {
                    const wmMatch = wm.match(/预计周数[\uff1a:]\s*([^\n\r]+)/);
                    if (wmMatch) {
                        const val = wmMatch[1].trim();
                        if (val.includes('周')) {
                            weeks = val;
                            break;
                        }
                        if (!weeks) weeks = val;
                    }
                }
                if (weeks && !weeks.includes('周')) {
                    weeks += ' 周';
                }
            }
            
            // 从details中提取学习内容（支持中英文冒号）
            const descMatch = details.match(/学习内容[\uff1a:]\s*([^\n\r]+)/);
            if (descMatch) {
                description = descMatch[1].trim();
            }
            
            // 生成阶段卡片HTML
            return `
                <div class="stage-card">
                    <div class="stage-header">
                        <span class="stage-badge">阶段 ${stageNum}</span>
                        <span class="stage-topic">${topic}</span>
                        <span class="stage-level">${level}</span>
                    </div>
                    <div class="stage-details">
                        <div class="stage-detail">
                            <span class="detail-icon">⏱️</span>
                            <span class="detail-label">学习时间</span>
                            <span class="detail-value">${learningTime}</span>
                        </div>
                        <div class="stage-detail">
                            <span class="detail-icon">📅</span>
                            <span class="detail-label">预计周数</span>
                            <span class="detail-value">${weeks}</span>
                        </div>
                        <div class="stage-detail-full">
                            <span class="detail-icon">📚</span>
                            <span class="detail-label">学习内容</span>
                            <span class="detail-value">${description}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        // 处理资源项，转换为美观的卡片形式
        formattedContent = formattedContent.replace(/(\d+)\.\s*[\[【](.*?)[\]】]\s*(.*?)\s*-\s*(https?:\/\/[^\s]+)/g, function(match, index, type, title, url) {
            // 为了确保收藏正确的资源，我们需要获取实际的资源ID
            // 这里我们使用一个完整的映射，将所有资源名称映射到对应的资源ID
            const resourceIdMap = {
                // Python相关
                'Python基础教程': 1,
                'Python进阶': 2,
                '廖雪峰Python教程': 3,
                'Python Cookbook': 4,
                'LeetCode Python题库': 5,
                'Python函数式编程': 6,
                'Python并发编程': 7,
                'Requests库文档': 8,
                'Python 100天': 9,
                'Python正则表达式': 10,
                'Flask Web开发': 11,
                'Django入门': 12,
                'Python爬虫教程': 13,
                'NumPy教程': 14,
                'Python单元测试': 15,
                'Python装饰器': 16,
                'Python生成器': 17,
                'Python多线程': 18,
                'Python类型注解': 19,
                'Python项目结构': 20,
                'Pandas官方文档': 21,
                'Matplotlib教程': 22,
                'Kaggle Pandas课程': 23,
                '数据清洗实战': 24,
                'Seaborn教程': 25,
                'Plotly入门': 26,
                '数据预处理': 27,
                'Excel数据分析': 28,
                'SQL数据分析': 29,
                '统计学基础': 30,
                'Tableau入门': 31,
                'Power BI教程': 32,
                '时间序列分析': 33,
                'A/B测试指南': 34,
                '数据思维': 35,
                'Scikit-learn教程': 36,
                'PyTorch官方教程': 37,
                'Kaggle机器学习入门': 38,
                'TensorFlow教程': 39,
                '机器学习实战': 40,
                '吴恩达机器学习': 41,
                '李宏毅机器学习': 42,
                'Fast.ai教程': 43,
                '机器学习公式详解': 44,
                'XGBoost文档': 45,
                'LightGBM教程': 46,
                '神经网络入门': 47,
                '卷积神经网络': 48,
                '自然语言处理': 49,
                '强化学习': 50,
                '特征工程': 51,
                '模型调参': 52,
                '模型评估': 53,
                '机器学习系统设计': 54,
                'MLOps基础': 55,
                // Java相关
                'Java基础教程': 56,
                'Oracle Java文档': 57,
                'Spring官方指南': 58,
                'JVM规范': 59,
                'Java并发编程': 60,
                'Maven教程': 61,
                'Gradle入门': 62,
                'MyBatis文档': 63,
                'Hibernate教程': 64,
                'Java 8新特性': 65,
                'Java性能调优': 66,
                '设计模式': 67,
                'Java单元测试': 68,
                'Mockito使用': 69,
                'Java网络编程': 70,
                // Web前端相关
                'MDN Web文档': 71,
                '现代JavaScript教程': 72,
                'Vue官方教程': 73,
                'React官方文档': 74,
                'Webpack官方指南': 75,
                'CSS教程': 76,
                'HTML5教程': 77,
                'TypeScript手册': 78,
                'Node.js教程': 79,
                'npm文档': 80,
                'Git教程': 81,
                'WebAssembly': 82,
                'PWA教程': 83,
                '浏览器工作原理': 84,
                '前端性能优化': 85,
                'Web安全指南': 86,
                'CSS Grid布局': 87,
                'Flexbox教程': 88,
                'Sass入门': 89,
                'Web组件开发': 90,
                // 数据库相关
                'MySQL官方教程': 91,
                'Redis官方文档': 92,
                'MongoDB教程': 93,
                'PostgreSQL文档': 94,
                'SQLite教程': 95,
                '数据库设计': 96,
                'SQL优化': 97,
                '事务ACID': 98,
                'Elasticsearch': 99,
                'Cassandra教程': 100,
                'Neo4j图数据库': 101,
                'InfluxDB时序数据库': 102,
                '数据库分片': 103,
                '备份与恢复': 104,
                'NoSQL入门': 105,
                // 算法相关
                'GeeksforGeeks算法': 106,
                'LeetCode题库': 107,
                'OI Wiki': 108,
                '算法导论': 109,
                '可视化算法': 110,
                '排序算法': 111,
                '动态规划': 112,
                '图论算法': 113,
                '字符串匹配': 114,
                '剑指Offer': 115,
                // C++相关
                'C++基础教程': 116,
                'C++参考手册': 117,
                'C++内存管理': 118,
                'C++ STL教程': 119,
                'C++11新特性': 120,
                'C++多线程': 121,
                'C++设计模式': 122,
                'C++性能优化': 123,
                'C++智能指针': 124,
                'C++模板元编程': 125,
                // 运维相关
                'Linux教程': 126,
                'Shell脚本教程': 127,
                'Docker官方教程': 128,
                'K8s官方教程': 129,
                'Linux命令大全': 130,
                'Vim教程': 131,
                'Nginx配置': 132,
                'Jenkins教程': 133,
                'Ansible文档': 134,
                'Prometheus监控': 135,
                // 数学相关
                '线性代数入门': 136,
                '线性代数基础': 137,
                '微积分入门': 138,
                '微积分基础': 139,
                '统计学基础': 140,
                '概率论基础': 141,
                '数学分析基础': 142,
                '离散数学': 143,
                '数论基础': 144,
                '数学建模': 145,
                // 工具相关
                'VS Code文档': 146,
                'Postman文档': 147,
                'Git官方文档': 148,
                'GitHub指南': 149,
                'Docker Compose': 150,
                'Makefile教程': 151,
                'CMake文档': 152,
                'Jupyter教程': 153,
                'PyCharm指南': 154,
                'IntelliJ教程': 155,
                'Chrome DevTools': 156,
                'Fiddler教程': 157,
                'Charles使用': 158,
                'Sublime Text': 159,
                'Zsh配置': 160
            };
            
            // 尝试从映射中获取资源ID，如果没有则使用索引作为默认值
            const resourceId = resourceIdMap[title.trim()] || parseInt(index);
            return `
                <div class="resource-item">
                    <div class="resource-header">
                        <span class="resource-index">${index}</span>
                        <span class="resource-tag">${type}</span>
                        <span class="resource-title">${title.trim()}</span>
                        <button class="collection-btn" onclick="addCollection(${resourceId})"><span>⭐</span> 收藏</button>
                        <button class="learn-btn" onclick="startLearning(${resourceId}, '${title.trim()}', this)"><span>📖</span> 开始学习</button>
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
    
    // 如果是机器人消息，检查是否包含资源列表，并恢复学习状态
    if (sender === 'bot') {
        setTimeout(() => {
            loadLearningState();
        }, 100);
    }
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
                
                // 为了确保收藏正确的资源，我们需要获取实际的资源ID
                // 这里我们使用一个完整的映射，将所有资源名称映射到对应的资源ID
                const resourceIdMap = {
                    // Python相关
                    'Python基础教程': 1,
                    'Python进阶': 2,
                    '廖雪峰Python教程': 3,
                    'Python Cookbook': 4,
                    'LeetCode Python题库': 5,
                    'Python函数式编程': 6,
                    'Python并发编程': 7,
                    'Requests库文档': 8,
                    'Python 100天': 9,
                    'Python正则表达式': 10,
                    'Flask Web开发': 11,
                    'Django入门': 12,
                    'Python爬虫教程': 13,
                    'NumPy教程': 14,
                    'Python单元测试': 15,
                    'Python装饰器': 16,
                    'Python生成器': 17,
                    'Python多线程': 18,
                    'Python类型注解': 19,
                    'Python项目结构': 20,
                    'Pandas官方文档': 21,
                    'Matplotlib教程': 22,
                    'Kaggle Pandas课程': 23,
                    '数据清洗实战': 24,
                    'Seaborn教程': 25,
                    'Plotly入门': 26,
                    '数据预处理': 27,
                    'Excel数据分析': 28,
                    'SQL数据分析': 29,
                    '统计学基础': 30,
                    'Tableau入门': 31,
                    'Power BI教程': 32,
                    '时间序列分析': 33,
                    'A/B测试指南': 34,
                    '数据思维': 35,
                    'Scikit-learn教程': 36,
                    'PyTorch官方教程': 37,
                    'Kaggle机器学习入门': 38,
                    'TensorFlow教程': 39,
                    '机器学习实战': 40,
                    '吴恩达机器学习': 41,
                    '李宏毅机器学习': 42,
                    'Fast.ai教程': 43,
                    '机器学习公式详解': 44,
                    'XGBoost文档': 45,
                    'LightGBM教程': 46,
                    '神经网络入门': 47,
                    '卷积神经网络': 48,
                    '自然语言处理': 49,
                    '强化学习': 50,
                    '特征工程': 51,
                    '模型调参': 52,
                    '模型评估': 53,
                    '机器学习系统设计': 54,
                    'MLOps基础': 55,
                    // Java相关
                    'Java基础教程': 56,
                    'Oracle Java文档': 57,
                    'Spring官方指南': 58,
                    'JVM规范': 59,
                    'Java并发编程': 60,
                    'Maven教程': 61,
                    'Gradle入门': 62,
                    'MyBatis文档': 63,
                    'Hibernate教程': 64,
                    'Java 8新特性': 65,
                    'Java性能调优': 66,
                    '设计模式': 67,
                    'Java单元测试': 68,
                    'Mockito使用': 69,
                    'Java网络编程': 70,
                    // Web前端相关
                    'MDN Web文档': 71,
                    '现代JavaScript教程': 72,
                    'Vue官方教程': 73,
                    'React官方文档': 74,
                    'Webpack官方指南': 75,
                    'CSS教程': 76,
                    'HTML5教程': 77,
                    'TypeScript手册': 78,
                    'Node.js教程': 79,
                    'npm文档': 80,
                    'Git教程': 81,
                    'WebAssembly': 82,
                    'PWA教程': 83,
                    '浏览器工作原理': 84,
                    '前端性能优化': 85,
                    'Web安全指南': 86,
                    'CSS Grid布局': 87,
                    'Flexbox教程': 88,
                    'Sass入门': 89,
                    'Web组件开发': 90,
                    // 数据库相关
                    'MySQL官方教程': 91,
                    'Redis官方文档': 92,
                    'MongoDB教程': 93,
                    'PostgreSQL文档': 94,
                    'SQLite教程': 95,
                    '数据库设计': 96,
                    'SQL优化': 97,
                    '事务ACID': 98,
                    'Elasticsearch': 99,
                    'Cassandra教程': 100,
                    'Neo4j图数据库': 101,
                    'InfluxDB时序数据库': 102,
                    '数据库分片': 103,
                    '备份与恢复': 104,
                    'NoSQL入门': 105,
                    // 算法相关
                    'GeeksforGeeks算法': 106,
                    'LeetCode题库': 107,
                    'OI Wiki': 108,
                    '算法导论': 109,
                    '可视化算法': 110,
                    '排序算法': 111,
                    '动态规划': 112,
                    '图论算法': 113,
                    '字符串匹配': 114,
                    '剑指Offer': 115,
                    // C++相关
                    'C++基础教程': 116,
                    'C++参考手册': 117,
                    'C++内存管理': 118,
                    'C++ STL教程': 119,
                    'C++11新特性': 120,
                    'C++多线程': 121,
                    'C++设计模式': 122,
                    'C++性能优化': 123,
                    'C++智能指针': 124,
                    'C++模板元编程': 125,
                    // 运维相关
                    'Linux教程': 126,
                    'Shell脚本教程': 127,
                    'Docker官方教程': 128,
                    'K8s官方教程': 129,
                    'Linux命令大全': 130,
                    'Vim教程': 131,
                    'Nginx配置': 132,
                    'Jenkins教程': 133,
                    'Ansible文档': 134,
                    'Prometheus监控': 135,
                    // 数学相关
                    '线性代数入门': 136,
                    '线性代数基础': 137,
                    '微积分入门': 138,
                    '微积分基础': 139,
                    '统计学基础': 140,
                    '概率论基础': 141,
                    '数学分析基础': 142,
                    '离散数学': 143,
                    '数论基础': 144,
                    '数学建模': 145,
                    // 工具相关
                    'VS Code文档': 146,
                    'Postman文档': 147,
                    'Git官方文档': 148,
                    'GitHub指南': 149,
                    'Docker Compose': 150,
                    'Makefile教程': 151,
                    'CMake文档': 152,
                    'Jupyter教程': 153,
                    'PyCharm指南': 154,
                    'IntelliJ教程': 155,
                    'Chrome DevTools': 156,
                    'Fiddler教程': 157,
                    'Charles使用': 158,
                    'Sublime Text': 159,
                    'Zsh配置': 160
                };
                
                // 尝试从映射中获取资源ID，如果没有则使用索引作为默认值
                const resourceId = resourceIdMap[title] || parseInt(index);
                formatted.push(`
                    <div class="resource-item">
                        <div class="resource-header">
                            <span class="resource-index">${index}</span>
                            <span class="resource-tag">${type}</span>
                            <span class="resource-title">${title || '学习资源'}</span>
                            <button class="collection-btn" onclick="addCollection(${resourceId})"><span>⭐</span> 收藏</button>
                            <button class="learn-btn" onclick="startLearning(${resourceId}, '${title}', this)"><span>📖</span> 开始学习</button>
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
        // 检查元素是否存在，只在推荐界面中执行
        if (messagesDiv) {
            // 清空并加载历史
            messagesDiv.innerHTML = '';
            
            // 从服务器加载对话历史（优先从内存状态，其次从数据库）
            const response = await fetch('/check-conversation-state');
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                // 直接遍历历史记录，后端已按时间升序返回
                data.history.forEach(item => {
                    // 显示用户消息
                    const userDiv = document.createElement('div');
                    userDiv.className = 'message user-message';
                    userDiv.innerHTML = `
                        <div class="message-avatar">👤</div>
                        <div class="message-content-wrapper">
                            <div class="message-content">${item.user}</div>
                            <div class="timestamp">${item.time}</div>
                        </div>
                    `;
                    messagesDiv.appendChild(userDiv);
                    
                    // 显示机器人消息
                    const botDiv = document.createElement('div');
                    botDiv.className = 'message bot-message';
                    
                    // 处理机器人消息内容，应用与addMessage函数相同的美化处理
                    let formattedContent = item.bot;
                    
                    // 直接移除所有#符号，确保它们不会显示在页面上
                    formattedContent = formattedContent.replace(/#+/g, '');
                    
                    // 将HTML换行符转换为普通换行符
                    formattedContent = formattedContent.replace(/<br\s*\/?>/gi, '\n');
                    
                    // 处理阶段信息，转换为美观的卡片形式
                    const stageRegex = /阶段\s*(\d+)\s*[:：]\s*([^(]+?)\s*\(\s*([^)]+?)\s*\)\s*[\n\r]+((?:-\s*(?!推荐资源)[^\n\r]*[\n\r]*?)+?)(?=\n阶段|\n- 推荐资源[:：]|\Z)/gi;
                    formattedContent = formattedContent.replace(stageRegex, function(match, stageNum, topic, level, details) {
                        topic = topic.trim();
                        level = level.trim();
                        let learningTime = '';
                        let weeks = '';
                        let description = '';
                        
                        const timeMatches = details.match(/学习时间[\uff1a:]\s*([^\n\r]+)/g);
                        if (timeMatches && timeMatches.length > 0) {
                            const lastTimeMatch = timeMatches[timeMatches.length - 1].match(/学习时间[\uff1a:]\s*([^\n\r]+)/);
                            if (lastTimeMatch) {
                                learningTime = lastTimeMatch[1].trim();
                                if (!learningTime.includes('小时')) learningTime += ' 小时';
                            }
                        }
                        
                        const weekMatches = details.match(/预计周数[\uff1a:]\s*([^\n\r]+)/g);
                        if (weekMatches) {
                            for (let wm of weekMatches) {
                                const wmMatch = wm.match(/预计周数[\uff1a:]\s*([^\n\r]+)/);
                                if (wmMatch) {
                                    const val = wmMatch[1].trim();
                                    if (val.includes('周')) { weeks = val; break; }
                                    if (!weeks) weeks = val;
                                }
                            }
                            if (weeks && !weeks.includes('周')) weeks += ' 周';
                        }
                        
                        const descMatch = details.match(/学习内容[\uff1a:]\s*([^\n\r]+)/);
                        if (descMatch) description = descMatch[1].trim();
                        
                        return `<div class="stage-card"><div class="stage-header"><span class="stage-badge">阶段 ${stageNum}</span><span class="stage-topic">${topic}</span><span class="stage-level">${level}</span></div><div class="stage-details"><div class="stage-detail"><span class="detail-icon">⏱️</span><span class="detail-label">学习时间</span><span class="detail-value">${learningTime}</span></div><div class="stage-detail"><span class="detail-icon">📅</span><span class="detail-label">预计周数</span><span class="detail-value">${weeks}</span></div><div class="stage-detail-full"><span class="detail-icon">📚</span><span class="detail-label">学习内容</span><span class="detail-value">${description}</span></div></div></div>`;
                    });
                    
                    // 处理资源项，转换为美观的卡片形式
                    formattedContent = formattedContent.replace(/(\d+)\.\s*[\[【](.*?)[\]】]\s*(.*?)\s*-\s*(https?:\/\/[^\s]+)/g, function(match, index, type, title, url) {
                        // 为了确保收藏正确的资源，我们需要获取实际的资源ID
                        // 这里我们使用一个完整的映射，将所有资源名称映射到对应的资源ID
                        const resourceIdMap = {
                            // Python相关
                            'Python基础教程': 1,
                            'Python进阶': 2,
                            '廖雪峰Python教程': 3,
                            'Python Cookbook': 4,
                            'LeetCode Python题库': 5,
                            'Python函数式编程': 6,
                            'Python并发编程': 7,
                            'Requests库文档': 8,
                            'Python 100天': 9,
                            'Python正则表达式': 10,
                            'Flask Web开发': 11,
                            'Django入门': 12,
                            'Python爬虫教程': 13,
                            'NumPy教程': 14,
                            'Python单元测试': 15,
                            'Python装饰器': 16,
                            'Python生成器': 17,
                            'Python多线程': 18,
                            'Python类型注解': 19,
                            'Python项目结构': 20,
                            'Pandas官方文档': 21,
                            'Matplotlib教程': 22,
                            'Kaggle Pandas课程': 23,
                            '数据清洗实战': 24,
                            'Seaborn教程': 25,
                            'Plotly入门': 26,
                            '数据预处理': 27,
                            'Excel数据分析': 28,
                            'SQL数据分析': 29,
                            '统计学基础': 30,
                            'Tableau入门': 31,
                            'Power BI教程': 32,
                            '时间序列分析': 33,
                            'A/B测试指南': 34,
                            '数据思维': 35,
                            'Scikit-learn教程': 36,
                            'PyTorch官方教程': 37,
                            'Kaggle机器学习入门': 38,
                            'TensorFlow教程': 39,
                            '机器学习实战': 40,
                            '吴恩达机器学习': 41,
                            '李宏毅机器学习': 42,
                            'Fast.ai教程': 43,
                            '机器学习公式详解': 44,
                            'XGBoost文档': 45,
                            'LightGBM教程': 46,
                            '神经网络入门': 47,
                            '卷积神经网络': 48,
                            '自然语言处理': 49,
                            '强化学习': 50,
                            '特征工程': 51,
                            '模型调参': 52,
                            '模型评估': 53,
                            '机器学习系统设计': 54,
                            'MLOps基础': 55,
                            // Java相关
                            'Java基础教程': 56,
                            'Oracle Java文档': 57,
                            'Spring官方指南': 58,
                            'JVM规范': 59,
                            'Java并发编程': 60,
                            'Maven教程': 61,
                            'Gradle入门': 62,
                            'MyBatis文档': 63,
                            'Hibernate教程': 64,
                            'Java 8新特性': 65,
                            'Java性能调优': 66,
                            '设计模式': 67,
                            'Java单元测试': 68,
                            'Mockito使用': 69,
                            'Java网络编程': 70,
                            // Web前端相关
                            'MDN Web文档': 71,
                            '现代JavaScript教程': 72,
                            'Vue官方教程': 73,
                            'React官方文档': 74,
                            'Webpack官方指南': 75,
                            'CSS教程': 76,
                            'HTML5教程': 77,
                            'TypeScript手册': 78,
                            'Node.js教程': 79,
                            'npm文档': 80,
                            'Git教程': 81,
                            'WebAssembly': 82,
                            'PWA教程': 83,
                            '浏览器工作原理': 84,
                            '前端性能优化': 85,
                            'Web安全指南': 86,
                            'CSS Grid布局': 87,
                            'Flexbox教程': 88,
                            'Sass入门': 89,
                            'Web组件开发': 90,
                            // 数据库相关
                            'MySQL官方教程': 91,
                            'Redis官方文档': 92,
                            'MongoDB教程': 93,
                            'PostgreSQL文档': 94,
                            'SQLite教程': 95,
                            '数据库设计': 96,
                            'SQL优化': 97,
                            '事务ACID': 98,
                            'Elasticsearch': 99,
                            'Cassandra教程': 100,
                            'Neo4j图数据库': 101,
                            'InfluxDB时序数据库': 102,
                            '数据库分片': 103,
                            '备份与恢复': 104,
                            'NoSQL入门': 105,
                            // 算法相关
                            'GeeksforGeeks算法': 106,
                            'LeetCode题库': 107,
                            'OI Wiki': 108,
                            '算法导论': 109,
                            '可视化算法': 110,
                            '排序算法': 111,
                            '动态规划': 112,
                            '图论算法': 113,
                            '字符串匹配': 114,
                            '剑指Offer': 115,
                            // C++相关
                            'C++基础教程': 116,
                            'C++参考手册': 117,
                            'C++内存管理': 118,
                            'C++ STL教程': 119,
                            'C++11新特性': 120,
                            'C++多线程': 121,
                            'C++设计模式': 122,
                            'C++性能优化': 123,
                            'C++智能指针': 124,
                            'C++模板元编程': 125,
                            // 运维相关
                            'Linux教程': 126,
                            'Shell脚本教程': 127,
                            'Docker官方教程': 128,
                            'K8s官方教程': 129,
                            'Linux命令大全': 130,
                            'Vim教程': 131,
                            'Nginx配置': 132,
                            'Jenkins教程': 133,
                            'Ansible文档': 134,
                            'Prometheus监控': 135,
                            // 数学相关
                            '线性代数入门': 136,
                            '线性代数基础': 137,
                            '微积分入门': 138,
                            '微积分基础': 139,
                            '统计学基础': 140,
                            '概率论基础': 141,
                            '数学分析基础': 142,
                            '离散数学': 143,
                            '数论基础': 144,
                            '数学建模': 145,
                            // 工具相关
                            'VS Code文档': 146,
                            'Postman文档': 147,
                            'Git官方文档': 148,
                            'GitHub指南': 149,
                            'Docker Compose': 150,
                            'Makefile教程': 151,
                            'CMake文档': 152,
                            'Jupyter教程': 153,
                            'PyCharm指南': 154,
                            'IntelliJ教程': 155,
                            'Chrome DevTools': 156,
                            'Fiddler教程': 157,
                            'Charles使用': 158,
                            'Sublime Text': 159,
                            'Zsh配置': 160
                        };
                        
                        // 尝试从映射中获取资源ID，如果没有则使用索引作为默认值
                        const resourceId = resourceIdMap[title.trim()] || parseInt(index);
                        return `
                            <div class="resource-item">
                                <div class="resource-header">
                                    <span class="resource-index">${index}</span>
                                    <span class="resource-tag">${type}</span>
                                    <span class="resource-title">${title.trim()}</span>
                                    <button class="collection-btn" onclick="addCollection(${resourceId})"><span>⭐</span> 收藏</button>
                                    <button class="learn-btn" onclick="startLearning(${resourceId}, '${title.trim()}', this)"><span>📖</span> 开始学习</button>
                                </div>
                                <a href="${url}" class="resource-link" target="_blank">${url}</a>
                            </div>
                        `;
                    });
                    
                    botDiv.innerHTML = `
                        <div class="message-avatar">🤖</div>
                        <div class="message-content-wrapper">
                            <div class="message-content">${formattedContent}</div>
                            <div class="timestamp">${item.time}</div>
                        </div>
                    `;
                    messagesDiv.appendChild(botDiv);
                });
            } else {
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
            }
            
            // 滚动到对话最底端
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    } catch (error) {
        console.log('初始化聊天界面失败:', error);
        // 显示欢迎消息作为 fallback
        const messagesDiv = document.getElementById('chat-messages');
        if (messagesDiv) {
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
            
            // 滚动到对话最底端
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
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

// 跳转到用户管理页面
function showUserProfile() {
    window.location.href = '/user';
}

// 添加收藏
async function addCollection(resourceId) {
    try {
        const response = await fetch('/collection/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({resource_id: resourceId})
        });
        const data = await response.json();
        
        if (data.success) {
            alert('收藏成功');
        } else {
            alert('收藏失败: ' + data.message);
        }
    } catch (error) {
        console.error('添加收藏失败:', error);
        alert('添加收藏失败，请稍后再试');
    }
}

// 学习计时器
let learningTimer = null;
let learningDuration = 0;        // 当前累计学习时长
let sessionStartDuration = 0;    // 本次学习开始时的累计时长（用于计算本次增量）
let currentResourceId = null;
let currentResourceTitle = null;
let currentLearnBtn = null;

// 页面加载时恢复学习状态
document.addEventListener('DOMContentLoaded', () => {
    // 延迟执行，确保DOM渲染完成
    setTimeout(() => {
        loadLearningState();
    }, 500);
});

// 加载学习状态
async function loadLearningState() {
    try {
        const response = await fetch('/api/learning-state');
        const data = await response.json();
        
        if (data.success && data.data) {
            const state = data.data;
            
            if (state.resource_id && state.status === 'learning') {
                currentResourceId = state.resource_id;
                currentResourceTitle = state.resource_name || '未知资源';
                learningDuration = state.duration || 0;
                // 设置本次学习的起始时长，用于计算增量
                sessionStartDuration = learningDuration;
                
                // 重新开始计时
                learningTimer = setInterval(() => {
                    learningDuration++;
                }, 60000);
                
                window.addEventListener('beforeunload', handleBeforeUnload);
                
                // 更新对应按钮的状态
                updateLearnButtonState(state.resource_id, 'learning', currentResourceTitle);
                
                // 禁用其他学习按钮
                disableOtherLearnButtons(state.resource_id);
            } else if (state.resource_id && state.status === 'paused') {
                currentResourceId = state.resource_id;
                currentResourceTitle = state.resource_name || '未知资源';
                learningDuration = state.duration || 0;
                // 设置本次学习的起始时长，用于计算增量
                sessionStartDuration = learningDuration;
                
                // 更新对应按钮的状态为暂停
                updateLearnButtonState(state.resource_id, 'paused', currentResourceTitle);
                
                // 暂停状态下启用所有学习按钮
                enableAllLearnButtons();
            }
        }
    } catch (error) {
        console.error('加载学习状态失败:', error);
    }
}

// 更新学习按钮状态
function updateLearnButtonState(resourceId, status, resourceName = '') {
    const buttons = document.querySelectorAll('.learn-btn');
    buttons.forEach(btn => {
        const onclickStr = btn.getAttribute('onclick');
        if (onclickStr && onclickStr.includes(`startLearning(${resourceId}`)) {
            currentLearnBtn = btn;
            
            if (status === 'learning') {
                btn.innerHTML = '<span>⏸️</span> 暂停学习';
                btn.onclick = function() { pauseLearning(); };
                btn.classList.add('learning');
                btn.classList.remove('disabled');
            } else if (status === 'paused') {
                btn.innerHTML = '<span>▶️</span> 继续学习';
                // 使用闭包捕获当前按钮、资源ID和资源名称，避免闭包陷阱
                btn.onclick = (function(currentBtn, currentResourceId, currentResourceName) {
                    return function() { startLearning(currentResourceId, currentResourceName, currentBtn); };
                })(btn, resourceId, resourceName);
                btn.classList.remove('learning');
                btn.classList.remove('disabled');
            }
        }
    });
}

// 禁用其他学习按钮
function disableOtherLearnButtons(activeResourceId) {
    const buttons = document.querySelectorAll('.learn-btn');
    buttons.forEach(btn => {
        const onclickStr = btn.getAttribute('onclick');
        if (onclickStr) {
            // 检查是否是当前正在学习的资源按钮
            const isActiveBtn = onclickStr.includes(`startLearning(${activeResourceId}`);
            if (!isActiveBtn) {
                btn.classList.add('disabled');
                btn.setAttribute('data-tooltip', `请先暂停「${currentResourceTitle}」的学习`);
                // 移除点击事件
                btn.onclick = function(e) {
                    e.preventDefault();
                    return false;
                };
            }
        }
    });
}

// 启用所有学习按钮
function enableAllLearnButtons() {
    const buttons = document.querySelectorAll('.learn-btn');
    buttons.forEach(btn => {
        btn.classList.remove('disabled');
        btn.removeAttribute('data-tooltip');
        // 恢复点击事件（需要重新绑定，这里简单处理）
        const onclickStr = btn.getAttribute('onclick');
        if (onclickStr) {
            // 尝试从onclick字符串中提取资源ID和名称
            const match = onclickStr.match(/startLearning\((\d+),\s*['"]([^'"]+)['"]/);
            if (match) {
                const resourceId = parseInt(match[1]);
                const resourceTitle = match[2];
                btn.onclick = (function(id, title, currentBtn) {
                    return function() { startLearning(id, title, currentBtn); };
                })(resourceId, resourceTitle, btn);
            }
        }
    });
}

// 开始学习
async function startLearning(resourceId, resourceTitle, btnElement) {
    try {
        // 如果正在学习其他资源，先结束它
        if (currentResourceId && learningTimer !== null && currentResourceId !== resourceId) {
            await endLearning();
        }
        
        const response = await fetch('/api/start-learning', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({resource_id: resourceId, resource_name: resourceTitle})
        });
        const data = await response.json();
        
        if (data.success) {
            currentResourceId = resourceId;
            currentResourceTitle = resourceTitle;
            currentLearnBtn = btnElement;
            // 使用后端返回的累计学习时长，而不是重置为0
            learningDuration = data.duration || 0;
            // 记录本次学习开始时的累计时长，用于计算本次学习增量
            sessionStartDuration = learningDuration;
            
            // 开始计时
            learningTimer = setInterval(() => {
                learningDuration++;
            }, 60000); // 每分钟更新一次
            
            // 更新按钮状态为"暂停学习"
            btnElement.innerHTML = '<span>⏸️</span> 暂停学习';
            btnElement.onclick = function() { pauseLearning(); };
            btnElement.classList.add('learning');
            
            // 禁用其他学习按钮
            disableOtherLearnButtons(resourceId);
            
            alert(`开始学习「${resourceTitle}」！学习时长将被记录。`);
            
            // 提示用户关闭标签页时结束学习
            window.addEventListener('beforeunload', handleBeforeUnload);
        } else {
            alert('开始学习失败: ' + data.message);
        }
    } catch (error) {
        console.error('开始学习失败:', error);
        alert('开始学习失败，请稍后再试');
    }
}

// 暂停学习
async function pauseLearning() {
    if (!currentResourceId || learningTimer === null) {
        return;
    }
    
    // 计算本次学习的增量时长（不是累计时长）
    const sessionDuration = learningDuration - sessionStartDuration;
    
    try {
        const response = await fetch('/api/pause-learning', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                resource_id: currentResourceId,
                duration: sessionDuration,  // 传递增量时长，不是累计时长
                progress: 50.0
            })
        });
        const data = await response.json();
        
        if (data.success) {
            alert(`学习已暂停！本次学习时长：${sessionDuration}分钟`);
        } else {
            alert('暂停学习失败: ' + data.message);
        }
    } catch (error) {
        console.error('暂停学习失败:', error);
    } finally {
        // 清除计时器
        clearInterval(learningTimer);
        learningTimer = null;
        
        // 启用所有学习按钮
        enableAllLearnButtons();
        
        // 更新按钮状态为"继续学习"
        if (currentLearnBtn) {
            currentLearnBtn.innerHTML = `<span>▶️</span> 继续学习`;
            // 使用闭包捕获当前的资源ID和资源名称，避免页面切换时变量被清空
            const resourceId = currentResourceId;
            const resourceTitle = currentResourceTitle;
            const learnBtn = currentLearnBtn;
            currentLearnBtn.onclick = function() { startLearning(resourceId, resourceTitle, learnBtn); };
            currentLearnBtn.classList.remove('learning');
        }
    }
}

// 结束学习
async function endLearning(completed = false) {
    if (!currentResourceId || learningTimer === null) {
        return;
    }
    
    // 计算本次学习的增量时长（不是累计时长）
    const sessionDuration = learningDuration - sessionStartDuration;
    
    try {
        const response = await fetch('/api/end-learning', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                resource_id: currentResourceId,
                duration: sessionDuration,  // 传递增量时长，不是累计时长
                completed: completed ? 1 : 0,
                progress: completed ? 100 : 50
            })
        });
        const data = await response.json();
        
        if (data.success) {
            alert(`学习结束！本次学习时长：${sessionDuration}分钟`);
        } else {
            alert('结束学习失败: ' + data.message);
        }
    } catch (error) {
        console.error('结束学习失败:', error);
    } finally {
        // 清除计时器
        clearInterval(learningTimer);
        learningTimer = null;
        
        // 启用所有学习按钮
        enableAllLearnButtons();
        
        // 在清空之前先捕获资源信息
        const resourceId = currentResourceId;
        const resourceTitle = currentResourceTitle;
        const learnBtn = currentLearnBtn;
        
        // 清空状态
        learningDuration = 0;
        currentResourceId = null;
        currentResourceTitle = null;
        
        // 恢复按钮状态为"开始学习"
        if (learnBtn) {
            learnBtn.innerHTML = '<span>📖</span> 开始学习';
            learnBtn.onclick = function() { startLearning(resourceId, resourceTitle, learnBtn); };
            learnBtn.classList.remove('learning');
            currentLearnBtn = null;
        }
        
        window.removeEventListener('beforeunload', handleBeforeUnload);
    }
}

// 页面关闭前处理 - 只在登出时清除状态
function handleBeforeUnload(event) {
    // 页面切换时不暂停学习，保持学习状态
    // 只有明确点击暂停按钮才暂停
}

// 取消收藏
async function removeCollection(resourceId) {
    if (confirm('确定要取消收藏吗？')) {
        try {
            const response = await fetch('/collection/remove', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({resource_id: resourceId})
            });
            const data = await response.json();
            
            if (data.success) {
                alert('取消收藏成功');
                // 直接从收藏列表中删除对应的收藏项
                const collectionItems = document.querySelectorAll('.collection-item');
                collectionItems.forEach(item => {
                    const deleteButton = item.querySelector('.collection-delete');
                    if (deleteButton && deleteButton.onclick.toString().includes(resourceId)) {
                        item.remove();
                    }
                });
                
                // 检查是否还有收藏项，如果没有则显示空收藏提示
                const collectionsList = document.querySelector('.collections-list');
                if (collectionsList && collectionsList.children.length === 0) {
                    collectionsList.innerHTML = '<div class="empty-collection">暂无收藏资源</div>';
                }
            } else {
                alert('取消收藏失败: ' + data.message);
            }
        } catch (error) {
            console.error('取消收藏失败:', error);
            alert('取消收藏失败，请稍后再试');
        }
    }
}

// 检查收藏状态
async function checkCollectionStatus(resourceId) {
    try {
        const response = await fetch(`/collection/check?resource_id=${resourceId}`);
        const data = await response.json();
        return data.success ? data.is_collected : false;
    } catch (error) {
        console.error('检查收藏状态失败:', error);
        return false;
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
    
    // 检查当前页面是否为用户管理页面
    const userContainer = document.querySelector('.user-container');
    if (!userContainer) {
        // 添加浏览资源库按钮（仅在推荐界面添加）
        const headerRight = document.querySelector('.header-right');
        if (headerRight) {
            const libraryButton = document.createElement('button');
            libraryButton.className = 'library-button';
            libraryButton.textContent = '浏览资源库';
            libraryButton.onclick = showResourceLibrary;
            headerRight.insertBefore(libraryButton, headerRight.firstChild);
        }
    }
    
    // 强制刷新缓存
    console.log('Main.js loaded and executed');
});