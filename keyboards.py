# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder # Удобный построитель

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру главного меню."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📜 Искать Фрагмент", callback_data="action:seek")
    )
    builder.row(
        InlineKeyboardButton(text="👁️‍🗨️ Узреть Знак", callback_data="action:sigil")
    )
    builder.row(
        InlineKeyboardButton(text="📚 Запросить Лор", callback_data="action:lore_menu")
    )
    builder.row(
        InlineKeyboardButton(text="✨ Иные Тайны", callback_data="action:mysteries_menu")
    )
    return builder.as_markup()

def lore_topics_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора тем лора."""
    builder = InlineKeyboardBuilder()
    # Добавляем кнопки для конкретных тем
    builder.button(text="Библиотека", callback_data="action:lore:library")
    builder.button(text="Масоны", callback_data="action:lore:masons")
    builder.button(text="Иллюминаты", callback_data="action:lore:illuminati")
    # Кнопка для запроса другой темы текстом
    builder.button(text="Другое (введите тему)", callback_data="action:lore:other")
    # Кнопка Назад
    builder.button(text="⬅️ Назад", callback_data="action:main_menu")
    # Расставляем кнопки (можно настроить ширину)
    builder.adjust(2, 2, 1) # 2 кнопки в первых двух рядах, 1 в последнем
    return builder.as_markup()

def mysteries_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для меню "Иные Тайны"."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏺 Найти Артефакт", callback_data="action:mystery:artifact")
    builder.button(text="🔢 Число Судьбы", callback_data="action:mystery:numerology")
    builder.button(text="🃏 Карта Дня", callback_data="action:mystery:tarot")
    builder.button(text="⬅️ Назад", callback_data="action:main_menu")
    builder.adjust(1) # По одной кнопке в ряд
    return builder.as_markup()

def back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
     """Клавиатура с кнопкой "Назад" в главное меню."""
     builder = InlineKeyboardBuilder()
     builder.button(text="⬅️ Назад", callback_data="action:main_menu")
     return builder.as_markup()