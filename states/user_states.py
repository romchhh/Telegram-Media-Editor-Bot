from aiogram.dispatcher.filters.state import StatesGroup, State

class VerifyUserState(StatesGroup):
    waiting_for_answer = State()
    
class DownloadState(StatesGroup):
    downloading = State()
    
class VideoProcessingState(StatesGroup):
    waiting_for_footage = State()
    waiting_for_background = State()
    
