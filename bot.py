import datetime
from datetime import datetime, timedelta
import logging
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import mysql.connector
from mysql.connector import Error

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
db_config = {
    'user': 'root',
    'password': 'P@$$w0rd',
    'host': 'localhost',
    'database': 'match_db'  # Database name
}

# Encryption key (should be stored securely, e.g., in environment variables)
key_str = 'my_secret_key'

# File to store sessions
session_file = 'sessions.json'

# Function to create database connection
def create_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"Connected to MySQL Server version {db_info}")
        return connection
    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        return None

# States for conversation handler
USERNAME, PASSWORD, AFTER_LOGIN, SELECT_MONTH = range(4)

# Function to save sessions to file
def save_sessions(sessions):
    with open(session_file, 'w') as file:
        json.dump(sessions, file)

# Function to load sessions from file
def load_sessions():
    try:
        with open(session_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to get main keyboard based on login status
def get_main_keyboard(logged_in=False, is_admin=False):
    if logged_in:
        if is_admin:
            keyboard = [
                [KeyboardButton("Доступные команды"), KeyboardButton("Информация о матчах")],
                [KeyboardButton("Сотрудники студии"), KeyboardButton("Матчи в других месяцах")],
                [KeyboardButton("Выйти из профиля")]
            ]
        else:
            keyboard = [
                [KeyboardButton("Информация о матчах")],
                [KeyboardButton("Матчи в других месяцах")],
                [KeyboardButton("Выйти из профиля")]
            ]
    else:
        keyboard = [[KeyboardButton("Вход")]]
    
    return ReplyKeyboardMarkup(keyboard)

# Handler for /start command and "Вход" button
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sessions = load_sessions()
    user_id = str(update.message.from_user.id)
    if user_id in sessions:
        session = sessions[user_id]
        context.user_data['logged_in'] = True
        context.user_data['username'] = session['username']
        context.user_data['user_id'] = session['user_id']
        
        is_admin = session['username'] == "Артем"
        
        await update.message.reply_text(f"Добро пожаловать обратно, {session['username']}!")
        await update.message.reply_text('Вы можете использовать следующие команды:', reply_markup=get_main_keyboard(logged_in=True, is_admin=is_admin))
        return AFTER_LOGIN

    await update.message.reply_text('Приветствую! Введите ваш логин для входа:', reply_markup=get_main_keyboard())
    return USERNAME

# Handler for username input
async def username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['username'] = update.message.text
    await update.message.reply_text('Введите пароль:')
    return PASSWORD

# Handler for password input
async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = context.user_data['username']
    input_password = update.message.text

    # Check credentials in the database
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM staff WHERE staff_name = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            encrypted_password = result['password']
            decrypted_password = decrypt_password(encrypted_password, key_str)
            
            if decrypted_password == input_password:
                context.user_data['logged_in'] = True
                context.user_data['user_id'] = result['staff_id']
                
                sessions = load_sessions()
                user_id = str(update.message.from_user.id)
                sessions[user_id] = {
                    'username': username,
                    'user_id': result['staff_id']
                }
                save_sessions(sessions)

                # Save chat_id to staff table
                chat_id = update.message.from_user.id
                update_staff_chat_id(connection, result['staff_id'], chat_id)

                is_admin = username == "Артем Кулишов"
                
                await update.message.reply_text(f"Добро пожаловать, {username}!")
                await update.message.reply_text('Вы можете использовать следующие команды:', reply_markup=get_main_keyboard(logged_in=True, is_admin=is_admin))
                return AFTER_LOGIN
            else:
                await update.message.reply_text("Неверное имя пользователя или пароль. Пожалуйста, попробуйте снова.", reply_markup=get_main_keyboard())
                return ConversationHandler.END
        else:
            await update.message.reply_text("Неверное имя пользователя или пароль. Пожалуйста, попробуйте снова.", reply_markup=get_main_keyboard())
            return ConversationHandler.END
    else:
        await update.message.reply_text("Не удалось установить соединение с базой данных. Пожалуйста, повторите попытку позже.")
        return ConversationHandler.END

# Function to update chat_id in staff table
def update_staff_chat_id(connection, staff_id, chat_id):
    try:
        cursor = connection.cursor()
        update_query = "UPDATE staff SET chat_id = %s WHERE staff_id = %s"
        cursor.execute(update_query, (chat_id, staff_id))
        connection.commit()
        cursor.close()
        logger.info(f"Chat_id {chat_id} updated for staff_id {staff_id}")
    except Error as e:
        logger.error(f"Error updating chat_id for staff_id {staff_id}: {e}")
    finally:
        if connection.is_connected():
            connection.close()

# Function to decrypt password
def decrypt_password(encrypted_password, key_str):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        query = "SELECT AES_DECRYPT(%s, %s)"
        cursor.execute(query, (encrypted_password, key_str))
        decrypted_password = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return decrypted_password.decode('utf-8') if decrypted_password else None
    else:
        logger.error("Не удалось установить соединение с базой данных для расшифровки пароля.")
        return None

# Handler for /info command
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Возможные команды:\n/start - начало работы\n/info - информация о командах\n/show_data - показать данные из базы данных')

# Handler for /logout command
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    sessions = load_sessions()
    user_id = str(update.message.from_user.id)
    if user_id in sessions:
        del sessions[user_id]
    save_sessions(sessions)
    await update.message.reply_text("Вы вышли из системы. Введите /start для нового входа.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

# Handler for /cancel command (cancels login process)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Вход отменен.', reply_markup=get_main_keyboard())
    return ConversationHandler.END

# Helper function to get the current week's date range
def get_current_week_date_range():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday
    return start_of_week.date(), end_of_week.date()

# Handler to show data from database
# Handler to show data from database
async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get('logged_in'):
        await update.message.reply_text("Пожалуйста, войдите в систему, чтобы получить доступ к этой команде.", reply_markup=get_main_keyboard())
        return

    user_id = context.user_data['user_id']
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        start_of_week, end_of_week = get_current_week_date_range()
        query = """
        SELECT
            events.event_id,
            events.match_date,
            events.match_time,
            events.broadcast_key,
            locations.location_name,
            home_team.team_name AS home_team_name,
            away_team.team_name AS away_team_name,
            customers.customer_name,
            events.comment,
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
        WHERE (events.operator_id = %s
           OR events.director_id = %s
           OR events.commentator_id = %s
           OR events.photograph_id = %s
           OR events.employee1_id = %s
           OR events.employee2_id = %s
           OR events.employee3_id = %s)
           AND events.match_date BETWEEN %s AND %s
        ORDER BY events.match_date
        """
        cursor.execute(query, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, start_of_week, end_of_week))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        if results:
            message = "Предстоящие события на этой неделе:\n\n"
            for row in results:
                message += f"Дата: {row['match_date']}, Время: {row['match_time']}\n"
                message += f"Место: {row['location_name']}\n"
                message += f"Ключ трансляции: {row.get('broadcast_key', 'Нет данных')}\n"
                message += f"Команды: {row['home_team_name']} vs {row['away_team_name']}\n"
                message += f"Заказчик: {row['customer_name']}\n"
                message += f"Комментарии: {row['comment']}\n"
                message += f"Оператор: {row['operator_name']}\n"
                message += f"Директор: {row['director_name']}\n"
                message += f"Комментатор: {row['commentator_name']}\n"
                message += f"Фотограф: {row['photograph_name']}\n"
                message += f"Сотрудник 1: {row['employee1_name']}\n"
                message += f"Сотрудник 2: {row['employee2_name']}\n"
                message += f"Сотрудник 3: {row['employee3_name']}\n"
                message += "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Нет запланированных событий на этой неделе.")
    else:
        await update.message.reply_text("Не удалось установить соединение с базой данных. Пожалуйста, повторите попытку позже.")

# Handler to show studio staff
async def show_staff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM staff"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        if results:
            message = "Сотрудники студии:\n\n"
            for row in results:
                message += f"ID: {row['staff_id']}, Имя: {row['staff_name']}, Должность: {row['role']}\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Нет сотрудников.")
    else:
        await update.message.reply_text("Не удалось установить соединение с базой данных. Пожалуйста, повторите попытку позже.")

# Handler for showing matches in other months
async def select_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Январь"), KeyboardButton("Февраль")],
        [KeyboardButton("Март"), KeyboardButton("Апрель")],
        [KeyboardButton("Май"), KeyboardButton("Июнь")],
        [KeyboardButton("Июль"), KeyboardButton("Август")],
        [KeyboardButton("Сентябрь"), KeyboardButton("Октябрь")],
        [KeyboardButton("Ноябрь"), KeyboardButton("Декабрь")],
        [KeyboardButton("Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите месяц:", reply_markup=reply_markup)
    return SELECT_MONTH

async def show_matches_for_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    selected_month = update.message.text
    if selected_month == "Назад":
        is_admin = context.user_data['username'] == "Артем Кулишов"
        await update.message.reply_text('Вы вернулись в главное меню.', reply_markup=get_main_keyboard(logged_in=True, is_admin=is_admin))
        return AFTER_LOGIN

    user_id = context.user_data['user_id']
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            events.event_id,
            events.match_date,
            events.match_time,
            events.broadcast_key,
            locations.location_name,
            home_team.team_name AS home_team_name,
            away_team.team_name AS away_team_name,
            customers.customer_name,
            events.comment,
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
        WHERE (events.operator_id = %s
           OR events.director_id = %s
           OR events.commentator_id = %s
           OR events.photograph_id = %s
           OR events.employee1_id = %s
           OR events.employee2_id = %s
           OR events.employee3_id = %s)
          AND MONTH(events.match_date) = %s
        ORDER BY events.match_date
        """
        month_number = {
            "Январь": 1,
            "Февраль": 2,
            "Март": 3,
            "Апрель": 4,
            "Май": 5,
            "Июнь": 6,
            "Июль": 7,
            "Август": 8,
            "Сентябрь": 9,
            "Октябрь": 10,
            "Ноябрь": 11,
            "Декабрь": 12
        }.get(selected_month, 1)
        
        cursor.execute(query, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, month_number))
        results = cursor.fetchall()
        cursor.close()
        connection.close()

        if results:
            message = f"События на {selected_month}:\n\n"
            for row in results:
                message += f"Дата: {row['match_date']}, Время: {row['match_time']}\n"
                message += f"Место: {row['location_name']}\n"
                message += f"Ключ трансляции: {row.get('broadcast_key', 'Нет данных')}\n"
                message += f"Команды: {row['home_team_name']} vs {row['away_team_name']}\n"
                message += f"Заказчик: {row['customer_name']}\n"
                message += f"Комментарии: {row['comment']}\n"
                message += f"Оператор: {row['operator_name']}\n"
                message += f"Директор: {row['director_name']}\n"
                message += f"Комментатор: {row['commentator_name']}\n"
                message += f"Фотограф: {row['photograph_name']}\n"
                message += f"Сотрудник 1: {row['employee1_name']}\n"
                message += f"Сотрудник 2: {row['employee2_name']}\n"
                message += f"Сотрудник 3: {row['employee3_name']}\n"
                message += "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(f"Нет запланированных событий на {selected_month}.")
    else:
        await update.message.reply_text("Не удалось установить соединение с базой данных. Пожалуйста, повторите попытку позже.")
    return SELECT_MONTH

def main() -> None:
    application = Application.builder().token("7031730538:AAG9NHD8cJwK_4t_JO34ra9IVeTrFqXk_X0").build()

    # Add conversation handler with the states USERNAME, PASSWORD, AFTER_LOGIN, and SELECT_MONTH
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.Regex('^(Вход)$'), start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
            AFTER_LOGIN: [
                CommandHandler('info', info),
                CommandHandler('logout', logout),
                CommandHandler('cancel', cancel),
                MessageHandler(filters.Regex('^(Информация о матчах)$'), show_data),
                MessageHandler(filters.Regex('^(Сотрудники студии)$'), show_staff),
                MessageHandler(filters.Regex('^(Матчи в других месяцах)$'), select_month),
                MessageHandler(filters.Regex('^(Доступные команды)$'), info),
                MessageHandler(filters.Regex('^(Выйти из профиля)$'), logout),
            ],
            SELECT_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_matches_for_month)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
