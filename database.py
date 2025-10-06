
import sqlite3
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name='applications.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
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
                help_type TEXT DEFAULT '🔧 Физическая помощь',
                status TEXT DEFAULT 'new',
                specialist_id INTEGER,
                specialist_name TEXT,
                accepted_date TEXT,
                completed_date TEXT,
                solution_comment TEXT,
                created_date TEXT,
                message_id INTEGER
            )
        ''')
        
        # НОВАЯ ТАБЛИЦА ДЛЯ ОЦЕНОК
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                specialist_id INTEGER,
                specialist_name TEXT,
                rating INTEGER,
                comment TEXT,  
                rated_at TEXT,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("База данных инициализирована с таблицей оценок и колонкой help_type")
    
    def save_application_message_id(self, application_id, message_id):
        """Сохранение ID сообщения заявки"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('UPDATE applications SET message_id = ? WHERE id = ?', 
                      (message_id, application_id))
        conn.commit()
        conn.close()
        logger.info(f"Сообщение {message_id} сохранено для заявки #{application_id}")
    
    def get_application_message_id(self, application_id):
        """Получение ID сообщения заявки"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT message_id FROM applications WHERE id = ?', (application_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else None
    
    def get_all_applications(self):
        """Получение всех заявок"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Проверяем структуру таблицы
        cursor.execute("PRAGMA table_info(applications)")
        columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Колонки в таблице applications: {columns}")
        
        # Формируем запрос в зависимости от наличия колонки message_id
        if 'message_id' in columns:
            cursor.execute('''
                SELECT id, user_name, user_department, audience, problem, status, 
                       specialist_name, created_date, accepted_date, completed_date, message_id, help_type
                FROM applications 
                ORDER BY id DESC
            ''')
        else:
            cursor.execute('''
                SELECT id, user_name, user_department, audience, problem, status, 
                       specialist_name, created_date, accepted_date, completed_date, NULL as message_id, help_type
                FROM applications 
                ORDER BY id DESC
            ''')
        
        applications = cursor.fetchall()
        conn.close()
        return applications
    
    def save_rating(self, application_id, specialist_id, specialist_name, rating):
        """Сохранение оценки специалиста"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ratings (application_id, specialist_id, specialist_name, rating, rated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (application_id, specialist_id, specialist_name, rating, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info(f"Оценка {rating} сохранена для специалиста {specialist_name} (заявка #{application_id})")
    
    def get_specialist_ratings(self, specialist_id=None, specialist_name=None):
        """Получение статистики оценок специалиста"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if specialist_id:
            cursor.execute('SELECT rating FROM ratings WHERE specialist_id = ?', (specialist_id,))
        elif specialist_name:
            cursor.execute('SELECT rating FROM ratings WHERE specialist_name = ?', (specialist_name,))
        else:
            # Все оценки
            cursor.execute('SELECT rating FROM ratings')
        
        ratings = [row[0] for row in cursor.fetchall()]
        
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            rating_counts = {}
            for i in range(1, 11):
                rating_counts[i] = ratings.count(i)
        else:
            avg_rating = 0
            rating_counts = {i: 0 for i in range(1, 11)}
        
        conn.close()
        
        return {
            'ratings': ratings,
            'average': round(avg_rating, 2),
            'count': len(ratings),
            'distribution': rating_counts
        }
    
    def get_all_ratings_stats(self):
        """Получение статистики всех оценок"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Общая статистика
        cursor.execute('SELECT COUNT(*), AVG(rating) FROM ratings')
        total_count, total_avg = cursor.fetchone()
        total_avg = round(total_avg, 2) if total_avg else 0
        
        # Статистика по специалистам
        cursor.execute('''
            SELECT specialist_name, COUNT(*), AVG(rating) 
            FROM ratings 
            GROUP BY specialist_name 
            ORDER BY AVG(rating) DESC
        ''')
        specialists_stats = cursor.fetchall()
        
        # Распределение оценок
        cursor.execute('''
            SELECT rating, COUNT(*) 
            FROM ratings 
            GROUP BY rating 
            ORDER BY rating
        ''')
        distribution = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_count': total_count or 0,
            'total_average': total_avg,
            'specialists': [
                {
                    'name': name,
                    'count': count,
                    'average': round(avg, 2) if avg else 0
                }
                for name, count, avg in specialists_stats
            ],
            'distribution': distribution
        }
    
    def has_application_rating(self, application_id):
        """Проверка, есть ли оценка для заявки"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM ratings WHERE application_id = ?', (application_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_user(self, user_id):
        """Получение данных пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        return user_data
    
    def save_user(self, user_id, user_name, user_info):
        """Сохранение пользователя в базу данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO users (user_id, user_name, user_info, registration_date) VALUES (?, ?, ?, ?)', 
                      (user_id, user_name, user_info, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info(f"Пользователь {user_name} сохранен")
    
    def save_application(self, user_id, audience, problem, help_type="🔧 Физическая помощь"):
        """Сохранение заявки в базу данных с учетом типа помощи"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT user_name, user_info FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            user_name, user_department = user_data
            # Добавляем тип помощи в запрос
            cursor.execute('INSERT INTO applications (user_id, user_name, user_department, audience, problem, help_type, created_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, "new")', 
                          (user_id, user_name, user_department, audience, problem, help_type, datetime.now().isoformat()))
            conn.commit()
            application_id = cursor.lastrowid
            conn.close()
            logger.info(f"Заявка #{application_id} сохранена (тип помощи: {help_type})")
            return application_id, user_name, user_department
        conn.close()
        return None, None, None
    
    def accept_application(self, application_id, specialist_id, specialist_name):
        """Принятие заявки специалистом"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('UPDATE applications SET status = "accepted", specialist_id = ?, specialist_name = ?, accepted_date = ? WHERE id = ? AND status = "new"', 
                      (specialist_id, specialist_name, datetime.now().isoformat(), application_id))
        conn.commit()
        success = cursor.rowcount > 0
        cursor.execute('SELECT user_id, user_name, user_department, audience, problem FROM applications WHERE id = ?', (application_id,))
        application_data = cursor.fetchone()
        conn.close()
        if success and application_data:
            return True, application_data
        return False, None
    
    def reject_application(self, application_id):
        """Отклонение заявки"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('UPDATE applications SET status = "rejected" WHERE id = ? AND status = "new"', (application_id,))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            cursor.execute('SELECT user_id, user_name, user_department, audience, problem FROM applications WHERE id = ?', (application_id,))
            application_data = cursor.fetchone()
        else:
            application_data = None
        conn.close()
        return success, application_data
    
    def complete_application(self, application_id):
        """Завершение заявки без комментария"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('UPDATE applications SET status = "completed", completed_date = ? WHERE id = ?', 
                      (datetime.now().isoformat(), application_id))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            cursor.execute('SELECT user_id, user_name, user_department, audience, problem, specialist_name FROM applications WHERE id = ?', (application_id,))
            application_data = cursor.fetchone()
        else:
            application_data = None
        conn.close()
        return success, application_data
    
    def complete_application_with_comment(self, application_id, comment):
        """Завершение заявки с комментарием"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('UPDATE applications SET status = "completed", completed_date = ?, solution_comment = ? WHERE id = ?', 
                      (datetime.now().isoformat(), comment, application_id))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            cursor.execute('SELECT user_id, user_name, user_department, audience, problem, specialist_name FROM applications WHERE id = ?', (application_id,))
            application_data = cursor.fetchone()
        else:
            application_data = None
        conn.close()
        return success, application_data
    
    def transfer_application(self, application_id, new_specialist_id, new_specialist_name):
        """Передача заявки другому специалисту"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Обновляем специалиста
        cursor.execute('''
            UPDATE applications 
            SET specialist_id = ?, specialist_name = ?, accepted_date = ?
            WHERE id = ? AND status = "accepted"
        ''', (new_specialist_id, new_specialist_name, datetime.now().isoformat(), application_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        
        if success:
            cursor.execute('SELECT user_id, user_name, user_department, audience, problem FROM applications WHERE id = ?', (application_id,))
            application_data = cursor.fetchone()
        else:
            application_data = None
        
        conn.close()
        
        return success, application_data, None
    
    def get_application_by_id(self, application_id):
        """Получение заявки по ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, user_name, user_department, audience, problem, specialist_name FROM applications WHERE id = ?', (application_id,))
        application_data = cursor.fetchone()
        conn.close()
        return application_data
    
    def get_today_stats(self):
        """Статистика за сегодня"""
        today = date.today().isoformat()
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM applications WHERE date(created_date) = ?', (today,))
        total_today = cursor.fetchone()[0]
        cursor.execute('SELECT status, COUNT(*) FROM applications WHERE date(created_date) = ? GROUP BY status', (today,))
        status_stats = cursor.fetchall()
        cursor.execute('SELECT specialist_name, COUNT(*) FROM applications WHERE date(accepted_date) = ? AND specialist_name IS NOT NULL GROUP BY specialist_name', (today,))
        specialists_today = cursor.fetchall()
        cursor.execute('SELECT specialist_name, COUNT(*) FROM applications WHERE date(completed_date) = ? AND specialist_name IS NOT NULL GROUP BY specialist_name', (today,))
        completed_today = cursor.fetchall()
        conn.close()
        return {
            'total_today': total_today,
            'status_stats': dict(status_stats),
            'specialists_today': dict(specialists_today),
            'completed_today': dict(completed_today)
        }
    
    def get_all_time_stats(self):
        """Статистика за все время"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM applications')
        total_all_time = cursor.fetchone()[0]
        cursor.execute('SELECT status, COUNT(*) FROM applications GROUP BY status')
        status_stats_all = cursor.fetchall()
        cursor.execute('SELECT specialist_name, COUNT(*) FROM applications WHERE specialist_name IS NOT NULL GROUP BY specialist_name ORDER BY COUNT(*) DESC')
        specialists_all = cursor.fetchall()
        cursor.execute("SELECT specialist_name, COUNT(*) FROM applications WHERE status = 'completed' AND specialist_name IS NOT NULL GROUP BY specialist_name ORDER BY COUNT(*) DESC")
        completed_all = cursor.fetchall()
        cursor.execute('SELECT user_name, user_department, COUNT(*) FROM applications GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT 5')
        top_users = cursor.fetchall()
        conn.close()
        return {
            'total_all_time': total_all_time,
            'status_stats_all': dict(status_stats_all),
            'specialists_all': dict(specialists_all),
            'completed_all': dict(completed_all),
            'top_users': top_users
        }
    
    def get_specialist_stats(self, specialist_id=None, specialist_name=None):
        """Статистика по специалисту"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if specialist_id:
            cursor.execute('SELECT COUNT(*) FROM applications WHERE specialist_id = ?', (specialist_id,))
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM applications WHERE specialist_id = ? AND status = 'completed'", (specialist_id,))
            completed = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM applications WHERE specialist_id = ? AND date(accepted_date) = date('now')", (specialist_id,))
            today = cursor.fetchone()[0]
        elif specialist_name:
            cursor.execute('SELECT COUNT(*) FROM applications WHERE specialist_name = ?', (specialist_name,))
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM applications WHERE specialist_name = ? AND status = 'completed'", (specialist_name,))
            completed = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM applications WHERE specialist_name = ? AND date(accepted_date) = date('now')", (specialist_name,))
            today = cursor.fetchone()[0]
        else:
            total = completed = today = 0
        
        conn.close()
        return {
            'total': total,
            'completed': completed,
            'today': today
        }
    
    def get_average_waiting_time(self):
        """Среднее время ожидания"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT AVG((julianday(accepted_date) - julianday(created_date)) * 24 * 60) FROM applications WHERE accepted_date IS NOT NULL AND created_date IS NOT NULL')
            result = cursor.fetchone()
            avg_wait_minutes = result[0] if result and result[0] is not None else 0
            
            cursor.execute('SELECT AVG((julianday(completed_date) - julianday(created_date)) * 24 * 60) FROM applications WHERE completed_date IS NOT NULL AND created_date IS NOT NULL')
            result = cursor.fetchone()
            avg_completion_minutes = result[0] if result and result[0] is not None else 0
            
            return {
                'avg_wait_minutes': round(avg_wait_minutes, 1),
                'avg_completion_minutes': round(avg_completion_minutes, 1)
            }
        except Exception as e:
            logger.error(f"Ошибка при расчете времени ожидания: {e}")
            return {'avg_wait_minutes': 0, 'avg_completion_minutes': 0}
        finally:
            conn.close()
    
    def get_user_waiting_stats(self, user_id):
        """Статистика ожидания пользователя"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT AVG((julianday(accepted_date) - julianday(created_date)) * 24 * 60) FROM applications WHERE user_id = ? AND accepted_date IS NOT NULL AND created_date IS NOT NULL', (user_id,))
            result = cursor.fetchone()
            user_avg_wait = result[0] if result and result[0] is not None else 0
            
            cursor.execute('SELECT COUNT(*) FROM applications WHERE user_id = ? AND status = "new"', (user_id,))
            result = cursor.fetchone()
            active_applications = result[0] if result else 0
            
            return {
                'user_avg_wait': round(user_avg_wait, 1) if user_avg_wait else 0,
                'active_applications': active_applications
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики пользователя: {e}")
            return {'user_avg_wait': 0, 'active_applications': 0}
        finally:
            conn.close()
