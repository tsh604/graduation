# llm_service.py
"""
智谱AI大模型服务 - 使用GLM-4-Flash模型
对应黎盈盈论文的"大模型驱动对话"
"""
import os
import re
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

class ZhipuLLMService:
    """使用智谱AI大模型"""
    
    def __init__(self):
        # 从.env文件读取API Key
        self.api_key = os.getenv('ZHIPUAI_API_KEY')
        
        if not self.api_key:
            print("⚠️ 未设置API Key，使用简化版")
            self.use_simple = True
        else:
            # 初始化智谱AI客户端
            self.client = ZhipuAI(api_key=self.api_key)
            self.use_simple = False
            print("✅ 智谱AI服务初始化成功")
    
    def _clean_markdown(self, text):
        """清理Markdown标记，让显示更友好"""
        if not text:
            return text
        
        # 去掉加粗标记 **text**
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # 去掉斜体标记 *text*（但要小心不要替换列表项）
        # 先把独立的*替换掉
        text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
        
        # 将列表项开头的 * 或 - 改为 •
        text = re.sub(r'^\s*\*\s+', '  • ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*-\s+', '  • ', text, flags=re.MULTILINE)
        
        # 去掉数字列表的格式（保留数字）
        text = re.sub(r'^\s*(\d+)\.\s+', r'  \1. ', text, flags=re.MULTILINE)
        
        # 去掉标题标记
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # 去掉代码块标记
        text = text.replace('```', '')
        
        return text.strip()
    
    def chat(self, prompt, system_prompt=None):
        """调用大模型进行对话"""
        if self.use_simple:
            return self._simple_chat(prompt)
        
        try:
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            # 调用智谱AI的GLM-4-Flash模型（免费版）
            response = self.client.chat.completions.create(
                model='glm-4-flash',  # 免费模型
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # 清理Markdown标记
            content = self._clean_markdown(content)
            
            return content
            
        except Exception as e:
            print(f"大模型调用错误: {e}")
            return self._simple_chat(prompt)
    
    def extract_intent(self, user_input):
        """用大模型提取意图"""
        if self.use_simple:
            return self._simple_extract_intent(user_input)
        
        prompt = f"""
        分析用户的输入，判断他的意图属于哪一类：
        1. 想学习新知识（包含：想学、入门、教程、怎么学等）
        2. 对某个知识点有疑问（包含：什么、怎么、如何、为什么等）
        3. 想要资源推荐（包含：推荐、有什么、哪些等）
        4. 闲聊或其他
        
        用户输入：{user_input}
        
        只返回数字（1、2、3或4）。
        """
        result = self.chat(prompt)
        try:
            return int(result.strip())
        except:
            return 3
    
    def extract_knowledge_points(self, user_input):
        """用大模型提取知识点"""
        if self.use_simple:
            return self._simple_extract_knowledge(user_input)
        
        prompt = f"""
        从用户的输入中提取他想要学习的知识点或技术领域。
        如果有多个，用逗号分隔。
        如果没有明确的知识点，返回"通用编程"。
        
        用户输入：{user_input}
        """
        result = self.chat(prompt)
        return [kp.strip() for kp in result.split(',') if kp.strip()]
    
    def _simple_chat(self, prompt):
        """简化版回复（当API不可用时使用）"""
        prompt_lower = prompt.lower()
        if "python" in prompt_lower:
            return "Python是一门非常适合初学者的编程语言。它的语法简洁，应用广泛，在数据分析、Web开发、人工智能等领域都有大量应用。"
        elif "java" in prompt_lower:
            return "Java是一门经典的编程语言，在企业级开发中应用广泛。学习Java需要掌握面向对象编程思想、JVM原理等。"
        elif "机器学习" in prompt_lower or "machine learning" in prompt_lower:
            return "机器学习是人工智能的核心领域。建议先从基础的线性回归、分类算法学起，然后逐步深入学习。"
        elif "前端" in prompt_lower or "vue" in prompt_lower or "react" in prompt_lower:
            return "前端开发主要学习HTML、CSS和JavaScript。现在流行的框架有Vue、React等。"
        elif "数据分析" in prompt_lower:
            return "数据分析需要掌握Python、pandas、numpy等工具，还需要统计学知识。"
        elif "谢谢" in prompt_lower or "thank" in prompt_lower:
            return "不客气！很高兴能帮到你。如果还有其他问题，随时问我！"
        else:
            return "我理解你想学习这方面的知识。让我为你推荐一些学习资源。"
    
    def _simple_extract_intent(self, user_input):
        """简化版意图识别"""
        user_input = user_input.lower()
        if any(word in user_input for word in ["想学", "学习", "入门", "教程", "怎么学"]):
            return 1
        elif any(word in user_input for word in ["推荐", "有什么", "哪些"]):
            return 3
        elif any(word in user_input for word in ["什么", "怎么", "如何", "为什么", "?"]):
            return 2
        else:
            return 4
    
    def _simple_extract_knowledge(self, user_input):
        """简化版知识点提取"""
        common_kps = ["python", "java", "前端", "机器学习", "数据分析", 
                     "深度学习", "vue", "react", "数据库", "算法", 
                     "linux", "docker", "git"]
        text_lower = user_input.lower()
        found = []
        for kp in common_kps:
            if kp in text_lower:
                found.append(kp)
        return found if found else ["编程"]

if __name__ == '__main__':
    print("="*50)
    print("测试智谱AI大模型服务")
    print("="*50)
    
    llm = ZhipuLLMService()
    
    test_inputs = [
        "我想学Python",
        "推荐机器学习的资源",
        "前端怎么入门",
        "Java和Python哪个好",
        "谢谢"
    ]
    
    for test in test_inputs:
        print(f"\n用户输入: {test}")
        print(f"回复: {llm.chat(test)}")