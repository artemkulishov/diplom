from datetime import timedelta
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector
from mysql.connector import Error
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

from bot import create_db_connection

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

db_config = {
    'user': 'root',
    'password': 'P@$$w0rd',
    'host': 'localhost',
    'database': 'match_db'
}

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = {'admin_valdlen2024': User(1, 'admin_valdlen2024', 'Adm1n$Lh!s2024')}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/locations', methods=['GET'])
def get_locations():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT location_id AS id, location_name AS name FROM locations")
        locations = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(locations)
    else:
        return jsonify({'message': 'Ошибка подключения к базе данных'}), 500

@app.route('/teams', methods=['GET'])
def get_teams():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT team_id AS id, team_name AS name FROM teams")
        teams = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(teams)
    else:
        return jsonify({'message': 'Ошибка подключения к базе данных'}), 500

@app.route('/customers', methods=['GET'])
def get_customers():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT customer_id AS id, customer_name AS name FROM customers")
        customers = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(customers)
    else:
        return jsonify({'message': 'Ошибка подключения к базе данных'}), 500

@app.route('/staff', methods=['GET'])
def get_staff():
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT staff_id AS id, staff_name AS name FROM staff")
        staff = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(staff)
    else:
        return jsonify({'message': 'Ошибка подключения к базе данных'}), 500

@app.route('/save', methods=['POST'])
def save_match():
    data = request.json
    logger.info(f"Received data: {data}")
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            def check_existence(table, column, value):
                query = f"SELECT {column} FROM {table} WHERE {column} = %s"
                cursor.execute(query, (value,))
                return cursor.fetchone()

            if not check_existence('locations', 'location_id', data['location_id']):
                logger.error(f"Invalid location_id: {data['location_id']}")
                return jsonify({'message': 'Ошибка: Неверное значение location_id'}), 400

            if not check_existence('customers', 'customer_id', data['customer_id']):
                logger.error(f"Invalid customer_id: {data['customer_id']}")
                return jsonify({'message': 'Ошибка: Неверное значение customer_id'}), 400

            if data.get('director_id') and not check_existence('staff', 'staff_id', data['director_id']):
                logger.error(f"Invalid director_id: {data['director_id']}")
                return jsonify({'message': 'Ошибка: Неверное значение director_id'}), 400

            if data.get('commentator_id') and not check_existence('staff', 'staff_id', data['commentator_id']):
                logger.error(f"Invalid commentator_id: {data['commentator_id']}")
                return jsonify({'message': 'Ошибка: Неверное значение commentator_id'}), 400

            if data.get('photograph_id') and not check_existence('staff', 'staff_id', data['photograph_id']):
                logger.error(f"Invalid photograph_id: {data['photograph_id']}")
                return jsonify({'message': 'Ошибка: Неверное значение photograph_id'}), 400

            if data.get('employee1_id') and not check_existence('staff', 'staff_id', data['employee1_id']):
                logger.error(f"Invalid employee1_id: {data['employee1_id']}")
                return jsonify({'message': 'Ошибка: Неверное значение employee1_id'}), 400

            if data.get('employee2_id') and not check_existence('staff', 'staff_id', data['employee2_id']):
                logger.error(f"Invalid employee2_id: {data['employee2_id']}")
                return jsonify({'message': 'Ошибка: Неверное значение employee2_id'}), 400

            if data.get('employee3_id') and not check_existence('staff', 'staff_id', data['employee3_id']):
                logger.error(f"Invalid employee3_id: {data['employee3_id']}")
                return jsonify({'message': 'Ошибка: Неверное значение employee3_id'}), 400

            query = """
                INSERT INTO events (
                    location_id, home_team_id, away_team_id, match_date, match_time, 
                    broadcast_key, customer_id, comment, operator_id, director_id, 
                    commentator_id, photograph_id, employee1_id, employee2_id, employee3_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(query, (
                data['location_id'], data['home_team_id'], data['away_team_id'], data['match_date'], data['match_time'],
                data['broadcast_key'], data['customer_id'], data['comment'], data.get('operator_id'), data.get('director_id'),
                data.get('commentator_id'), data.get('photograph_id'), data.get('employee1_id'), data.get('employee2_id'), data.get('employee3_id')
            ))

            connection.commit()
            logger.info("Match saved successfully")
            cursor.close()
            connection.close()
            return jsonify({'message': 'Матч успешно добавлен!'})
        except mysql.connector.Error as e:
            logger.error(f"Error while executing query: {e}")
            connection.rollback()
            return jsonify({'message': 'Ошибка при сохранении данных проверьте дату и время'}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        return jsonify({'message': 'Ошибка подключения к базе данных'}), 500
    
@app.route('/delete', methods=['POST'])
def delete_match():
    data = request.json
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            # First delete rows from the event_staff table
            delete_event_staff_query = "DELETE FROM event_staff WHERE event_id = %s"
            cursor.execute(delete_event_staff_query, (data['event_id'],))
            
            # Then delete the row from the events table
            delete_event_query = "DELETE FROM events WHERE event_id = %s"
            cursor.execute(delete_event_query, (data['event_id'],))

            connection.commit()
            return jsonify({'message': 'Матч успешно удален!'})
        except mysql.connector.Error as e:
            logger.error(f"Error while executing query: {e}")
            connection.rollback()
            return jsonify({'message': 'Ошибка при удалении данных'}), 500
        finally:
            cursor.close()
            connection.close()
    else:
        return jsonify({'message': 'Ошибка подключения к базе данных'}), 500

def convert_timedelta_to_str(obj):
    if isinstance(obj, timedelta):
        return str(obj)
    return obj

@app.route('/view', methods=['GET'])
def view_matches():
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    events.event_id AS event_id,
                    events.match_date AS match_date,
                    events.match_time AS match_time,
                    events.broadcast_key AS broadcast_key,
                    locations.location_name AS location_name,
                    home_team.team_name AS home_team_name,
                    away_team.team_name AS away_team_name,
                    customers.customer_name AS customer_name,
                    events.comment AS comment,
                    operator.staff_name AS operator_name,
                    director.staff_name AS director_name,
                    commentator.staff_name AS commentator_name,
                    photograph.staff_name AS photograph_name,
                    employee1.staff_name AS employee1_name,
                    employee2.staff_name AS employee2_name,
                    employee3.staff_name AS employee3_name
                FROM events
                JOIN locations ON events.location_id = locations.location_id
                JOIN teams AS home_team ON events.home_team_id = home_team.team_id
                JOIN teams AS away_team ON events.away_team_id = away_team.team_id
                JOIN customers ON events.customer_id = customers.customer_id
                LEFT JOIN staff AS operator ON events.operator_id = operator.staff_id
                LEFT JOIN staff AS director ON events.director_id = director.staff_id
                LEFT JOIN staff AS commentator ON events.commentator_id = commentator.staff_id
                LEFT JOIN staff AS photograph ON events.photograph_id = photograph.staff_id
                LEFT JOIN staff AS employee1 ON events.employee1_id = employee1.staff_id
                LEFT JOIN staff AS employee2 ON events.employee2_id = employee2.staff_id
                LEFT JOIN staff AS employee3 ON events.employee3_id = employee3.staff_id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Convert timedelta to string before JSON serialization
            for result in results:
                result['match_time'] = convert_timedelta_to_str(result['match_time'])

            cursor.close()
            connection.close()
            return jsonify(results)
        except mysql.connector.Error as e:
            logger.error(f"Error while executing query: {e}")
            return jsonify({'message': 'Ошибка при выполнении запроса к базе данных'}), 500
        except TypeError as te:
            logger.error(f"Type error: {te}")
            return jsonify({'message': 'Ошибка при сериализации данных'}), 500
    else:
        return jsonify({'message': 'Ошибка подключения к базе данных'}), 500

if __name__ == '__main__':
    app.run(debug=True)
