from aiogram import types, Dispatcher
from main import bot, dp
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InputFile
from keyboards.user_keyboards import *
import os, asyncio, aiofiles, shutil, requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from moviepy.editor import VideoFileClip, vfx, CompositeVideoClip, ImageClip
from moviepy_video_handler import VideoProcessor
from states.user_states import VideoProcessingState
from aiogram.dispatcher import FSMContext
from data.config import token
from io import BytesIO

user_data = {}

@dp.callback_query_handler(lambda c: c.data == "back")
async def handle_upload_video(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption("<b>@MediaKipCutBot:</b> - це простий і зручний бот для створення контенту.\n\n"
                    "<b>Бот дозволяє:</b>\n\n"
                    " Шукати цікаві моменти в медіа та вирізати їх\n"
                    " Накладати футажі\n"
                    " Створювати та налаштовувати фільтри будь-якого формату\n"
                    " І багато іншого\n\n"
                    "by @nowayrm", 
            parse_mode='HTML', 
            reply_markup=get_start_keyboard()
        )
    
    
@dp.callback_query_handler(lambda c: c.data == "back_to_edit")
async def handle_back_to_edit(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_text("Оберіть параметри:",
                                     reply_markup=edit_media(user_data[user_id]))
    
@dp.callback_query_handler(lambda c: c.data == "back_to_edit_with_state", 
                           state=[VideoProcessingState.waiting_for_footage, VideoProcessingState.waiting_for_background])
async def handle_back_to_edit(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_text("Оберіть параметри:",
                                     reply_markup=edit_media(user_data[user_id]))
    
    await state.finish()
    


    
@dp.callback_query_handler(lambda c: c.data == "upload_video")
async def handle_upload_video(callback_query: types.CallbackQuery):
    await callback_query.message.edit_caption("📹 Будь ласка, надішліть ваше відео у форматі MP4, MOV або іншому підтримуваному форматі.", reply_markup=back_markup())
    await bot.answer_callback_query(callback_query.id)
    
    
downloads = {}


@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT], state="*")  
async def process_video(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}  

    state_data = await state.get_state()

    if state_data == VideoProcessingState.waiting_for_footage.state:

        if message.content_type == types.ContentType.VIDEO:
            footage = message.video
            footage_ext = 'mp4'
        elif message.content_type == types.ContentType.PHOTO:
            footage = message.photo[-1] 
            footage_ext = 'jpg'
        else:
            await message.answer("⚠️ Надішліть лише відео або фото у цьому стані.")
            return

        file_info = await bot.get_file(footage.file_id)
        file_path = file_info.file_path
        footage_file = await bot.download_file(file_path)

        footage_path = f"downloads/{user_id}/footage/{footage.file_id}.{footage_ext}"
        os.makedirs(os.path.dirname(footage_path), exist_ok=True)

        with open(footage_path, 'wb') as f:
            f.write(footage_file.read())

        if 'footage' in user_data[user_id]:
            old_footage_path = user_data[user_id]['footage']
            if os.path.exists(old_footage_path):
                os.remove(old_footage_path)

        user_data[user_id]['footage'] = footage_path

        print(user_data[user_id])
        print("Футаж збережений")

        await message.answer("Оберіть параметри:", reply_markup=edit_media(user_data[user_id]))

        await state.finish()
        return
    
    elif state_data == VideoProcessingState.waiting_for_background.state:

        if message.content_type == types.ContentType.VIDEO:
            background = message.video
            background_ext = 'mp4'
        elif message.content_type == types.ContentType.PHOTO:
            background = message.photo[-1] 
            background_ext = 'jpg'
        else:
            await message.answer("⚠️ Надішліть лише відео або фото у цьому стані.")
            return

        file_info = await bot.get_file(background.file_id)
        file_path = file_info.file_path
        background_file = await bot.download_file(file_path)

        background_path = f"downloads/{user_id}/background/{background.file_id}.{background_ext}"
        os.makedirs(os.path.dirname(background_path), exist_ok=True)

        with open(background_path, 'wb') as f:
            f.write(background_file.read())

        if 'background' in user_data[user_id]:
            old_background_path = user_data[user_id]['background']
            if os.path.exists(old_background_path):
                os.remove(old_background_path)

        user_data[user_id]['background'] = background_path

        print(user_data[user_id])

        await message.answer("Оберіть параметри:", reply_markup=edit_media(user_data[user_id]))

        await state.finish()
        return
    
    
    
    file_extension = ""
    file_unique_id = ""

    if message.content_type == types.ContentType.VIDEO:
        file_id = message.video.file_id
        file_extension = ".mp4"
        file_unique_id = message.video.file_unique_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
        file_extension = message.document.file_name.split('.')[-1]
        file_unique_id = message.document.file_unique_id

        if file_extension.lower() not in ["mp4", "mov", "avi", "mkv", "flv"]:
            await message.answer("⚠️ Неправильний формат файлу. Будь ласка, надішліть відео у форматі MP4, MOV, AVI або іншому підтримуваному форматі.")
            return
    loading_message = await bot.send_message(user_id, "Процес завантаження відео...", reply_markup=cancel_button())

    downloads[user_id] = {
        'file_id': file_id,
        'file_extension': file_extension,
        'file_unique_id': file_unique_id,  # Зберігаємо file_unique_id
        'loading_message_id': loading_message.message_id 
    }

    asyncio.create_task(download_file(user_id))


async def get_file_path(file_id):
    # Replace 'your_bot_token' with your actual bot token
    url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
    
    # Make a GET request to the Telegram API
    response = requests.get(url)
    
    if response.status_code == 200:
        file_info = response.json()
        # Check if the result contains the file path
        if file_info['ok']:
            return file_info['result']['file_path']
        
            print(file_info)
        else:
            print(f"Error: {file_info['description']}")
    else:
        print(f"Error: Unable to fetch file info, status code: {response.status_code}")

async def download_file(user_id):
    if user_id in downloads:
        file_id = downloads[user_id]['file_id']
        file_extension = downloads[user_id]['file_extension']

        # Отримуємо шлях до файлу
        file_path = await get_file_path(file_id)
        # file_path = file.file_path
        
        print(file_path)

        # Формуємо правильний URL для завантаження файлу
        file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

        # Виконуємо запит для завантаження файлу
        response = requests.get(file_url)
        if response.status_code == 200:
            destination = f"downloads/{user_id}/{file_id}{file_extension}"
            user_data[user_id]['main_video'] = destination
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, 'wb') as f:
                f.write(response.content)

            await bot.edit_message_text("✅ Відео успішно завантажено! Оберіть параметри:",
                                        chat_id=user_id,
                                        message_id=downloads[user_id]['loading_message_id'],
                                        reply_markup=edit_media(user_data[user_id]))

        else:
            await bot.send_message(user_id, "Не вдалося завантажити файл.")
        
        # Очищуємо завантажені дані
        del downloads[user_id]


@dp.callback_query_handler(lambda c: c.data == 'background')
async def effect_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}

    effects = [
        ("Розмитий", "blurred"),
        ("Чорний фон", "black"),
    ]

    keyboard = InlineKeyboardMarkup(row_width=2)
    for effect_name, effect_code in effects:
        button = InlineKeyboardButton(effect_name, callback_data=f"background_{effect_code}")
        keyboard.add(button) 
    keyboard.add(InlineKeyboardButton("Відео фон", callback_data=f"video_background"))
    keyboard.add(InlineKeyboardButton("← Назад", callback_data=f"back_to_edit"))

    await callback_query.message.edit_text("Оберіть ефект:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('background_'))
async def background_choice_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    background_code = callback_query.data.split('_')[1]

    user_data[user_id]['background'] = background_code

    background_names = {
        "blurred": "Розмитий",
        "black": "Чорний фон"
    }
    selected_effect_name = background_names.get(background_code, "Невідомий ефект")
    await callback_query.message.edit_text(
        f"Оберіть параметри:",
        reply_markup=edit_media(user_data[user_id])
    )



@dp.callback_query_handler(lambda c: c.data == 'position')
async def position_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}

    positions = [
        ("Зверху", "top"),
        ("Центр", "center"),
        ("Знизу", "bottom"),
    ]

    keyboard = InlineKeyboardMarkup(row_width=2)
    for position_name, position_code in positions:
        button = InlineKeyboardButton(position_name, callback_data=f"position_{position_code}")
        keyboard.add(button) 
    keyboard.add(InlineKeyboardButton("← Назад", callback_data=f"back_to_edit"))

    await callback_query.message.edit_text(f"Оберіть параметри:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('position_'))
async def position_choice_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    position_code = callback_query.data.split('_')[1]

    user_data[user_id]['position'] = position_code

    position_names = {
        "top": "Зверху",
        "centre": "Центр",
        "bottom": "Знизу"
    }
    selected_effect_name = position_names.get(position_code, "Невідомий ефект")
    await callback_query.message.edit_text(
        f"Оберіть параметри:",
        reply_markup=edit_media(user_data[user_id])
    )
    
    

@dp.callback_query_handler(lambda c: c.data == 'reflection')
async def reflection_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}
    if user_data[user_id].get('mirror', 0) == 0:
        user_data[user_id]['mirror'] = 1  # Enable mirror
        mirror_status = "✅Віддзеркалення"  # Indicate it's active
    else:
        user_data[user_id]['mirror'] = 0  # Disable mirror
        mirror_status = "☑️Віддзеркалення"  # Indicate it's inactive
    keyboard = edit_media(user_data[user_id])
    await callback_query.message.edit_text("Оберіть параметри:", reply_markup=keyboard)

  
@dp.callback_query_handler(lambda c: c.data == 'fragment_count')
async def fragment_count_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}

    keyboard = InlineKeyboardMarkup(row_width=4)
    for i in range(1, 9):  
        button = InlineKeyboardButton(f"{i} фрагментів", callback_data=f"set_fragment_{i}")
        keyboard.add(button)
    keyboard.add(InlineKeyboardButton("← Назад", callback_data="back_to_edit"))
    await callback_query.message.edit_text("Оберіть кількість фрагментів:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('set_fragment_'))
async def set_fragment_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    fragment_count = int(callback_query.data.split('_')[2])

    user_data[user_id]['fragment_count'] = fragment_count  
    keyboard = edit_media(user_data[user_id])
    
    await callback_query.message.edit_text("Оберіть параметри:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'segment_length')
async def segment_length_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}

    durations = [
        ("15 секунд", 15),
        ("30 секунд", 30),
        ("45 секунд", 45),
        ("1 хвилина", 60),
        ("1.5 хвилини", 90),
        ("2 хвилини", 120),
        ("2.5 хвилини", 150),
        ("3 хвилини", 180)
    ]

    keyboard = InlineKeyboardMarkup(row_width=4)
    for duration_label, duration_value in durations:
        button = InlineKeyboardButton(duration_label, callback_data=f"set_length_{duration_value}")
        keyboard.add(button)

    keyboard.add(InlineKeyboardButton("← Назад", callback_data="back_to_edit"))
    await callback_query.message.edit_text("Оберіть довжину:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('set_length_'))
async def set_length_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    length_value = int(callback_query.data.split('_')[2])  

    user_data[user_id]['segment_length'] = length_value 
    keyboard = edit_media(user_data[user_id])
    
    await callback_query.message.edit_text("Оберіть параметри:", reply_markup=keyboard)
 
@dp.callback_query_handler(lambda c: c.data == "cancel_download")
async def cancel_download(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in downloads:
        del downloads[user_id]
        await callback_query.message.edit_text("Завантаження відео відмінено.")
    else:
        await callback_query.answer("Немає активного завантаження для відміни.", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == 'cancel')
async def cancel_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Так", callback_data="confirm_cancel"),
        InlineKeyboardButton("Ні", callback_data="cancel_cancel")
    )
    await callback_query.message.edit_text("Ви впевнені, що хочете скасувати всі зміни?", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'confirm_cancel')
async def confirm_cancel_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in user_data:
        del user_data[user_id]
    download_dir = f"downloads/{user_id}"
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)

    await callback_query.answer("Всі зміни успішно видалено!")
    photo_path = 'data/posterLogo.png'

    await callback_query.message.delete()
    await callback_query.message.answer_photo(
        photo=InputFile(photo_path), 
        caption="<b>@MediaKipCutBot:</b> - це простий і зручний бот для створення контенту.\n\n"
                "<b>Бот дозволяє:</b>\n\n"
                " Шукати цікаві моменти в медіа та вирізати їх\n"
                " Накладати футажі\n"
                " Створювати та налаштовувати фільтри будь-якого формату\n"
                " І багато іншого\n\n"
                "by @nowayrm", 
        parse_mode='HTML', 
        reply_markup=get_start_keyboard()
    )
 
@dp.callback_query_handler(lambda c: c.data == 'cancel_cancel')
async def cancel_cancel_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    keyboard = edit_media(user_data[user_id])
    await callback_query.message.edit_text("Оберіть параметри:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'add_footage')
async def add_footage_callback(callback_query: CallbackQuery, state: FSMContext):
    await VideoProcessingState.waiting_for_footage.set()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("← Назад", callback_data=f"back_to_edit_with_state"))
    await callback_query.message.edit_text("Будь ласка, надішліть футаж (відео або фото).", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'video_background')
async def add_footage_callback(callback_query: CallbackQuery, state: FSMContext):
    await VideoProcessingState.waiting_for_background.set()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("← Назад", callback_data=f"back_to_edit_with_state"))
    await callback_query.message.edit_text("Будь ласка, надішліть фон (відео або фото).", reply_markup=keyboard)
    
    
    
@dp.callback_query_handler(lambda c: c.data == "quatity")
async def process_quality_selection(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if 'quality' not in user_data[user_id]:
        user_data[user_id]['quality'] = '720p'

    quality_keyboard = InlineKeyboardMarkup(row_width=2)
    quality_keyboard.add(
        InlineKeyboardButton("720p", callback_data="quality_720p"),
        InlineKeyboardButton("1080p 🛡️", callback_data="quality_1080p_premium")
    )
    quality_keyboard.add(InlineKeyboardButton("Придбати преміум", callback_data="buy_premium"))
    quality_keyboard.add(InlineKeyboardButton("← Назад", callback_data=f"back_to_edit"))

    await bot.edit_message_text("Оберіть якість відео:", chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=quality_keyboard)

@dp.callback_query_handler(lambda c: c.data == "quality_720p")
async def process_quality_720p(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data[user_id]['quality'] = '720p'  
    await callback_query.message.edit_text("Оберіть параметри:", reply_markup=edit_media(user_data[user_id]))

@dp.callback_query_handler(lambda c: c.data == "quality_1080p_premium")
async def process_quality_1080p_premium(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data[user_id]['quality'] = '1080p'  
 
    await callback_query.message.edit_text("Оберіть параметри:", reply_markup=edit_media(user_data[user_id]))


@dp.callback_query_handler(lambda c: c.data == "buy_premium")
async def process_purchase_premium(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    await bot.send_message(user_id, "Щоб придбати преміум, перейдіть за посиланням: [Придбати преміум](https://your-payment-link.com)", parse_mode="Markdown")



@dp.callback_query_handler(lambda c: c.data == 'next')
async def next_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}

    final_video_name = "final_video.mp4"

    user_data[user_id].get("mirror", 0) # 1 or 0
    # state = await dp.storage.get_state(callback_query.chat_instance)
    # print(state)

    background_option = user_data[user_id].get("background", "black")
    background_video = None
    if background_option == "video":
        background_video = user_data[user_id].get("background_video"),
    footage_path = user_data[user_id].get("footage", None)
    position = user_data[user_id].get("position", "center")


    print(user_data[user_id])

    video_processor = VideoProcessor(user_data[user_id].get("main_video"))
    video_processor.process(
        output_path=final_video_name,
        footage_path=footage_path,
        position=position,
        background_option=background_option,
        background_video_path=background_video
    )

    with open(final_video_name, 'rb') as final_file:
        await bot.send_video(callback_query.message.chat.id, final_file)

    if footage_path:
        os.remove(footage_path)
    os.remove(final_video_name)
    await callback_query.message.answer("Обробка завершена!")
    
    
def register_callbacks(dp: Dispatcher):
    dp.register_callback_query_handler(handle_upload_video, lambda c: c.data == 'check')