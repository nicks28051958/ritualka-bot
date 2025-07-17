import re
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from states.states import ClientRegistration
from keyboards.main_keyboard import (
    get_registration_keyboard, 
    get_registration_confirm_keyboard,
    get_registration_edit_keyboard,
    get_client_data_keyboard,
    get_main_keyboard,
    get_cancel_keyboard
)
from config import ADMIN_IDS
from database.db import Database

router = Router()

# Валидация данных
def validate_phone(phone: str) -> bool:
    """Валидация номера телефона"""
    phone_pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    return bool(re.match(phone_pattern, phone))

def validate_email(email: str) -> bool:
    """Валидация email"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_passport_series(series: str) -> bool:
    """Валидация серии паспорта"""
    return len(series) == 4 and series.isdigit()

def validate_passport_number(number: str) -> bool:
    """Валидация номера паспорта"""
    return len(number) == 6 and number.isdigit()

def validate_date(date_str: str) -> bool:
    """Валидация даты"""
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def format_client_data(client_data: dict) -> str:
    """Форматирование данных клиента для отображения"""
    text = "📋 <b>Ваши данные:</b>\n\n"
    
    fields = [
        ("👤 ФИО", client_data.get('full_name', 'Не указано')),
        ("📱 Телефон", client_data.get('phone', 'Не указано')),
        ("📧 Email", client_data.get('email', 'Не указано')),
        ("📅 Дата рождения", client_data.get('birth_date', 'Не указано')),
        ("🆔 Серия паспорта", client_data.get('passport_series', 'Не указано')),
        ("🔢 Номер паспорта", client_data.get('passport_number', 'Не указано')),
        ("🏛️ Кем выдан", client_data.get('passport_issued_by', 'Не указано')),
        ("📅 Дата выдачи", client_data.get('passport_issue_date', 'Не указано')),
        ("🏠 Адрес", client_data.get('address', 'Не указано')),
        ("📞 Контакт для связи", client_data.get('emergency_contact', 'Не указано')),
        ("👥 Отношение", client_data.get('relationship', 'Не указано')),
    ]
    
    for label, value in fields:
        text += f"{label}: {value}\n"
    
    text += f"\n✅ Статус верификации: {'Верифицирован' if client_data.get('is_verified') else 'Не верифицирован'}"
    
    return text

@router.message(F.text == "👤 Регистрация")
async def registration_menu(message: Message, db: Database):
    """Меню регистрации"""
    is_registered = await db.is_client_registered(message.from_user.id)
    
    if is_registered:
        client_data = await db.get_client_data(message.from_user.id)
        text = format_client_data(client_data)
        await message.answer(text, reply_markup=get_client_data_keyboard(), parse_mode="HTML")
    else:
        text = "👋 Добро пожаловать в систему регистрации клиентов!\n\n"
        text += "Для получения полного доступа к услугам необходимо заполнить анкету с вашими данными.\n\n"
        text += "📋 <b>Что потребуется:</b>\n"
        text += "• ФИО\n"
        text += "• Номер телефона\n"
        text += "• Email (необязательно)\n"
        text += "• Дата рождения\n"
        text += "• Паспортные данные\n"
        text += "• Адрес проживания\n"
        text += "• Контакт для экстренной связи\n"
        text += "• Отношение к усопшему\n\n"
        text += "Выберите действие:"
        
        await message.answer(text, reply_markup=get_registration_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "registration:start")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    """Начало регистрации"""
    await callback.answer()
    
    text = "📝 <b>Регистрация клиента</b>\n\n"
    text += "Пожалуйста, введите ваше полное имя (ФИО):\n\n"
    text += "Пример: Иванов Иван Иванович"
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_full_name)

@router.callback_query(F.data == "registration:my_data")
async def show_my_data(callback: CallbackQuery, db: Database):
    """Показать данные клиента"""
    await callback.answer()
    
    client_data = await db.get_client_data(callback.from_user.id)
    if client_data:
        text = format_client_data(client_data)
        await callback.message.edit_text(text, reply_markup=get_client_data_keyboard(), parse_mode="HTML")
    else:
        await callback.message.edit_text("❌ Данные не найдены. Пожалуйста, зарегистрируйтесь.", 
                                       reply_markup=get_registration_keyboard())

@router.callback_query(F.data == "registration:edit")
async def edit_registration(callback: CallbackQuery):
    """Редактирование данных"""
    await callback.answer()
    
    text = "✏️ <b>Редактирование данных</b>\n\n"
    text += "Выберите поле для редактирования:"
    
    await callback.message.edit_text(text, reply_markup=get_registration_edit_keyboard(), parse_mode="HTML")

@router.callback_query(F.data.startswith("registration:edit:"))
async def edit_field(callback: CallbackQuery, state: FSMContext):
    """Выбор поля для редактирования"""
    await callback.answer()
    
    field = callback.data.split(":")[2]
    field_names = {
        "full_name": "полное имя (ФИО)",
        "phone": "номер телефона",
        "email": "email",
        "birth_date": "дату рождения (ДД.ММ.ГГГГ)",
        "passport_series": "серию паспорта (4 цифры)",
        "passport_number": "номер паспорта (6 цифр)",
        "passport_issued_by": "кем выдан паспорт",
        "passport_issue_date": "дату выдачи паспорта (ДД.ММ.ГГГГ)",
        "address": "адрес проживания",
        "emergency_contact": "контакт для экстренной связи",
        "relationship": "отношение к усопшему"
    }
    
    text = f"✏️ <b>Редактирование</b>\n\n"
    text += f"Введите {field_names.get(field, field)}:\n\n"
    
    if field == "phone":
        text += "Пример: +7 (999) 123-45-67"
    elif field == "email":
        text += "Пример: example@mail.ru"
    elif field == "birth_date" or field == "passport_issue_date":
        text += "Формат: ДД.ММ.ГГГГ"
    elif field == "passport_series":
        text += "4 цифры, например: 1234"
    elif field == "passport_number":
        text += "6 цифр, например: 123456"
    
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    
    # Устанавливаем состояние в зависимости от поля
    state_map = {
        "full_name": ClientRegistration.waiting_for_full_name,
        "phone": ClientRegistration.waiting_for_phone,
        "email": ClientRegistration.waiting_for_email,
        "birth_date": ClientRegistration.waiting_for_birth_date,
        "passport_series": ClientRegistration.waiting_for_passport_series,
        "passport_number": ClientRegistration.waiting_for_passport_number,
        "passport_issued_by": ClientRegistration.waiting_for_passport_issued_by,
        "passport_issue_date": ClientRegistration.waiting_for_passport_issue_date,
        "address": ClientRegistration.waiting_for_address,
        "emergency_contact": ClientRegistration.waiting_for_emergency_contact,
        "relationship": ClientRegistration.waiting_for_relationship
    }
    
    await state.set_state(state_map.get(field))
    await state.update_data(editing_field=field)

@router.callback_query(F.data == "registration:confirm")
async def confirm_registration(callback: CallbackQuery, state: FSMContext, db: Database):
    """Подтверждение регистрации"""
    await callback.answer()
    
    data = await state.get_data()
    
    # Сохраняем данные в базу
    success = await db.save_client_data(
        telegram_id=callback.from_user.id,
        full_name=data.get('full_name'),
        phone=data.get('phone'),
        email=data.get('email'),
        birth_date=data.get('birth_date'),
        passport_series=data.get('passport_series'),
        passport_number=data.get('passport_number'),
        passport_issued_by=data.get('passport_issued_by'),
        passport_issue_date=data.get('passport_issue_date'),
        address=data.get('address'),
        emergency_contact=data.get('emergency_contact'),
        relationship=data.get('relationship')
    )
    
    if success:
        text = "✅ <b>Регистрация завершена!</b>\n\n"
        text += "Ваши данные успешно сохранены в системе.\n"
        text += "Теперь вы можете пользоваться всеми услугами.\n\n"
        text += "Для возврата в главное меню нажмите кнопку ниже."
        
        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.message.answer(
            "🏠 Главное меню",
            reply_markup=get_main_keyboard(is_admin=callback.from_user.id in ADMIN_IDS)
        )
    else:
        text = "❌ <b>Ошибка при сохранении данных</b>\n\n"
        text += "Пожалуйста, попробуйте еще раз или обратитесь к администратору."
        
        await callback.message.edit_text(text, parse_mode="HTML")
    
    await state.clear()

@router.callback_query(F.data == "registration:cancel")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    """Отмена регистрации"""
    await callback.answer()
    
    await state.clear()
    await callback.message.edit_text("❌ Регистрация отменена.")
    await callback.message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard(is_admin=callback.from_user.id in ADMIN_IDS)
    )

@router.callback_query(F.data == "registration:back")
async def back_to_registration(callback: CallbackQuery):
    """Возврат к меню регистрации"""
    await callback.answer()
    
    text = "👋 <b>Регистрация клиентов</b>\n\n"
    text += "Выберите действие:"
    
    await callback.message.edit_text(text, reply_markup=get_registration_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "registration:verify")
async def verify_client(callback: CallbackQuery, db: Database):
    """Верификация клиента"""
    await callback.answer()
    
    success = await db.verify_client(callback.from_user.id)
    
    if success:
        text = "✅ <b>Клиент верифицирован!</b>\n\n"
        text += "Статус верификации обновлен."
    else:
        text = "❌ <b>Ошибка при верификации</b>\n\n"
        text += "Пожалуйста, попробуйте еще раз."
    
    await callback.message.edit_text(text, parse_mode="HTML")

# Обработчики ввода данных
@router.message(ClientRegistration.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Обработка ввода ФИО"""
    full_name = message.text.strip()
    
    if len(full_name) < 5:
        await message.answer("❌ ФИО должно содержать минимум 5 символов. Попробуйте еще раз:")
        return
    
    await state.update_data(full_name=full_name)
    
    text = "📱 <b>Введите номер телефона:</b>\n\n"
    text += "Пример: +7 (999) 123-45-67"
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_phone)

@router.message(ClientRegistration.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка ввода телефона"""
    phone = message.text.strip()
    
    if not validate_phone(phone):
        await message.answer("❌ Неверный формат номера телефона. Попробуйте еще раз:")
        return
    
    await state.update_data(phone=phone)
    
    text = "📧 <b>Введите email (необязательно):</b>\n\n"
    text += "Пример: example@mail.ru\n"
    text += "Или нажмите 'Пропустить'"
    
    keyboard = get_cancel_keyboard()
    keyboard.keyboard.append([{"text": "⏭️ Пропустить"}])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_email)

@router.message(ClientRegistration.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    """Обработка ввода email"""
    if message.text == "⏭️ Пропустить":
        email = None
    else:
        email = message.text.strip()
        if email and not validate_email(email):
            await message.answer("❌ Неверный формат email. Попробуйте еще раз:")
            return
    
    await state.update_data(email=email)
    
    text = "📅 <b>Введите дату рождения:</b>\n\n"
    text += "Формат: ДД.ММ.ГГГГ\n"
    text += "Пример: 15.03.1990"
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_birth_date)

@router.message(ClientRegistration.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    """Обработка ввода даты рождения"""
    birth_date = message.text.strip()
    
    if not validate_date(birth_date):
        await message.answer("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ:")
        return
    
    await state.update_data(birth_date=birth_date)
    
    text = "🆔 <b>Введите серию паспорта:</b>\n\n"
    text += "4 цифры, например: 1234"
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_passport_series)

@router.message(ClientRegistration.waiting_for_passport_series)
async def process_passport_series(message: Message, state: FSMContext):
    """Обработка ввода серии паспорта"""
    series = message.text.strip()
    
    if not validate_passport_series(series):
        await message.answer("❌ Серия паспорта должна содержать 4 цифры. Попробуйте еще раз:")
        return
    
    await state.update_data(passport_series=series)
    
    text = "🔢 <b>Введите номер паспорта:</b>\n\n"
    text += "6 цифр, например: 123456"
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_passport_number)

@router.message(ClientRegistration.waiting_for_passport_number)
async def process_passport_number(message: Message, state: FSMContext):
    """Обработка ввода номера паспорта"""
    number = message.text.strip()
    
    if not validate_passport_number(number):
        await message.answer("❌ Номер паспорта должен содержать 6 цифр. Попробуйте еще раз:")
        return
    
    await state.update_data(passport_number=number)
    
    text = "🏛️ <b>Введите кем выдан паспорт:</b>\n\n"
    text += "Пример: УФМС России по г. Москве"
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_passport_issued_by)

@router.message(ClientRegistration.waiting_for_passport_issued_by)
async def process_passport_issued_by(message: Message, state: FSMContext):
    """Обработка ввода кем выдан паспорт"""
    issued_by = message.text.strip()
    
    if len(issued_by) < 5:
        await message.answer("❌ Название должно содержать минимум 5 символов. Попробуйте еще раз:")
        return
    
    await state.update_data(passport_issued_by=issued_by)
    
    text = "📅 <b>Введите дату выдачи паспорта:</b>\n\n"
    text += "Формат: ДД.ММ.ГГГГ\n"
    text += "Пример: 20.05.2015"
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_passport_issue_date)

@router.message(ClientRegistration.waiting_for_passport_issue_date)
async def process_passport_issue_date(message: Message, state: FSMContext):
    """Обработка ввода даты выдачи паспорта"""
    issue_date = message.text.strip()
    
    if not validate_date(issue_date):
        await message.answer("❌ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ:")
        return
    
    await state.update_data(passport_issue_date=issue_date)
    
    text = "🏠 <b>Введите адрес проживания:</b>\n\n"
    text += "Пример: г. Москва, ул. Тверская, д. 1, кв. 1"
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_address)

@router.message(ClientRegistration.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    """Обработка ввода адреса"""
    address = message.text.strip()
    
    if len(address) < 10:
        await message.answer("❌ Адрес должен содержать минимум 10 символов. Попробуйте еще раз:")
        return
    
    await state.update_data(address=address)
    
    text = "📞 <b>Введите контакт для экстренной связи:</b>\n\n"
    text += "ФИО и телефон человека, которого можно связать в экстренном случае\n"
    text += "Пример: Иванова Мария Петровна, +7 (999) 123-45-67"
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_emergency_contact)

@router.message(ClientRegistration.waiting_for_emergency_contact)
async def process_emergency_contact(message: Message, state: FSMContext):
    """Обработка ввода контакта для экстренной связи"""
    emergency_contact = message.text.strip()
    
    if len(emergency_contact) < 10:
        await message.answer("❌ Контакт должен содержать минимум 10 символов. Попробуйте еще раз:")
        return
    
    await state.update_data(emergency_contact=emergency_contact)
    
    text = "👥 <b>Введите ваше отношение к усопшему:</b>\n\n"
    text += "Пример: сын, дочь, супруг, брат, сестра, друг и т.д."
    
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_relationship)

@router.message(ClientRegistration.waiting_for_relationship)
async def process_relationship(message: Message, state: FSMContext):
    """Обработка ввода отношения к усопшему"""
    relationship = message.text.strip()
    
    if len(relationship) < 2:
        await message.answer("❌ Отношение должно содержать минимум 2 символа. Попробуйте еще раз:")
        return
    
    await state.update_data(relationship=relationship)
    
    # Показываем все введенные данные для подтверждения
    data = await state.get_data()
    
    text = "📋 <b>Проверьте введенные данные:</b>\n\n"
    text += f"👤 <b>ФИО:</b> {data.get('full_name', 'Не указано')}\n"
    text += f"📱 <b>Телефон:</b> {data.get('phone', 'Не указано')}\n"
    text += f"📧 <b>Email:</b> {data.get('email', 'Не указано')}\n"
    text += f"📅 <b>Дата рождения:</b> {data.get('birth_date', 'Не указано')}\n"
    text += f"🆔 <b>Серия паспорта:</b> {data.get('passport_series', 'Не указано')}\n"
    text += f"🔢 <b>Номер паспорта:</b> {data.get('passport_number', 'Не указано')}\n"
    text += f"🏛️ <b>Кем выдан:</b> {data.get('passport_issued_by', 'Не указано')}\n"
    text += f"📅 <b>Дата выдачи:</b> {data.get('passport_issue_date', 'Не указано')}\n"
    text += f"🏠 <b>Адрес:</b> {data.get('address', 'Не указано')}\n"
    text += f"📞 <b>Контакт для связи:</b> {data.get('emergency_contact', 'Не указано')}\n"
    text += f"👥 <b>Отношение:</b> {data.get('relationship', 'Не указано')}\n\n"
    text += "Все данные верны?"
    
    await message.answer(text, reply_markup=get_registration_confirm_keyboard(), parse_mode="HTML")
    await state.set_state(ClientRegistration.waiting_for_confirm)

# Обработчик отмены
@router.message(F.text == "❌ Отмена")
async def cancel_input(message: Message, state: FSMContext):
    """Отмена ввода данных"""
    current_state = await state.get_state()
    if current_state and not current_state.startswith(
        ("ClientRegistration", "FuneralForm", "MemoryRecord", "AIHelper")
    ):
        return
    await state.clear()
    await message.answer(
        "❌ Ввод данных отменен.",
        reply_markup=get_main_keyboard(is_admin=message.from_user.id in ADMIN_IDS)
    )