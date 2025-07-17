from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from keyboards.main_keyboard import (
    get_main_keyboard,
    get_cancel_keyboard,
    get_ai_lawyer_actions_keyboard  # Новый импорт!
)
from config import ADMIN_IDS
from services.openai_service import OpenAIService
from database.db import Database
from states.states import AIHelper

router = Router()

@router.message(Command("ask_lawyer"))
@router.message(Command("documents"))
@router.message(F.text == "🤖 AI-помощник по документам")
async def start_ai_lawyer(message: Message, state: FSMContext):
    """Начало работы с AI-помощником"""
    await state.set_state(AIHelper.waiting_for_question)
    help_text = """
🤖 **AI-помощник по документам**

Я помогу вам с вопросами по оформлению документов для похорон.

📋 **Примеры вопросов:**
• Как оформить свидетельство о смерти?
• Какие документы нужны для кремации?
• Как получить справку о смерти?
• Какие льготы положены при похоронах?

💬 **Задайте ваш вопрос:**
(максимум 500 символов)
    """.strip()
    await message.answer(help_text, reply_markup=get_cancel_keyboard())

@router.message(AIHelper.waiting_for_question, F.text)
async def process_ai_question(message: Message, state: FSMContext, db: Database):
    """Обработка вопроса для AI-помощника"""
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "❌ Действие отменено.",
            reply_markup=get_main_keyboard(is_admin=message.from_user.id in ADMIN_IDS)
        )
        return

    question = message.text.strip()
    logging.info(f"AI-помощник: получен вопрос: {question}")

    # Проверяем длину вопроса
    if len(question) > 500:
        await message.answer(
            "⚠️ Вопрос слишком длинный. Максимум 500 символов.\n"
            "Сократите ваш вопрос и попробуйте снова."
        )
        return

    # Проверяем на пустой ввод
    if not question or question.isspace():
        await message.answer(
            "⚠️ Вопрос не может быть пустым. Пожалуйста, задайте ваш вопрос."
        )
        return

    # Логируем запрос
    await db.log_request(
        telegram_id=message.from_user.id,
        request_type="ai_lawyer",
        request_data=question
    )

    # Отправляем сообщение о обработке
    processing_msg = await message.answer("🤖 Обрабатываю ваш вопрос...")

    try:
        # Получаем ответ от AI
        openai_service = OpenAIService()
        response = await openai_service.get_legal_advice(question)

        # Логируем ответ
        await db.log_request(
            telegram_id=message.from_user.id,
            request_type="ai_lawyer_response",
            request_data=question,
            response_data=response
        )

        # Отправляем ответ с инлайн-клавиатурой
        await processing_msg.edit_text(
            f"🤖 **Ответ на ваш вопрос:**\n\n{response}\n\n"
            "Выберите действие ниже:",
            reply_markup=get_ai_lawyer_actions_keyboard()
        )

    except Exception as e:
        logging.error(f"Ошибка AI-помощника: {e}", exc_info=True)
        await processing_msg.edit_text(
            "❌ Произошла ошибка при обработке вашего вопроса.\n"
            "Попробуйте позже или обратитесь к администратору."
        )
    # Не очищаем state! — пользователь сам решает, что делать дальше

# ===== Обработка кнопок после ответа ассистента =====

@router.callback_query(F.data == "ai_lawyer:ask_again")
async def ai_lawyer_ask_again(call: CallbackQuery, state: FSMContext):
    await state.set_state(AIHelper.waiting_for_question)
    help_text = (
        "🤖 **AI-помощник по документам**\n\n"
        "Задайте следующий вопрос (максимум 500 символов):"
    )
    await call.message.answer(help_text, reply_markup=get_cancel_keyboard())
    await call.answer()

@router.callback_query(F.data == "ai_lawyer:to_main")
async def ai_lawyer_to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=get_main_keyboard(is_admin=call.from_user.id in ADMIN_IDS)
    )
    await call.answer()
