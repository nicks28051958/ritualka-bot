from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_IDS
from keyboards.main_keyboard import (
    get_main_keyboard,
    get_admin_panel_keyboard,
    get_cancel_keyboard,
)
from states.states import AddProduct
from database.db import Database

router = Router()


def get_confirm_keyboard(step: str):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"add_product:{step}:confirm"),
        InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"add_product:{step}:edit"),
    )
    builder.adjust(2)
    return builder.as_markup()


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
async def add_product(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AddProduct.waiting_for_name)
    await message.answer(
        "Введите вид товара:",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddProduct.waiting_for_name)
async def process_product_name(message: Message, state: FSMContext):
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "❌ Добавление товара отменено.",
            reply_markup=get_admin_panel_keyboard(),
        )
        return

    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(AddProduct.confirm_name)
    await message.answer(
        f"Вид товара: <b>{name}</b>",
        reply_markup=get_confirm_keyboard("name"),
    )


@router.callback_query(F.data == "add_product:name:confirm")
async def confirm_product_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AddProduct.waiting_for_price)
    await callback.message.edit_text("Введите цену товара:")
    await callback.message.answer(
        "Введите цену товара:",
        reply_markup=get_cancel_keyboard(),
    )


@router.callback_query(F.data == "add_product:name:edit")
async def edit_product_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AddProduct.waiting_for_name)
    await callback.message.edit_text("Введите вид товара:")
    await callback.message.answer(
        "Введите вид товара:",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddProduct.waiting_for_price)
async def process_product_price(message: Message, state: FSMContext):
    if message.text.lower() == "❌ отмена":
        await state.clear()
        await message.answer(
            "❌ Добавление товара отменено.",
            reply_markup=get_admin_panel_keyboard(),
        )
        return

    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректную цену:")
        return

    await state.update_data(price=price)
    await state.set_state(AddProduct.confirm_price)
    await message.answer(
        f"Цена товара: {price} ₽",
        reply_markup=get_confirm_keyboard("price"),
    )


@router.callback_query(F.data == "add_product:price:confirm")
async def confirm_product_price(callback: CallbackQuery, state: FSMContext, db: Database):
    await callback.answer()
    data = await state.get_data()
    name = data.get("name")
    price = data.get("price")
    await db.add_product(name=name, price=price)
    await state.clear()
    await callback.message.edit_text("✅ Товар добавлен.")
    await callback.message.answer(
        "🛠 <b>Админ-панель</b>",
        reply_markup=get_admin_panel_keyboard(),
    )


@router.callback_query(F.data == "add_product:price:edit")
async def edit_product_price(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AddProduct.waiting_for_price)
    await callback.message.edit_text("Введите цену товара:")
    await callback.message.answer(
        "Введите цену товара:",
        reply_markup=get_cancel_keyboard(),
    )


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

