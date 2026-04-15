# recommender.py
"""
推荐引擎 - 融合多种推荐策略
对应董永峰论文的"混合推荐算法"
"""
import sqlite3
from knowledge_graph import get_related_knowledge, get_resources_by_kg

class Recommender:
    def __init__(self, db_path='data/learning.db'):
        self.db_path = db_path
    
    def content_based_recommend(self, knowledge_points, limit=5):
        """
        基于内容的推荐
        根据知识点匹配资源
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        all_resources = []
        for kp in knowledge_points:
            cursor.execute('''
                SELECT * FROM resources 
                WHERE knowledge_point LIKE ? OR description LIKE ?
                LIMIT ?
            ''', ('%' + kp + '%', '%' + kp + '%', limit))
            resources = cursor.fetchall()
            all_resources.extend(resources)
        
        conn.close()
        # 去重
        seen = set()
        unique_resources = []
        for r in all_resources:
            if r[0] not in seen:
                seen.add(r[0])
                unique_resources.append(r)
        
        return unique_resources[:limit]
    
    def _get_exact_match_resources(self, knowledge_point, limit=5):
        """获取精确匹配知识点的资源"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM resources WHERE knowledge_point = ? LIMIT ?
        ''', (knowledge_point, limit))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def kg_based_recommend(self, knowledge_point, limit=5):
        """
        基于知识图谱的推荐
        对应李春英论文方法
        """
        # 获取相关知识点的资源ID
        resource_ids = get_resources_by_kg(knowledge_point)
        
        if not resource_ids:
            return []
        
        # 从数据库查询具体资源
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 限制返回数量
        ids_to_query = resource_ids[:limit]
        placeholders = ','.join(['?'] * len(ids_to_query))
        cursor.execute(f'''
            SELECT * FROM resources WHERE id IN ({placeholders})
        ''', ids_to_query)
        
        resources = cursor.fetchall()
        conn.close()
        return resources[:limit]
    
    def _extract_keywords(self, text):
        """增强版关键词提取"""
        common_kps = {
            "python": "Python",
            "java": "Java",
            "c++": "C++",
            "c语言": "C语言",
            "c#": "C#",
            "前端": "前端开发",
            "后端": "后端开发",
            "机器学习": "机器学习",
            "数据分析": "数据分析",
            "深度学习": "深度学习",
            "vue": "Vue",
            "react": "React",
            "数据库": "数据库",
            "算法": "算法",
            "linux": "Linux",
            "docker": "Docker",
            "git": "Git",
            "android": "Android",
            "ios": "iOS",
            "运维": "运维"
        }
        
        text_lower = text.lower()
        found = []
        for key, value in common_kps.items():
            if key in text_lower:
                found.append(value)
        return found
    
    def hybrid_recommend(self, user_input, limit=10):
        """
        优化版混合推荐策略 - 返回更多资源供后续筛选
        limit: 返回的最大资源数量
        """
        # 1. 提取知识点
        knowledge_points = self._extract_keywords(user_input)
        
        # 如果没有提取到知识点，尝试从输入中直接获取
        if not knowledge_points:
            common_tech = ["c++", "c语言", "java", "python", "javascript", "html", "css", 
                          "前端", "后端", "数据库", "机器学习", "数据分析", "android", "ios"]
            for tech in common_tech:
                if tech in user_input.lower():
                    if tech == "c++":
                        knowledge_points = ["C++"]
                    elif tech == "c语言":
                        knowledge_points = ["C语言"]
                    else:
                        knowledge_points = [tech.capitalize()]
                    break
        
        # 如果还是没有，返回空列表
        if not knowledge_points:
            return []
        
        # 2. 先获取精确匹配的资源
        main_kp = knowledge_points[0]
        exact_recs = self._get_exact_match_resources(main_kp, limit=8)
        
        # 3. 再获取模糊匹配的资源（返回更多，供筛选）
        content_recs = self.content_based_recommend([main_kp], limit=15)
        
        # 4. 合并去重
        seen = set()
        final_recs = []
        
        # 先添加精确匹配的资源
        for rec in exact_recs:
            if rec[0] not in seen:
                seen.add(rec[0])
                final_recs.append(rec)
        
        # 再添加模糊匹配的资源
        for rec in content_recs:
            if rec[0] not in seen and len(final_recs) < limit:
                # 如果是Python，避免推荐太多数据分析/机器学习的内容
                if main_kp == "Python" and rec[2] in ["数据分析", "机器学习", "深度学习"]:
                    if len([r for r in final_recs if r[2] == "Python"]) < 3:
                        continue
                seen.add(rec[0])
                final_recs.append(rec)
        
        return final_recs[:limit]

# 测试代码
if __name__ == '__main__':
    recommender = Recommender()
    
    print("="*50)
    print("测试推荐功能")
    print("="*50)
    
    test_inputs = ["我想学Python", "推荐机器学习", "前端开发", "C++", "Java"]
    
    for test in test_inputs:
        print(f"\n用户输入: {test}")
        results = recommender.hybrid_recommend(test, limit=10)
        print(f"推荐结果数: {len(results)}")
        for i, r in enumerate(results, 1):
            print(f"  {i}. 【{r[2]}】{r[1]} - {r[3]}")