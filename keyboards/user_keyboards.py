from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    video_button = InlineKeyboardButton(text="Завантажити відео", callback_data="upload_video")
    premium_button = InlineKeyboardButton(text="Преміум підписка", callback_data="buy_premium")
    
    keyboard.add(video_button, premium_button)
    
    return keyboard


def back_markup():
    keyboard = InlineKeyboardMarkup(row_width=1)   
    back_button = InlineKeyboardButton(text="← Назад", callback_data="back")
    keyboard.add(back_button)   
    return keyboard


def cancel_button():
    keyboard = InlineKeyboardMarkup()
    cancel_btn = InlineKeyboardButton(text="❌ Відмінити", callback_data="cancel_download")
    keyboard.add(cancel_btn)
    return keyboard


def edit_media(user_data):
    effect_names = {
        "blurred": "Розмитий",
        "black": "Чорний фон"
    }
    background_path = user_data.get('background', "")
    if background_path.endswith('.mp4'):
        selected_effect_name = "Відео"
    elif background_path.endswith('.jpg'):
        selected_effect_name = "Фото"
    else:
        selected_effect_name = effect_names.get(user_data.get('background'), "")
        
    position_names = {
        "top": "Зверху",
        "centre": "Центр",
        "bottom": "Знизу"
    }
    selected_position = position_names.get(user_data.get('position'), "")

    mirror_status = "✅Віддзеркалення" if user_data.get('mirror', 0) == 1 else "☑️Віддзеркалення"
    fragment_count = user_data.get('fragment_count', 0)
    segment_length = user_data.get('segment_length', 0)
    quality = user_data.get('quality', '720p')

    if segment_length > 0:
        minutes = segment_length // 60
        seconds = segment_length % 60

        segment_length_label = ""
        if minutes > 0:
            segment_length_label += f"{minutes} хв"
        if seconds > 0:
            if minutes > 0:
                segment_length_label += f" {seconds} сек"
            else:
                segment_length_label += f"{seconds} сек"
    else:
        segment_length_label = ""

    keyboard = InlineKeyboardMarkup(row_width=2)
    if 'footage' in user_data:
        keyboard.add(InlineKeyboardButton("Футаж ✅", callback_data="add_footage"))
    else:
        keyboard.add(InlineKeyboardButton("Додати футаж", callback_data="add_footage"))

    keyboard.add(
        InlineKeyboardButton(f"Фрагменти: {fragment_count}" if fragment_count > 0 else "Фрагменти", callback_data="fragment_count"),
        InlineKeyboardButton(f"Довжина: {segment_length_label}", callback_data="segment_length"),
        InlineKeyboardButton(f"Задній фон: {selected_effect_name}", callback_data="background"),
        InlineKeyboardButton(f"Позиція: {selected_position}", callback_data="position"),
        InlineKeyboardButton(mirror_status, callback_data="reflection"),
        InlineKeyboardButton(f"Якість: {quality}", callback_data="quatity"),
    )
    keyboard.add(
        InlineKeyboardButton("← Скасувати", callback_data="cancel"),
        InlineKeyboardButton("Далі →", callback_data=f"next")
    )

    return keyboard




