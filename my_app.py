from flask import Flask, render_template, request, jsonify
import sqlite3
from flask import g

app = Flask(__name__)
DATABASE = 'database.db'

# 数据库连接（同前）
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 初始化数据库（同前）
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0
            )
        ''')
        db.commit()

# 首页（同前）
@app.route('/')
def index():
    return render_template('index.html')

# API: 获取所有任务（新增）
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    db = get_db()
    tasks = db.execute('SELECT * FROM tasks').fetchall()
    return jsonify([dict(task) for task in tasks])  # 转换为字典列表

# API: 添加任务（优化响应）
@app.route('/api/tasks', methods=['POST'])
def add_task():
    task = request.json.get('content')
    if task:
        db = get_db()
        cursor = db.execute('INSERT INTO tasks (content) VALUES (?)', (task,))
        db.commit()
        new_id = cursor.lastrowid  # 获取新任务的ID
        return jsonify({'id': new_id, 'status': 'success'}), 201
    return jsonify({'status': 'error'}), 400

# API: 删除任务（同前）
@app.route('/api/tasks', methods=['DELETE'])
def delete_task():
    task_id = request.json.get('id')
    if task_id:
        db = get_db()
        db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        db.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

# API: 切换任务状态（同前）
@app.route('/api/tasks/complete', methods=['POST'])
def complete_task():
    task_id = request.json.get('id')
    if task_id:
        db = get_db()
        db.execute('UPDATE tasks SET completed = NOT completed WHERE id = ?', (task_id,))
        db.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)