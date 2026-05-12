# database.py
import sqlite3
import os
from datetime import datetime, timedelta

def init_database():
    """初始化数据库，创建表并插入示例数据"""
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/learning.db')
    conn.text_factory = str
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
            description TEXT,
            learning_time REAL,
            price REAL
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
    
    # 创建推荐得分表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendation_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_id TEXT,
            resource_id INTEGER,
            resource_name TEXT,
            score REAL,
            relevance_cost REAL,
            format_cost REAL,
            goal_cost REAL,
            time_cost REAL,
            price_cost REAL,
            recommended_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建收藏表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES resources(id),
            UNIQUE(user_id, resource_id)
        )
    ''')
    
    # 创建用户偏好设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            save_history INTEGER DEFAULT 1,
            current_learning_resource_id INTEGER,
            current_learning_status TEXT DEFAULT 'idle',
            current_learning_duration INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (current_learning_resource_id) REFERENCES resources(id)
        )
    ''')
    
    # 创建学习记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            start_time DATETIME,
            end_time DATETIME,
            duration INTEGER DEFAULT 0,
            progress REAL DEFAULT 0,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES resources(id)
        )
    ''')
    
    # 创建每日签到表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_checkin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            checkin_date DATE NOT NULL,
            streak_days INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, checkin_date)
        )
    ''')
    
    # 检查是否已有数据
    cursor.execute('SELECT COUNT(*) FROM resources')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("首次运行，插入150条学习资源...")
        
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
            
            # ===== 10. 数学基础 (10条) =====
            ('线性代数入门', '视频', '线性代数', '初级', 'https://www.khanacademy.org/math/linear-algebra', 'Khan Academy线性代数课程'),
            ('线性代数基础', '课程', '线性代数', '初级', 'https://www.coursera.org/learn/linear-algebra-machine-learning', '机器学习中的线性代数'),
            ('微积分入门', '视频', '微积分', '初级', 'https://www.khanacademy.org/math/calculus-1', 'Khan Academy微积分课程'),
            ('微积分基础', '课程', '微积分', '初级', 'https://www.coursera.org/learn/calculus-1', 'Coursera微积分课程'),
            ('统计学基础', '视频', '统计学', '初级', 'https://www.khanacademy.org/math/statistics-probability', 'Khan Academy统计学课程'),
            ('概率论基础', '课程', '概率论', '初级', 'https://www.coursera.org/learn/probability-intro', 'Coursera概率论课程'),
            ('数学分析基础', '书籍', '数学', '初级', 'https://book.douban.com/subject/26899182/', '数学分析入门'),
            ('离散数学', '课程', '数学', '中级', 'https://www.coursera.org/learn/discrete-mathematics', '离散数学基础'),
            ('数论基础', '文章', '数学', '中级', 'https://www.geeksforgeeks.org/number-theory-basics/', '数论入门'),
            ('数学建模', '课程', '数学', '中级', 'https://www.coursera.org/learn/mathematical-modeling', '数学建模基础'),
            
            # ===== 11. 开发工具 (15条) =====
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
        
        import random
        
        # 为每个资源添加学习时间和价格数据
        resources_with_time_and_price = []
        for resource in sample_resources:
            # 为不同类型和难度的资源设置合理的学习时间和价格
            title, resource_type, knowledge_point, difficulty, url, description = resource
            
            # 按照用户要求的范围设置学习时间（小时）
            if difficulty == '初级':
                learning_time = random.randint(40, 60)
            elif difficulty == '中级':
                learning_time = random.randint(60, 80)
            elif difficulty == '高级':
                learning_time = random.randint(80, 100)
            else:
                learning_time = random.randint(50, 70)  # 默认范围
            
            # 按照用户要求的范围设置价格（元）
            price = random.randint(50, 100)
            
            # 添加到新列表
            resources_with_time_and_price.append(resource + (learning_time, price))
        
        # 插入数据，包括学习时间和价格
        cursor.executemany('''
            INSERT INTO resources (title, type, knowledge_point, difficulty, url, description, learning_time, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', resources_with_time_and_price)
        
        conn.commit()
        
        # 显示插入结果
        cursor.execute('SELECT MIN(id), MAX(id), COUNT(*) FROM resources')
        min_id, max_id, total = cursor.fetchone()
        print(f"成功插入 {total} 条学习资源")
        print(f"资源ID从 {min_id} 到 {max_id}")
        
    else:
        print(f"数据库已有 {count} 条数据，跳过插入")
        cursor.execute('SELECT MIN(id), MAX(id) FROM resources')
        min_id, max_id = cursor.fetchone()
        print(f"当前资源ID范围: {min_id} 到 {max_id}")
    
    conn.close()
    print("数据库初始化完成！")


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
    print("警告：此操作将删除所有数据！")
    # 自动确认重置
    confirm = 'y'
    
    if confirm.lower() == 'y':
        # 删除数据库文件
        db_path = 'data/learning.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"已删除 {db_path}")
        
        # 重新初始化
        init_database()
        print("数据库重置完成！")
    else:
        print("操作已取消")


def is_dialogue_exists(user_id, user_message, bot_response):
    """检查对话是否已存在于数据库"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM dialogues WHERE user_id = ? AND user_message = ? AND bot_response = ?',
        (user_id, user_message, bot_response)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def clear_user_dialogues():
    """清空对话历史表并重置自增ID"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM dialogues')
    # 重置自增计数器，使ID从1开始
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="dialogues"')
    conn.commit()
    conn.close()
    print("对话历史已清空，ID已重置")

# 用户相关函数
def register_user(username, email, password):
    """注册新用户"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, password)
        )
        conn.commit()
        return True, "注册成功"
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed: users.username' in str(e):
            return False, "用户名已存在"
        elif 'UNIQUE constraint failed: users.email' in str(e):
            return False, "邮箱已被注册"
        else:
            return False, f"注册失败: {e}"
    except Exception as e:
        return False, f"注册失败: {e}"
    finally:
        conn.close()

def verify_user(email, password):
    """验证用户凭证"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'SELECT id, username FROM users WHERE email = ? AND password = ?',
            (email, password)
        )
        user = cursor.fetchone()
        if user:
            # 更新最后登录时间（使用本地时间）
            user_id = user[0]
            from datetime import datetime
            local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (local_time, user_id)
            )
            conn.commit()
            return True, user
        else:
            return False, "邮箱或密码错误"
    except Exception as e:
        return False, f"验证失败: {e}"
    finally:
        conn.close()

def get_user_by_email(email):
    """根据邮箱获取用户信息"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, username, email FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return None
    finally:
        conn.close()

def get_user_by_id(user_id):
    """根据ID获取用户信息"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, username, email, created_at, last_login FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return None
    finally:
        conn.close()

def update_user(user_id, username=None, email=None):
    """更新用户信息"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        if username and email:
            cursor.execute('UPDATE users SET username = ?, email = ? WHERE id = ?', 
                         (username, email, user_id))
        elif username:
            cursor.execute('UPDATE users SET username = ? WHERE id = ?', 
                         (username, user_id))
        elif email:
            cursor.execute('UPDATE users SET email = ? WHERE id = ?', 
                         (email, user_id))
        
        conn.commit()
        return True, "更新成功"
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if 'UNIQUE constraint failed: users.username' in str(e):
            return False, "用户名已存在"
        elif 'UNIQUE constraint failed: users.email' in str(e):
            return False, "邮箱已被使用"
        else:
            return False, f"更新失败: {e}"
    except Exception as e:
        print(f"更新用户信息失败: {e}")
        conn.rollback()
        return False, f"更新失败: {e}"
    finally:
        conn.close()

def update_password(user_id, old_password, new_password):
    """修改密码"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 先验证旧密码
        cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result:
            return False, "用户不存在"
        
        if result[0] != old_password:
            return False, "旧密码不正确"
        
        # 更新密码
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
        conn.commit()
        return True, "密码修改成功"
    except Exception as e:
        print(f"修改密码失败: {e}")
        conn.rollback()
        return False, f"修改密码失败: {e}"
    finally:
        conn.close()

def reset_password_by_email(email, new_password):
    """通过邮箱重置密码（忘记密码功能）"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 检查邮箱是否存在
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        
        if not result:
            return False, "该邮箱未注册"
        
        # 更新密码
        cursor.execute('UPDATE users SET password = ? WHERE email = ?', (new_password, email))
        conn.commit()
        return True, "密码重置成功"
    except Exception as e:
        print(f"重置密码失败: {e}")
        conn.rollback()
        return False, f"重置密码失败: {e}"
    finally:
        conn.close()

def delete_user(user_id):
    """删除用户账户"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 删除用户的收藏
        cursor.execute('DELETE FROM collections WHERE user_id = ?', (user_id,))
        
        # 删除用户的对话历史
        cursor.execute('DELETE FROM dialogues WHERE user_id = ?', (user_id,))
        
        # 删除用户偏好设置
        cursor.execute('DELETE FROM user_preferences WHERE user_id = ?', (user_id,))
        
        # 删除用户
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        return True, "账户删除成功"
    except Exception as e:
        print(f"删除账户失败: {e}")
        conn.rollback()
        return False, f"删除账户失败: {e}"
    finally:
        conn.close()

def get_user_preferences(user_id):
    """获取用户偏好设置"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT save_history FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            return {'save_history': bool(result[0])}
        else:
            # 如果没有设置，返回默认值
            return {'save_history': True}
    except Exception as e:
        print(f"获取用户偏好失败: {e}")
        return {'save_history': True}
    finally:
        conn.close()

def set_user_preferences(user_id, save_history=None):
    """设置用户偏好"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 先检查是否已有记录
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            # 更新现有记录
            if save_history is not None:
                cursor.execute('UPDATE user_preferences SET save_history = ? WHERE user_id = ?', 
                             (int(save_history), user_id))
        else:
            # 插入新记录
            cursor.execute('INSERT INTO user_preferences (user_id, save_history) VALUES (?, ?)', 
                         (user_id, int(save_history) if save_history is not None else 1))
        
        conn.commit()
        return True, "设置成功"
    except Exception as e:
        print(f"设置用户偏好失败: {e}")
        conn.rollback()

def get_current_learning_state(user_id):
    """获取用户当前学习状态"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT current_learning_resource_id, current_learning_status, current_learning_duration, current_learning_resource_name
            FROM user_preferences 
            WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        if result:
            resource_id = result[0]
            # 从learning_records获取当前进度
            cursor.execute('''
                SELECT progress FROM learning_records
                WHERE user_id = ? AND resource_id = ? AND end_time IS NULL
            ''', (user_id, resource_id))
            progress_result = cursor.fetchone()
            
            return {
                'resource_id': resource_id,
                'status': result[1],
                'duration': result[2] or 0,
                'resource_name': result[3],
                'progress': progress_result[0] if progress_result else 0.0
            }
        return None
    except Exception as e:
        print(f"获取学习状态失败: {e}")
        return None
    finally:
        conn.close()

def update_learning_state(user_id, resource_id, status, duration=0, resource_name=None):
    """更新用户学习状态"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 先检查是否已有记录
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            # 更新现有记录
            cursor.execute('''
                UPDATE user_preferences 
                SET current_learning_resource_id = ?, current_learning_status = ?, current_learning_duration = ?, current_learning_resource_name = ?
                WHERE user_id = ?
            ''', (resource_id, status, duration, resource_name, user_id))
        else:
            # 插入新记录
            cursor.execute('''
                INSERT INTO user_preferences (user_id, save_history, current_learning_resource_id, current_learning_status, current_learning_duration, current_learning_resource_name)
                VALUES (?, 1, ?, ?, ?, ?)
            ''', (user_id, resource_id, status, duration, resource_name))
        
        conn.commit()
        return True, "学习状态已更新"
    except Exception as e:
        print(f"更新学习状态失败: {e}")
        conn.rollback()
        return False, f"更新失败: {e}"
    finally:
        conn.close()

def clear_learning_state(user_id):
    """清除用户学习状态（登出时调用）"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE user_preferences 
            SET current_learning_resource_id = NULL, current_learning_status = 'idle', current_learning_duration = 0
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        return True, "学习状态已清除"
    except Exception as e:
        print(f"清除学习状态失败: {e}")
        conn.rollback()
        return False, f"清除失败: {e}"
    finally:
        conn.close()

def clear_user_history(user_id):
    """清除用户历史记录，并重新排序后续记录的ID"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 步骤1：找到被删除用户的所有记录的ID
        cursor.execute('SELECT id FROM dialogues WHERE user_id = ? ORDER BY id', (user_id,))
        deleted_ids = [row[0] for row in cursor.fetchall()]
        
        if not deleted_ids:
            conn.commit()
            return True, "没有需要清除的记录"
        
        # 步骤2：删除该用户的记录
        cursor.execute('DELETE FROM dialogues WHERE user_id = ?', (user_id,))
        
        # 步骤3：找出所有大于被删除记录中最小ID的记录
        min_deleted_id = min(deleted_ids)
        max_deleted_id = max(deleted_ids)
        deleted_count = len(deleted_ids)
        
        # 步骤4：将后续记录的ID往前移动
        cursor.execute('''
            UPDATE dialogues 
            SET id = id - ? 
            WHERE id > ?
        ''', (deleted_count, max_deleted_id))
        
        # 步骤5：重新设置自增计数器，使新记录从当前最大ID+1开始
        cursor.execute('SELECT MAX(id) FROM dialogues')
        max_id = cursor.fetchone()[0]
        
        if max_id:
            cursor.execute('UPDATE sqlite_sequence SET seq = ? WHERE name = "dialogues"', (max_id,))
        else:
            cursor.execute('DELETE FROM sqlite_sequence WHERE name = "dialogues"')
        
        conn.commit()
        return True, f"已清除{deleted_count}条记录，后续记录ID已重新排序"
    except Exception as e:
        print(f"清除历史记录失败: {e}")
        conn.rollback()
        return False, f"清除失败: {e}"
    finally:
        conn.close()

def get_user_dialogues(user_id):
    """获取用户的对话历史（带行号，从1开始）"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 使用ROW_NUMBER()为每个用户的对话添加行号（从1开始）
        cursor.execute('''
            SELECT user_message, bot_response, 
                   ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp) as row_num
            FROM dialogues 
            WHERE user_id = ? 
            ORDER BY timestamp
        ''', (user_id,))
        results = cursor.fetchall()
        
        dialogues = []
        for row in results:
            dialogues.append({
                'user_message': row[0],
                'bot_response': row[1],
                'row_num': row[2]  # 添加行号，每个用户从1开始
            })
        
        return dialogues
    except Exception as e:
        print(f"获取对话历史失败: {e}")
        return []
    finally:
        conn.close()

# 收藏相关函数
def add_collection(user_id, resource_id):
    """添加收藏"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO collections (user_id, resource_id) VALUES (?, ?)',
            (user_id, resource_id)
        )
        conn.commit()
        return True, "收藏成功"
    except sqlite3.IntegrityError:
        return False, "已收藏过该资源"
    except Exception as e:
        return False, f"收藏失败: {e}"
    finally:
        conn.close()

def remove_collection(user_id, resource_id):
    """取消收藏"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 首先获取要删除的收藏记录的id
        cursor.execute(
            'SELECT id FROM collections WHERE user_id = ? AND resource_id = ?',
            (user_id, resource_id)
        )
        result = cursor.fetchone()
        if not result:
            return False, "未找到收藏记录"
        
        deleted_id = result[0]
        
        # 删除这条记录
        cursor.execute(
            'DELETE FROM collections WHERE user_id = ? AND resource_id = ?',
            (user_id, resource_id)
        )
        conn.commit()
        
        # 对所有id大于删除id的记录，将它们的id减1
        cursor.execute(
            'UPDATE collections SET id = id - 1 WHERE id > ?',
            (deleted_id,)
        )
        conn.commit()
        
        # 重置AUTOINCREMENT计数器
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="collections"')
        cursor.execute('INSERT INTO sqlite_sequence (name, seq) VALUES ("collections", (SELECT COALESCE(MAX(id), 0) FROM collections))')
        conn.commit()
        
        return True, "取消收藏成功"
    except Exception as e:
        return False, f"取消收藏失败: {e}"
    finally:
        conn.close()

def get_user_collections(user_id):
    """获取用户的收藏列表"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT r.id, r.title, r.type, r.knowledge_point, r.difficulty, r.url, r.description, r.learning_time, r.price, c.collected_at
            FROM resources r
            JOIN collections c ON r.id = c.resource_id
            WHERE c.user_id = ?
            ORDER BY c.collected_at DESC
        ''', (user_id,))
        collections = cursor.fetchall()
        return collections
    except Exception as e:
        print(f"获取收藏列表失败: {e}")
        return []

def create_learning_record(user_id, resource_id):
    """创建学习记录（如果已有未完成记录则复用，已有完成记录则重新激活并保留进度）"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 先检查是否已有该资源的未完成记录
        cursor.execute('''
            SELECT id FROM learning_records 
            WHERE user_id = ? AND resource_id = ? AND end_time IS NULL
            LIMIT 1
        ''', (user_id, resource_id))
        existing_uncompleted = cursor.fetchone()
        
        if existing_uncompleted:
            # 已有未完成的记录，复用它（继续学习）
            return True, "已有学习记录"
        
        # 检查是否已有该资源的已完成记录
        cursor.execute('''
            SELECT id, progress FROM learning_records 
            WHERE user_id = ? AND resource_id = ? AND end_time IS NOT NULL
            ORDER BY start_time DESC
            LIMIT 1
        ''', (user_id, resource_id))
        existing_completed = cursor.fetchone()
        
        # 获取当前本地时间
        from datetime import datetime
        local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if existing_completed:
            # 已有已完成的记录，重新激活它（保留进度和累计时长）
            record_id, saved_progress = existing_completed
            cursor.execute('''
                UPDATE learning_records 
                SET start_time = ?, end_time = NULL, completed = 0
                WHERE id = ?
            ''', (local_time, record_id))
            conn.commit()
            return True, "学习记录已重新激活"
        
        # 创建新记录
        cursor.execute('''
            INSERT INTO learning_records (user_id, resource_id, start_time, progress)
            VALUES (?, ?, ?, 0)
        ''', (user_id, resource_id, local_time))
        conn.commit()
        return True, "学习记录已创建"
    except Exception as e:
        print(f"创建学习记录失败: {e}")
        conn.rollback()
        return False, f"创建失败: {e}"
    finally:
        conn.close()

def update_learning_record(user_id, resource_id, duration, completed=0, progress=0.0):
    """更新学习记录（更新现有记录，不创建新记录）"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 先获取当前累计时长
        cursor.execute('''
            SELECT duration FROM learning_records 
            WHERE user_id = ? AND resource_id = ? AND end_time IS NULL
        ''', (user_id, resource_id))
        current_duration = cursor.fetchone()
        current_duration = current_duration[0] if current_duration else 0
        
        # 计算更新后的累计时长（分钟）
        new_total_duration = current_duration + duration
        
        # 获取资源的总学习时长（小时）
        cursor.execute('''
            SELECT learning_time FROM resources WHERE id = ?
        ''', (resource_id,))
        resource = cursor.fetchone()
        total_time_hours = resource[0] if resource and resource[0] else 60  # 默认60小时
        
        # 将累计学习时长（分钟）转换为小时
        total_duration_hours = new_total_duration / 60
        
        # 计算进度：(累计学习时长(小时) / 资源总时长(小时)) * 100，保留两位小数
        if total_time_hours > 0:
            calculated_progress = round(min(100, (total_duration_hours / total_time_hours) * 100), 2)
        else:
            calculated_progress = 0.0
        
        cursor.execute('''
            UPDATE learning_records 
            SET duration = ?, progress = ?
            WHERE user_id = ? AND resource_id = ? AND end_time IS NULL
        ''', (new_total_duration, calculated_progress, user_id, resource_id))
        conn.commit()
        return True, "学习记录已更新"
    except Exception as e:
        print(f"更新学习记录失败: {e}")
        conn.rollback()
        return False, f"更新失败: {e}"
    finally:
        conn.close()

def complete_learning_record(user_id, resource_id, duration, completed=0, progress=0.0):
    """完成学习记录（设置结束时间）"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 获取当前本地时间
        from datetime import datetime
        local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 先获取当前累计时长
        cursor.execute('''
            SELECT duration FROM learning_records 
            WHERE user_id = ? AND resource_id = ? AND end_time IS NULL
        ''', (user_id, resource_id))
        current_duration = cursor.fetchone()
        current_duration = current_duration[0] if current_duration else 0
        
        # 计算更新后的累计时长（分钟）
        new_total_duration = current_duration + duration
        
        # 获取资源的总学习时长（小时）
        cursor.execute('''
            SELECT learning_time FROM resources WHERE id = ?
        ''', (resource_id,))
        resource = cursor.fetchone()
        total_time_hours = resource[0] if resource and resource[0] else 60  # 默认60小时
        
        # 将累计学习时长（分钟）转换为小时
        total_duration_hours = new_total_duration / 60
        
        # 计算进度：(累计学习时长(小时) / 资源总时长(小时)) * 100，保留两位小数
        if total_time_hours > 0:
            calculated_progress = round(min(100, (total_duration_hours / total_time_hours) * 100), 2)
        else:
            calculated_progress = 0.0
        
        cursor.execute('''
            UPDATE learning_records 
            SET end_time = ?, duration = ?, progress = ?, completed = ?
            WHERE user_id = ? AND resource_id = ? AND end_time IS NULL
        ''', (local_time, new_total_duration, calculated_progress, completed, user_id, resource_id))
        conn.commit()
        return True, "学习记录已完成"
    except Exception as e:
        print(f"完成学习记录失败: {e}")
        conn.rollback()
        return False, f"完成失败: {e}"
    finally:
        conn.close()

def get_learning_stats(user_id):
    """获取用户学习统计"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        # 已学习资源数（去重）
        cursor.execute('SELECT COUNT(DISTINCT resource_id) FROM learning_records WHERE user_id = ?', (user_id,))
        learned_count = cursor.fetchone()[0] or 0
        
        # 总学习时长（分钟）
        cursor.execute('SELECT SUM(duration) FROM learning_records WHERE user_id = ?', (user_id,))
        total_minutes = cursor.fetchone()[0] or 0
        
        # 完成的资源数
        cursor.execute('SELECT COUNT(DISTINCT resource_id) FROM learning_records WHERE user_id = ? AND completed = 1', (user_id,))
        completed_count = cursor.fetchone()[0] or 0
        
        # 完成率
        completion_rate = round((completed_count / learned_count) * 100) if learned_count > 0 else 0
        
        # 获取每个资源的详细进度
        cursor.execute('''
            SELECT r.title, lr.progress 
            FROM learning_records lr
            JOIN resources r ON lr.resource_id = r.id
            WHERE lr.user_id = ?
            GROUP BY lr.resource_id
            ORDER BY lr.start_time DESC
        ''', (user_id,))
        resource_details = []
        for row in cursor.fetchall():
            resource_details.append({
                'title': row[0],
                'progress': round(row[1], 2) if row[1] else 0.0
            })
        
        return {
            'learned_count': learned_count,
            'total_hours': round(total_minutes / 60, 1),
            'completed_count': completed_count,
            'completion_rate': completion_rate,
            'resource_details': resource_details
        }
    except Exception as e:
        print(f"获取学习统计失败: {e}")
        return {
            'learned_count': 0,
            'total_hours': 0,
            'completed_count': 0,
            'completion_rate': 0,
            'resource_details': []
        }
    finally:
        conn.close()

def checkin_user(user_id):
    """用户每日签到"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查今天是否已签到
        cursor.execute('''
            SELECT id, streak_days FROM daily_checkin 
            WHERE user_id = ? AND checkin_date = ?
        ''', (user_id, today))
        existing = cursor.fetchone()
        
        if existing:
            return False, "今日已签到", 0
        
        # 获取昨天的连续天数
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT streak_days FROM daily_checkin 
            WHERE user_id = ? AND checkin_date = ?
        ''', (user_id, yesterday))
        yesterday_record = cursor.fetchone()
        
        if yesterday_record:
            streak_days = yesterday_record[0] + 1
        else:
            streak_days = 1
        
        # 插入签到记录
        cursor.execute('''
            INSERT INTO daily_checkin (user_id, checkin_date, streak_days)
            VALUES (?, ?, ?)
        ''', (user_id, today, streak_days))
        conn.commit()
        
        return True, "签到成功", streak_days
    except Exception as e:
        print(f"签到失败: {e}")
        conn.rollback()
        return False, f"签到失败: {e}", 0
    finally:
        conn.close()

def get_checkin_status(user_id):
    """获取用户签到状态"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查今天是否已签到
        cursor.execute('''
            SELECT streak_days FROM daily_checkin 
            WHERE user_id = ? AND checkin_date = ?
        ''', (user_id, today))
        today_record = cursor.fetchone()
        
        checked_in = today_record is not None
        current_streak = today_record[0] if today_record else 0
        
        # 获取本周签到情况
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT checkin_date FROM daily_checkin 
            WHERE user_id = ? AND checkin_date >= ?
            ORDER BY checkin_date
        ''', (user_id, week_start))
        week_checkins = [row[0] for row in cursor.fetchall()]
        
        # 获取最高连续天数
        cursor.execute('''
            SELECT MAX(streak_days) FROM daily_checkin WHERE user_id = ?
        ''', (user_id,))
        max_streak = cursor.fetchone()[0] or 0
        
        # 获取总签到天数
        cursor.execute('''
            SELECT COUNT(*) FROM daily_checkin WHERE user_id = ?
        ''', (user_id,))
        total_days = cursor.fetchone()[0] or 0
        
        return {
            'checked_in': checked_in,
            'current_streak': current_streak,
            'week_checkins': week_checkins,
            'max_streak': max_streak,
            'total_days': total_days
        }
    except Exception as e:
        print(f"获取签到状态失败: {e}")
        return {
            'checked_in': False,
            'current_streak': 0,
            'week_checkins': [],
            'max_streak': 0,
            'total_days': 0
        }
    finally:
        conn.close()

def check_collection(user_id, resource_id):
    """检查资源是否已被收藏"""
    conn = sqlite3.connect('data/learning.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'SELECT id FROM collections WHERE user_id = ? AND resource_id = ?',
            (user_id, resource_id)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"检查收藏状态失败: {e}")
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    
    # 如果带参数 --reset 则重置数据库
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_database()
        
        # 测试查询
        print("\n" + "="*50)
        print("测试查询功能")
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