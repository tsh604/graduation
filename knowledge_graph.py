# knowledge_graph.py
"""
知识图谱 - 根据数据库动态构建
"""
import sqlite3

class KnowledgeGraphBuilder:
    def __init__(self, db_path='data/learning.db'):
        self.db_path = db_path
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """从数据库构建知识图谱"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取所有知识点
        cursor.execute('SELECT DISTINCT knowledge_point FROM resources')
        topics = [row[0] for row in cursor.fetchall()]
        
        # 构建简单的关系
        graph = {}
        
        # 定义一些常见的关系（可以根据实际数据扩展）
        relations = {
            "Python": ["数据分析", "机器学习"],
            "Java": ["Spring Boot"],
            "前端开发": ["Vue", "React", "JavaScript"],
            "机器学习": ["深度学习", "数据分析"],
            "数据分析": ["Python", "机器学习"],
            "C++": ["系统编程"],
            "算法": ["数据结构"],
            "数学": ["线性代数", "微积分", "概率论", "统计学"],
            "线性代数": ["数学", "微积分"],
            "微积分": ["数学", "线性代数"],
            "概率论": ["数学", "统计学"],
            "统计学": ["数学", "概率论"],
            "物理学": ["数学"],
            "化学": ["数学", "物理学"],
            "生物学": ["化学", "物理学"],
            "经济学": ["数学", "统计学"],
            "哲学": ["历史"],
            "历史": ["地理"],
            "地理": ["历史"],
            "艺术": ["历史"]
        }
        
        # 定义学习依赖关系（前置知识）
        prerequisites = {
            "乘法": ["加法"],
            "除法": ["乘法", "减法"],
            "代数": ["四则运算"],
            "几何": ["代数"],
            "Python": ["编程基础"],
            "Java": ["编程基础"],
            "C++": ["编程基础"],
            "数据分析": ["Python", "统计学"],
            "机器学习": ["数据分析", "线性代数", "微积分"],
            "深度学习": ["机器学习"],
            "前端开发": ["HTML", "CSS", "JavaScript"],
            "Vue": ["JavaScript"],
            "React": ["JavaScript"],
            "Spring Boot": ["Java"],
            "算法": ["数据结构"],
            "系统编程": ["C++"],
            "线性代数": ["数学"],
            "微积分": ["数学"],
            "概率论": ["数学"],
            "统计学": ["数学", "概率论"],
            "离散数学": ["数学"],
            "数论": ["数学", "离散数学"],
            "几何学": ["数学"],
            "拓扑学": ["数学", "几何学"],
            "抽象代数": ["数学", "线性代数"],
            "微分方程": ["数学", "微积分"],
            "复分析": ["数学", "微积分"],
            "实分析": ["数学", "微积分"],
            "数值分析": ["数学", "线性代数", "微积分"],
            "数学建模": ["数学", "线性代数", "微积分", "统计学"],
            "物理学": ["数学"],
            "力学": ["物理学", "数学"],
            "电磁学": ["物理学", "数学"],
            "热学": ["物理学", "数学"],
            "光学": ["物理学", "数学"],
            "量子力学": ["物理学", "数学", "线性代数", "微积分"],
            "化学": ["数学", "物理学"],
            "有机化学": ["化学"],
            "无机化学": ["化学"],
            "物理化学": ["化学", "物理学", "数学"],
            "生物学": ["化学", "物理学"],
            "细胞生物学": ["生物学"],
            "分子生物学": ["生物学", "化学"],
            "遗传学": ["生物学", "化学"],
            "经济学": ["数学", "统计学"],
            "微观经济学": ["经济学"],
            "宏观经济学": ["经济学"],
            "金融学": ["经济学", "数学", "统计学"],
            "哲学": ["历史"],
            "西方哲学": ["哲学"],
            "中国哲学": ["哲学"],
            "历史": ["地理"],
            "古代史": ["历史"],
            "近代史": ["历史", "古代史"],
            "地理": ["历史"],
            "自然地理": ["地理"],
            "人文地理": ["地理"],
            "艺术": ["历史"],
            "艺术史": ["艺术"],
            "音乐": ["艺术"],
            "绘画": ["艺术"],
            "雕塑": ["艺术"]
        }
        
        for topic in topics:
            graph[topic] = {
                "related": relations.get(topic, []),
                "prerequisites": prerequisites.get(topic, []),
                "resources": self._get_resource_ids(topic)
            }
        
        conn.close()
        return graph
    
    def _get_resource_ids(self, topic):
        """获取某知识点的资源ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM resources WHERE knowledge_point = ? LIMIT 5', (topic,))
        ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ids
    
    def get_related_knowledge(self, knowledge_point):
        """获取相关知识点的推荐"""
        if knowledge_point in self.graph:
            return self.graph[knowledge_point].get("related", [])
        return []
    
    def get_resources_by_kg(self, knowledge_point):
        """根据知识图谱获取资源ID列表"""
        if knowledge_point in self.graph:
            return self.graph[knowledge_point].get("resources", [])
        return []

# 创建全局实例
kg_builder = KnowledgeGraphBuilder()
knowledge_graph = kg_builder.graph
get_related_knowledge = kg_builder.get_related_knowledge
get_resources_by_kg = kg_builder.get_resources_by_kg

if __name__ == '__main__':
    print("="*50)
    print("知识图谱构建完成")
    print("="*50)
    for topic, data in knowledge_graph.items():
        print(f"\n{topic}:")
        print(f"  相关: {data['related']}")
        print(f"  资源数: {len(data['resources'])}")