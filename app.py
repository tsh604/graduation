# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import uuid
from database import init_database, save_dialogue, clear_user_dialogues, register_user, verify_user, get_user_by_email
from recommender import Recommender
from path_planner import generate_learning_plan, get_learning_efficiency_tips
import json
import re
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 尝试导入ZhipuLLMService，如果失败则使用默认实现
try:
    from llm_service import ZhipuLLMService
    llm_available = True
except Exception as e:
    llm_available = False
    # 创建一个简单的替代实现
    class ZhipuLLMService:
        def chat(self, prompt):
            return "我是一个学习助手，可以为你提供学习方案和建议。"

# 初始化数据库
init_database()

# 应用启动时清空对话历史，确保每次启动都是一个新对话
clear_user_dialogues()

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'

# 设置 session 配置 - 解决历史记录残留问题
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'learning_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# 禁用静态文件缓存
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# 初始化各模块
recommender = Recommender()
llm = None

# 延迟初始化智谱AI服务
def get_llm():
    global llm
    if llm is None:
        llm = ZhipuLLMService()
    return llm

# 存储对话状态的字典
dialogue_state = {}

class DialogueManager:
    """对话管理器 - 实现多轮追问"""
    
    @staticmethod
    def get_state(session_id):
        """获取对话状态"""
        if session_id not in dialogue_state:
            dialogue_state[session_id] = {
                'stage': 'initial',  # initial, asking_topic, asking_level, asking_goal, asking_time_budget, asking_money_budget, recommending
                'context': {
                    'topic': None,      # 学习主题
                    'level': None,      # 难度级别
                    'goal': None,       # 学习目标
                    'time_budget': None, # 时间预算（小时）
                    'money_budget': None, # 金钱预算（元）
                },
                'history': []
            }
        return dialogue_state[session_id]
    
    @staticmethod
    def clear_state(session_id):
        """清空指定用户的对话状态"""
        if session_id in dialogue_state:
            del dialogue_state[session_id]
            return True
        return False
    
    @staticmethod
    def update_state(session_id, **kwargs):
        """更新对话状态"""
        state = DialogueManager.get_state(session_id)
        for key, value in kwargs.items():
            if key in state['context']:
                state['context'][key] = value
            else:
                state[key] = value
        return state
    
    @staticmethod
    def _extract_topic(message):
        """提取学习主题 - 增强版"""
        message_lower = message.lower().strip()
        
        # 检查是否是后续学习请求，如果是，返回None
        follow_up_keywords = ["后续", "之后", "然后", "接着", "下一步", "学完", "之后学", "接下来", "进阶"]
        if any(word in message_lower for word in follow_up_keywords):
            return None
        
        # 直接匹配单个词的主题
        direct_matches = {
            "python": "Python",
            "java": "Java",
            "c++": "C++",
            "cpp": "C++",
            "c语言": "C语言",
            "前端": "前端开发",
            "后端": "后端开发",
            "机器学习": "机器学习",
            "数据分析": "数据分析",
            "深度学习": "深度学习",
            "算法": "算法",
            "vue": "Vue",
            "react": "React",
            "数据库": "数据库",
            "linux": "Linux",
            "英语": "英语",
            "日语": "日语",
            "法语": "法语",
            "德语": "德语"
        }
        
        if message_lower in direct_matches:
            return direct_matches[message_lower]
        
        # 包含匹配
        topics = {
            "python": "Python",
            "java": "Java",
            "c++": "C++",
            "cpp": "C++",
            "c语言": "C语言",
            "前端": "前端开发",
            "后端": "后端开发",
            "机器学习": "机器学习",
            "数据分析": "数据分析",
            "深度学习": "深度学习",
            "算法": "算法",
            "vue": "Vue",
            "react": "React",
            "数据库": "数据库",
            "linux": "Linux",
            "docker": "Docker",
            "git": "Git",
            "go": "Go语言",
            "rust": "Rust",
            "英语": "英语",
            "日语": "日语",
            "法语": "法语",
            "德语": "德语",
            "运维": "运维",
            "工具": "工具"
        }
        
        for key, value in topics.items():
            if key in message_lower:
                return value
        
        # 尝试从消息中提取主题关键词
        # 处理"我想学习X"、"学习X"等常见句式
        import re
        match = re.search(r'(?:我想学习|学习|想学)\s*(.+?)[。？！]?', message)
        if match:
            topic = match.group(1).strip()
            if topic and not any(word in topic for word in follow_up_keywords):
                return topic
        
        # 如果没有匹配，可能是新主题，用大模型提取
        try:
            prompt = f"从这句话中提取他想学习的技术主题：'{message}'。只返回主题名称，如果没有明确主题返回'未知'。"
            result = get_llm().chat(prompt)
            # 检查结果是否是默认回复
            if result and result != "未知" and "我是一个学习助手" not in result:
                return result
        except:
            pass
        
        return None
    
    @staticmethod
    def _extract_level(message):
        """提取难度级别 - 增强版"""
        message_lower = message.lower()
        
        # 直接匹配难度级别
        if "初级" in message_lower:
            return "初级"
        elif "中级" in message_lower:
            return "中级"
        elif "高级" in message_lower:
            return "高级"
        
        # 初级水平关键词
        beginner_words = [
            "零", "0", "入门", "初学者", "小白", "没学过", "从零", 
            "新手", "刚接触", "不会", "初学", "基础", "beginner",
            "零基础", "无基础", "没有基础", "完全不会"
        ]
        
        # 中级水平关键词
        intermediate_words = [
            "有基础", "学过", "了解", "会一点", "有一点",
            "有一点基础", "有经验", "用过", "熟悉", "intermediate",
            "有一定基础", "有些经验", "不是零基础", "接触过",
            "有一点经验", "会一些", "知道一些"
        ]
        
        # 高级水平关键词
        advanced_words = [
            "深入", "专家", "精通", "熟练", "advanced",
            "多年经验", "资深", "professional", "expert", "大神"
        ]
        
        # 先检查是否是明确的否定（如果明确说"没有基础"）
        if any(word in message_lower for word in ["没有基础", "零基础", "无基础", "完全不会"]):
            return "初级"
        
        # 检查中级水平
        for word in intermediate_words:
            if word in message_lower:
                return "中级"
        
        # 检查高级水平
        for word in advanced_words:
            if word in message_lower:
                return "高级"
        
        # 检查初级水平
        for word in beginner_words:
            if word in message_lower:
                return "初级"
        
        # 如果没有匹配，返回None让系统继续追问
        return None
    
    @staticmethod
    def _extract_goal(message):
        """提取学习目标"""
        message_lower = message.lower()
        
        # 直接匹配学习目标
        if "找工作" in message_lower:
            return "找工作"
        elif "兴趣学习" in message_lower:
            return "兴趣学习"
        elif "项目开发" in message_lower:
            return "项目开发"
        elif "考取证书" in message_lower:
            return "考取证书"
        
        # 找工作相关
        if any(word in message_lower for word in ["工作", "就业", "offer", "求职", "面试", "转行"]):
            return "找工作"
        
        # 兴趣学习相关
        elif any(word in message_lower for word in ["兴趣", "爱好", "玩玩", "有趣", "了解一下"]):
            return "兴趣学习"
        
        # 项目开发相关
        elif any(word in message_lower for word in ["项目", "开发", "做东西", "实战", "写代码"]):
            return "项目开发"
        
        # 考证书相关
        elif any(word in message_lower for word in ["考试", "证书", "认证", "考证"]):
            return "考取证书"
        
        return None
    
    @staticmethod
    def _has_resources(topic):
        """检查是否有相关资源"""
        recommendations = recommender.hybrid_recommend(topic, limit=5)
        return len(recommendations) > 0
    
    @staticmethod
    def _handle_resource_search(topic, subtopic):
        """处理资源搜索请求"""
        try:
            # 使用大模型搜索相关资源
            prompt = f"请为学习{topic}的{subtopic}提供3个高质量的学习资源，包括资源名称、类型（视频/课程/书籍/文章）、难度级别（初级/中级/高级）、URL链接和简短描述。格式为JSON数组，每个资源包含title、type、knowledge_point、difficulty、url、description字段。"
            
            result = get_llm().chat(prompt)
            
            # 检查结果是否是默认回复
            if "我是一个学习助手" in result:
                return f'抱歉，暂时无法为{topic}的{subtopic}搜索资源。你可以尝试学习其他内容，或者稍后再试。'
            
            # 解析大模型返回的JSON
            import json
            try:
                resources = json.loads(result)
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回友好的错误信息
                return f'抱歉，搜索到的资源格式不正确。你可以尝试学习其他内容，或者稍后再试。'
            
            # 验证返回的数据格式
            if not isinstance(resources, list) or len(resources) == 0:
                return f'抱歉，搜索到的资源格式不正确。你可以尝试学习其他内容，或者稍后再试。'
            
            # 添加到数据库
            conn = sqlite3.connect('data/learning.db')
            cursor = conn.cursor()
            
            added_count = 0
            for resource in resources:
                # 检查资源是否包含必要字段
                required_fields = ['title', 'type', 'knowledge_point', 'difficulty', 'url', 'description']
                if all(field in resource for field in required_fields):
                    # 检查是否已存在
                    cursor.execute('SELECT id FROM resources WHERE title = ? AND url = ?', (resource['title'], resource['url']))
                    if not cursor.fetchone():
                        cursor.execute('''
                            INSERT INTO resources (title, type, knowledge_point, difficulty, url, description)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (resource['title'], resource['type'], resource['knowledge_point'], resource['difficulty'], resource['url'], resource['description']))
                        added_count += 1
            
            conn.commit()
            conn.close()
            
            # 重新构建知识图谱
            from knowledge_graph import KnowledgeGraphBuilder
            global kg_builder, knowledge_graph
            kg_builder = KnowledgeGraphBuilder()
            knowledge_graph = kg_builder.graph
            
            return f'成功添加{added_count}个资源到系统中。现在我可以为你生成{topic}的{subtopic}学习方案了。你想了解更多关于{topic}的什么内容？'
        except Exception as e:
            return f'搜索资源失败: {str(e)}'
    
    @staticmethod
    def _is_thanks(message):
        """检查是否是感谢/拒绝类消息"""
        message_lower = message.lower()
        thanks_keywords = [
            "不用", "谢谢", "不需要", "不用了", "算了", "就这样吧", 
            "没事了", "好的谢谢", "ok", "好的", "不了", "不用谢谢",
            "不必了", "就这样", "可以了", "好了", "知道了"
        ]
        
        # 检查是否包含解释关键词，避免将解释请求误识别为感谢/拒绝类消息
        explain_keywords = ["解释", "是什么", "什么意思", "什么是", "介绍", "介绍一下", "能说说", "能解释", "讲解", "说明"]
        if any(keyword in message_lower for keyword in explain_keywords):
            return False
        
        # 只有当消息中包含感谢/拒绝类关键词，且不包含解释关键词时，才识别为感谢/拒绝类消息
        return any(word in message_lower for word in thanks_keywords)
    
    @staticmethod
    def _generate_recommendation(context):
        """生成个性化学习方案 - 根据水平和目标生成最优学习路径"""
        topic = context.get('topic', '编程')
        level = context.get('level', '初级')
        goal = context.get('goal', '学习')
        time_budget = context.get('time_budget', None)
        money_budget = context.get('money_budget', None)
        daily_time = context.get('daily_time', 2)  # 默认每天学习2小时
        time_per_week = daily_time * 7  # 每周学习时间 = 每天学习时间 × 7天
        
        # 计算总学习时间（小时）：时间预算（天） × 每天学习时间（小时）
        if time_budget:
            # 检查用户输入的时间单位
            is_hours = context.get('is_hours', False)
            if not is_hours:
                # 如果是天、月、年单位，转换为总学习时间（小时）：天数 × 每天学习时间
                time_budget = time_budget * daily_time
        
        # 清空得分表，为新对话准备干净的数据
        conn = sqlite3.connect('data/learning.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM recommendation_scores')
        conn.commit()
        conn.close()
        
        # 生成学习方案
        try:
            plan = generate_learning_plan(topic, level, goal, time_budget=time_budget, money_budget=money_budget, time_per_week=time_per_week)
            
            # 构建回复
            response = f"根据你的{level}水平和{goal}的目标，我为你制定了以下学习方案：\n\n"
            response += f"🎯 学习目标：{topic}\n"
            response += f"📊 当前水平：{level}\n"
            response += f"🎨 学习目的：{goal}\n"
            if time_budget:
                response += f"⏱️ 时间预算：{time_budget} 小时\n"
            if money_budget:
                response += f"💰 金钱预算：{money_budget} 元\n"
            response += f"⏱️ 总学习时间：{plan['total_time']} 小时\n"
            response += f"📅 预计需要：{plan['total_weeks']} 周\n"
            response += f"📚 每周建议学习：{plan['time_per_week']} 小时\n\n"
            
            # 添加学习阶段
            response += "## 学习阶段规划\n\n"
            for stage in plan['stages']:
                response += f"### 阶段 {stage['stage']}: {stage['topic']} ({stage['level']})\n"
                response += f"- 学习时间：{stage['learning_time']} 小时\n"
                response += f"- 预计周数：{stage['weeks_needed']} 周\n"
                response += f"- 学习内容：{stage['description']}\n"
                
                if stage['resources']:
                    response += "- 推荐资源：\n"
                    for i, res in enumerate(stage['resources'], 1):
                        response += f"  {i}. [{res['type']}] {res['title']} - {res['url']}\n"
                response += "\n"
            
            # 添加学习效率建议
            efficiency_tips = get_learning_efficiency_tips(topic, goal)
            response += "## 学习效率建议\n\n"
            for tip in efficiency_tips:
                response += f"- {tip}\n"
            
            response += "\n如果你想调整学习计划，或者了解其他技术的学习方案，随时告诉我！"
            return response
        except Exception as e:
            # 打印异常信息，以便调试
            print(f"生成学习方案失败: {str(e)}")
            # 生成失败时的备用方案
            return f"抱歉，暂时无法为{topic}生成学习方案。你想了解其他技术吗？"
    
    @staticmethod
    def _handle_followup(message, context):
        """处理后续对话 - 增强版（包含感谢语处理）"""
        message_lower = message.lower()
        
        # ========== 优先级0：感谢/拒绝类 ==========
        if DialogueManager._is_thanks(message):
            return "好的，如果有需要随时再来问我！祝你学习顺利！"
        
        # ========== 优先级1：解释功能 ==========
        explain_keywords = ["解释", "是什么", "什么意思", "什么是", "介绍", "介绍一下", "能说说", "能解释", "讲解", "说明"]
        if any(word in message_lower for word in explain_keywords):
            # 获取当前主题
            current_topic = context.get('topic', '编程')
            
            # 检查用户想解释哪个术语
            terms_to_explain = []
            
            # 特例：同时解释数据分析和机器学习
            if "数据分析" in message and "机器学习" in message:
                terms_to_explain = ["数据分析和机器学习"]
            else:
                # 常见技术术语列表 - 包含复合术语
                tech_terms = [
                    "Python并发编程", "Python多线程", "Python函数式编程", "Python装饰器",
                    "C++多线程", "C++并发编程", "C++设计模式", "C++性能优化",
                    "Maven", "Spring", "Spring Boot", "Docker", "Git", "GitHub", 
                    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
                    "HTML", "CSS", "JavaScript", "Vue", "React", "Angular",
                    "Python", "Java", "C++", "Go", "Rust",
                    "机器学习", "深度学习", "数据分析", "Web开发", "前端", "后端",
                    "算法", "数据结构", "Linux", "Shell", "Kubernetes"
                ]
                
                # 转换为小写进行匹配，处理特殊字符
                terms_map = {}
                for term in tech_terms:
                    # 处理特殊字符，如"C++" -> "c++"
                    term_lower = term.lower()
                    terms_map[term_lower] = term
                
                # 按长度排序，优先匹配长术语
                sorted_terms = sorted(tech_terms, key=len, reverse=True)
                
                message_lower = message.lower()
                original_message = message
                # 处理用户输入中的特殊字符，确保匹配
                message_lower = message_lower.replace("python", "python")
                message_lower = message_lower.replace("c++", "c++")
                
                # 收集所有匹配的术语
                matched_terms = []
                for term in sorted_terms:
                    term_lower = term.lower()
                    if term_lower in message_lower:
                        matched_terms.append(term)
                        # 从消息中移除已匹配的术语，避免重复匹配
                        message_lower = message_lower.replace(term_lower, "")
                
                # 按原始输入顺序排序
                if matched_terms:
                    # 创建术语到索引的映射
                    term_positions = {}
                    for term in matched_terms:
                        pos = original_message.lower().find(term.lower())
                        if pos != -1:
                            term_positions[term] = pos
                    
                    # 按位置排序
                    matched_terms.sort(key=lambda x: term_positions[x])
                
                # 如果找到多个术语，添加到解释列表
                if matched_terms:
                    terms_to_explain = matched_terms
                else:
                    # 如果没有匹配到，尝试更灵活的匹配
                    if "python" in message_lower:
                        if any(keyword in message_lower for keyword in ["并发", "多线程", "并发编程"]):
                            terms_to_explain = ["Python并发编程"]
                    elif "java" in message_lower:
                        if any(keyword in message_lower for keyword in ["并发", "多线程", "并发编程"]):
                            terms_to_explain = ["Java并发编程"]
                    elif "c++" in message_lower:
                        if any(keyword in message_lower for keyword in ["并发", "多线程", "并发编程"]):
                            terms_to_explain = ["C++多线程"]
                        elif any(keyword in message_lower for keyword in ["设计模式"]):
                            terms_to_explain = ["C++设计模式"]
                    
                    # 如果还是没有匹配，尝试提取消息中可能的术语
                    if not terms_to_explain:
                        # 去除解释关键词，提取核心内容
                        clean_message = message
                        for keyword in explain_keywords:
                            clean_message = clean_message.replace(keyword, "").strip()
                        
                        # 如果还有内容，使用提取的内容
                        if clean_message:
                            terms_to_explain = [clean_message]
                        else:
                            # 如果还是没找到，就用当前主题
                            terms_to_explain = [current_topic]
            
            # 构建解释的响应
            if len(terms_to_explain) == 1:
                term = terms_to_explain[0]
                if term == "数据分析和机器学习":
                    prompt = f"""
                    用户想了解数据分析和机器学习的区别和联系。
                    请用通俗易懂的语言解释：
                    1. 数据分析是什么？主要做什么？举个例子
                    2. 机器学习是什么？主要做什么？举个例子
                    3. 两者的区别和联系
                    4. 如果想学习，建议从哪里开始
                    """
                else:
                    prompt = f"""
                    用户想了解什么是{term}。
                    请用通俗易懂的语言解释，就像对完全不懂的人解释一样：
                    1. {term}是什么（简单定义）
                    2. 它是用来做什么的？（举1-2个生活中的例子）
                    3. 学习它需要什么基础？
                    4. 有什么学习建议？
                    
                    语气要友好热情，用例子帮助理解。
                    """
                result = get_llm().chat(prompt)
                # 检查结果是否是默认回复
                if "我是一个学习助手" in result:
                    return f"抱歉，暂时无法解释{term}。你可以尝试学习其他内容，或者稍后再试。"
                return result
            else:
                # 处理多个术语的解释
                responses = []
                for term in terms_to_explain:
                    prompt = f"""
                    用户想了解什么是{term}。
                    请用通俗易懂的语言解释，就像对完全不懂的人解释一样：
                    1. {term}是什么（简单定义）
                    2. 它是用来做什么的？（举1-2个生活中的例子）
                    3. 学习它需要什么基础？
                    4. 有什么学习建议？
                    
                    语气要友好热情，用例子帮助理解。
                    """
                    explanation = get_llm().chat(prompt)
                    # 检查结果是否是默认回复
                    if "我是一个学习助手" not in explanation:
                        responses.append(f"## {term}\n\n{explanation}")
                
                # 组合所有解释
                if responses:
                    return "\n\n".join(responses)
                else:
                    return "抱歉，暂时无法解释这些术语。你可以尝试学习其他内容，或者稍后再试。"
        
        # ========== 优先级2：后续学什么 ==========
        follow_up_keywords = ["后续", "之后", "然后", "接着", "下一步", "学完", "之后学", "接下来", "进阶"]
        if any(word in message_lower for word in follow_up_keywords):
            topic = context.get('topic', '编程')
            initial_level = context.get('level', '初级')
            
            # 基于初始水平推断当前水平
            current_level = "中级" if initial_level == "初级" else "高级"
            
            # 从知识图谱获取相关进阶主题
            from knowledge_graph import knowledge_graph
            if topic in knowledge_graph:
                related = knowledge_graph[topic].get("related", [])
                if related:
                    response = f"学完{topic}{initial_level}内容后，你已经具备了{current_level}水平，建议你可以学习：\n"
                    for i, r in enumerate(related[:3], 1):
                        response += f"{i}. {r}\n"
                    response += f"\n你想了解哪个方向的详细学习路径吗？或者需要我解释某个方向是什么吗？"
                    return response
            
            return f"学完{topic}{initial_level}内容后，你已经具备了{current_level}水平，可以继续学习进阶内容，或者结合实际项目来巩固。你对哪个方向特别感兴趣？"
        
        # ========== 优先级3：更多资源 ==========
        more_keywords = ["更多", "还有吗", "其他的", "别的", "additional", "extra", "另外"]
        if any(word in message_lower for word in more_keywords):
            topic = context.get('topic', '编程')
            # 获取更多推荐
            recommendations = recommender.hybrid_recommend(topic, limit=10)
            if len(recommendations) > 5:
                response = "这里还有一些其他资源推荐：\n\n"
                for i, rec in enumerate(recommendations[5:8], 1):
                    # 转换链接为可点击的HTML链接
                    link = rec[5] if len(rec) > 5 else ""
                    if link:
                        response += f"{i}. 【{rec[2]}】{rec[1]} - <a href='{link}' target='_blank'>{link}</a>\n"
                    else:
                        response += f"{i}. 【{rec[2]}】{rec[1]}\n"
                return response
            else:
                return "目前就这些资源，你可以先看看这些是否适合。如果想学习其他技术，也可以告诉我。"
        
        # ========== 优先级4：怎么学 ==========
        how_keywords = ["怎么学", "如何学习", "学习方法", "学习路线", "学习路径", "学习计划", "怎么入门"]
        if any(word in message_lower for word in how_keywords):
            topic = context.get('topic', '编程')
            level = context.get('level', '初级')
            
            prompt = f"""
            用户想学习{topic}，当前是{level}水平。
            请给出一条清晰的学习路径建议，包括：
            1. 基础阶段学什么
            2. 进阶阶段学什么
            3. 实践项目建议
            4. 推荐的学习资源类型
            """
            result = get_llm().chat(prompt)
            # 检查结果是否是默认回复
            if "我是一个学习助手" in result:
                return f"抱歉，暂时无法为{topic}提供学习方法建议。你可以尝试学习其他内容，或者稍后再试。"
            return result
        
        # ========== 优先级5：对比 ==========
        compare_keywords = ["对比", "区别", "哪个好", "vs", "versus", "和", "比较"]
        if any(word in message_lower for word in compare_keywords) and ("和" in message_lower or "vs" in message_lower):
            prompt = f"""
            用户问：{message}
            请解释这两个技术的区别和各自的应用场景，帮助用户做出选择。
            """
            result = get_llm().chat(prompt)
            # 检查结果是否是默认回复
            if "我是一个学习助手" in result:
                return "抱歉，暂时无法提供对比信息。你可以尝试学习其他内容，或者稍后再试。"
            return result
        
        # ========== 优先级6：学习时间 ==========
        time_keywords = ["多久", "多长时间", "几个月", "几年", "学习周期"]
        if any(word in message_lower for word in time_keywords):
            topic = context.get('topic', '编程')
            level = context.get('level', '初级')
            
            prompt = f"""
            用户问学习{topic}需要多长时间，当前是{level}水平。
            请给出一个 realistic 的时间估计，包括：
            1. 达到入门水平需要多久
            2. 达到找工作水平需要多久
            3. 影响学习速度的因素
            """
            result = get_llm().chat(prompt)
            # 检查结果是否是默认回复
            if "我是一个学习助手" in result:
                return f"抱歉，暂时无法为{topic}提供学习时间估计。你可以尝试学习其他内容，或者稍后再试。"
            return result
        
        # ========== 优先级7：就业前景 ==========
        job_keywords = ["就业", "找工作", "薪资", "工资", "前景", "岗位", "职位"]
        if any(word in message_lower for word in job_keywords):
            topic = context.get('topic', '编程')
            
            prompt = f"""
            用户问学习{topic}的就业前景。
            请介绍：
            1. 相关职位有哪些
            2. 薪资水平大概多少
            3. 市场需求如何
            4. 发展前景
            """
            result = get_llm().chat(prompt)
            # 检查结果是否是默认回复
            if "我是一个学习助手" in result:
                return f"抱歉，暂时无法为{topic}提供就业前景信息。你可以尝试学习其他内容，或者稍后再试。"
            return result
        
        # ========== 默认回复 ==========
        prompt = f"""
            用户正在学习{context.get('topic', '编程')}，{context.get('level', '初级')}水平。
            用户说：{message}
            
            请生成一个有帮助的回复，可以：
            1. 回答用户的具体问题
            2. 提供学习建议
            3. 保持对话的连贯性，不要重复问已经问过的问题
            """
        result = get_llm().chat(prompt)
        # 检查结果是否是默认回复
        if "我是一个学习助手" in result:
            return "抱歉，我没有理解你的问题。你可以尝试换一种方式表达，或者告诉我你想学习的具体内容。"
        return result
    
    @staticmethod
    def process_message(user_message, state):
        """处理用户消息，返回回复和下一阶段"""
        context = state['context']
        stage = state['stage']
        
        # 首先检查是否是感谢/拒绝类消息（所有阶段都优先处理）
        if DialogueManager._is_thanks(user_message):
            # 重置对话状态，以便用户可以开始新的对话
            state['stage'] = 'initial'
            state['context'] = {}
            return "好的，如果有需要随时再来问我！祝你学习顺利！"
        
        # 检查是否请求资源库
        message_lower = user_message.lower()
        if any(keyword in message_lower for keyword in ['资源库', '有什么资源', '资源', '学习资源', '浏览资源']):
            return "我已经为你准备了学习资源库，你可以点击聊天界面上方的'浏览资源库'按钮来查看所有可用的学习领域。"
        
        # 检查是否是解释请求（所有阶段都优先处理）
        explain_keywords = ["解释", "是什么", "什么意思", "什么是", "介绍", "介绍一下", "能说说", "能解释", "讲解", "说明"]
        if any(keyword in message_lower for keyword in explain_keywords):
            # 直接调用处理后续对话的方法，处理解释请求
            return DialogueManager._handle_followup(user_message, context)
        
        # 根据当前阶段处理
        if stage == 'initial':
            # 第一次对话：直接尝试提取主题
            topic = DialogueManager._extract_topic(user_message)
            if topic:
                # 先检查是否有相关资源
                if not DialogueManager._has_resources(topic):
                    context['topic'] = topic
                    state['stage'] = 'asking_subtopic'
                    return f"暂时没有找到{topic}的相关资源。你想学习{topic}的什么具体内容？我可以为你搜索相关资源。"
                else:
                    context['topic'] = topic
                    state['stage'] = 'asking_level'
                    # 根据学习主题选择合适的问话方式
                    # 编程相关主题
                    programming_topics = ['Python', 'Java', 'C++', '前端开发', '后端开发', '机器学习', '数据分析', 'Vue', 'React', '数据库', 'Linux', 'Docker', 'Git', 'Go语言', 'Rust']
                    # 语言学习相关主题
                    language_topics = ['英语', '日语', '法语', '德语']
                    # 其他主题
                    other_topics = ['数学', '物理学', '化学', '生物学', '历史', '地理', '经济学', '哲学', '艺术']
                    
                    if any(programming in topic for programming in programming_topics):
                        return f"好的，你想学{context['topic']}。你是编程初学者还是有一定编程基础？"
                    elif any(language in topic for language in language_topics):
                        return f"好的，你想学{context['topic']}。你是语言初学者还是有一定语言基础？"
                    else:
                        return f"好的，你想学{context['topic']}。你是初学者还是有一定基础？"
            else:
                state['stage'] = 'asking_topic'
                return "我没太明白你想学什么。能具体说一下吗？比如：Python、Java、前端开发等"
        
        # 处理子主题询问
        elif stage == 'asking_subtopic':
            # 检查用户是否输入了新的主题
            new_topic = DialogueManager._extract_topic(user_message)
            if new_topic and new_topic != context.get('topic'):
                # 重置对话状态，开始新的对话
                context['topic'] = new_topic
                # 先检查是否有相关资源
                if not DialogueManager._has_resources(new_topic):
                    state['stage'] = 'asking_subtopic'
                    return f"暂时没有找到{new_topic}的相关资源。你想学习{new_topic}的什么具体内容？我可以为你搜索相关资源。"
                else:
                    state['stage'] = 'asking_level'
                    # 根据学习主题选择合适的问话方式
                    # 编程相关主题
                    programming_topics = ['Python', 'Java', 'C++', '前端开发', '后端开发', '机器学习', '数据分析', 'Vue', 'React', '数据库', 'Linux', 'Docker', 'Git', 'Go语言', 'Rust']
                    # 语言学习相关主题
                    language_topics = ['英语', '日语', '法语', '德语']
                    # 其他主题
                    other_topics = ['数学', '物理学', '化学', '生物学', '历史', '地理', '经济学', '哲学', '艺术']
                    
                    if any(programming in new_topic for programming in programming_topics):
                        return f"好的，你想学{new_topic}。你是编程初学者还是有一定编程基础？"
                    elif any(language in new_topic for language in language_topics):
                        return f"好的，你想学{new_topic}。你是语言初学者还是有一定语言基础？"
                    else:
                        return f"好的，你想学{new_topic}。你是初学者还是有一定基础？"
            
            subtopic = user_message.strip()
            context['subtopic'] = subtopic
            # 搜索并添加资源
            result = DialogueManager._handle_resource_search(context['topic'], subtopic)
            state['stage'] = 'asking_level'
            return result
        
        elif stage == 'asking_topic':
            # 提取主题
            topic = DialogueManager._extract_topic(user_message)
            if topic:
                # 先检查是否有相关资源
                if not DialogueManager._has_resources(topic):
                    context['topic'] = topic
                    return f"抱歉，暂时没有找到{topic}的相关资源。你想学习其他内容吗？"
                else:
                    context['topic'] = topic
                    state['stage'] = 'asking_level'
                    # 根据学习主题选择合适的问话方式
                    # 编程相关主题
                    programming_topics = ['Python', 'Java', 'C++', '前端开发', '后端开发', '机器学习', '数据分析', 'Vue', 'React', '数据库', 'Linux', 'Docker', 'Git', 'Go语言', 'Rust']
                    # 语言学习相关主题
                    language_topics = ['英语', '日语', '法语', '德语']
                    # 其他主题
                    other_topics = ['数学', '物理学', '化学', '生物学', '历史', '地理', '经济学', '哲学', '艺术']
                    
                    if any(programming in topic for programming in programming_topics):
                        return f"好的，你想学{context['topic']}。你是编程初学者还是有一定编程基础？"
                    elif any(language in topic for language in language_topics):
                        return f"好的，你想学{context['topic']}。你是语言初学者还是有一定语言基础？"
                    else:
                        return f"好的，你想学{context['topic']}。你是初学者还是有一定基础？"
            else:
                return "我没太明白你想学什么。能具体说一下吗？比如：Python、Java、前端开发等"
        
        elif stage == 'asking_level':
            # 先尝试提取难度级别
            level = DialogueManager._extract_level(user_message)
            
            if level:
                context['level'] = level
                state['stage'] = 'asking_goal'
                return f"你主要想达到什么学习目标？比如：找工作、兴趣学习、项目开发等"
            else:
                # 检查用户是否输入了新的主题
                new_topic = DialogueManager._extract_topic(user_message)
                if new_topic and new_topic != context.get('topic'):
                    # 重置对话状态，开始新的对话
                    context['topic'] = new_topic
                    # 先检查是否有相关资源
                    if not DialogueManager._has_resources(new_topic):
                        state['stage'] = 'asking_subtopic'
                        return f"暂时没有找到{new_topic}的相关资源。你想学习{new_topic}的什么具体内容？我可以为你搜索相关资源。"
                    else:
                        state['stage'] = 'asking_level'
                        # 根据学习主题选择合适的问话方式
                        # 编程相关主题
                        programming_topics = ['Python', 'Java', 'C++', '前端开发', '后端开发', '机器学习', '数据分析', 'Vue', 'React', '数据库', 'Linux', 'Docker', 'Git', 'Go语言', 'Rust']
                        # 语言学习相关主题
                        language_topics = ['英语', '日语', '法语', '德语']
                        # 其他主题
                        other_topics = ['数学', '物理学', '化学', '生物学', '历史', '地理', '经济学', '哲学', '艺术']
                        
                        if any(programming in new_topic for programming in programming_topics):
                            return f"好的，你想学{new_topic}。你是编程初学者还是有一定编程基础？"
                        elif any(language in new_topic for language in language_topics):
                            return f"好的，你想学{new_topic}。你是语言初学者还是有一定语言基础？"
                        else:
                            return f"好的，你想学{new_topic}。你是初学者还是有一定基础？"
                
                # 如果不是新主题，继续追问基础水平
                # 根据学习主题选择合适的问话方式
                topic = context.get('topic', '')
                # 编程相关主题
                programming_topics = ['Python', 'Java', 'C++', '前端开发', '后端开发', '机器学习', '数据分析', 'Vue', 'React', '数据库', 'Linux', 'Docker', 'Git', 'Go语言', 'Rust']
                # 语言学习相关主题
                language_topics = ['英语', '日语', '法语', '德语']
                # 其他主题
                other_topics = ['数学', '物理学', '化学', '生物学', '历史', '地理', '经济学', '哲学', '艺术']
                
                if any(programming in topic for programming in programming_topics):
                    return "能告诉我你的编程基础水平吗？是零基础，还是有一定编程经验？"
                elif any(language in topic for language in language_topics):
                    return "能告诉我你的语言基础水平吗？是零基础，还是有一定基础？"
                else:
                    return "能告诉我你的基础水平吗？是零基础，还是有一定基础？"
        
        elif stage == 'asking_goal':
            # 提取目标
            goal = DialogueManager._extract_goal(user_message)
            if goal:
                context['goal'] = goal
                state['stage'] = 'asking_time_budget'
                return "你打算在多长时间内达到学习目的的水平？"
            else:
                return "能告诉我你的学习目标吗？比如想找相关工作，还是纯兴趣学习？"
        
        elif stage == 'asking_time_budget':
            # 提取时间预算，支持小时、天、月、年等单位
            try:
                message = user_message.strip().lower()
                time_budget = 0
                is_hours = False
                
                if '小时' in message:
                    # 处理小时单位
                    time_str = message.replace('小时', '').strip()
                    time_budget = float(time_str)
                    is_hours = True
                    if time_budget <= 0:
                        return "请输入有效的学习时间"
                elif '天' in message:
                    # 处理天单位
                    time_str = message.replace('天', '').strip()
                    days = float(time_str)
                    if days > 0 and days <= 365:
                        # 存储天数
                        time_budget = days
                elif '月' in message:
                    # 处理月单位
                    time_str = message.replace('个月', '').replace('月', '').strip()
                    months = float(time_str)
                    if months > 0 and months <= 12:
                        # 转换为天数（每月按28天计算）
                        time_budget = months * 28
                elif '年' in message:
                    # 处理年单位
                    time_str = message.replace('年', '').strip()
                    years = float(time_str)
                    if years > 0 and years <= 5:
                        # 转换为天数（每年按365天计算）
                        time_budget = years * 365
                else:
                    # 尝试直接解析为数字（默认小时）
                    time_budget = float(message)
                    is_hours = True
                    if time_budget <= 0:
                        return "请输入有效的学习时间"
                
                # 检查时间预算是否有效
                if time_budget > 0:
                    # 存储时间预算和单位信息
                    context['time_budget'] = time_budget
                    context['is_hours'] = is_hours
                    state['stage'] = 'asking_daily_time'
                    return "你每天打算学习多长时间？"
                else:
                    return "请输入有效的学习时间"
            except ValueError:
                return "请输入有效的学习时间"
        
        elif stage == 'asking_daily_time':
            # 提取每天学习时间
            try:
                message = user_message.strip().lower()
                if '小时' in message:
                    time_str = message.replace('小时', '').strip()
                    daily_time = float(time_str)
                else:
                    daily_time = float(message)
                if daily_time > 0 and daily_time <= 12:
                    context['daily_time'] = daily_time
                    state['stage'] = 'asking_money_budget'
                    return "你学习所消耗的金钱预算是多少？"
                else:
                    return "请输入有效的每天学习时间"
            except ValueError:
                return "请输入有效的每天学习时间"
        elif stage == 'asking_money_budget':
            # 提取金钱预算，支持带有"元"字的输入
            try:
                message = user_message.strip().lower()
                # 移除"元"字
                money_str = message.replace('元', '').strip()
                money_budget = float(money_str)
                if money_budget >= 0:
                    context['money_budget'] = money_budget
                    state['stage'] = 'recommending'
                    # 进入推荐阶段
                    return DialogueManager._generate_recommendation(context)
                else:
                    return "请输入有效的金钱预算"
            except ValueError:
                return "请输入有效的金钱预算"
        
        elif stage == 'recommending':
            # 检查是否是解释类问题
            explain_keywords = ["解释", "是什么", "什么意思", "什么是", "介绍", "介绍一下", "能说说", "能解释", "讲解", "说明"]
            is_explain = any(word in user_message.lower() for word in explain_keywords)
            
            if is_explain:
                # 如果是解释类问题，直接进入_handle_followup
                return DialogueManager._handle_followup(user_message, context)
            
            # 检查是否想学新东西
            topic = DialogueManager._extract_topic(user_message)
            if topic and topic != context.get('topic'):
                # 先检查新主题是否有资源
                if not DialogueManager._has_resources(topic):
                    context['topic'] = topic
                    return f"抱歉，暂时没有找到{topic}的相关资源。你想学习其他内容吗？"
                else:
                    context['topic'] = topic
                    context['level'] = None
                    context['goal'] = None
                    state['stage'] = 'asking_level'
                    return f"好的，你想学{context['topic']}。你是初学者还是有一定基础？"
            else:
                # 继续当前话题的讨论
                return DialogueManager._handle_followup(user_message, context)
        
        return "我明白你的意思了，能说得更具体一些吗？"

@app.route('/')
def index():
    """首页 - 聊天界面（需要登录）"""
    # 检查用户是否登录
    if 'user_id' not in session or 'username' not in session:
        return redirect(url_for('login_page'))
    
    # 清空得分表，为新对话准备干净的数据
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recommendation_scores')
    # 重置自增ID计数器
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="recommendation_scores"')
    conn.commit()
    conn.close()
    
    return render_template('index.html')

@app.route('/login')
def login_page():
    """登录页面"""
    if 'user_id' in session and 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/chat', methods=['POST'])
def chat():
    """处理对话 - 实现多轮追问（需要登录）"""
    if 'user_id' not in session or 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
        
    data = request.json
    user_message = data.get('message', '')
    user_id = session.get('user_id', 'unknown')
    
    # 获取对话状态
    state = DialogueManager.get_state(user_id)
    
    # 记录用户消息
    state['history'].append({'role': 'user', 'content': user_message})
    
    # 处理消息
    response = DialogueManager.process_message(user_message, state)
    
    # 记录机器人回复
    state['history'].append({'role': 'assistant', 'content': response})
    
    # 保存到数据库
    save_dialogue(user_id, user_message, response)
    
    return jsonify({
        'response': response,
        'stage': state['stage']
    })

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """重置对话 - 新对话功能（需要登录）"""
    if 'user_id' not in session or 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
        
    user_id = session.get('user_id', 'unknown')
    
    # 清空对话状态
    if user_id in dialogue_state:
        del dialogue_state[user_id]
        print(f"用户 {user_id} 的对话已重置")
    
    # 清空对话历史表
    clear_user_dialogues()
    
    session.pop('_flashes', None)
    
    return jsonify({'status': 'success', 'message': '对话已重置'})

@app.route('/history', methods=['GET'])
def get_history():
    """获取对话历史（需要登录）"""
    if 'user_id' not in session or 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
        
    user_id = session.get('user_id', 'unknown')
    
    if user_id not in dialogue_state:
        return jsonify({'history': []})
    
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_message, bot_response, timestamp 
        FROM dialogues 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''', (user_id,))
    history = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'history': [{'user': h[0], 'bot': h[1], 'time': h[2]} for h in history]
    })

@app.route('/kg-data', methods=['GET'])
def get_kg_data():
    """返回知识图谱数据给前端（需要登录）"""
    if 'user_id' not in session or 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
        
    from knowledge_graph import knowledge_graph
    return jsonify(knowledge_graph)

@app.route('/domains', methods=['GET'])
def get_domains():
    """获取所有可用的学习领域（需要登录）"""
    if 'user_id' not in session or 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
        
    from knowledge_graph import knowledge_graph
    domains = list(knowledge_graph.keys())
    return jsonify({'domains': domains})

@app.route('/search-resource', methods=['POST'])
def search_resource():
    """使用大模型搜索资源并添加到数据库（需要登录）"""
    if 'user_id' not in session or 'username' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
        
    data = request.json
    topic = data.get('topic', '')
    subtopic = data.get('subtopic', '')
    
    if not topic:
        return jsonify({'status': 'error', 'message': '缺少主题参数'})
    
    try:
        # 使用大模型搜索相关资源
        prompt = f"请为学习{topic}的{subtopic}提供3个高质量的学习资源，包括资源名称、类型（视频/课程/书籍/文章）、难度级别（初级/中级/高级）、URL链接和简短描述。格式为JSON数组，每个资源包含title、type、knowledge_point、difficulty、url、description字段。"
        
        result = get_llm().chat(prompt)
        
        # 检查结果是否是默认回复
        if "我是一个学习助手" in result:
            return jsonify({'status': 'error', 'message': '搜索资源失败：无法获取有效的资源信息'})
        
        # 解析大模型返回的JSON
        import json
        resources = json.loads(result)
        
        # 验证返回的数据格式
        if not isinstance(resources, list) or len(resources) == 0:
            return jsonify({'status': 'error', 'message': '搜索资源失败：返回的数据格式不正确'})
        
        # 添加到数据库
        conn = sqlite3.connect('data/learning.db')
        cursor = conn.cursor()
        
        added_count = 0
        for resource in resources:
            # 检查资源是否包含必要字段
            required_fields = ['title', 'type', 'knowledge_point', 'difficulty', 'url', 'description']
            if all(field in resource for field in required_fields):
                # 检查是否已存在
                cursor.execute('SELECT id FROM resources WHERE title = ? AND url = ?', (resource['title'], resource['url']))
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO resources (title, type, knowledge_point, difficulty, url, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (resource['title'], resource['type'], resource['knowledge_point'], resource['difficulty'], resource['url'], resource['description']))
                    added_count += 1
        
        conn.commit()
        conn.close()
        
        # 重新构建知识图谱
        from knowledge_graph import KnowledgeGraphBuilder
        global kg_builder, knowledge_graph
        kg_builder = KnowledgeGraphBuilder()
        knowledge_graph = kg_builder.graph
        
        return jsonify({'status': 'success', 'message': f'成功添加{added_count}个资源', 'resources': resources})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'搜索资源失败: {str(e)}'})

@app.route('/@vite/client')
def vite_client():
    """处理Vite客户端请求，避免404错误"""
    # 返回一个空的响应，状态码204表示无内容
    return '', 204

@app.route('/favicon.ico')
def favicon():
    """处理favicon.ico请求，避免404错误"""
    # 返回一个空的响应，状态码204表示无内容
    return '', 204

# 用户认证相关路由
@app.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'success': False, 'message': '请填写所有必填字段'}), 400
        
        # 验证用户名和邮箱格式
        if len(username) < 3:
            return jsonify({'success': False, 'message': '用户名至少3个字符'}), 400
        
        if '@' not in email:
            return jsonify({'success': False, 'message': '请输入有效的邮箱地址'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密码至少6个字符'}), 400
        
        # 调用注册函数
        success, message = register_user(username, email, password)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'success': False, 'message': '请填写邮箱和密码'}), 400
        
        # 调用验证函数
        success, result = verify_user(email, password)
        
        if success:
            # 登录成功，设置session
            user_id, username = result
            session['user_id'] = user_id
            session['username'] = username
            session['email'] = email
            
            return jsonify({
                'success': True, 
                'message': '登录成功',
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email
                }
            }), 200
        else:
            return jsonify({'success': False, 'message': result}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        # 清空对话状态
        user_id = session.get('user_id', 'unknown')
        if user_id in dialogue_state:
            del dialogue_state[user_id]
        
        # 清空对话历史表
        clear_user_dialogues()
        
        # 清空推荐得分表
        conn = sqlite3.connect('data/learning.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM recommendation_scores')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="recommendation_scores"')
        conn.commit()
        conn.close()
        
        # 清除session
        session.clear()
        return jsonify({'success': True, 'message': '登出成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'登出失败: {str(e)}'}), 500

@app.route('/profile', methods=['GET'])
def profile():
    """获取用户个人资料"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '未登录'}), 401
        
        user_id = session['user_id']
        username = session['username']
        email = session['email']
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'username': username,
                'email': email
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取个人资料失败: {str(e)}'}), 500

if __name__ == '__main__':
    # 清空对话状态
    dialogue_state.clear()
    app.run(debug=True, port=7777)