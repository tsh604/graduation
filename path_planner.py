# path_planner.py
"""
学习路径规划器 - 基于知识图谱和用户目标生成最优学习方案
"""
from knowledge_graph import knowledge_graph
import sqlite3
import random

class PathPlanner:
    def __init__(self, db_path='data/learning.db'):
        self.db_path = db_path
        self.kg = knowledge_graph
    
    def _get_resources_by_topic(self, topic, level=None, limit=3, original_topic=None, used_resource_ids=None, goal=None, money_budget=None):
        """根据主题和难度获取资源
        
        Args:
            topic: 当前学习主题
            level: 难度级别
            limit: 返回资源数量限制
            original_topic: 原始目标主题（用于获取相关的基础资源）
            used_resource_ids: 已使用的资源ID集合，用于避免重复推荐
            goal: 学习目标
            money_budget: 金钱预算（元）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        resources = []
        used_ids = used_resource_ids or set()
        
        # 1. 首先尝试精确匹配，根据学习目标调整查询
        if level:
            # 对于Python主题，优先获取Python相关资源
            if 'Python' in topic:
                # 首先尝试获取Python基础教程
                cursor.execute('''
                    SELECT * FROM resources 
                    WHERE title LIKE ? 
                    AND difficulty = ?
                ''', ('%Python基础教程%', level))
                basic_tutorial = cursor.fetchall()
                
                # 然后根据学习目标获取其他Python相关资源
                if goal == '找工作':
                    # 找工作目标：优先包含"面试"、"就业"、"项目"等关键词的资源
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?) 
                        AND difficulty = ?
                        AND title NOT LIKE ?
                        AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                        LIMIT ?
                    ''', ('%Python%', '%Python%', '%Python%', level, '%Python基础教程%', '%面试%', '%就业%', '%项目%', limit * 10))
                elif goal == '兴趣学习':
                    # 兴趣学习目标：优先包含"趣味"、"入门"、"实践"等关键词的资源
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?) 
                        AND difficulty = ?
                        AND title NOT LIKE ?
                        AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                        LIMIT ?
                    ''', ('%Python%', '%Python%', '%Python%', level, '%Python基础教程%', '%趣味%', '%入门%', '%实践%', limit * 10))
                elif goal == '项目开发':
                    # 项目开发目标：优先包含"项目"、"实战"、"开发"等关键词的资源
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?) 
                        AND difficulty = ?
                        AND title NOT LIKE ?
                        AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                        LIMIT ?
                    ''', ('%Python%', '%Python%', '%Python%', level, '%Python基础教程%', '%项目%', '%实战%', '%开发%', limit * 10))
                else:
                    # 其他目标：使用基本查询
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?) 
                        AND difficulty = ?
                        AND title NOT LIKE ?
                        LIMIT ?
                    ''', ('%Python%', '%Python%', '%Python%', level, '%Python基础教程%', limit * 10))
                other_resources = cursor.fetchall()
                
                # 合并资源
                resources = []
                if basic_tutorial:
                    resources.extend(basic_tutorial)
                if other_resources:
                    resources.extend(other_resources)
                
                # 根据学习目标添加特定的Python资源
                if goal == '找工作':
                    # 找工作目标：优先添加系统学习资源和面试相关资源
                    # 1. Python 100天教程（系统的学习资源，对找工作也很有帮助）
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%100天%', level))
                    python100 = cursor.fetchone()
                    if python100 and python100 not in resources:
                        resources.append(python100)
                        if len(resources) >= limit:
                            pass
                    
                    # 2. LeetCode Python题库
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%LeetCode%', level))
                    leetcode = cursor.fetchone()
                    if leetcode and leetcode not in resources:
                        resources.append(leetcode)
                        if len(resources) >= limit:
                            pass
                    
                    # 3. 廖雪峰Python教程
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%廖雪峰%', level))
                    liaoxuefeng = cursor.fetchone()
                    if liaoxuefeng and liaoxuefeng not in resources:
                        resources.append(liaoxuefeng)
                        if len(resources) >= limit:
                            pass
                elif goal == '兴趣学习':
                    # 兴趣学习目标：优先添加趣味性强的Python资源
                    # 1. Python 100天教程
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%100天%', level))
                    python100 = cursor.fetchone()
                    if python100 and python100 not in resources:
                        resources.append(python100)
                        if len(resources) >= limit:
                            pass
                    
                    # 2. 廖雪峰Python教程
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%廖雪峰%', level))
                    liaoxuefeng = cursor.fetchone()
                    if liaoxuefeng and liaoxuefeng not in resources:
                        resources.append(liaoxuefeng)
                        if len(resources) >= limit:
                            pass
                elif goal == '项目开发':
                    # 项目开发目标：优先添加与项目开发相关的Python资源
                    # 1. Jupyter教程
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%Jupyter%', level))
                    jupyter = cursor.fetchone()
                    if jupyter and jupyter not in resources:
                        resources.append(jupyter)
                        if len(resources) >= limit:
                            pass
                    
                    # 2. PyCharm指南
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%PyCharm%', level))
                    pycharm = cursor.fetchone()
                    if pycharm and pycharm not in resources:
                        resources.append(pycharm)
                        if len(resources) >= limit:
                            pass
                
                # 如果没有找到足够的资源，尝试获取所有Python资源（不限制难度）
                if not resources or len(resources) < limit:
                    # 首先尝试根据学习目标获取资源
                    if goal == '找工作':
                        # 找工作目标：优先包含"面试"、"就业"、"项目"等关键词的资源
                        cursor.execute('''
                            SELECT *, learning_time FROM resources 
                            WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                            AND title NOT LIKE ?
                            AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                            LIMIT ?
                        ''', ('%Python%', '%Python%', '%Python%', '%Python基础教程%', '%面试%', '%就业%', '%项目%', limit * 10))
                    elif goal == '兴趣学习':
                        # 兴趣学习目标：优先包含"趣味"、"入门"、"实践"等关键词的资源
                        cursor.execute('''
                            SELECT *, learning_time FROM resources 
                            WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                            AND title NOT LIKE ?
                            AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                            LIMIT ?
                        ''', ('%Python%', '%Python%', '%Python%', '%Python基础教程%', '%趣味%', '%入门%', '%实践%', limit * 10))
                    elif goal == '项目开发':
                        # 项目开发目标：优先包含"项目"、"实战"、"开发"等关键词的资源
                        cursor.execute('''
                            SELECT *, learning_time FROM resources 
                            WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                            AND title NOT LIKE ?
                            AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                            LIMIT ?
                        ''', ('%Python%', '%Python%', '%Python%', '%Python基础教程%', '%项目%', '%实战%', '%开发%', limit * 10))
                    else:
                        # 其他目标：使用基本查询
                        cursor.execute('''
                            SELECT *, learning_time FROM resources 
                            WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                            AND title NOT LIKE ?
                            LIMIT ?
                        ''', ('%Python%', '%Python%', '%Python%', '%Python基础教程%', limit * 10))
                    more_resources = cursor.fetchall()
                    if more_resources:
                        resources.extend(more_resources)
                
                # 如果还是没有足够的资源，获取所有Python资源
                if not resources or len(resources) < limit:
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND title NOT LIKE ?
                        LIMIT ?
                    ''', ('%Python%', '%Python%', '%Python%', '%Python基础教程%', limit * 10))
                    fallback_resources = cursor.fetchall()
                    if fallback_resources:
                        resources.extend(fallback_resources)
            else:
                # 基础SQL查询
                base_query = '''
                    SELECT *, learning_time FROM resources 
                    WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?) 
                    AND difficulty = ?
                '''
                
                # 提取主题名称（去除难度级别部分）
                topic_name = topic.split(' ')[0].split('(')[0]
                
                # 根据学习目标添加额外条件
                if goal == '找工作':
                    # 找工作目标：优先包含"面试"、"就业"、"项目"等关键词的资源
                    base_query += " AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)"
                    cursor.execute(base_query + " LIMIT ?", 
                                  ('%' + topic_name + '%', '%' + topic_name + '%', '%' + topic_name + '%', 
                                   level, '%面试%', '%就业%', '%项目%', limit * 3))
                elif goal == '兴趣学习':
                    # 兴趣学习目标：优先包含"趣味"、"入门"、"实践"等关键词的资源
                    base_query += " AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)"
                    cursor.execute(base_query + " LIMIT ?", 
                                  ('%' + topic_name + '%', '%' + topic_name + '%', '%' + topic_name + '%', 
                                   level, '%趣味%', '%入门%', '%实践%', limit * 3))
                elif goal == '项目开发':
                    # 项目开发目标：优先包含"项目"、"实战"、"开发"等关键词的资源
                    base_query += " AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)"
                    cursor.execute(base_query + " LIMIT ?", 
                                  ('%' + topic_name + '%', '%' + topic_name + '%', '%' + topic_name + '%', 
                                   level, '%项目%', '%实战%', '%开发%', limit * 3))
                else:
                    # 其他目标：使用基本查询
                    cursor.execute(base_query + " LIMIT ?", 
                                  ('%' + topic_name + '%', '%' + topic_name + '%', '%' + topic_name + '%', 
                                   level, limit * 3))
                resources = cursor.fetchall()
        else:
            # 没有指定难度级别时的查询
            cursor.execute('''
                SELECT *, learning_time FROM resources 
                WHERE knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?
                LIMIT ?
            ''', ('%' + topic + '%', '%' + topic + '%', '%' + topic + '%', limit * 3))  # 获取更多资源以便过滤
            resources = cursor.fetchall()
        
        # 2. 如果没有找到资源，尝试获取通用资源
        if not resources:
            # 对于编程基础，首先尝试获取通用编程基础资源（不包含Python特定资源）
            if '编程基础' in topic:
                # 定义编程相关的关键词
                programming_keywords = ['编程', '代码', '算法', '数据结构', '计算机', '技术', '前端', '后端', '开发', '软件', '程序', '语言', '语法', '逻辑', '调试', '版本控制', 'Git', 'Linux', '命令行', '终端', '编辑器', 'IDE', '环境', '配置', '变量', '函数', '循环', '条件', '数据类型', '运算符', '表达式', '语句', '结构', '设计', '模式', '面向对象', '过程', '函数式', '编程范式']
                
                # 先尝试获取通用编程基础资源，排除Python特定资源和数学资源
                if goal == '找工作':
                    # 找工作目标：优先包含"面试"、"就业"、"项目"等关键词的资源
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%编程%', '%基础%', '%编程%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', '%面试%', '%就业%', '%项目%', limit * 5))
                elif goal == '兴趣学习':
                    # 兴趣学习目标：优先包含"趣味"、"入门"、"实践"等关键词的资源
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%编程%', '%基础%', '%编程%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', '%趣味%', '%入门%', '%实践%', limit * 5))
                elif goal == '项目开发':
                    # 项目开发目标：优先包含"项目"、"实战"、"开发"等关键词的资源
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND (title LIKE ? OR description LIKE ? OR knowledge_point LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%编程%', '%基础%', '%编程%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', '%项目%', '%实战%', '%开发%', limit * 5))
                else:
                    # 其他目标：使用基本查询
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%编程%', '%基础%', '%编程%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                resources = cursor.fetchall()
                
                # 如果还是没有，再尝试获取通用编程资源
                if not resources:
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%编程%', '%代码%', '%编程%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取与编程相关的其他资源
                if not resources:
                    # 获取前端相关资源
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%前端%', '%HTML%', '%CSS%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取Linux相关资源
                if not resources:
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%Linux%', '%命令%', '%Linux%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取Git相关资源
                if not resources:
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%Git%', '%版本%', '%Git%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取算法相关资源
                if not resources:
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%算法%', '%数据结构%', '%算法%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取数据库相关资源
                if not resources:
                    cursor.execute('''
                        SELECT *, learning_time FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%数据库%', '%SQL%', '%数据库%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取编程相关的其他资源
                if not resources:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%编程%', '%程序%', '%编程%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取技术相关资源
                if not resources:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%技术%', '%计算机%', '%技术%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 确保至少有一些资源
                if not resources:
                    # 尝试获取前端相关资源
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%前端%', '%HTML%', '%CSS%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取Git相关资源
                if not resources:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%Git%', '%版本%', '%Git%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 如果还是没有，尝试获取数据库相关资源
                if not resources:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', (level or '初级', '%数据库%', '%SQL%', '%数据库%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%', limit * 5))
                    resources = cursor.fetchall()
                
                # 强制添加一些编程相关的资源，确保至少有3个资源
                # 根据学习目标选择不同的资源
                if goal == '找工作':
                    # 找工作目标：优先推荐GitHub、LeetCode等与就业相关的资源
                    # 1. GitHub指南
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%GitHub%', level or '初级'))
                    github_guide = cursor.fetchone()
                    if github_guide and github_guide not in resources:
                        resources.append(github_guide)
                        if len(resources) >= limit:
                            pass
                    
                    # 2. Git教程
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%Git%', level or '初级'))
                    git_tutorial = cursor.fetchone()
                    if git_tutorial and git_tutorial not in resources:
                        resources.append(git_tutorial)
                        if len(resources) >= limit:
                            pass
                    
                    # 3. Linux教程
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%Linux%', level or '初级'))
                    linux_tutorial = cursor.fetchone()
                    if linux_tutorial and linux_tutorial not in resources:
                        resources.append(linux_tutorial)
                        if len(resources) >= limit:
                            pass
                elif goal == '兴趣学习':
                    # 兴趣学习目标：优先推荐HTML、CSS等趣味性强的资源
                    # 1. HTML5教程
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%HTML5%', level or '初级'))
                    html_tutorial = cursor.fetchone()
                    if html_tutorial and html_tutorial not in resources:
                        resources.append(html_tutorial)
                        if len(resources) >= limit:
                            pass
                    
                    # 2. CSS教程
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%CSS%', level or '初级'))
                    css_tutorial = cursor.fetchone()
                    if css_tutorial and css_tutorial not in resources:
                        resources.append(css_tutorial)
                        if len(resources) >= limit:
                            pass
                    
                    # 3. MDN Web文档
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%MDN%', level or '初级'))
                    mdn_tutorial = cursor.fetchone()
                    if mdn_tutorial and mdn_tutorial not in resources:
                        resources.append(mdn_tutorial)
                        if len(resources) >= limit:
                            pass
                elif goal == '项目开发':
                    # 项目开发目标：优先推荐Git、npm等与项目开发相关的资源
                    # 1. Git教程
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%Git%', level or '初级'))
                    git_tutorial = cursor.fetchone()
                    if git_tutorial and git_tutorial not in resources:
                        resources.append(git_tutorial)
                        if len(resources) >= limit:
                            pass
                    
                    # 2. npm文档
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%npm%', level or '初级'))
                    npm_tutorial = cursor.fetchone()
                    if npm_tutorial and npm_tutorial not in resources:
                        resources.append(npm_tutorial)
                        if len(resources) >= limit:
                            pass
                    
                    # 3. VS Code文档
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? AND difficulty = ?
                    ''', ('%VS Code%', level or '初级'))
                    vscode_tutorial = cursor.fetchone()
                    if vscode_tutorial and vscode_tutorial not in resources:
                        resources.append(vscode_tutorial)
                        if len(resources) >= limit:
                            pass
                
                # 如果还是没有足够的资源，获取所有编程相关资源
                if len(resources) < limit:
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE difficulty = ? 
                        AND (knowledge_point LIKE ? OR knowledge_point LIKE ? OR knowledge_point LIKE ? OR knowledge_point LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND NOT (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                    ''', (level or '初级', '%前端%', '%Git%', '%Linux%', '%编程%', '%Python%', '%Python%', '%Python%', '%数学%', '%数学%', '%数学%'))
                    all_programming_resources = cursor.fetchall()
                    
                    for res in all_programming_resources:
                        if res not in resources:
                            resources.append(res)
                            if len(resources) >= limit:
                                break
            else:
                # 对于其他主题（如Java、C++等），尝试获取相关资源
                # 提取主题名称（去除难度级别部分）
                topic_name = topic.split(' ')[0].split('(')[0]
                
                # 尝试获取与主题相关的资源
                # 对于Java，直接查询knowledge_point为Java的资源
                if topic_name == 'Java':
                    # 尝试获取与用户水平匹配的Java相关资源
                    if level:
                        # 首先查询指定难度的资源
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE (knowledge_point = ? OR title LIKE ? OR description LIKE ?) 
                            AND difficulty = ?
                            LIMIT ?
                        ''', (topic_name, '%' + topic_name + '%', '%' + topic_name + '%', level, limit * 10))
                        resources = cursor.fetchall()
                        
                        # 如果没有足够的资源，尝试获取更低难度的资源
                        if len(resources) < limit:
                            if level == '中级':
                                # 中级用户可以使用初级资源
                                cursor.execute('''
                                    SELECT * FROM resources 
                                    WHERE (knowledge_point = ? OR title LIKE ? OR description LIKE ?) 
                                    AND difficulty = '初级'
                                    LIMIT ?
                                ''', (topic_name, '%' + topic_name + '%', '%' + topic_name + '%', limit * 5))
                                beginner_resources = cursor.fetchall()
                                resources.extend(beginner_resources)
                            elif level == '高级':
                                # 高级用户可以使用初级和中级资源
                                cursor.execute('''
                                    SELECT * FROM resources 
                                    WHERE (knowledge_point = ? OR title LIKE ? OR description LIKE ?) 
                                    AND difficulty IN ('初级', '中级')
                                    LIMIT ?
                                ''', (topic_name, '%' + topic_name + '%', '%' + topic_name + '%', limit * 5))
                                lower_resources = cursor.fetchall()
                                resources.extend(lower_resources)
                    else:
                        # 没有指定难度级别，获取所有Java相关资源
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE knowledge_point = ?
                            LIMIT ?
                        ''', (topic_name, limit * 10))
                        resources = cursor.fetchall()
                    
                    # 如果还是没有，尝试获取所有包含Java的资源
                    if not resources:
                        if level:
                            cursor.execute('''
                                SELECT * FROM resources 
                                WHERE (knowledge_point LIKE ? OR title LIKE ? OR description LIKE ?) 
                                AND difficulty = ?
                                LIMIT ?
                            ''', ('%' + topic_name + '%', '%' + topic_name + '%', '%' + topic_name + '%', level, limit * 10))
                        else:
                            cursor.execute('''
                                SELECT * FROM resources 
                                WHERE (knowledge_point LIKE ? OR title LIKE ?)
                                LIMIT ?
                            ''', ('%' + topic_name + '%', '%' + topic_name + '%', limit * 10))
                        resources = cursor.fetchall()
                    
                    # 只添加与用户水平匹配的Java相关资源
                    # 1. Java基础教程
                    if level:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE (title LIKE ? OR knowledge_point LIKE ?) 
                            AND difficulty = ?
                        ''', ('%Java%', '%Java%', level))
                    else:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE title LIKE ? OR knowledge_point LIKE ?
                        ''', ('%Java%', '%Java%'))
                    java_resources = cursor.fetchall()
                    for res in java_resources:
                        if res not in resources:
                            resources.append(res)
                            if len(resources) >= limit * 5:
                                break
                # 对于算法，直接查询knowledge_point为算法的资源
                elif topic_name == '算法':
                    # 尝试获取与用户水平匹配的算法相关资源
                    if level:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE (knowledge_point = ? OR title LIKE ? OR description LIKE ?) 
                            AND difficulty = ?
                            LIMIT ?
                        ''', (topic_name, '%' + topic_name + '%', '%' + topic_name + '%', level, limit * 10))
                    else:
                        # 没有指定难度级别，获取所有算法相关资源
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE knowledge_point = ?
                            LIMIT ?
                        ''', (topic_name, limit * 10))
                    resources = cursor.fetchall()
                    
                    # 如果还是没有，尝试获取所有包含算法的资源
                    if not resources:
                        if level:
                            cursor.execute('''
                                SELECT * FROM resources 
                                WHERE (knowledge_point LIKE ? OR title LIKE ? OR description LIKE ?) 
                                AND difficulty = ?
                                LIMIT ?
                            ''', ('%' + topic_name + '%', '%' + topic_name + '%', '%' + topic_name + '%', level, limit * 10))
                        else:
                            cursor.execute('''
                                SELECT * FROM resources 
                                WHERE (knowledge_point LIKE ? OR title LIKE ?)
                                LIMIT ?
                            ''', ('%' + topic_name + '%', '%' + topic_name + '%', limit * 10))
                        resources = cursor.fetchall()
                    
                    # 强制添加一些算法相关的资源，确保至少有3个资源
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? OR knowledge_point LIKE ?
                    ''', ('%算法%', '%算法%'))
                    algorithm_resources = cursor.fetchall()
                    for res in algorithm_resources:
                        if res not in resources:
                            resources.append(res)
                            if len(resources) >= limit * 5:
                                break
                # 对于深度学习，直接查询knowledge_point为深度学习的资源
                elif topic_name == '深度学习':
                    # 尝试获取所有深度学习相关资源（不限制难度）
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE knowledge_point = ?
                        LIMIT ?
                    ''', (topic_name, limit * 10))
                    resources = cursor.fetchall()
                    
                    # 如果还是没有，尝试获取所有包含深度学习的资源
                    if not resources:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE (knowledge_point LIKE ? OR title LIKE ?)
                            LIMIT ?
                        ''', ('%' + topic_name + '%', '%' + topic_name + '%', limit * 10))
                        resources = cursor.fetchall()
                    
                    # 强制添加一些深度学习相关的资源，确保至少有3个资源
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? OR knowledge_point LIKE ?
                    ''', ('%深度学习%', '%深度学习%'))
                    deep_learning_resources = cursor.fetchall()
                    for res in deep_learning_resources:
                        if res not in resources:
                            resources.append(res)
                            if len(resources) >= limit * 5:
                                break
                # 对于数据分析，直接查询knowledge_point为数据分析的资源
                elif topic_name == '数据分析':
                    # 尝试获取所有数据分析相关资源（不限制难度）
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE knowledge_point = ?
                        LIMIT ?
                    ''', (topic_name, limit * 10))
                    resources = cursor.fetchall()
                    
                    # 如果还是没有，尝试获取所有包含数据分析的资源
                    if not resources:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE (knowledge_point LIKE ? OR title LIKE ?)
                            LIMIT ?
                        ''', ('%' + topic_name + '%', '%' + topic_name + '%', limit * 10))
                        resources = cursor.fetchall()
                    
                    # 强制添加一些数据分析相关的资源，确保至少有3个资源
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? OR knowledge_point LIKE ?
                    ''', ('%数据分析%', '%数据分析%'))
                    data_analysis_resources = cursor.fetchall()
                    for res in data_analysis_resources:
                        if res not in resources:
                            resources.append(res)
                            if len(resources) >= limit * 5:
                                break
                # 对于机器学习，直接查询knowledge_point为机器学习的资源
                elif topic_name == '机器学习':
                    # 尝试获取所有机器学习相关资源（不限制难度）
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE knowledge_point = ?
                        LIMIT ?
                    ''', (topic_name, limit * 10))
                    resources = cursor.fetchall()
                    
                    # 如果还是没有，尝试获取所有包含机器学习的资源
                    if not resources:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE (knowledge_point LIKE ? OR title LIKE ?)
                            LIMIT ?
                        ''', ('%' + topic_name + '%', '%' + topic_name + '%', limit * 10))
                        resources = cursor.fetchall()
                    
                    # 强制添加一些机器学习相关的资源，确保至少有3个资源
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE title LIKE ? OR knowledge_point LIKE ?
                    ''', ('%机器学习%', '%机器学习%'))
                    machine_learning_resources = cursor.fetchall()
                    for res in machine_learning_resources:
                        if res not in resources:
                            resources.append(res)
                            if len(resources) >= limit * 5:
                                break
                # 对于其他编程语言，如C++、JavaScript等，也直接获取所有相关资源
                elif topic_name in ['C++', 'JavaScript']:
                    # 尝试获取所有相关资源（不限制难度）
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR title LIKE ?)
                        LIMIT ?
                    ''', ('%' + topic_name + '%', '%' + topic_name + '%', limit * 5))
                    resources = cursor.fetchall()
                else:
                    # 其他主题的查询
                    cursor.execute('''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?) 
                        AND difficulty = ?
                        LIMIT ?
                    ''', ('%' + topic_name + '%', '%' + topic_name + '%', '%' + topic_name + '%', level or '初级', limit * 5))
                    resources = cursor.fetchall()
                    
                    # 如果还是没有，尝试获取与主题相关的其他资源
                    if not resources:
                        # 尝试获取所有与主题相关的资源（不限制难度）
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                            LIMIT ?
                        ''', ('%' + topic_name + '%', '%' + topic_name + '%', '%' + topic_name + '%', limit * 5))
                        resources = cursor.fetchall()
                    
                    # 如果还是没有，为C++、JavaScript等编程语言添加特定资源
                    if not resources and topic_name in ['C++', 'JavaScript']:
                        # 对于C++，尝试获取C++基础教程
                        if topic_name == 'C++':
                            cursor.execute('''
                                SELECT * FROM resources 
                                WHERE (title LIKE ? OR knowledge_point LIKE ?)
                                AND difficulty = ?
                                LIMIT ?
                            ''', ('%C++%', '%C++%', level or '初级', limit * 5))
                            resources = cursor.fetchall()
                        # 对于JavaScript，尝试获取JavaScript基础教程
                        elif topic_name == 'JavaScript':
                            cursor.execute('''
                                SELECT * FROM resources 
                                WHERE (title LIKE ? OR knowledge_point LIKE ?)
                                AND difficulty = ?
                                LIMIT ?
                            ''', ('%JavaScript%', '%JavaScript%', level or '初级', limit * 5))
                            resources = cursor.fetchall()

                
                # 对于数学相关主题，获取数学基础资源
                if '数学' in topic_name or '代数' in topic_name or '微积分' in topic_name:
                    cursor.execute('''
                    SELECT * FROM resources 
                    WHERE difficulty = ? 
                    AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                    LIMIT ?
                ''', (level or '初级', '%数学%', '%统计%', '%数学%', limit * 3))
                resources = cursor.fetchall()
            
            # 对于前端开发相关主题，获取前端相关资源
            if '前端' in topic or 'HTML' in topic or 'CSS' in topic or 'JavaScript' in topic:
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
            # 只有当前面没有获取到资源时，才执行后面的逻辑
            # 避免覆盖前面已经获取到的Java等编程语言的资源
            if not resources and original_topic:
                # 定义与编程相关的主题
                programming_topics = {'Python', 'Java', 'C++', '编程基础', '前端开发', 'JavaScript', 'Vue', 'React', 'Spring Boot', '系统编程', '算法', '数据结构'}
                # 定义不相关的主题
                unrelated_topics = ['数学', '物理', '化学', '生物', '历史', '地理', '文学', '艺术', '音乐', '体育']
                
                # 如果原始主题是编程相关的，只获取编程相关的资源
                if original_topic in programming_topics:
                    # 构建不相关主题的排除条件
                    exclude_conditions = []
                    exclude_params = []
                    for unrelated in unrelated_topics:
                        exclude_conditions.extend(['knowledge_point NOT LIKE ?', 'description NOT LIKE ?', 'title NOT LIKE ?'])
                        exclude_params.extend(['%' + unrelated + '%', '%' + unrelated + '%', '%' + unrelated + '%'])
                    
                    # 对于Python主题，只查询包含Python的资源
                    if original_topic == 'Python':
                        # 构建查询语句
                        query = '''
                            SELECT * FROM resources 
                            WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                            AND ''' + ' AND '.join(exclude_conditions) + '''
                            LIMIT ?
                        '''
                        
                        # 构建参数（不限制难度）
                        params = ['%' + original_topic + '%', '%' + original_topic + '%', '%' + original_topic + '%'] + exclude_params + [limit * 3]
                    else:
                        # 对于其他编程相关主题，查询包含主题和编程/代码的资源
                        # 构建查询语句
                        query = '''
                            SELECT * FROM resources 
                            WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                            AND (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                            AND ''' + ' AND '.join(exclude_conditions) + '''
                            LIMIT ?
                        '''
                        
                        # 构建参数（不限制难度）
                        params = ['%' + original_topic + '%', '%' + original_topic + '%', '%' + original_topic + '%', '%编程%', '%代码%', '%编程%'] + exclude_params + [limit * 3]
                    cursor.execute(query, params)
                else:
                    # 否则，获取与原始主题相关的资源
                    # 同样排除不相关主题
                    exclude_conditions = []
                    exclude_params = []
                    for unrelated in unrelated_topics:
                        exclude_conditions.extend(['knowledge_point NOT LIKE ?', 'description NOT LIKE ?', 'title NOT LIKE ?'])
                        exclude_params.extend(['%' + unrelated + '%', '%' + unrelated + '%', '%' + unrelated + '%'])
                    
                    # 构建查询语句
                    query = '''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND ''' + ' AND '.join(exclude_conditions) + '''
                        LIMIT ?
                    '''
                    
                    # 构建参数（不限制难度）
                    params = ['%' + original_topic + '%', '%' + original_topic + '%', '%' + original_topic + '%'] + exclude_params + [limit * 3]
                    cursor.execute(query, params)
                resources = cursor.fetchall()
            
            # 如果还是没有，获取与原始主题相关的通用资源
            if not resources and original_topic:
                # 定义与编程相关的主题
                programming_topics = {'Python', 'Java', 'C++', '编程基础', '前端开发', 'JavaScript', 'Vue', 'React', 'Spring Boot', '系统编程', '算法', '数据结构'}
                # 定义不相关的主题
                unrelated_topics = ['数学', '物理', '化学', '生物', '历史', '地理', '文学', '艺术', '音乐', '体育']
                
                # 如果原始主题是编程相关的，只获取编程相关的资源
                if original_topic in programming_topics:
                    # 构建不相关主题的排除条件
                    exclude_conditions = []
                    exclude_params = []
                    for unrelated in unrelated_topics:
                        exclude_conditions.extend(['knowledge_point NOT LIKE ?', 'description NOT LIKE ?', 'title NOT LIKE ?'])
                        exclude_params.extend(['%' + unrelated + '%', '%' + unrelated + '%', '%' + unrelated + '%'])
                    
                    # 构建查询语句
                    query = '''
                        SELECT * FROM resources 
                        WHERE (knowledge_point LIKE ? OR description LIKE ? OR title LIKE ?)
                        AND ''' + ' AND '.join(exclude_conditions) + '''
                        LIMIT ?'''
                        
                    # 构建参数（不限制难度）
                    params = ['%编程%', '%代码%', '%编程%'] + exclude_params + [limit * 3]
                    cursor.execute(query, params)
                    resources = cursor.fetchall()
        
        # 过滤掉已使用的资源和与难度不匹配的资源
        filtered_resources = []
        
        # 优先处理Python相关资源
        if 'Python' in topic:
            # 优先添加Python相关的资源
            python_resources = []
            other_resources = []
            
            for res in resources:
                # 对于Python主题，即使资源已被使用，也可以重新推荐Python相关资源
                # 确保资源难度与当前级别匹配
                if level:
                    # 对于初级用户，只推荐初级资源
                    if level == '初级' and res[4] != '初级':
                        continue
                    # 对于中级用户，推荐初级和中级资源
                    elif level == '中级' and res[4] == '高级':
                        continue
                    # 对于高级用户，推荐所有级别资源
                
                # 区分Python相关和非Python相关资源
                if 'Python' in res[1] or 'Python' in (res[2] or '') or 'Python' in (res[3] or ''):
                    python_resources.append(res)
                else:
                    other_resources.append(res)
            
            # 对Python资源进行排序，优先推荐学习成本低、适合初学者的资源
            if level == '初级':
                # 定义资源评分函数，考虑以下因素：
                # 1. 是否包含基础关键词（权重2）
                # 2. 是否是课程形式（通常更系统，权重1）
                def score_resource(res):
                    score = 0
                    title_lower = (res[1] or '').lower()
                    # 基础关键词加分
                    if '基础' in title_lower or '入门' in title_lower or 'tutorial' in title_lower:
                        score += 2
                    # 课程形式加分
                    if '课程' in title_lower or '教程' in title_lower:
                        score += 1
                    return score
                
                # 按评分排序
                python_resources.sort(key=score_resource, reverse=True)
            
            # 优先使用Python相关资源
            filtered_resources = python_resources + other_resources
            # 限制数量
            filtered_resources = filtered_resources[:limit]
        else:
            # 对于非Python主题，使用原始逻辑
            # 提取主题名称（去除难度级别部分）
            topic_name = topic.split(' ')[0].split('(')[0]
            
            # 定义资源评分函数，考虑学习成本和适合度
            def score_resource(res):
                score = 0
                title_lower = (res[1] or '').lower()
                resource_text = ''
                for i in range(1, min(5, len(res))):
                    if res[i]:
                        resource_text += str(res[i]) + ' '
                
                # 基础关键词加分
                if '基础' in title_lower or '入门' in title_lower or 'tutorial' in title_lower:
                    score += 2
                # 课程形式加分
                if '课程' in title_lower or '教程' in title_lower:
                    score += 1
                # 与主题相关性加分
                if topic_name in resource_text:
                    score += 1
                return score
            
            # 过滤并排序资源
            candidate_resources = []
            
            for res in resources:
                if res[0] not in used_ids:
                    # 确保资源难度与当前级别匹配
                    if level:
                        # 对于所有主题，都要考虑难度字段的限制
                        # 对于初级用户，只推荐初级资源
                        if level == '初级' and res[4] != '初级':
                            continue
                        # 对于中级用户，推荐初级和中级资源
                        elif level == '中级' and res[4] == '高级':
                            continue
                        # 对于高级用户，推荐所有级别资源
                    
                    # 检查资源是否与主题相关
                    resource_text = ''
                    for i in range(1, min(5, len(res))):
                        if res[i]:
                            resource_text += str(res[i]) + ' '
                    
                    if '编程基础' in topic:
                        # 对于编程基础主题，只推荐与编程相关的资源
                        programming_keywords = ['编程', '代码', '算法', '数据结构', '计算机', '技术', '前端', '后端', '开发', '软件', '程序', '语言', '语法', '逻辑', '调试', '版本控制', 'Git', 'Linux', '命令行', '终端', '编辑器', 'IDE', '环境', '配置', 'HTML', 'CSS', 'JavaScript', '前端开发']
                        unrelated_keywords = ['数学', '物理', '化学', '生物', '历史', '地理', '文学', '艺术', '音乐', '体育']
                        
                        # 检查是否包含编程相关关键词
                        has_programming_keyword = any(keyword in resource_text for keyword in programming_keywords)
                        # 检查是否包含不相关关键词
                        has_unrelated_keyword = any(keyword in resource_text for keyword in unrelated_keywords)
                        
                        # 只有包含编程相关关键词且不包含不相关关键词的资源才被推荐
                        if not has_programming_keyword or has_unrelated_keyword:
                            continue
                    # 对于前端开发主题，只推荐与前端相关的资源
                    elif topic_name == '前端开发':
                        frontend_keywords = ['html', 'css', 'javascript', '前端', 'web', '网页', '浏览器', 'dom', 'js', '前端开发']
                        has_frontend_keyword = any(keyword in resource_text.lower() for keyword in frontend_keywords)
                        if not has_frontend_keyword:
                            continue
                    # 对于数据分析主题，只推荐与数据分析相关的资源
                    elif topic_name == '数据分析':
                        data_keywords = ['数据', '分析', '统计', 'excel', 'python', 'pandas', 'numpy', '数据处理', '数据可视化']
                        has_data_keyword = any(keyword in resource_text.lower() for keyword in data_keywords)
                        if not has_data_keyword:
                            continue
                    
                    candidate_resources.append(res)
            
            # 按评分排序
            candidate_resources.sort(key=score_resource, reverse=True)
            
            # 限制数量
            filtered_resources = candidate_resources[:limit]
            
            # 对于Java、算法、深度学习、数据分析和机器学习主题，如果资源数量不足，只添加与用户水平匹配的资源
            if (topic_name in ['Java', '算法', '深度学习', '数据分析', '机器学习']) and len(filtered_resources) < limit:
                # 再次查询所有相关资源
                conn = sqlite3.connect('data/learning.db')
                cursor = conn.cursor()
                # 对于算法、深度学习、数据分析和机器学习，使用LIKE查询以获取更多相关资源
                if topic_name in ['算法', '深度学习', '数据分析', '机器学习']:
                    # 考虑难度级别
                    if level:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE (knowledge_point LIKE ? OR title LIKE ?) AND difficulty = ?
                        ''', ('%' + topic_name + '%', '%' + topic_name + '%', level))
                    else:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE knowledge_point LIKE ? OR title LIKE ?
                        ''', ('%' + topic_name + '%', '%' + topic_name + '%'))
                else:
                    # 对于Java，使用精确匹配
                    if level:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE knowledge_point = ? AND difficulty = ?
                        ''', (topic_name, level))
                    else:
                        cursor.execute('''
                            SELECT * FROM resources 
                            WHERE knowledge_point = ?
                        ''', (topic_name,))
                all_resources = cursor.fetchall()
                conn.close()
                
                # 添加未使用的资源，只添加与用户水平匹配的
                for res in all_resources:
                    if res[0] not in used_ids and res not in filtered_resources:
                        # 确保资源难度与当前级别匹配
                        if level:
                            if level == '初级' and res[4] != '初级':
                                continue
                            elif level == '中级' and res[4] == '高级':
                                continue
                            # 高级用户可以使用所有级别资源
                        filtered_resources.append(res)
                        if len(filtered_resources) >= limit:
                            break
                
                # 不再强制填充到limit数量，只推荐与用户水平匹配的资源
        
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
        
        # 定义水平优先级
        level_priority = {'初级': 1, '中级': 2, '高级': 3}
        current_priority = level_priority.get(current_level, 1)
        
        # 定义与编程相关的主题
        programming_topics = {'Python', 'Java', 'C++', '编程基础', '前端开发', 'JavaScript', 'Vue', 'React', 'Spring Boot', '系统编程', '算法', '数据结构'}
        
        # 定义数学相关主题
        math_topics = {'数学', '线性代数', '微积分', '概率论', '统计学'}
        
        def dfs(topic, level):
            if topic in visited:
                return
            
            visited.add(topic)
            
            # 获取前置知识
            prerequisites = self.kg.get(topic, {}).get('prerequisites', [])
            
            # 先处理前置知识
            for prereq in prerequisites:
                if prereq not in visited:
                    # 根据用户当前水平决定是否添加前置知识
                    # 如果用户水平是中级或高级，跳过初级前置知识
                    if current_priority >= 2:
                        # 跳过所有初级前置知识
                        continue
                    
                    # 只有当前置知识与编程相关时才添加
                    if target_topic in programming_topics and prereq not in programming_topics:
                        # 跳过与编程无关的前置知识
                        continue
                    
                    dfs(prereq, '初级')
            
            # 处理数学相关主题：如果已经添加了数学，就不再添加其分支主题
            has_math = any(item[0] == '数学' for item in path)
            if has_math and topic in math_topics and topic != '数学':
                return
            
            # 特殊处理：如果路径中已经有数学，就不再添加统计学
            if topic == '统计学':
                has_math = any(item[0] == '数学' for item in path)
                if has_math:
                    return
            
            # 添加当前主题到路径
            path.append((topic, level))
        
        # 开始构建路径
        dfs(target_topic, current_level)
        
        return path
    
    def _optimize_path(self, path, goal):
        """优化学习路径，根据目标调整顺序和内容"""
        optimized_path = []
        
        # 提取编程基础相关的项目
        programming_basics = [item for item in path if '编程基础' in item[0]]
        
        # 提取其他项目
        other_items = [item for item in path if item not in programming_basics]
        
        # 根据目标调整路径
        if goal == '找工作':
            # 找工作目标：优先核心技能，增加项目实践
            core_topics = ['Python', 'Java', 'C++', '前端开发', '数据分析', '机器学习']
            project_topics = ['项目开发', '实战']
            
            # 优先处理核心技能
            core_path = [item for item in other_items if any(core in item[0] for core in core_topics)]
            non_core_path = [item for item in other_items if item not in core_path]
            
            # 确保编程基础在最前面
            optimized_path = programming_basics + core_path + non_core_path
        
        elif goal == '项目开发':
            # 项目开发目标：提前引入项目实践
            # 确保编程基础在最前面
            optimized_path = programming_basics + other_items
            # 在适当位置插入项目实践
            if len(optimized_path) > 2:
                mid_point = len(optimized_path) // 2
                optimized_path.insert(mid_point, ('项目实践', '中级'))
        
        elif goal == '兴趣学习':
            # 兴趣学习目标：保持趣味性，减少理论
            # 确保编程基础在最前面
            non_theory_items = [item for item in other_items if '理论' not in item[0]]
            optimized_path = programming_basics + non_theory_items
        
        else:
            # 确保编程基础在最前面
            optimized_path = programming_basics + other_items
        
        return optimized_path
    
    def generate_learning_plan(self, topic, level, goal, time_budget=None, money_budget=None, time_per_week=10):
        """
        生成学习方案
        
        Args:
            topic: 学习主题
            level: 当前水平
            goal: 学习目标
            time_budget: 时间预算（小时）
            money_budget: 金钱预算（元）
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
            'time_budget': time_budget,
            'money_budget': money_budget,
            'total_time': 0,
            'total_weeks': 0,
            'stages': []
        }
        
        total_time = 0
        used_resource_ids = set()  # 用于跟踪已使用的资源ID，避免重复推荐
        
        # 计算每个阶段的学习时间，以便根据时间预算调整路径
        stage_times = []
        for stage_topic, stage_level in optimized_path:
            learning_time = self._get_learning_time(stage_topic, stage_level)
            stage_times.append((stage_topic, stage_level, learning_time))
        
        # 根据时间预算调整学习路径
        if time_budget:
            # 按重要性排序，核心技能优先
            core_topics = ['Python', 'Java', 'C++', '前端开发', '数据分析', '机器学习']
            stage_times.sort(key=lambda x: x[0] in core_topics, reverse=True)
            
            # 选择不超过时间预算的阶段
            selected_stages = []
            remaining_time = time_budget
            for stage_topic, stage_level, learning_time in stage_times:
                if remaining_time >= learning_time:
                    selected_stages.append((stage_topic, stage_level))
                    remaining_time -= learning_time
                else:
                    # 如果时间不够，只选择核心主题
                    if stage_topic in core_topics:
                        selected_stages.append((stage_topic, stage_level))
                        break
            
            # 重新排序，确保编程基础在最前面
            programming_basics = [s for s in selected_stages if '编程基础' in s[0]]
            other_stages = [s for s in selected_stages if s not in programming_basics]
            optimized_path = programming_basics + other_stages
        
        for i, (stage_topic, stage_level) in enumerate(optimized_path):
            # 获取资源，传递当前阶段的主题、已使用的资源ID、学习目标和金钱预算
            filtered_resources = self._get_resources_by_topic(
                stage_topic, stage_level, original_topic=stage_topic, 
                used_resource_ids=used_resource_ids, limit=3, goal=goal, money_budget=money_budget
            )
            
            # 记录使用的资源ID
            for res in filtered_resources:
                used_resource_ids.add(res[0])
            
            # 如果过滤后没有资源，尝试获取更多资源
            if not filtered_resources:
                # 尝试获取更多资源，不传递used_resource_ids，以获取所有可能的资源
                more_resources = self._get_resources_by_topic(
                    stage_topic, stage_level, original_topic=stage_topic, 
                    limit=5, goal=goal, money_budget=money_budget
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
            
            # 重新初始化随机数生成器的种子值，确保每次生成的学习时间都不同
            random.seed()
            
            # 根据资源的难度为每个资源生成随机学习时间
            learning_time = 0
            for res in filtered_resources:
                # 获取资源难度
                difficulty = res[4] if len(res) >= 5 else '初级'
                # 根据难度生成随机学习时间
                if difficulty == '初级':
                    resource_time = random.randint(40, 60)
                elif difficulty == '中级':
                    resource_time = random.randint(60, 80)
                elif difficulty == '高级':
                    resource_time = random.randint(80, 100)
                else:
                    resource_time = 50
                learning_time += resource_time
            total_time += learning_time
            
            # 计算需要的周数，保留小数点后一位
            weeks_needed = max(0.1, round(learning_time / time_per_week, 1))
            
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
        plan['total_weeks'] = max(0.1, round(total_time / time_per_week, 1))
        
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
