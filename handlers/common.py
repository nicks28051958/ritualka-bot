from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.main_keyboard import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user = message.from_user

    # Первая часть — уважительное и нейтральное приветствие
    await message.answer(
        f"🕊 Здравствуйте, {user.first_name}.\n\n"
        f"Вы обратились в агентство <b>«ЕвроСервис»</b>.\n"
        f"Мы оказываем поддержку в организации похорон, оформлении документов, "
        f"установке памятников и создании <b>Уголков памяти</b>.\n\n"
        f"Каждая история — особенная. Мы рядом, чтобы помочь вам с уважением к чувствам и памяти близких."
    )

    # Вторая часть — меню
    await message.answer(
        f"Пожалуйста, выберите нужный раздел в меню ниже.\n\n"
        f"Если вы не уверены, с чего начать — нажмите <b>«Помощь»</b>.",
        reply_markup=get_main_keyboard()
    )

# Обработчик кнопки «🏠 Главное меню»
@router.message(F.text == "🏠 Главное меню")
async def cmd_home(message: Message, state: FSMContext):
    await state.clear()
    # Повторяем логику главного меню
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=get_main_keyboard()
    )

# Обработчик команды и кнопки /help и «Помощь»
@router.message(F.text == "ℹ️ Помощь")
@router.message(F.text == "Помощь")
@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вот список доступных команд и кнопок:\n"
        "🏠 Главное меню — вернуться в начало\n"
        "🏛️ Организация похорон — подбор услуг\n"
        "🤖 AI-помощник по документам — юридические консультации\n"
        "🛍️ Товары — каталог ритуальных товаров\n"
        "🕯️ Уголок памяти — создать мемориал\n"
        "👤 Регистрация — зарегистрировать вас в системе\n\n"
        "Просто нажмите на нужную кнопку внизу.",
        reply_markup=get_main_keyboard()
    )
