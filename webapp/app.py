from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='applications.db'):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        return user_data
    
    def save_user(self, user_id, user_name, user_info):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO users (user_id, user_name, user_info, registration_date) VALUES (?, ?, ?, ?)', 
                      (user_id, user_name, user_info, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def save_application(self, user_id, audience, problem, help_type="🔧 Помощь в очной форме"):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_info FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            user_name, user_department = user_data
            cursor.execute('INSERT INTO applications (user_id, user_name, user_department, audience, problem, help_type, created_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, "new")', 
                          (user_id, user_name, user_department, audience, problem, help_type, datetime.now().isoformat()))
            conn.commit()
            application_id = cursor.lastrowid
            conn.close()
            return application_id, user_name, user_department
        conn.close()
        return None, None, None
    
    def get_user_applications(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, audience, problem, status, created_date, specialist_name 
            FROM applications 
            WHERE user_id = ? 
            ORDER BY id DESC
        ''', (user_id,))
        applications = cursor.fetchall()
        conn.close()
        return applications
    
    def get_user_stats(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM applications WHERE user_id = ?', (user_id,))
        applications = cursor.fetchall()
        conn.close()
        
        total = len(applications)
        active = len([app for app in applications if app[0] in ['new', 'accepted']])
        completed = len([app for app in applications if app[0] == 'completed'])
        
        return {
            'total': total,
            'active': active,
            'completed': completed
        }

db = Database()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/register', methods=['POST'])
def api_register_user():
    """API регистрации пользователя для Mini App"""
    try:
        data = request.json
        user_id = data.get('user_id')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        username = data.get('username', '')
        
        # Проверяем, существует ли пользователь
        user_data = db.get_user(user_id)
        
        if not user_data:
            # Создаем нового пользователя
            user_name = f"{first_name} {last_name}".strip() or f"User{user_id}"
            user_department = "Не указан"
            
            db.save_user(user_id, user_name, user_department)
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'user_name': user_name,
                'user_department': user_department
            })
        else:
            return jsonify({
                'success': True,
                'user_id': user_data[0],
                'user_name': user_data[1],
                'user_department': user_data[2]
            })
            
    except Exception as e:
        logger.error(f"API register error: {e}")
        return jsonify({'success': False, 'error': 'Registration failed'}), 500

@app.route('/api/create-application', methods=['POST'])
def api_create_application():
    """API создания заявки из Mini App"""
    try:
        data = request.json
        user_id = data.get('user_id')
        audience = data.get('audience')
        problem = data.get('problem')
        help_type = data.get('help_type', '🔧 Помощь в очной форме')
        
        application_id, user_name, user_department = db.save_application(
            user_id, audience, problem, help_type
        )
        
        if application_id:
            # Здесь можно добавить интеграцию с основным ботом
            # для отправки уведомления в группу
            logger.info(f"New application #{application_id} from user {user_id}")
            
            return jsonify({
                'success': True,
                'application_id': application_id,
                'message': 'Application created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create application'}), 400
            
    except Exception as e:
        logger.error(f"API create application error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/user-stats/<int:user_id>')
def api_user_stats(user_id):
    """API получения статистики пользователя"""
    try:
        stats = db.get_user_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"API user stats error: {e}")
        return jsonify({'total': 0, 'active': 0, 'completed': 0})

@app.route('/api/user-applications/<int:user_id>')
def api_user_applications(user_id):
    """API получения заявок пользователя"""
    try:
        applications_data = db.get_user_applications(user_id)
        applications = []
        
        for app in applications_data:
            applications.append({
                'id': app[0],
                'audience': app[1],
                'problem': app[2],
                'status': app[3],
                'created_date': app[4],
                'specialist_name': app[5]
            })
        
        return jsonify(applications)
    except Exception as e:
        logger.error(f"API user applications error: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)