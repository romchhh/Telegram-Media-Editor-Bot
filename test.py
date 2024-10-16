import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from moviepy.editor import VideoFileClip, vfx, CompositeVideoClip, ImageClip

API_TOKEN = '6496449692:AAFWiSxoBUjzkzhf6CSIUhEPPh2MKN1Ky8s'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Створюємо клас для керування станами
class VideoProcessingState(StatesGroup):
    waiting_for_main_video = State()  # Очікування головного відео
    waiting_for_footage = State()     # Очікування футажу

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привіт, відправ мені відео, яке треба обробити.")
    await VideoProcessingState.waiting_for_main_video.set()  # Переходимо до стану очікування головного відео

@dp.message_handler(state=VideoProcessingState.waiting_for_main_video, content_types=types.ContentType.VIDEO)
async def handle_main_video(message: types.Message, state: FSMContext):
    video = message.video
    file_info = await bot.get_file(video.file_id)
    file_path = file_info.file_path

    # Завантажуємо головне відео
    video_file = await bot.download_file(file_path)
    video_name = f"{video.file_id}.mp4"
    with open(video_name, 'wb') as f:
        f.write(video_file.read())

    # Зберігаємо назву головного відео у стані
    await state.update_data(main_video=video_name)

    await message.reply("Тепер скинь футаж (відео або фото з зеленим фоном).")
    await VideoProcessingState.waiting_for_footage.set()  # Переходимо до стану очікування футажу

@dp.message_handler(state=VideoProcessingState.waiting_for_footage, content_types=[types.ContentType.VIDEO, types.ContentType.PHOTO])
async def handle_footage(message: types.Message, state: FSMContext):
    # Отримуємо стан користувача, де збережено головне відео
    user_data = await state.get_data()
    main_video_name = user_data['main_video']

    if message.content_type == types.ContentType.VIDEO:
        footage = message.video
        footage_ext = 'mp4'
    else:
        footage = message.photo[-1]  # Отримуємо найбільшу за розміром версію фото
        footage_ext = 'jpg'

    file_info = await bot.get_file(footage.file_id)
    file_path = file_info.file_path

    # Завантажуємо футаж
    footage_file = await bot.download_file(file_path)
    footage_name = f"{footage.file_id}.{footage_ext}"
    with open(footage_name, 'wb') as f:
        f.write(footage_file.read())

    # Зберігаємо футаж у стані
    await state.update_data(footage=footage_name)

    # Обробка відео
    await process_videos(message, state)

async def process_videos(message: types.Message, state: FSMContext):
    # Отримуємо стан користувача
    user_data = await state.get_data()
    main_video_name = user_data['main_video']
    footage_name = user_data['footage']

    # Обробляємо головне відео
    clip = VideoFileClip(main_video_name)

    # Розміри для відео 9:16 (наприклад, для повноекранного відео на телефоні)
    phone_width = 1080
    phone_height = 1920

    # Створюємо фонове відео з ефектом розмиття
    blurred_background = clip.fx(vfx.blur, sigma=25).resize((phone_width, phone_height))

    # Змінюємо розмір основного відео, щоб воно було придатним для перегляду на телефоні
    main_video = clip.resize(width=phone_width).set_position(("center", "center"))

    # Обробляємо футаж (видаляємо зелений фон)
    if footage_name.endswith('.mp4'):
        footage_clip = VideoFileClip(footage_name)
        footage_clip_no_bg = footage_clip.fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)
    else:
        # Якщо це фото, перетворюємо його на ImageClip
        footage_clip = ImageClip(footage_name).set_duration(clip.duration)
        footage_clip_no_bg = footage_clip.fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)

    # Змінюємо розмір футажу і ставимо його внизу відео
    footage_clip_no_bg = footage_clip_no_bg.resize(height=300).set_position(("center", phone_height - 300))

    # Об'єднуємо заблюрений фон, основне відео і футаж
    final_clip = CompositeVideoClip([blurred_background, main_video, footage_clip_no_bg.set_duration(main_video.duration)])

    # Зберігаємо оброблене відео
    final_video_name = "final_video.mp4"
    final_clip.write_videofile(final_video_name)

    # Відправляємо оброблене відео користувачу
    with open(final_video_name, 'rb') as final_file:
        await bot.send_video(message.chat.id, final_file)

    # Видаляємо тимчасові файли
    os.remove(main_video_name)
    os.remove(footage_name)
    os.remove(final_video_name)

    # Очищаємо стан
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
