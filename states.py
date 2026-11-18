from aiogram.fsm.state import State, StatesGroup

class ConfigurationStates(StatesGroup):
    selecting_component = State()
    waiting_for_budget = State()
    viewing_component = State()