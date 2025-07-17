from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.main_keyboard import (
    get_funeral_services_keyboard,
    get_funeral_budget_keyboard,
    get_cross_type_keyboard,
)

router = Router()

# Словарь для отображения русских названий услуг
SERVICE_LABELS = {
    "transport": "Перевозка тела",
    "coffin": "Гроб",
    "wreaths": "Венки",
    "cross": "Крест",
    "hall": "Прощальный зал",
    "ceremoniymaster": "Церемониймейстер",
    "simple_funeral": "Обычные похороны",
    "cremation": "Кремация"
}

class FuneralForm(StatesGroup):
    waiting_for_address = State()
    waiting_for_wreaths = State()

# Начало сценария "Организация похорон"
@router.message(F.text == "🏛️ Организация похорон")
async def funeral_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(selected_services=[])
    await message.answer(
        "🖤 *Примите наши искренние соболезнования...*\n\n"
        "Выберите необходимые услуги (можно несколько):",
        parse_mode="Markdown",
        reply_markup=get_funeral_services_keyboard()
    )

# Обработка выбора услуги
@router.callback_query(F.data.startswith("funeral_service:"))
async def funeral_service_callback(call: CallbackQuery, state: FSMContext):
    action = call.data.split(":")[1]
    data = await state.get_data()
    selected = data.get("selected_services", [])

    if action == "done":
        # Завершение — выбор бюджета
        await call.message.answer("Пожалуйста, выберите бюджет похорон:", reply_markup=get_funeral_budget_keyboard())
        await call.answer()
        return

    if action not in selected:
        selected.append(action)
        await state.update_data(selected_services=selected)

    # Реализация логики для отдельных услуг:
    if action == "transport":
        await call.message.answer("Пожалуйста, укажите адрес, где находится тело:")
        await state.set_state(FuneralForm.waiting_for_address)
    elif action == "wreaths":
        await call.message.answer("Сколько венков вам потребуется?")
        await state.set_state(FuneralForm.waiting_for_wreaths)
    elif action == "cross":
        await call.message.answer("Выберите вариант креста:", reply_markup=get_cross_type_keyboard())
    else:
        # Просто обновляем меню (отмечая выбранное)
        await call.message.edit_reply_markup(reply_markup=get_funeral_services_keyboard(selected))
    await call.answer()

# Получение адреса для перевозки
@router.message(FuneralForm.waiting_for_address)
async def handle_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    selected = data.get("selected_services", [])
    await message.answer("Спасибо! Адрес записан.")
    # Возвращаем меню для дальнейшего выбора
    await message.answer(
        "Можете выбрать другие услуги:",
        reply_markup=get_funeral_services_keyboard(selected)
    )
    await state.set_data({"selected_services": selected, **data})

# Получение количества венков
@router.message(FuneralForm.waiting_for_wreaths)
async def handle_wreaths(message: Message, state: FSMContext):
    await state.update_data(wreaths=message.text)
    data = await state.get_data()
    selected = data.get("selected_services", [])
    await message.answer("Количество венков записано.")
    await message.answer(
        "Можете выбрать другие услуги:",
        reply_markup=get_funeral_services_keyboard(selected)
    )
    await state.set_data({"selected_services": selected, **data})

# Обработка выбора типа креста
@router.callback_query(F.data.startswith("cross:"))
async def cross_type_callback(call: CallbackQuery, state: FSMContext):
    cross_type = call.data.split(":")[1]
    cross_label = {
        "orthodox": "Православный",
        "catholic": "Католический",
        "metal": "Металлический",
        "wood": "Деревянный"
    }.get(cross_type, cross_type)
    await state.update_data(cross_type=cross_label)
    data = await state.get_data()
    selected = data.get("selected_services", [])
    await call.message.answer(f"Выбран крест: {cross_label}.")
    await call.message.answer(
        "Можете выбрать другие услуги:",
        reply_markup=get_funeral_services_keyboard(selected)
    )
    await state.set_data({"selected_services": selected, **data})
    await call.answer()

# Обработка выбора бюджета
@router.callback_query(F.data.startswith("budget:"))
async def budget_chosen(call: CallbackQuery, state: FSMContext):
    budget = call.data.split(":")[1]
    await state.update_data(budget=budget)
    data = await state.get_data()
    summary = f"Выбранный бюджет: до {budget} руб.\n"
    if 'address' in data:
        summary += f"Адрес перевозки: {data['address']}\n"
    if 'wreaths' in data:
        summary += f"Количество венков: {data['wreaths']}\n"
    if 'cross_type' in data:
        summary += f"Тип креста: {data['cross_type']}\n"
    # --- Русские названия выбранных услуг ---
    selected_keys = data.get("selected_services", [])
    services_rus = [SERVICE_LABELS.get(key, key) for key in selected_keys]
    summary += "Выбранные услуги: " + ", ".join(services_rus)
    await call.message.answer("Спасибо! Ваша заявка принята.\n" + summary)
    await state.clear()
    await call.answer()
