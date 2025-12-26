from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    timezone = State()


class TimezoneStates(StatesGroup):
    timezone = State()


class RemindStates(StatesGroup):
    text = State()
    time = State()
