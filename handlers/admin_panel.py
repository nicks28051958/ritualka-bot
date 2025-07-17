from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import ADMIN_IDS
from keyboards.main_keyboard import get_main_keyboard, get_admin_panel_keyboard

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
@router.message(F.text == "🛠 Админ-панель")
async def admin_menu(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа.")
        return
    await message.answer("🛠 <b>Админ-панель</b>", reply_markup=get_admin_panel_keyboard())


@router.message(F.text == "➕ Добавить товар")
async def add_product(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Заглушка добавления товара.")


@router.message(F.text == "➖ Удалить товар")
async def remove_product(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Заглушка удаления товара.")


@router.message(F.text == "⬅️ Назад")
async def back_to_main_from_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_main_keyboard(is_admin=True)
    )

