# path_planner.py
"""
学习路径规划器 - 基于知识图谱和用户目标生成最优学习方案
"""
from knowledge_graph import knowledge_graph
import sqlite3

class PathPlanner:
    def __init__(self, db_path='data/learning.db'):
        self.db_path = db_path
        self.kg = knowledge_graph
    
    def _get_resources_by_topic(self, topic, level=None, limit=3, original_topic=None, used_resource_ids=None):
        """根据主题和难度获取资源
        
        Args:
            topic: 当前学习主题
            level: 难度级别
            limit: 返回资源数量限制
            original_topic: 原始目标主题（用于获取相关的基础资源）
            used_resource_ids: 已使用的资源ID集合，用于避免重复推荐
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        resources = []
        used_ids = used_resource_ids or set()
        
        # 1. 首先尝试精确匹配
        if level:
            cursor.execute('''
                SELECT * FROM resources 
                WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?) 
                AND difficulty = ?
                LIMIT ?
            ''', ('%' + topic + '%', '%' + topic + '%', '%' + topic + '%', level, limit * 3))  # 获取更多资源以便过滤
        else:
            cursor.execute('''
                SELECT * FROM resources 
                WHERE knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?
                LIMIT ?
            ''', ('%' + topic + '%', '%' + topic + '%', '%' + topic + '%', limit * 3))  # 获取更多资源以便过滤
        
        resources = cursor.fetchall()
        
        # 2. 如果没有找到资源，尝试获取通用资源
        if not resources:
            # 对于编程基础，获取与原始主题相关的编程入门资源
            if '编程基础' in topic and original_topic:
                # 尝试获取与原始主题相关的基础资源
                cursor.execute('''
                    SELECT * FROM resources 
                    WHERE (knowledge_point LIKE ? OR knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                    LIMIT ?
                ''', ('%' + original_topic + '%', '%编程%', '%' + original_topic + '%', '%' + original_topic + '%', limit * 5))
                resources = cursor.fetchall()
                
                # 如果还是没有，获取通用编程基础资源
                if not resources:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', ('%编程%', '%基础%', '%编程%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，获取任何编程相关的资源
                if not resources:
                    cursor.execute('''
                        SELECT * FROM resources 
                        LIMIT ?
                    ''', (limit * 5,))
                    resources = cursor.fetchall()
            
            # 对于数学相关主题，获取数学基础资源
            elif '数学' in topic or '代数' in topic or '微积分' in topic:
                cursor.execute('''
                    SELECT * FROM resources 
                    WHERE difficulty = ? 
                    AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                    LIMIT ?
                ''', (level or '初级', '%数学%', '%统计%', '%数学%', limit * 3))
                resources = cursor.fetchall()
            
            # 对于前端开发相关主题，获取前端相关资源
            elif '前端' in topic or 'HTML' in topic or 'CSS' in topic or 'JavaScript' in topic:
                cursor.execute('''
                    SELECT * FROM resources 
                    WHERE difficulty = ? 
                    AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                    LIMIT ?
                ''', (level or '初级', '%前端%', '%HTML%', '%CSS%', limit * 3))
                resources = cursor.fetchall()
                
                # 如果还是没有，获取JavaScript相关资源
                if not resources:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%JavaScript%', '%前端%', '%JavaScript%', limit * 3))
                    resources = cursor.fetchall()
            
            # 对于其他主题，获取相关的初级资源
            if not resources:
                # 尝试获取与原始主题相关的资源
                if original_topic:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%' + original_topic + '%', '%' + original_topic + '%', '%' + original_topic + '%', limit * 3))
                    resources = cursor.fetchall()
                
                # 如果还是没有，获取通用初级资源
                if not resources:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        LIMIT ?
                    ''', (level or '初级', limit * 3))
                    resources = cursor.fetchall()
        
        # 过滤掉已使用的资源
        filtered_resources = []
        for res in resources:
            if res[0] not in used_ids:
                filtered_resources.append(res)
                if len(filtered_resources) >= limit:
                    break
        
        conn.close()
        return filtered_resources
    
    def _get_learning_time(self, topic, level):
        """估算学习时间（小时）"""
        time_estimates = {
            '初级': {
                'Python': 40,
                'Java': 50,
                'C++': 60,
                '前端开发': 45,
                '数据分析': 35,
                '机器学习': 60,
                '数据库': 30,
                '算法': 40,
                'Linux': 35,
                'HTML': 10,
                'CSS': 15,
                'JavaScript': 25,
                '编程基础': 20,
                '数学': 50,
                '物理学': 45,
                '化学': 40,
                '生物学': 35,
                '英语': 60,
                '历史': 30,
                '地理': 25,
                '经济学': 40,
                '哲学': 35,
                '艺术': 30
            },
            '中级': {
                'Python': 60,
                'Java': 70,
                'C++': 80,
                '前端开发': 65,
                '数据分析': 55,
                '机器学习': 80,
                '数据库': 45,
                '算法': 60,
                'Linux': 50,
                'Vue': 30,
                'React': 35,
                'Spring Boot': 40,
                '深度学习': 70,
                '线性代数': 50,
                '微积分': 55,
                '概率论': 45,
                '统计学': 40,
                '离散数学': 50,
                '力学': 45,
                '电磁学': 45,
                '热学': 40,
                '光学': 40,
                '有机化学': 45,
                '无机化学': 45,
                '细胞生物学': 40,
                '微观经济学': 45,
                '宏观经济学': 45,
                '西方哲学': 40,
                '中国哲学': 40,
                '古代史': 35,
                '近代史': 35,
                '自然地理': 35,
                '人文地理': 35,
                '艺术史': 35
            },
            '高级': {
                'Python': 80,
                'Java': 90,
                'C++': 100,
                '前端开发': 85,
                '数据分析': 75,
                '机器学习': 100,
                '数据库': 65,
                '算法': 80,
                'Linux': 70,
                '深度学习': 90,
                '系统编程': 80,
                '数论': 60,
                '几何学': 55,
                '拓扑学': 65,
                '抽象代数': 60,
                '微分方程': 60,
                '复分析': 65,
                '实分析': 65,
                '数值分析': 60,
                '数学建模': 65,
                '量子力学': 70,
                '物理化学': 60,
                '分子生物学': 55,
                '遗传学': 55,
                '金融学': 60,
                '雕塑': 50
            }
        }
        
        # 查找最接近的主题
        for key in time_estimates.get(level, {}):
            if key in topic or topic in key:
                return time_estimates[level][key]
        
        # 默认时间
        time_defaults = {'初级': 30, '中级': 50, '高级': 70}
        return time_defaults.get(level, 40)
    
    def _build_learning_path(self, target_topic, current_level, goal):
        """构建学习路径"""
        path = []
        visited = set()
        
        def dfs(topic, level):
            if topic in visited:
                return
            visited.add(topic)
            
            # 获取前置知识
            prerequisites = self.kg.get(topic, {}).get('prerequisites', [])
            
            # 先处理前置知识
            for prereq in prerequisites:
                if prereq not in visited:
                    dfs(prereq, '初级' if level == '初级' else '初级')
            
            # 添加当前主题到路径
            path.append((topic, level))
        
        # 开始构建路径
        dfs(target_topic, current_level)
        
        return path
    
    def _optimize_path(self, path, goal):
        """优化学习路径，根据目标调整顺序和内容"""
        optimized_path = []
        
        # 根据目标调整路径
        if goal == '找工作':
            # 找工作目标：优先核心技能，增加项目实践
            core_topics = ['Python', 'Java', 'C++', '前端开发', '数据分析', '机器学习']
            project_topics = ['项目开发', '实战']
            
            # 优先处理核心技能
            core_path = [item for item in path if any(core in item[0] for core in core_topics)]
            other_path = [item for item in path if item not in core_path]
            optimized_path = core_path + other_path
        
        elif goal == '项目开发':
            # 项目开发目标：提前引入项目实践
            optimized_path = path
            # 在适当位置插入项目实践
            if len(path) > 2:
                mid_point = len(path) // 2
                optimized_path.insert(mid_point, ('项目实践', '中级'))
        
        elif goal == '兴趣学习':
            # 兴趣学习目标：保持趣味性，减少理论
            optimized_path = [item for item in path if '理论' not in item[0]]
        
        else:
            optimized_path = path
        
        return optimized_path
    
    def generate_learning_plan(self, topic, level, goal, time_per_week=10):
        """
        生成学习方案
        
        Args:
            topic: 学习主题
            level: 当前水平
            goal: 学习目标
            time_per_week: 每周学习时间（小时）
            
        Returns:
            学习方案字典
        """
        # 1. 构建学习路径
        raw_path = self._build_learning_path(topic, level, goal)
        
        # 2. 优化路径
        optimized_path = self._optimize_path(raw_path, goal)
        
        # 3. 为每个阶段添加资源和时间估计
        plan = {
            'topic': topic,
            'level': level,
            'goal': goal,
            'time_per_week': time_per_week,
            'total_time': 0,
            'total_weeks': 0,
            'stages': []
        }
        
        total_time = 0
        used_resource_ids = set()  # 用于跟踪已使用的资源ID，避免重复推荐
        
        for i, (stage_topic, stage_level) in enumerate(optimized_path):
            # 获取资源，传递原始主题和已使用的资源ID
            filtered_resources = self._get_resources_by_topic(
                stage_topic, stage_level, original_topic=topic, 
                used_resource_ids=used_resource_ids, limit=3
            )
            
            # 记录使用的资源ID
            for res in filtered_resources:
                used_resource_ids.add(res[0])
            
            # 如果过滤后没有资源，尝试获取更多资源
            if not filtered_resources:
                # 尝试获取更多资源，不传递used_resource_ids，以获取所有可能的资源
                more_resources = self._get_resources_by_topic(
                    stage_topic, stage_level, original_topic=topic, 
                    limit=5
                )
                # 手动过滤已使用的资源
                new_resources = []
                for res in more_resources:
                    if res[0] not in used_resource_ids:
                        new_resources.append(res)
                        used_resource_ids.add(res[0])
                    if len(new_resources) >= 3:
                        break
                filtered_resources = new_resources
            
            # 估算学习时间
            learning_time = self._get_learning_time(stage_topic, stage_level)
            total_time += learning_time
            
            # 计算需要的周数
            weeks_needed = max(1, int(learning_time / time_per_week))
            
            stage = {
                'stage': i + 1,
                'topic': stage_topic,
                'level': stage_level,
                'learning_time': learning_time,
                'weeks_needed': weeks_needed,
                'resources': [
                    {
                        'title': r[1],
                        'type': r[2],
                        'difficulty': r[4],
                        'url': r[5],
                        'description': r[6]
                    } for r in filtered_resources
                ],
                'description': self._get_stage_description(stage_topic, stage_level, goal)
            }
            
            plan['stages'].append(stage)
        
        # 计算总时间和总周数
        plan['total_time'] = total_time
        plan['total_weeks'] = max(1, int(total_time / time_per_week))
        
        return plan
    
    def _get_stage_description(self, topic, level, goal):
        """获取阶段描述"""
        descriptions = {
            'Python': {
                '初级': '学习Python基础语法、数据类型、控制流等基础知识',
                '中级': '学习面向对象编程、异常处理、模块和包等进阶内容',
                '高级': '学习并发编程、装饰器、生成器、元编程等高级特性'
            },
            'Java': {
                '初级': '学习Java基础语法、面向对象编程、异常处理等基础知识',
                '中级': '学习集合框架、IO流、多线程等进阶内容',
                '高级': '学习JVM原理、设计模式、性能优化等高级特性'
            },
            '前端开发': {
                '初级': '学习HTML、CSS、JavaScript基础',
                '中级': '学习框架（Vue/React）、模块化开发、前端工程化',
                '高级': '学习性能优化、PWA、WebAssembly等高级技术'
            },
            '数据分析': {
                '初级': '学习数据清洗、基本统计分析、数据可视化基础',
                '中级': '学习Pandas、NumPy、Matplotlib等库的使用',
                '高级': '学习特征工程、模型选择、大数据分析'
            },
            '机器学习': {
                '初级': '学习机器学习基础概念、常用算法原理',
                '中级': '学习Scikit-learn、模型训练和评估',
                '高级': '学习深度学习、模型调优、MLOps'
            },
            '数学': {
                '初级': '学习数学基础概念、基本运算和几何知识',
                '中级': '学习代数、几何、三角函数等进阶内容',
                '高级': '学习数学分析、抽象代数等高级数学知识'
            },
            '线性代数': {
                '初级': '学习线性代数基本概念和运算',
                '中级': '学习矩阵理论、向量空间等进阶内容',
                '高级': '学习线性变换、特征值等高级线性代数知识'
            },
            '微积分': {
                '初级': '学习微积分基本概念和运算',
                '中级': '学习导数、积分等进阶内容',
                '高级': '学习多元微积分、级数等高级微积分知识'
            },
            '概率论': {
                '初级': '学习概率论基本概念和原理',
                '中级': '学习概率分布、期望方差等进阶内容',
                '高级': '学习随机过程、贝叶斯统计等高级概率论知识'
            },
            '统计学': {
                '初级': '学习统计学基本概念和方法',
                '中级': '学习假设检验、回归分析等进阶内容',
                '高级': '学习多元统计、时间序列分析等高级统计学知识'
            },
            '物理学': {
                '初级': '学习物理学基本概念和定律',
                '中级': '学习力学、电磁学等进阶内容',
                '高级': '学习量子力学、相对论等高级物理学知识'
            },
            '化学': {
                '初级': '学习化学基本概念和元素周期表',
                '中级': '学习无机化学、有机化学等进阶内容',
                '高级': '学习物理化学、量子化学等高级化学知识'
            },
            '生物学': {
                '初级': '学习生物学基本概念和生命现象',
                '中级': '学习细胞生物学、遗传学等进阶内容',
                '高级': '学习分子生物学、生物进化等高级生物学知识'
            },
            '英语': {
                '初级': '学习英语基础语法和词汇',
                '中级': '学习英语听说读写等进阶技能',
                '高级': '学习英语专业领域词汇和高级表达'
            },
            '历史': {
                '初级': '学习历史基本概念和重大事件',
                '中级': '学习古代史、近代史等进阶内容',
                '高级': '学习历史研究方法和专题史等高级历史知识'
            },
            '地理': {
                '初级': '学习地理基本概念和地图知识',
                '中级': '学习自然地理、人文地理等进阶内容',
                '高级': '学习地理信息系统、区域地理等高级地理知识'
            },
            '经济学': {
                '初级': '学习经济学基本概念和原理',
                '中级': '学习微观经济学、宏观经济学等进阶内容',
                '高级': '学习计量经济学、金融经济学等高级经济学知识'
            },
            '哲学': {
                '初级': '学习哲学基本概念和思想流派',
                '中级': '学习西方哲学、中国哲学等进阶内容',
                '高级': '学习哲学研究方法和专题哲学等高级哲学知识'
            },
            '艺术': {
                '初级': '学习艺术基本概念和欣赏方法',
                '中级': '学习艺术史、音乐、绘画等进阶内容',
                '高级': '学习艺术创作、艺术理论等高级艺术知识'
            },
            '项目实践': {
                '中级': '通过实际项目巩固所学知识，提升实战能力'
            }
        }
        
        if topic in descriptions:
            if level in descriptions[topic]:
                return descriptions[topic][level]
        
        return f'学习{topic}的{level}内容'
    
    def get_learning_efficiency_tips(self, topic, goal):
        """获取学习效率建议"""
        tips = {
            'Python': {
                '找工作': ['重点学习数据结构和算法', '多做LeetCode题目', '构建1-2个完整项目'],
                '项目开发': ['学习Flask或Django框架', '掌握数据库操作', '学习版本控制'],
                '兴趣学习': ['从小项目开始', '加入Python社区', '参与开源项目']
            },
            'Java': {
                '找工作': ['学习Spring Boot框架', '掌握数据库设计', '准备常见面试题'],
                '项目开发': ['学习微服务架构', '掌握Docker容器化', '学习CI/CD'],
                '兴趣学习': ['尝试不同的Java框架', '参与Java社区活动']
            },
            '前端开发': {
                '找工作': ['掌握React或Vue框架', '学习前端工程化', '构建响应式网站'],
                '项目开发': ['学习TypeScript', '掌握状态管理', '优化前端性能'],
                '兴趣学习': ['尝试不同的前端框架', '参与前端社区']
            },
            '数据分析': {
                '找工作': ['学习SQL和Python', '掌握Pandas和Matplotlib', '准备数据分析案例'],
                '项目开发': ['学习数据可视化工具', '掌握数据清洗技巧', '构建数据分析项目'],
                '兴趣学习': ['分析自己感兴趣的数据集', '参与Kaggle竞赛']
            },
            '机器学习': {
                '找工作': ['学习数学基础', '掌握常用算法', '参与Kaggle竞赛'],
                '项目开发': ['学习PyTorch或TensorFlow', '构建端到端机器学习项目', '学习模型部署'],
                '兴趣学习': ['从简单的项目开始', '学习不同类型的机器学习算法']
            }
        }
        
        if topic in tips:
            if goal in tips[topic]:
                return tips[topic][goal]
        
        # 默认建议
        return [
            '制定合理的学习计划，每天坚持学习',
            '理论结合实践，多动手编码',
            '遇到问题及时解决，不要堆积',
            '加入学习社区，与他人交流'
        ]

# 创建全局实例
path_planner = PathPlanner()
generate_learning_plan = path_planner.generate_learning_plan
get_learning_efficiency_tips = path_planner.get_learning_efficiency_tips

if __name__ == '__main__':
    # 测试学习方案生成
    print("="*50)
    print("测试学习方案生成")
    print("="*50)
    
    test_cases = [
        ('Python', '初级', '找工作'),
        ('机器学习', '中级', '项目开发'),
        ('前端开发', '初级', '兴趣学习')
    ]
    
    for topic, level, goal in test_cases:
        print(f"\n=== {topic} ({level}) - {goal} ===")
        plan = path_planner.generate_learning_plan(topic, level, goal)
        
        print(f"总学习时间: {plan['total_time']} 小时")
        print(f"预计需要: {plan['total_weeks']} 周")
        print(f"每周学习: {plan['time_per_week']} 小时")
        
        print("\n学习阶段:")
        for stage in plan['stages']:
            print(f"  阶段{stage['stage']}: {stage['topic']} ({stage['level']})")
            print(f"    学习时间: {stage['learning_time']} 小时")
            print(f"    需要周数: {stage['weeks_needed']} 周")
            print(f"    描述: {stage['description']}")
            if stage['resources']:
                print("    推荐资源:")
                for i, res in enumerate(stage['resources'], 1):
                    print(f"      {i}. [{res['type']}] {res['title']}")
