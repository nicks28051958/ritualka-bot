import pytest
from keyboards.main_keyboard import (
    get_main_keyboard,
    get_admin_panel_keyboard,
    get_admin_category_keyboard,
)


def extract(btn_markup):
    return [btn.text for row in btn_markup.keyboard for btn in row]


def test_admin_button_present():
    buttons = extract(get_main_keyboard(is_admin=True))
    assert "🛠 Админ-панель" in buttons


def test_admin_button_absent():
    buttons = extract(get_main_keyboard(is_admin=False))
    assert "🛠 Админ-панель" not in buttons


def test_admin_panel_keyboard():
    buttons = extract(get_admin_panel_keyboard())
    assert buttons == ["➕ Добавить товар", "➖ Удалить товар", "⬅️ Назад"]


def test_admin_category_keyboard():
    markup = get_admin_category_keyboard()
    btns = [btn.text for row in markup.inline_keyboard for btn in row]
    assert "🗿 Памятники" in btns
    assert "🪦 Надгробия" in btns
    assert "🚧 Ограды" in btns
