from main import bot, dp
from data.config import *
from filters.filters import *
from keyboards.user_keyboards import get_start_keyboard
from states.user_states import VerifyUserState
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from database.user_db import *

import random

html = 'HTML'

async def antiflood(*args, **kwargs):
    m = args[0]
    await m.answer("Не поспішай :)")

async def on_startup(dp):
    from handlers.user_handlers import dp as user_dp
    from callbacks.user_callbacks import register_callbacks
    register_callbacks(dp)


async def on_shutdown(dp):
    me = await bot.get_me()
    print(f'Bot: @{me.username} зупинений!')

def generate_math_question():
    num1 = random.randint(10, 20)
    num2 = random.randint(10, 20)
    correct_answer = num1 + num2
    return num1, num2, correct_answer

@dp.message_handler(IsPrivate(), commands=["start"])
@dp.throttled(antiflood, rate=1)
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username
    user_first_name = message.from_user.first_name

    create_table()

    if check_user(user_id):
        photo_path = 'data/posterLogo.png'

        await message.answer_photo(
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
        return
    await message.answer(f"Привіт, {user_name}! Давайте перевіримо, чи ви не бот.")
    num1, num2, correct_answer = generate_math_question()
    answers = [correct_answer, correct_answer + random.randint(1, 5), correct_answer - random.randint(1, 5)]
    random.shuffle(answers)
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for answer in answers:
        keyboard.add(InlineKeyboardButton(text=str(answer), callback_data=f"answer_{answer}"))
    await state.update_data(correct_answer=correct_answer)
    await message.answer(f"Скільки буде {num1} + {num2}?", reply_markup=keyboard)
    await VerifyUserState.waiting_for_answer.set()

@dp.callback_query_handler(lambda c: c.data.startswith('answer_'), state=VerifyUserState.waiting_for_answer)
async def process_answer(callback_query: types.CallbackQuery, state: FSMContext):
    answer = int(callback_query.data.split('_')[1])
    user_data = await state.get_data()
    correct_answer = user_data['correct_answer']

    if answer == correct_answer:
        user_id = callback_query.from_user.id
        user_name = callback_query.from_user.username
        add_user(user_id, user_name)

        photo_path = 'data/posterLogo.png'

        await callback_query.message.answer_photo(
            photo=InputFile(photo_path), 
            caption="<b>@MediaKipCutBot:</b> - це простий і зручний бот для створення контенту.\n\n"
                    "<b>Бот дозволяє:</b>\n\n"
                    "- Шукати цікаві моменти в медіа та вирізати їх\n"
                    "- Накладати футажі\n"
                    "- Створювати та налаштовувати фільтри будь-якого формату\n"
                    "- І багато іншого\n\n"
                    "by @nowayrm", 
            parse_mode='HTML', 
            reply_markup=get_start_keyboard()
        )
        await state.finish()
    else:
        await callback_query.message.answer("Невірно! Спробуйте ще раз.")
        await start(callback_query.message, state)
        
