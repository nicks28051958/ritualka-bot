from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List

# Главная клавиатура (ReplyKeyboard)
def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🏛️ Организация похорон"))
    builder.add(KeyboardButton(text="🤖 AI-помощник по документам"))
    builder.add(KeyboardButton(text="🛍️ Товары"))
    builder.add(KeyboardButton(text="🕯️ Уголок памяти"))
    builder.add(KeyboardButton(text="👤 Регистрация"))
    if is_admin:
        builder.add(KeyboardButton(text="🛠 Админ-панель"))
    builder.add(KeyboardButton(text="🏠 Главное меню"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# Клавиатура админ-панели
def get_admin_panel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="➕ Добавить товар"))
    builder.add(KeyboardButton(text="➖ Удалить товар"))
    builder.add(KeyboardButton(text="⬅️ Назад"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# Клавиатура выбора услуг для похорон (inline)
def get_funeral_services_keyboard(selected: List[str] = None) -> InlineKeyboardMarkup:
    if selected is None:
        selected = []
    builder = InlineKeyboardBuilder()
    services = [
        ("transport", "Перевозка тела"),
        ("coffin", "Гроб"),
        ("wreaths", "Венки"),
        ("cross", "Крест"),
        ("hall", "Прощальный зал"),
        ("ceremoniymaster", "Церемониймейстер"),
        ("simple_funeral", "Обычные похороны"),
        ("cremation", "Кремация")
    ]
    for key, name in services:
        text = f"✅ {name}" if key in selected else name
        builder.add(InlineKeyboardButton(text=text, callback_data=f"funeral_service:{key}"))
    builder.adjust(2)  # Размещение кнопок по 2 в ряду
    builder.row(InlineKeyboardButton(text="✅ Закончить выбор", callback_data="funeral_service:done"))
    return builder.as_markup()

# Клавиатура для выбора бюджета (inline)
def get_funeral_budget_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="До 50 000 руб.", callback_data="budget:50000"))
    builder.add(InlineKeyboardButton(text="До 70 000 руб.", callback_data="budget:70000"))
    builder.add(InlineKeyboardButton(text="До 90 000 руб.", callback_data="budget:90000"))
    builder.add(InlineKeyboardButton(text="До 110 000 руб.", callback_data="budget:110000"))
    return builder.as_markup()

# Клавиатура выбора типа креста (inline)
def get_cross_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Православный крест", callback_data="cross:orthodox"))
    builder.add(InlineKeyboardButton(text="Католический крест", callback_data="cross:catholic"))
    builder.add(InlineKeyboardButton(text="Металлический крест", callback_data="cross:metal"))
    builder.add(InlineKeyboardButton(text="Деревянный крест", callback_data="cross:wood"))
    return builder.as_markup()

# Клавиатура отмены (ReplyKeyboard)
def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)

# Клавиатура категорий товаров (inline)
def get_shop_categories_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⚰️ Гробы", callback_data="shop:category:coffin"))
    builder.add(InlineKeyboardButton(text="💐 Венки", callback_data="shop:category:wreath"))
    builder.add(InlineKeyboardButton(text="✝️ Кресты", callback_data="shop:category:cross"))
    builder.add(InlineKeyboardButton(text="🛒 Все товары", callback_data="shop:category:all"))
    builder.adjust(2)
    return builder.as_markup()

# Клавиатура товара (inline)
def get_product_keyboard(product_id: int, price: float) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=f"🛒 Выбрать ({price} ₽)", callback_data=f"product:select:{product_id}"))
    builder.add(InlineKeyboardButton(
        text="⬅️ Назад", callback_data="shop:back"))
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура уголка памяти (inline)
def get_memory_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Создать запись", callback_data="memory:create"))
    builder.add(InlineKeyboardButton(text="📖 Мои записи", callback_data="memory:my_records"))
    builder.add(InlineKeyboardButton(text="🕯️ Все записи", callback_data="memory:all_records"))
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура записи памяти (inline)
def get_memory_record_keyboard(record_id: int, can_add_candle: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if can_add_candle:
        builder.add(InlineKeyboardButton(text="🕯️ Зажечь свечу", callback_data=f"memory:candle:{record_id}"))
    builder.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="memory:back"))
    builder.adjust(1)
    return builder.as_markup()

# ========== РЕГИСТРАЦИЯ ==========

def get_registration_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="registration:start"))
    builder.add(InlineKeyboardButton(text="👤 Мои данные", callback_data="registration:my_data"))
    builder.adjust(1)
    return builder.as_markup()

def get_registration_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data="registration:confirm"))
    builder.add(InlineKeyboardButton(text="✏️ Изменить", callback_data="registration:edit"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="registration:cancel"))
    builder.adjust(2)
    return builder.as_markup()

def get_registration_edit_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="👤 ФИО", callback_data="registration:edit:full_name"))
    builder.add(InlineKeyboardButton(text="📱 Телефон", callback_data="registration:edit:phone"))
    builder.add(InlineKeyboardButton(text="📧 Email", callback_data="registration:edit:email"))
    builder.add(InlineKeyboardButton(text="📅 Дата рождения", callback_data="registration:edit:birth_date"))
    builder.add(InlineKeyboardButton(text="🆔 Серия паспорта", callback_data="registration:edit:passport_series"))
    builder.add(InlineKeyboardButton(text="🔢 Номер паспорта", callback_data="registration:edit:passport_number"))
    builder.add(InlineKeyboardButton(text="🏛️ Кем выдан", callback_data="registration:edit:passport_issued_by"))
    builder.add(InlineKeyboardButton(text="📅 Дата выдачи", callback_data="registration:edit:passport_issue_date"))
    builder.add(InlineKeyboardButton(text="🏠 Адрес", callback_data="registration:edit:address"))
    builder.add(InlineKeyboardButton(text="📞 Контакт для связи", callback_data="registration:edit:emergency_contact"))
    builder.add(InlineKeyboardButton(text="👥 Отношение", callback_data="registration:edit:relationship"))
    builder.adjust(2)
    return builder.as_markup()

def get_client_data_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✏️ Редактировать", callback_data="registration:edit"))
    builder.add(InlineKeyboardButton(text="✅ Верифицировать", callback_data="registration:verify"))
    builder.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="registration:back"))
    builder.adjust(2)
    return builder.as_markup()
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List

# ... (все твои клавиатуры, которые были выше, оставь без изменений)

# === Кнопки действий после ответа AI-ассистента ===
def get_ai_lawyer_actions_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="❓ Задать ещё вопрос", callback_data="ai_lawyer:ask_again"),
        InlineKeyboardButton(text="🏠 Вернуться в меню", callback_data="ai_lawyer:to_main")
    )
    builder.adjust(1)  # 2 - в ряд, 1 - столбец
    return builder.as_markup()
