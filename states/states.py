from aiogram.fsm.state import State, StatesGroup

class FuneralForm(StatesGroup):
    """Состояния для анкеты похорон"""
    waiting_for_body_location = State()
    waiting_for_funeral_type = State()
    waiting_for_services = State()
    waiting_for_budget = State()

class MemoryRecord(StatesGroup):
    """Состояния для создания записи памяти"""
    waiting_for_photo = State()
    waiting_for_name = State()
    waiting_for_birth_date = State()
    waiting_for_death_date = State()
    waiting_for_memory_text = State()

class ClientRegistration(StatesGroup):
    """Состояния для регистрации клиентов"""
    waiting_for_full_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_birth_date = State()
    waiting_for_passport_series = State()
    waiting_for_passport_number = State()
    waiting_for_passport_issued_by = State()
    waiting_for_passport_issue_date = State()
    waiting_for_address = State()
    waiting_for_emergency_contact = State()
    waiting_for_relationship = State()
    waiting_for_confirm = State()

class AdminStates(StatesGroup):
    """Состояния для администратора"""
    waiting_for_broadcast_message = State()

class AIHelper(StatesGroup):
    """Состояния для AI-помощника"""
    waiting_for_question = State()


class AddProduct(StatesGroup):
    """Состояния для добавления товара администратором"""
    waiting_for_category = State()
    confirm_category = State()
    waiting_for_name = State()
    confirm_name = State()
    waiting_for_price = State()
    confirm_price = State()


class RemoveProduct(StatesGroup):
    """Состояния для удаления товара"""
    waiting_for_category = State()
    waiting_for_product_id = State()
