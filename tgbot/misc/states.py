from aiogram.dispatcher.filters.state import State, StatesGroup


class Snils(StatesGroup):
    wait_for_ans = State()
