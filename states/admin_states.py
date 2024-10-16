from aiogram.dispatcher.filters.state import State, StatesGroup

    
class BroadcastState(StatesGroup):
    text = State()
    photo = State()
    button_name = State()
    button_url = State()
    preview = State()



class AdminStates(StatesGroup):
    waiting_for_answer = State()
    waiting_for_new_answer = State()
    waiting_for_first_answer = State()