import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import datetime

TOKEN = '8146033866:AAFf5XczwqqkYC_b80CgQXrR_kt6dacNHcc'

class Character:
    def __init__(self, name, level=1, xp=0, programming_hours=0, daily_tasks_completed=0):
        self.name = name
        self.level = level
        self.xp = xp
        self.programming_hours = programming_hours
        self.daily_tasks_completed = daily_tasks_completed

    def __str__(self):
        return f"Имя: {self.name}\nУровень: {self.level}\nОпыт: {self.xp}\nЧасов программирования сегодня: {self.programming_hours:.2f}\nВыполнено задач сегодня: {self.daily_tasks_completed}"


# Глобальные переменные
current_character = Character(name="Программист")
coding_start_time = None
lvl_xp = 0
level_thresholds = {
    1: 0,
    2: 100,
    3: 300,
    4: 600,
    5: 1200,
    6: 2000,
    7: 3000,
    8: 4500,
    9: 7000,
    10: 10000
   #Можно добавить дальше нужные уровни
}

tasks = {
    "task1": {"description": "Почитать документацию Python", "xp": 10},
    "task2": {"description": "Сделать лабу", "xp": 20},
    "task3": {"description": "Сделать небольшой проект", "xp": 50},
    "task4": {"description": "Сделать зарядку утром", "xp": 10},
    "task5": {"description": "Отжимания(100), Пресс(100), Подтягивания(80), Приседания(100)", "xp": 50}
}

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(current_character))


# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Вот список доступных команд: \n /start \n /profile \n /start_coding \n /stop_coding \n /tasks \n /complete task_id \n /add_task")


# Обработчик команды /profile
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=str(current_character))


# Обработчик команды /start_coding
async def start_coding_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global coding_start_time
    coding_start_time = datetime.datetime.now()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Таймер запущен! Удачи в кодинге!")


# Обработчик команды /add_task
async def add_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and len(context.args) >= 2:
        description = " ".join(context.args[:-1])
        task_type = context.args[-1].lower()
        xp = 0
        if task_type in ["daily", "one_time"]:
            new_task_id = f"task{len(tasks) + 1}"
            tasks[new_task_id] = {
                "description": description,
                "xp": xp,  
                "type": task_type
            }
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Задача '{description}' (тип: {task_type}) добавлена с ID: {new_task_id}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Неверный тип задачи. Должно быть 'daily' или 'one_time'.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Используйте /add_task <описание> <daily/one_time>")
    


# Обработчик команды /stop_coding
async def stop_coding_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global coding_start_time
    if coding_start_time:
        coding_end_time = datetime.datetime.now()
        duration = coding_end_time - coding_start_time
        hours = duration.total_seconds() / 3600
        current_character.programming_hours += hours
        coding_start_time = None
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Законено кодить! Программирование длилось {hours:.2f} часа. Обновленный профиль: \n {current_character}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Таймер не запущен. Начните с /start_coding")


# Обработчик команды /tasks
async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_list = "\n".join([f"{key}: {task['description']} (XP: {task['xp']})" for key, task in tasks.items()])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Список доступных задач:\n{task_list}")


def get_level_from_xp(xp):
    level = 1
    for lvl, threshold in level_thresholds.items():
        if xp >= threshold:
            level = lvl
        else:
            break 
    return level


def update_character_level(character):
    new_level = get_level_from_xp(character.xp)
    if new_level > character.level:
         character.level = new_level
         return True
    return False # Уровень не повысился
    
current_character = Character()


# Обработчик команды /complete task_id
async def complete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Укажите ID задачи: /complete task_id"
        )
        return

    task_id = context.args[0]

    if task_id not in tasks:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Задача не найдена. Проверьте /tasks"
        )
        return

    task = tasks[task_id]

    current_character.xp += task["xp"]
    current_character.daily_tasks_completed += 1
    level_up = update_character_level(current_character)
    message = f"Задача '{task['description']}' выполнена! Получено {task['xp']} XP. Обновленный профиль:\n{current_character}"
    if level_up:
         message += "\nУРОВЕНЬ ПОВЫШЕН!"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


    if task["type"] == "one_time":
        del tasks[task_id]  # Удаляем выполненную однодневную задачу
    else:
        tasks[task_id]["is_completed_today"] = True  # Отмечаем, что задача выполнена на сегодня


if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Создание приложения бота
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавление обработчиков команд
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help_command)
    profile_handler = CommandHandler('profile', profile_command)
    start_coding_handler = CommandHandler('start_coding', start_coding_command)
    stop_coding_handler = CommandHandler('stop_coding', stop_coding_command)
    tasks_handler = CommandHandler('tasks', tasks_command)
    complete_handler = CommandHandler('complete', complete_command)
    add_task_handler = CommandHandler('add_task', add_task_command)
    application.add_handler(add_task_handler)
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(profile_handler)
    application.add_handler(start_coding_handler)
    application.add_handler(stop_coding_handler)
    application.add_handler(tasks_handler)
    application.add_handler(complete_handler)


    # Запуск бота
    application.run_polling()