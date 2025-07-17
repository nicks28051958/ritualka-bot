import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states.states import MemoryRecord
from keyboards.main_keyboard import (
    get_memory_keyboard, get_memory_record_keyboard, get_cancel_keyboard, get_main_keyboard
)
from config import ADMIN_IDS
from database.db import Database
from services.memory_service import MemoryService

router = Router()

@router.message(Command("memory"))
@router.message(F.text == "🕯️ Уголок памяти")
async def start_memory(message: Message):
    """Начало работы с уголком памяти"""
    memory_text = """
🕯️ **Уголок памяти**

Здесь вы можете создать страницу памяти о дорогом человеке.

📝 **Что можно сделать:**
• Создать новую запись памяти
• Просмотреть свои записи
• Посмотреть все записи памяти
• Зажечь свечу в память

Выберите действие:
    """.strip()
    
    await message.answer(memory_text, reply_markup=get_memory_keyboard())

@router.callback_query(F.data == "memory:create")
async def start_create_memory(callback: CallbackQuery, state: FSMContext):
    """Начало создания записи памяти"""
    await state.set_state(MemoryRecord.waiting_for_photo)
    
    await callback.message.edit_text(
        "📸 **Создание записи памяти**\n\n"
        "Шаг 1: Отправьте фотографию усопшего\n"
        "(или отправьте 'пропустить' если фото нет)",
        reply_markup=get_cancel_keyboard()
    )

@router.message(MemoryRecord.waiting_for_photo)
async def process_memory_photo(message: Message, state: FSMContext):
    """Обработка фото для записи памяти"""
    if message.text and message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "❌ Создание записи отменено.",
            reply_markup=get_main_keyboard(is_admin=message.from_user.id in ADMIN_IDS)
        )
        return
    
    photo_path = None
    
    if message.photo:
        # Сохраняем фото
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await message.bot.get_file(file_id)
        
        # Создаем папку для фото если её нет
        os.makedirs("memory_photos", exist_ok=True)
        
        # Сохраняем файл
        photo_path = f"memory_photos/{file_id}.jpg"
        await message.bot.download_file(file.file_path, photo_path)
        
        await state.update_data(photo_path=photo_path)
        await message.answer("✅ Фото сохранено!")
    
    elif message.text and message.text.lower() == "пропустить":
        await message.answer("✅ Фото пропущено.")
    else:
        await message.answer("📸 Пожалуйста, отправьте фотографию или напишите 'пропустить'.")
        return
    
    await state.set_state(MemoryRecord.waiting_for_name)
    await message.answer(
        "📝 **Шаг 2:** Введите ФИО усопшего:",
        reply_markup=get_cancel_keyboard()
    )

@router.message(MemoryRecord.waiting_for_name)
async def process_memory_name(message: Message, state: FSMContext):
    """Обработка имени для записи памяти"""
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "❌ Создание записи отменено.",
            reply_markup=get_main_keyboard(is_admin=message.from_user.id in ADMIN_IDS)
        )
        return
    
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("⚠️ Имя должно содержать минимум 2 символа.")
        return
    
    await state.update_data(name=message.text.strip())
    await state.set_state(MemoryRecord.waiting_for_birth_date)
    
    await message.answer(
        "📅 **Шаг 3:** Введите дату рождения\n"
        "Формат: ДД.ММ.ГГГГ (например: 15.03.1950)",
        reply_markup=get_cancel_keyboard()
    )

@router.message(MemoryRecord.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    """Обработка даты рождения"""
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "❌ Создание записи отменено.",
            reply_markup=get_main_keyboard(is_admin=message.from_user.id in ADMIN_IDS)
        )
        return
    
    # Простая валидация даты
    if not message.text or len(message.text) != 10 or message.text[2] != '.' or message.text[5] != '.':
        await message.answer("⚠️ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ")
        return
    
    await state.update_data(birth_date=message.text)
    await state.set_state(MemoryRecord.waiting_for_death_date)
    
    await message.answer(
        "📅 **Шаг 4:** Введите дату смерти\n"
        "Формат: ДД.ММ.ГГГГ (например: 20.12.2023)",
        reply_markup=get_cancel_keyboard()
    )

@router.message(MemoryRecord.waiting_for_death_date)
async def process_death_date(message: Message, state: FSMContext):
    """Обработка даты смерти"""
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "❌ Создание записи отменено.",
            reply_markup=get_main_keyboard(is_admin=message.from_user.id in ADMIN_IDS)
        )
        return
    
    # Простая валидация даты
    if not message.text or len(message.text) != 10 or message.text[2] != '.' or message.text[5] != '.':
        await message.answer("⚠️ Неверный формат даты. Используйте формат ДД.ММ.ГГГГ")
        return
    
    await state.update_data(death_date=message.text)
    await state.set_state(MemoryRecord.waiting_for_memory_text)
    
    await message.answer(
        "💭 **Шаг 5:** Напишите текст памяти\n"
        "Расскажите о человеке, его жизни, достижениях, о том, каким он был...",
        reply_markup=get_cancel_keyboard()
    )

@router.message(MemoryRecord.waiting_for_memory_text)
async def process_memory_text(message: Message, state: FSMContext, db: Database):
    """Обработка текста памяти и создание записи"""
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "❌ Создание записи отменено.",
            reply_markup=get_main_keyboard(is_admin=message.from_user.id in ADMIN_IDS)
        )
        return
    
    if not message.text or len(message.text.strip()) < 10:
        await message.answer("⚠️ Текст памяти должен содержать минимум 10 символов.")
        return
    
    # Получаем все данные
    data = await state.get_data()
    
    # Создаем запись в базе
    record_id = await db.create_memory_record(
        telegram_id=message.from_user.id,
        name=data["name"],
        birth_date=data["birth_date"],
        death_date=data["death_date"],
        memory_text=message.text.strip(),
        photo_path=data.get("photo_path"),
        html_path=""  # Будет заполнено позже
    )
    
    # Создаем HTML-страницу
    memory_service = MemoryService()
    html_path = await memory_service.create_memory_page(
        record_id=record_id,
        name=data["name"],
        birth_date=data["birth_date"],
        death_date=data["death_date"],
        memory_text=message.text.strip(),
        photo_path=data.get("photo_path"),
        candles_count=0
    )
    
    # Обновляем путь к HTML в базе
    # (в реальном проекте здесь будет UPDATE запрос)
    
    await state.clear()
    
    success_text = f"""
✅ **Запись памяти создана!**

📝 **{data['name']}**
📅 {data['birth_date']} — {data['death_date']}

🕯️ Страница памяти готова.
Другие пользователи смогут зажечь свечу в память.

💡 Используйте кнопки ниже для управления:
    """.strip()
    
    await message.answer(
        success_text,
        reply_markup=get_memory_record_keyboard(record_id)
    )

@router.callback_query(F.data == "memory:my_records")
async def show_my_records(callback: CallbackQuery, db: Database):
    """Показать записи пользователя"""
    records = await db.get_memory_records(callback.from_user.id)
    
    if not records:
        await callback.message.edit_text(
            "📖 У вас пока нет записей памяти.\n"
            "Создайте первую запись!",
            reply_markup=get_memory_keyboard()
        )
        return
    
    # Показываем первую запись
    await show_memory_record(callback, records, 0)

@router.callback_query(F.data == "memory:all_records")
async def show_all_records(callback: CallbackQuery, db: Database):
    """Показать все записи памяти"""
    records = await db.get_memory_records()
    
    if not records:
        await callback.message.edit_text(
            "🕯️ Пока нет записей памяти.\n"
            "Будьте первым, кто создаст запись!",
            reply_markup=get_memory_keyboard()
        )
        return
    
    # Показываем первую запись
    await show_memory_record(callback, records, 0)

@router.callback_query(F.data.startswith("memory:candle:"))
async def add_candle(callback: CallbackQuery, db: Database):
    """Добавить свечу к записи памяти"""
    record_id = int(callback.data.split(":")[2])
    
    success = await db.add_candle(record_id, callback.from_user.id)
    
    if success:
        await callback.answer("🕯️ Свеча зажжена в память", show_alert=True)
        
        # Обновляем отображение записи
        records = await db.get_memory_records()
        record = next((r for r in records if r['id'] == record_id), None)
        
        if record:
            await show_memory_record(callback, [record], 0, can_add_candle=False)
    else:
        await callback.answer("🕯️ Вы уже зажигали свечу для этой записи", show_alert=True)

@router.callback_query(F.data == "memory:back")
async def back_to_memory_menu(callback: CallbackQuery):
    """Возврат в меню памяти"""
    await start_memory(callback.message)

async def show_memory_record(callback: CallbackQuery, records: list, index: int, can_add_candle: bool = True):
    """Показать запись памяти"""
    if index >= len(records):
        index = 0
    elif index < 0:
        index = len(records) - 1
    
    record = records[index]
    
    # Формируем текст записи
    record_text = f"""
🕯️ **Памяти {record['name']}**

📅 **Годы жизни:** {record['birth_date']} — {record['death_date']}

💭 **Память:**
{record['memory_text']}

🕯️ **Зажжено свечей:** {record['candles_count']}
    """.strip()
    
    # Создаем клавиатуру с навигацией
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    if len(records) > 1:
        builder.add(InlineKeyboardButton(text="⬅️", callback_data=f"memory:nav:{index-1}"))
        builder.add(InlineKeyboardButton(text=f"{index+1}/{len(records)}", callback_data="memory:info"))
        builder.add(InlineKeyboardButton(text="➡️", callback_data=f"memory:nav:{index+1}"))
        builder.adjust(3)
    
    # Кнопка свечи
    if can_add_candle:
        builder.add(InlineKeyboardButton(
            text="🕯️ Зажечь свечу", 
            callback_data=f"memory:candle:{record['id']}"
        ))
    
    # Кнопка возврата
    builder.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="memory:back"))
    builder.adjust(1)
    
    keyboard = builder.as_markup()
    
    await callback.message.edit_text(record_text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("memory:nav:"))
async def navigate_memory_records(callback: CallbackQuery, db: Database):
    """Навигация по записям памяти"""
    index = int(callback.data.split(":")[2])
    
    # Получаем все записи
    records = await db.get_memory_records()
    
    if not records:
        await callback.answer("❌ Записи не найдены", show_alert=True)
        return
    
    await show_memory_record(callback, records, index)

@router.callback_query(F.data == "memory:info")
async def memory_info(callback: CallbackQuery):
    """Информация о записях памяти"""
    await callback.answer("ℹ️ Используйте стрелки для навигации по записям", show_alert=True) 