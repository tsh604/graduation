# database.py
import sqlite3
import os

def init_database():
    """初始化数据库，创建表并插入示例数据"""
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
     
    # 创建学习资源表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT,
            knowledge_point TEXT,
            difficulty TEXT,
            url TEXT,
            description TEXT
        )
    ''')
    
    # 创建用户对话历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialogues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_message TEXT,
            bot_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 检查是否已有数据
    cursor.execute('SELECT COUNT(*) FROM resources')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("📦 首次运行，插入150条学习资源...")
        
        # ===== 150条真实有效的学习资源 =====
        sample_resources = [
            # ===== 1. Python基础 (20条) =====
            ('Python基础教程', '视频', 'Python', '初级', 'https://www.runoob.com/python3/python3-tutorial.html', '菜鸟教程Python3，适合零基础入门'),
            ('Python进阶', '视频', 'Python', '中级', 'https://docs.python.org/3/', 'Python官方文档，深入学习'),
            ('廖雪峰Python教程', '课程', 'Python', '初级', 'https://www.liaoxuefeng.com/wiki/1016959663602400', '国内最受欢迎的Python教程'),
            ('Python Cookbook', '书籍', 'Python', '中级', 'https://python3-cookbook.readthedocs.io/zh-cn/latest/', 'Python进阶必备'),
            ('LeetCode Python题库', '文章', 'Python', '初级', 'https://leetcode.cn/problemset/all/?topicSlugs=python', 'Python算法练习'),
            ('Python函数式编程', '视频', 'Python', '中级', 'https://coolshell.cn/articles/10822.html', '函数式编程入门'),
            ('Python并发编程', '课程', 'Python', '高级', 'https://python-parallel-programmning-cookbook.readthedocs.io/', '并发编程指南'),
            ('Requests库文档', '视频', 'Python', '中级', 'https://requests.readthedocs.io/zh-cn/latest/', '网络爬虫必备'),
            ('Python 100天', '课程', 'Python', '初级', 'https://github.com/jackfrued/Python-100-Days', '从新手到大师的100天'),
            ('Python正则表达式', '文章', 'Python', '中级', 'https://www.runoob.com/python3/python3-reg-expressions.html', '正则表达式详解'),
            ('Flask Web开发', '课程', 'Python', '中级', 'https://flask.palletsprojects.com/', 'Flask官方教程'),
            ('Django入门', '视频', 'Python', '中级', 'https://docs.djangoproject.com/zh-hans/', 'Django官方文档'),
            ('Python爬虫教程', '课程', 'Python', '中级', 'https://scrapy.org/doc/', 'Scrapy框架教程'),
            ('NumPy教程', '视频', 'Python', '中级', 'https://numpy.org/doc/stable/user/quickstart.html', '科学计算基础'),
            ('Python单元测试', '文章', 'Python', '中级', 'https://docs.python.org/3/library/unittest.html', 'unittest框架使用'),
            ('Python装饰器', '视频', 'Python', '高级', 'https://realpython.com/primer-on-python-decorators/', '装饰器深入理解'),
            ('Python生成器', '文章', 'Python', '中级', 'https://realpython.com/introduction-to-python-generators/', '生成器与yield'),
            ('Python多线程', '课程', 'Python', '高级', 'https://realpython.com/python-concurrency/', '并发编程实战'),
            ('Python类型注解', '文章', 'Python', '中级', 'https://realpython.com/python-type-checking/', '类型检查入门'),
            ('Python项目结构', '视频', 'Python', '中级', 'https://realpython.com/python-application-layouts/', '项目组织最佳实践'),
            
            # ===== 2. 数据分析 (15条) =====
            ('Pandas官方文档', '课程', '数据分析', '中级', 'https://pandas.pydata.org/docs/', '数据分析核心工具'),
            ('Matplotlib教程', '视频', '数据分析', '中级', 'https://matplotlib.org/stable/tutorials/index.html', '数据可视化基础'),
            ('Kaggle Pandas课程', '课程', '数据分析', '中级', 'https://www.kaggle.com/learn/pandas', '实战Pandas'),
            ('数据清洗实战', '文章', '数据分析', '中级', 'https://realpython.com/python-data-cleaning-numpy-pandas/', '数据清洗指南'),
            ('Seaborn教程', '视频', '数据分析', '中级', 'https://seaborn.pydata.org/tutorial.html', '统计可视化'),
            ('Plotly入门', '课程', '数据分析', '中级', 'https://plotly.com/python/', '交互式图表'),
            ('数据预处理', '文章', '数据分析', '初级', 'https://www.kaggle.com/learn/data-cleaning', 'Kaggle数据清洗课'),
            ('Excel数据分析', '视频', '数据分析', '初级', 'https://support.microsoft.com/zh-cn/excel', 'Excel官方教程'),
            ('SQL数据分析', '课程', '数据分析', '中级', 'https://www.w3schools.com/sql/', 'SQL数据分析基础'),
            ('统计学基础', '视频', '数据分析', '初级', 'https://www.khanacademy.org/math/statistics-probability', '可汗学院统计学'),
            ('Tableau入门', '课程', '数据分析', '中级', 'https://www.tableau.com/learn/training', '可视化工具'),
            ('Power BI教程', '视频', '数据分析', '中级', 'https://docs.microsoft.com/zh-cn/power-bi/', '微软官方教程'),
            ('时间序列分析', '文章', '数据分析', '高级', 'https://otexts.com/fpp3/', '预测原理与实践'),
            ('A/B测试指南', '课程', '数据分析', '高级', 'https://www.optimizely.com/optimization-glossary/ab-testing/', 'AB测试详解'),
            ('数据思维', '书籍', '数据分析', '初级', 'https://www.amazon.com/Data-Science-Business-Data-Analytic-Thinking/dp/1449361323', '数据科学思维'),
            
            # ===== 3. 机器学习 (20条) =====
            ('Scikit-learn教程', '课程', '机器学习', '中级', 'https://scikit-learn.org/stable/tutorial/index.html', '机器学习经典库'),
            ('PyTorch官方教程', '视频', '深度学习', '高级', 'https://pytorch.org/tutorials/', '深度学习框架'),
            ('Kaggle机器学习入门', '课程', '机器学习', '中级', 'https://www.kaggle.com/learn/intro-to-machine-learning', '实战入门'),
            ('TensorFlow教程', '视频', '深度学习', '高级', 'https://www.tensorflow.org/tutorials', 'Google深度学习框架'),
            ('机器学习实战', '书籍', '机器学习', '中级', 'https://www.manning.com/books/machine-learning-in-action', '实战项目'),
            ('吴恩达机器学习', '课程', '机器学习', '初级', 'https://www.coursera.org/learn/machine-learning', '经典入门课程'),
            ('李宏毅机器学习', '视频', '机器学习', '中级', 'https://speech.ee.ntu.edu.tw/~hylee/ml/2021-spring.php', '中文课程'),
            ('Fast.ai教程', '课程', '深度学习', '中级', 'https://course.fast.ai/', '实战深度学习'),
            ('机器学习公式详解', '书籍', '机器学习', '高级', 'https://github.com/datawhalechina/pumpkin-book', '西瓜书公式推导'),
            ('XGBoost文档', '文章', '机器学习', '高级', 'https://xgboost.readthedocs.io/', '梯度提升框架'),
            ('LightGBM教程', '视频', '机器学习', '高级', 'https://lightgbm.readthedocs.io/', '微软高效框架'),
            ('神经网络入门', '课程', '深度学习', '中级', 'https://www.3blue1brown.com/topics/neural-networks', '3Blue1Brown动画讲解'),
            ('卷积神经网络', '视频', '深度学习', '高级', 'https://cs231n.stanford.edu/', '斯坦福CS231n'),
            ('自然语言处理', '课程', '深度学习', '高级', 'https://web.stanford.edu/class/cs224n/', '斯坦福CS224n'),
            ('强化学习', '视频', '机器学习', '高级', 'https://www.davidsilver.uk/teaching/', 'David Silver课程'),
            ('特征工程', '文章', '机器学习', '中级', 'https://www.kaggle.com/learn/feature-engineering', 'Kaggle特征工程'),
            ('模型调参', '课程', '机器学习', '高级', 'https://scikit-learn.org/stable/modules/grid_search.html', '网格搜索教程'),
            ('模型评估', '文章', '机器学习', '中级', 'https://scikit-learn.org/stable/modules/model_evaluation.html', '评估指标详解'),
            ('机器学习系统设计', '书籍', '机器学习', '高级', 'https://github.com/chiphuyen/machine-learning-systems-design', '系统设计指南'),
            ('MLOps基础', '视频', '机器学习', '高级', 'https://ml-ops.org/', 'MLOps最佳实践'),
            
            # ===== 4. Java开发 (15条) =====
            ('Java基础教程', '视频', 'Java', '初级', 'https://www.runoob.com/java/java-tutorial.html', '菜鸟教程Java入门'),
            ('Oracle Java文档', '课程', 'Java', '中级', 'https://docs.oracle.com/en/java/', '官方文档'),
            ('Spring官方指南', '课程', 'Java', '中级', 'https://spring.io/guides', 'Spring Boot入门'),
            ('JVM规范', '书籍', 'Java', '高级', 'https://docs.oracle.com/javase/specs/jvms/se8/html/', '深入理解JVM'),
            ('Java并发编程', '视频', 'Java', '高级', 'https://www.baeldung.com/java-concurrency', '并发编程实战'),
            ('Maven教程', '课程', 'Java', '中级', 'https://maven.apache.org/guides/', '项目构建工具'),
            ('Gradle入门', '视频', 'Java', '中级', 'https://gradle.org/guides/', '自动化构建'),
            ('MyBatis文档', '文章', 'Java', '中级', 'https://mybatis.org/mybatis-3/zh/', '持久层框架'),
            ('Hibernate教程', '课程', 'Java', '中级', 'https://hibernate.org/orm/documentation/', 'ORM框架'),
            ('Java 8新特性', '视频', 'Java', '中级', 'https://www.oracle.com/java/technologies/javase/8-whats-new.html', 'Lambda表达式'),
            ('Java性能调优', '文章', 'Java', '高级', 'https://www.baeldung.com/java-performance', '性能优化指南'),
            ('设计模式', '课程', 'Java', '中级', 'https://www.baeldung.com/design-patterns-series', 'Java实现设计模式'),
            ('Java单元测试', '视频', 'Java', '中级', 'https://junit.org/junit5/docs/current/user-guide/', 'JUnit5教程'),
            ('Mockito使用', '文章', 'Java', '中级', 'https://site.mockito.org/', 'Mock框架'),
            ('Java网络编程', '课程', 'Java', '中级', 'https://www.baeldung.com/java-networking', 'Socket编程'),
            
            # ===== 5. 前端开发 (20条) =====
            ('MDN Web文档', '课程', '前端', '初级', 'https://developer.mozilla.org/zh-CN/docs/Learn', '最权威的前端教程'),
            ('现代JavaScript教程', '视频', '前端', '中级', 'https://zh.javascript.info/', '从基础到高级'),
            ('Vue官方教程', '视频', '前端', '中级', 'https://cn.vuejs.org/tutorial/', '渐进式框架'),
            ('React官方文档', '视频', '前端', '中级', 'https://react.dev/learn', '组件化开发'),
            ('Webpack官方指南', '课程', '前端', '高级', 'https://webpack.js.org/guides/', '模块打包工具'),
            ('CSS教程', '文章', '前端', '初级', 'https://www.w3schools.com/css/', '样式表基础'),
            ('HTML5教程', '视频', '前端', '初级', 'https://www.w3schools.com/html/', '网页结构'),
            ('TypeScript手册', '课程', '前端', '中级', 'https://www.typescriptlang.org/docs/', 'JavaScript超集'),
            ('Node.js教程', '视频', '前端', '中级', 'https://nodejs.org/en/docs/', '服务端JavaScript'),
            ('npm文档', '文章', '前端', '初级', 'https://docs.npmjs.com/', '包管理工具'),
            ('Git教程', '视频', '前端', '初级', 'https://git-scm.com/book/zh/v2', '版本控制'),
            ('WebAssembly', '课程', '前端', '高级', 'https://webassembly.org/', '高性能Web应用'),
            ('PWA教程', '视频', '前端', '中级', 'https://web.dev/progressive-web-apps/', '渐进式Web应用'),
            ('浏览器工作原理', '文章', '前端', '高级', 'https://web.dev/howbrowserswork/', '深入理解浏览器'),
            ('前端性能优化', '课程', '前端', '高级', 'https://web.dev/performance/', '性能最佳实践'),
            ('Web安全指南', '视频', '前端', '中级', 'https://web.dev/secure/', '网络安全基础'),
            ('CSS Grid布局', '文章', '前端', '中级', 'https://css-tricks.com/snippets/css/complete-guide-grid/', '网格布局指南'),
            ('Flexbox教程', '视频', '前端', '中级', 'https://css-tricks.com/snippets/css/a-guide-to-flexbox/', '弹性布局'),
            ('Sass入门', '课程', '前端', '中级', 'https://sass-lang.com/guide/', 'CSS预处理器'),
            ('Web组件开发', '视频', '前端', '高级', 'https://developer.mozilla.org/zh-CN/docs/Web/Web_Components', '自定义元素'),
            
            # ===== 6. 数据库 (15条) =====
            ('MySQL官方教程', '文章', '数据库', '中级', 'https://dev.mysql.com/doc/refman/8.0/en/tutorial.html', '关系型数据库'),
            ('Redis官方文档', '文章', '数据库', '中级', 'https://redis.io/docs/latest/', '内存数据库'),
            ('MongoDB教程', '视频', '数据库', '中级', 'https://www.mongodb.com/docs/manual/tutorial/', '文档数据库'),
            ('PostgreSQL文档', '课程', '数据库', '中级', 'https://www.postgresql.org/docs/', '高级关系型数据库'),
            ('SQLite教程', '视频', '数据库', '初级', 'https://www.sqlite.org/docs.html', '嵌入式数据库'),
            ('数据库设计', '文章', '数据库', '中级', 'https://www.w3schools.com/sql/sql_ref_database.asp', '范式设计'),
            ('SQL优化', '课程', '数据库', '高级', 'https://use-the-index-luke.com/', '索引优化指南'),
            ('事务ACID', '视频', '数据库', '中级', 'https://www.postgresql.org/docs/current/mvvm.html', '事务处理'),
            ('Elasticsearch', '课程', '数据库', '高级', 'https://www.elastic.co/guide/index.html', '搜索引擎'),
            ('Cassandra教程', '视频', '数据库', '高级', 'https://cassandra.apache.org/doc/latest/', '分布式数据库'),
            ('Neo4j图数据库', '课程', '数据库', '高级', 'https://neo4j.com/docs/', '图数据库'),
            ('InfluxDB时序数据库', '视频', '数据库', '高级', 'https://docs.influxdata.com/influxdb/', '时序数据'),
            ('数据库分片', '文章', '数据库', '高级', 'https://www.mongodb.com/features/database-sharding', '分片技术'),
            ('备份与恢复', '课程', '数据库', '中级', 'https://dev.mysql.com/doc/refman/8.0/en/backup-and-recovery.html', '数据安全'),
            ('NoSQL入门', '视频', '数据库', '中级', 'https://www.mongodb.com/nosql-explained', 'NoSQL详解'),
            
            # ===== 7. 算法与数据结构 (10条) =====
            ('GeeksforGeeks算法', '课程', '算法', '中级', 'https://www.geeksforgeeks.org/data-structures/', '数据结构大全'),
            ('LeetCode题库', '视频', '算法', '高级', 'https://leetcode.cn/problemset/all/', '算法练习平台'),
            ('OI Wiki', '文章', '算法', '高级', 'https://oi-wiki.org/', '竞赛算法'),
            ('算法导论', '书籍', '算法', '高级', 'https://mitpress.mit.edu/books/introduction-algorithms', '经典教材'),
            ('可视化算法', '视频', '算法', '初级', 'https://visualgo.net/', '动画演示'),
            ('排序算法', '课程', '算法', '中级', 'https://www.toptal.com/developers/sorting-algorithms', '排序可视化'),
            ('动态规划', '文章', '算法', '高级', 'https://www.geeksforgeeks.org/dynamic-programming/', 'DP详解'),
            ('图论算法', '视频', '算法', '高级', 'https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/', '图算法'),
            ('字符串匹配', '课程', '算法', '中级', 'https://www.geeksforgeeks.org/algorithms-gq/string-algorithms/', 'KMP算法'),
            ('剑指Offer', '书籍', '算法', '中级', 'https://leetcode.cn/problem-list/xb9nqhhg/', '面试经典'),
            
            # ===== 8. C++ (10条) =====
            ('C++基础教程', '视频', 'C++', '初级', 'https://www.runoob.com/cplusplus/cpp-tutorial.html', '菜鸟教程C++'),
            ('C++参考手册', '课程', 'C++', '中级', 'https://zh.cppreference.com/', '标准库文档'),
            ('C++内存管理', '文章', 'C++', '高级', 'https://learn.microsoft.com/zh-cn/cpp/cpp/memory-management', '内存管理'),
            ('C++ STL教程', '视频', 'C++', '中级', 'https://www.geeksforgeeks.org/the-c-standard-template-library-stl/', '标准模板库'),
            ('C++11新特性', '课程', 'C++', '中级', 'https://www.geeksforgeeks.org/c-11-vs-c-14-vs-c-17/', '现代C++'),
            ('C++多线程', '视频', 'C++', '高级', 'https://www.geeksforgeeks.org/multithreading-in-cpp/', '并发编程'),
            ('C++设计模式', '文章', 'C++', '高级', 'https://www.geeksforgeeks.org/design-patterns-in-cpp/', '设计模式实现'),
            ('C++性能优化', '课程', 'C++', '高级', 'https://www.geeksforgeeks.org/optimization-techniques-in-c/', '优化技巧'),
            ('C++智能指针', '视频', 'C++', '中级', 'https://www.geeksforgeeks.org/smart-pointers-cpp/', '内存管理'),
            ('C++模板元编程', '课程', 'C++', '高级', 'https://www.geeksforgeeks.org/templates-cpp/', '模板编程'),
            
            # ===== 9. Linux与运维 (10条) =====
            ('Linux教程', '视频', 'Linux', '初级', 'https://www.runoob.com/linux/linux-tutorial.html', 'Linux基础'),
            ('Shell脚本教程', '文章', 'Linux', '中级', 'https://www.shellscript.sh/', '脚本编程'),
            ('Docker官方教程', '课程', '运维', '中级', 'https://docs.docker.com/get-started/', '容器化'),
            ('K8s官方教程', '视频', '运维', '高级', 'https://kubernetes.io/docs/tutorials/', '容器编排'),
            ('Linux命令大全', '文章', 'Linux', '初级', 'https://www.geeksforgeeks.org/linux-commands/', '常用命令'),
            ('Vim教程', '视频', 'Linux', '初级', 'https://www.vim.org/docs.php', '编辑器之神'),
            ('Nginx配置', '课程', '运维', '中级', 'https://nginx.org/en/docs/', 'Web服务器'),
            ('Jenkins教程', '视频', '运维', '中级', 'https://www.jenkins.io/doc/', 'CI/CD'),
            ('Ansible文档', '课程', '运维', '中级', 'https://docs.ansible.com/', '自动化运维'),
            ('Prometheus监控', '视频', '运维', '高级', 'https://prometheus.io/docs/', '监控系统'),
            
            # ===== 10. 开发工具 (15条) =====
            ('VS Code文档', '文章', '工具', '初级', 'https://code.visualstudio.com/docs', '编辑器'),
            ('Postman文档', '视频', '工具', '中级', 'https://learning.postman.com/docs/', 'API测试'),
            ('Git官方文档', '课程', '工具', '初级', 'https://git-scm.com/doc', '版本控制'),
            ('GitHub指南', '视频', '工具', '初级', 'https://guides.github.com/', '代码托管'),
            ('Docker Compose', '课程', '工具', '中级', 'https://docs.docker.com/compose/', '容器编排'),
            ('Makefile教程', '文章', '工具', '中级', 'https://www.gnu.org/software/make/manual/', '构建工具'),
            ('CMake文档', '视频', '工具', '中级', 'https://cmake.org/documentation/', '跨平台构建'),
            ('Jupyter教程', '课程', '工具', '初级', 'https://jupyter.org/documentation', '交互式编程'),
            ('PyCharm指南', '视频', '工具', '初级', 'https://www.jetbrains.com/pycharm/learn/', 'Python IDE'),
            ('IntelliJ教程', '课程', '工具', '中级', 'https://www.jetbrains.com/idea/learn/', 'Java IDE'),
            ('Chrome DevTools', '视频', '工具', '中级', 'https://developer.chrome.com/docs/devtools/', '前端调试'),
            ('Fiddler教程', '文章', '工具', '中级', 'https://docs.telerik.com/fiddler/', '抓包工具'),
            ('Charles使用', '视频', '工具', '中级', 'https://www.charlesproxy.com/documentation/', 'HTTP代理'),
            ('Sublime Text', '课程', '工具', '初级', 'https://www.sublimetext.com/docs/', '轻量编辑器'),
            ('Zsh配置', '文章', '工具', '中级', 'https://ohmyz.sh/', '终端美化'),
        ]
        
        cursor.executemany('''
            INSERT INTO resources (title, type, knowledge_point, difficulty, url, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_resources)
        
        conn.commit()
        
        # 显示插入结果
        cursor.execute('SELECT MIN(id), MAX(id), COUNT(*) FROM resources')
        min_id, max_id, total = cursor.fetchone()
        print(f"✅ 成功插入 {total} 条学习资源")
        print(f"✅ 资源ID从 {min_id} 到 {max_id}")
        
    else:
        print(f"📚 数据库已有 {count} 条数据，跳过插入")
        cursor.execute('SELECT MIN(id), MAX(id) FROM resources')
        min_id, max_id = cursor.fetchone()
        print(f"💡 当前资源ID范围: {min_id} 到 {max_id}")
    
    conn.close()
    print("✅ 数据库初始化完成！")


def get_resources_by_knowledge(knowledge_point):
    """根据知识点查询资源"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM resources WHERE knowledge_point LIKE ? OR description LIKE ?
    ''', ('%' + knowledge_point + '%', '%' + knowledge_point + '%'))
    results = cursor.fetchall()
    conn.close()
    return results


def get_resources_by_knowledge_exact(knowledge_point):
    """精确匹配知识点查询（用于优先推荐）"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM resources WHERE knowledge_point = ?
    ''', (knowledge_point,))
    results = cursor.fetchall()
    conn.close()
    return results


def save_dialogue(user_id, user_message, bot_response):
    """保存对话记录"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dialogues (user_id, user_message, bot_response)
        VALUES (?, ?, ?)
    ''', (user_id, user_message, bot_response))
    conn.commit()
    conn.close()


def get_all_topics():
    """获取所有知识点"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT knowledge_point FROM resources')
    topics = [row[0] for row in cursor.fetchall()]
    conn.close()
    return topics


def reset_database():
    """彻底重置数据库（删除后重建）"""
    print("⚠️  警告：此操作将删除所有数据！")
    confirm = input("是否继续？(y/n): ")
    
    if confirm.lower() == 'y':
        # 删除数据库文件
        db_path = 'data/learning.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ 已删除 {db_path}")
        
        # 重新初始化
        init_database()
        print("🎉 数据库重置完成！")
    else:
        print("❌ 操作已取消")


if __name__ == '__main__':
    import sys
    
    # 如果带参数 --reset 则重置数据库
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_database()
        
        # 测试查询
        print("\n" + "="*50)
        print("🔍 测试查询功能")
        print("="*50)
        
        print("\n=== Python相关资源 ===")
        python_resources = get_resources_by_knowledge('Python')
        print(f"找到 {len(python_resources)} 个Python相关资源")
        for r in python_resources[:5]:
            print(f"  - {r[1]} ({r[2]}) - {r[3]}")
        
        print("\n=== 数据分析相关资源 ===")
        data_resources = get_resources_by_knowledge('数据分析')
        print(f"找到 {len(data_resources)} 个数据分析相关资源")
        for r in data_resources[:5]:
            print(f"  - {r[1]} ({r[2]}) - {r[3]}")
        
        print("\n=== 所有知识点 ===")
        topics = get_all_topics()
        print(f"知识点列表 ({len(topics)}个):")
        for i, topic in enumerate(sorted(topics), 1):
            print(f"  {i}. {topic}")