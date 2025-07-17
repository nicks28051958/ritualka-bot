from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.main_keyboard import (
    get_shop_categories_keyboard, get_product_keyboard, get_main_keyboard
)
from database.db import Database

router = Router()

@router.message(Command("shop"))
@router.message(F.text == "🛍️ Товары")
async def start_shop(message: Message, db: Database):
    """Начало работы с магазином"""
    categories = await db.get_categories()
    shop_text = "\n".join([
        "🛍️ <b>Каталог товаров</b>",
        "",
        "Выберите категорию товаров:",
    ])

    await message.answer(shop_text, reply_markup=get_shop_categories_keyboard(categories))

@router.callback_query(F.data.startswith("shop:category:"))
async def show_category_products(callback: CallbackQuery, db: Database):
    """Показать товары выбранной категории"""
    category = callback.data.split(":")[2]
    
    if category == "all":
        products = await db.get_products_by_category()
    else:
        products = await db.get_products_by_category(category)
    
    if not products:
        await callback.answer("❌ Товары не найдены", show_alert=True)
        return
    
    # Отправляем первый товар с кнопками навигации
    await show_product(callback, products, 0)

@router.callback_query(F.data.startswith("shop:back"))
async def back_to_categories(callback: CallbackQuery, db: Database):
    """Возврат к категориям"""
    await start_shop(callback.message, db)

@router.callback_query(F.data.startswith("product:select:"))
async def select_product(callback: CallbackQuery, db: Database):
    """Выбор товара"""
    product_id = int(callback.data.split(":")[2])
    
    # Получаем информацию о товаре
    products = await db.get_products_by_category()
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    await callback.answer(
        f"✅ Товар '{product['name']}' добавлен в корзину!\n"
        f"Стоимость: {product['price']} ₽",
        show_alert=True
    )

async def show_product(callback: CallbackQuery, products: list, index: int):
    """Показать товар с навигацией"""
    if index >= len(products):
        index = 0
    elif index < 0:
        index = len(products) - 1
    
    product = products[index]
    
    # Формируем описание товара
    caption = f"""
🛍️ **{product['name']}**

{product['description']}

💰 **Цена:** {product['price']:,} ₽
    """.strip()
    
    # Создаем клавиатуру с навигацией
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    if len(products) > 1:
        builder.add(InlineKeyboardButton(text="⬅️", callback_data=f"shop:nav:{index-1}"))
        builder.add(InlineKeyboardButton(text=f"{index+1}/{len(products)}", callback_data="shop:info"))
        builder.add(InlineKeyboardButton(text="➡️", callback_data=f"shop:nav:{index+1}"))
        builder.adjust(3)
    
    # Кнопка выбора товара
    builder.add(InlineKeyboardButton(
        text=f"🛒 Выбрать ({product['price']} ₽)", 
        callback_data=f"product:select:{product['id']}"
    ))
    
    # Кнопка возврата
    builder.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="shop:back"))
    builder.adjust(1)
    
    keyboard = builder.as_markup()
    
    # Отправляем фото товара (если есть) или текстовое сообщение
    if product.get('photo_path') and product['photo_path'] != "photos/placeholder.jpg":
        try:
            # В реальном проекте здесь будет загрузка фото
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media="https://via.placeholder.com/400x300?text=Товар",
                    caption=caption
                ),
                reply_markup=keyboard
            )
        except:
            await callback.message.edit_text(caption, reply_markup=keyboard)
    else:
        await callback.message.edit_text(caption, reply_markup=keyboard)

@router.callback_query(F.data.startswith("shop:nav:"))
async def navigate_products(callback: CallbackQuery, db: Database):
    """Навигация по товарам"""
    index = int(callback.data.split(":")[2])
    
    # Получаем все товары
    products = await db.get_products_by_category()
    
    if not products:
        await callback.answer("❌ Товары не найдены", show_alert=True)
        return
    
    await show_product(callback, products, index)

@router.callback_query(F.data == "shop:info")
async def shop_info(callback: CallbackQuery):
    """Информация о магазине"""
    await callback.answer("ℹ️ Используйте стрелки для навигации по товарам", show_alert=True) 