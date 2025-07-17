import os
import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Voice, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from services.openai_service import OpenAIService
from keyboards.main_keyboard import get_main_keyboard
from states.states import AIHelper, ClientRegistration, FuneralForm, MemoryRecord

router = Router()

def get_voice_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="voice:confirm")],
        [InlineKeyboardButton(text="✏️ Изменить", callback_data="voice:edit")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="voice:cancel")],
    ])
    return builder

@router.message(F.voice)
async def process_voice_message(message: Message, db, state: FSMContext):
    logging.info(f"[VOICE] Получено голосовое сообщение от {message.from_user.id}")
    voice: Voice = message.voice
    file = await message.bot.get_file(voice.file_id)
    file_path = file.file_path
    local_path = f"voice_{message.from_user.id}_{voice.file_id}.ogg"
    await message.bot.download_file(file_path, local_path)

    try:
        openai_service = OpenAIService()
        loop = asyncio.get_running_loop()
        transcript = await loop.run_in_executor(
            None,
            lambda: openai_service.transcribe_voice_sync(local_path)
        )
        os.remove(local_path)
        if not transcript or len(transcript.strip()) < 2:
            await message.answer("❌ Не удалось распознать голосовое сообщение. Попробуйте еще раз или говорите чётче.")
            logging.warning(f"[VOICE] Не удалось распознать голосовое сообщение от {message.from_user.id}")
            return
        # Логируем голосовое сообщение
        await db.log_chat_message(message.from_user.id, "voice", transcript, "voice_transcription", True)
        # Сохраняем транскрипцию и состояние
        current_state = await state.get_state()
        await state.update_data(voice_transcript=transcript, voice_state=current_state)
        await message.answer(
            f"📝 Распознанный текст:\n<code>{transcript}</code>\n\nПодтвердите или отредактируйте текст.",
            reply_markup=get_voice_confirm_keyboard(),
            parse_mode="HTML"
        )
        logging.info(f"[VOICE] Транскрибация завершена для {message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка транскрибации голосового сообщения: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при распознавании голосового сообщения. Попробуйте позже.")
        if os.path.exists(local_path):
            os.remove(local_path)

@router.callback_query(F.data == "voice:confirm")
async def confirm_voice(callback: CallbackQuery, state: FSMContext, db):
    logging.info(f"[VOICE] Подтверждение голосового сообщения от {callback.from_user.id}")
    from handlers.ai_lawyer import process_ai_question
    from handlers.registration import (
        process_full_name, process_phone, process_email, process_birth_date, process_passport_series, process_passport_number, process_passport_issued_by, process_passport_issue_date, process_address, process_emergency_contact, process_relationship
    )
    from handlers.funeral import (
        process_body_location, process_funeral_type, process_services, process_budget
    )
    from handlers.memory import (
        process_memory_photo, process_memory_name, process_birth_date as process_memory_birth_date, process_death_date as process_memory_death_date, process_memory_text
    )
    data = await state.get_data()
    transcript = data.get("voice_transcript")
    voice_state = data.get("voice_state")
    if not transcript or not voice_state:
        await callback.answer("Нет текста для отправки", show_alert=True)
        return
    class MessageWithText:
        def __init__(self, orig_message, text):
            self.__dict__.update(orig_message.__dict__)
            self.text = text
        async def answer(self, *args, **kwargs):
            return await callback.message.answer(*args, **kwargs)
        async def reply(self, *args, **kwargs):
            return await callback.message.reply(*args, **kwargs)
    fake_message = MessageWithText(callback.message, transcript)
    logging.info(f"[VOICE] Передаю текст в обработчик состояния: {voice_state}")
    if voice_state == AIHelper.waiting_for_question.state:
        await process_ai_question(fake_message, state, db)
    elif voice_state == ClientRegistration.waiting_for_full_name.state:
        await process_full_name(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_phone.state:
        await process_phone(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_email.state:
        await process_email(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_birth_date.state:
        await process_birth_date(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_passport_series.state:
        await process_passport_series(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_passport_number.state:
        await process_passport_number(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_passport_issued_by.state:
        await process_passport_issued_by(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_passport_issue_date.state:
        await process_passport_issue_date(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_address.state:
        await process_address(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_emergency_contact.state:
        await process_emergency_contact(fake_message, state)
    elif voice_state == ClientRegistration.waiting_for_relationship.state:
        await process_relationship(fake_message, state)
    elif voice_state == FuneralForm.waiting_for_body_location.state:
        await process_body_location(fake_message, state, db)
    elif voice_state == FuneralForm.waiting_for_funeral_type.state:
        await process_funeral_type(fake_message, state, db)
    elif voice_state == FuneralForm.waiting_for_services.state:
        await process_services(fake_message, state, db)
    elif voice_state == FuneralForm.waiting_for_budget.state:
        await process_budget(fake_message, state, db)
    elif voice_state == MemoryRecord.waiting_for_photo.state:
        await process_memory_photo(fake_message, state)
    elif voice_state == MemoryRecord.waiting_for_name.state:
        await process_memory_name(fake_message, state)
    elif voice_state == MemoryRecord.waiting_for_birth_date.state:
        await process_memory_birth_date(fake_message, state)
    elif voice_state == MemoryRecord.waiting_for_death_date.state:
        await process_memory_death_date(fake_message, state)
    elif voice_state == MemoryRecord.waiting_for_memory_text.state:
        await process_memory_text(fake_message, state, db)
    else:
        await callback.message.answer(f"📝 Распознанный текст:\n<code>{transcript}</code>", parse_mode="HTML")
        await callback.message.answer("Выберите действие из меню.", reply_markup=get_main_keyboard())
    await state.update_data(voice_transcript=None, voice_state=None)
    await callback.answer()

@router.callback_query(F.data == "voice:edit")
async def edit_voice_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        "✏️ Введите исправленный текст:",
        reply_markup=None
    )
    data = await state.get_data()
    await state.update_data(voice_edit_state=data.get("voice_state"))

@router.message()
async def handle_voice_edit_text(message: Message, state: FSMContext, db):
    data = await state.get_data()
    voice_edit_state = data.get("voice_edit_state")
    if not voice_edit_state:
        return  # Не обрабатываем, чтобы другие роутеры могли обработать
    from handlers.ai_lawyer import process_ai_question
    from handlers.registration import (
        process_full_name, process_phone, process_email, process_birth_date, process_passport_series, process_passport_number, process_passport_issued_by, process_passport_issue_date, process_address, process_emergency_contact, process_relationship
    )
    from handlers.funeral import (
        process_body_location, process_funeral_type, process_services, process_budget
    )
    from handlers.memory import (
        process_memory_photo, process_memory_name, process_birth_date as process_memory_birth_date, process_death_date as process_memory_death_date, process_memory_text
    )
    class MessageWithText:
        def __init__(self, orig_message, text):
            self.__dict__.update(orig_message.__dict__)
            self.text = text
        async def answer(self, *args, **kwargs):
            return await message.answer(*args, **kwargs)
        async def reply(self, *args, **kwargs):
            return await message.reply(*args, **kwargs)
    fake_message = MessageWithText(message, message.text)
    if voice_edit_state == AIHelper.waiting_for_question.state:
        await process_ai_question(fake_message, state, db)
    elif voice_edit_state == ClientRegistration.waiting_for_full_name.state:
        await process_full_name(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_phone.state:
        await process_phone(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_email.state:
        await process_email(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_birth_date.state:
        await process_birth_date(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_passport_series.state:
        await process_passport_series(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_passport_number.state:
        await process_passport_number(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_passport_issued_by.state:
        await process_passport_issued_by(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_passport_issue_date.state:
        await process_passport_issue_date(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_address.state:
        await process_address(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_emergency_contact.state:
        await process_emergency_contact(fake_message, state)
    elif voice_edit_state == ClientRegistration.waiting_for_relationship.state:
        await process_relationship(fake_message, state)
    elif voice_edit_state == FuneralForm.waiting_for_body_location.state:
        await process_body_location(fake_message, state)
    elif voice_edit_state == FuneralForm.waiting_for_funeral_type.state:
        await process_funeral_type(fake_message, state)
    elif voice_edit_state == FuneralForm.waiting_for_services.state:
        await process_services(fake_message, state)
    elif voice_edit_state == FuneralForm.waiting_for_budget.state:
        await process_budget(fake_message, state)
    elif voice_edit_state == MemoryRecord.waiting_for_photo.state:
        await process_memory_photo(fake_message, state)
    elif voice_edit_state == MemoryRecord.waiting_for_name.state:
        await process_memory_name(fake_message, state)
    elif voice_edit_state == MemoryRecord.waiting_for_birth_date.state:
        await process_memory_birth_date(fake_message, state)
    elif voice_edit_state == MemoryRecord.waiting_for_death_date.state:
        await process_memory_death_date(fake_message, state)
    elif voice_edit_state == MemoryRecord.waiting_for_memory_text.state:
        await process_memory_text(fake_message, state, db)
    await state.update_data(voice_edit_state=None)

@router.callback_query(F.data == "voice:cancel")
async def cancel_voice(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Отправка голосового сообщения отменена")
    await state.clear()
    await callback.message.edit_text("❌ Отправка голосового сообщения отменена.")
    await callback.message.answer("🏠 Главное меню", reply_markup=get_main_keyboard()) 