from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
import logging

app = Flask(__name__)

# Для Railway - используем их файловую систему
DB_PATH = os.path.join(os.path.dirname(__file__), 'applications.db')

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            user_info TEXT NOT NULL,
            registration_date TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            user_department TEXT,
            audience TEXT,
            problem TEXT,
            help_type TEXT DEFAULT '🔧 Помощь в очной форме',
            status TEXT DEFAULT 'new',
            specialist_name TEXT,
            created_date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/create-application', methods=['POST'])
def create_application():
    try:
        data = request.json
        # Ваша логика создания заявки
        return jsonify({'success': True, 'application_id': 123})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)