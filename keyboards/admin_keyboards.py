from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, KeyboardButton, ContentTypes, ReplyKeyboardMarkup, \
    InputFile

def get_manager_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="Мої активні діалоги✅", callback_data="active_dialogs"),
        InlineKeyboardButton(text="Мої завершені діалоги❌", callback_data="completed_dialogs"),
    ]
    keyboard.add(*buttons)
    return keyboard



def get_admin_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="Активні діалоги✅", callback_data="adminactive_dialogs"),
        InlineKeyboardButton(text="Завершені діалоги❌", callback_data="admincompleted_dialogs"),
        InlineKeyboardButton(text="Статистика", callback_data='user_statistic'),
        InlineKeyboardButton(text="Розсилка", callback_data='mailing')
    ]
    keyboard.add(*buttons)
    return keyboard


def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    back_button = InlineKeyboardButton("Назад", callback_data="back")
    keyboard.add(back_button)
    return keyboard


def get_back2_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    back_button = InlineKeyboardButton("Назад", callback_data="back2")
    keyboard.add(back_button)
    return keyboard

def get_preview_markup():
    markup = InlineKeyboardMarkup()
    preview_button = InlineKeyboardButton("📤 Надіслати", callback_data="send_broadcast")
    cancel_button = InlineKeyboardButton("❌ Відміна", callback_data="cancel_broadcast")
    markup.row(preview_button, cancel_button)
    markup.one_time_keyboard = True
    return markup


def get_start_dialog_keyboard(question_id):
    keyboard = InlineKeyboardMarkup()
    start_dialog_button = InlineKeyboardButton(text="Почати діалог", callback_data=f"start_dialog:{question_id}")
    keyboard.add(start_dialog_button)
    return keyboard


def get_reply_keyboard(question_id):
    keyboard = InlineKeyboardMarkup()
    reply_button = InlineKeyboardButton("Відповісти", callback_data=f"reply_{question_id}")
    keyboard.add(reply_button)
    return keyboard

def start_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)  
    support_button = KeyboardButton(text="Admin Panel👨🏼‍💻")
    keyboard.add(support_button)
    return keyboard

def start_manager_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)  
    support_button = KeyboardButton(text="Manager Panel👨🏼‍💻")
    keyboard.add(support_button)
    return keyboard

def get_cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = KeyboardButton(text="Завершити діалог")
    keyboard.add(cancel_button)
    return keyboard