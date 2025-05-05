# handlers.py
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext # Для управления состояниями
from aiogram.fsm.state import State, StatesGroup # Для определения состояний
from aiogram.utils.markdown import hitalic, hcode, hbold

# Импортируем наши генераторы и клавиатуры
import generators
import keyboards # Импортируем новый файл

# Создаем роутер (или несколько, если хотите разделить логику)
router = Router()

# --- Определяем состояния для FSM ---
class UserInput(StatesGroup):
    waiting_for_numerology = State() # Состояние ожидания слова для нумерологии
    waiting_for_lore_topic = State() # Состояние ожидания темы лора

# --- Обработчики команд ---
@router.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext):
    await state.clear() # На всякий случай сбрасываем состояние
    start_text = generators.get_lore_snippet('start')
    await message.answer(
        f"<i>{start_text}</i>",
        reply_markup=keyboards.main_menu_keyboard() # Отправляем клавиатуру
    )

# --- Обработчики нажатий на Inline кнопки (Callback Query) ---

# Обработка нажатия на кнопку главного меню (возврат)
@router.callback_query(F.data == "action:main_menu")
async def cq_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear() # Сбрасываем состояние при возврате в меню
    await callback.message.edit_text(
        f"<i>{generators.get_lore_snippet('back')}</i>\n\n{generators.get_lore_snippet('start')}",
        reply_markup=keyboards.main_menu_keyboard()
    )
    await callback.answer() # Отвечаем на колбэк, чтобы убрать "часики"

# Обработка кнопки "Искать Фрагмент"
@router.callback_query(F.data == "action:seek")
async def cq_seek(callback: types.CallbackQuery):
    await callback.answer(text="Ищем фрагмент...", show_alert=False) # Ответ для пользователя
    phrase = generators.generate_mystic_phrase()
    # Редактируем сообщение, добавляя результат под ним
    await callback.message.edit_text(
        f"{callback.message.html_text}\n\n" # Оставляем старый текст меню
        f"<i>{generators.get_lore_snippet('seek')}</i>\n📜: {hitalic(phrase)}",
        reply_markup=keyboards.main_menu_keyboard() # Показываем меню снова
    )
    # Или можно просто отправить новое сообщение:
    # await callback.message.answer(f"📜: {hitalic(phrase)}")

# Обработка кнопки "Узреть Знак"
@router.callback_query(F.data == "action:sigil")
async def cq_sigil(callback: types.CallbackQuery):
    await callback.answer("Рисуем знак...")
    sigil = generators.generate_sigil_text()
    await callback.message.edit_text(
        f"{callback.message.html_text}\n\n"
        f"<i>{generators.get_lore_snippet('sigil')}</i>\n{hcode(sigil)}\n\n{hitalic('Что он значит? Возможно, ничего. Возможно, всё.')}",
        reply_markup=keyboards.main_menu_keyboard()
    )

# Обработка кнопки "Запросить Лор" (показывает меню лора)
@router.callback_query(F.data == "action:lore_menu")
async def cq_lore_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        f"<i>{generators.get_lore_snippet('lore_select')}</i>",
        reply_markup=keyboards.lore_topics_keyboard()
    )
    await callback.answer()

# Обработка выбора конкретной темы лора
@router.callback_query(F.data.startswith("action:lore:"))
async def cq_lore_topic(callback: types.CallbackQuery, state: FSMContext):
    topic = callback.data.split(":")[-1] # Извлекаем тему из callback_data

    if topic == "other":
        # Переводим пользователя в состояние ожидания ввода темы
        await state.set_state(UserInput.waiting_for_lore_topic)
        await callback.message.edit_text(
            f"<i>{generators.get_lore_snippet('other_lore_prompt')}</i>",
            # Можно убрать клавиатуру или добавить кнопку "Отмена"
            reply_markup=keyboards.back_to_main_menu_keyboard()
        )
    else:
        lore_text = generators.get_lore_snippet(topic)
        await callback.message.edit_text(
            f"Шепот из архивов о {hbold(topic)}:\n\n<i>{lore_text}</i>",
            reply_markup=keyboards.lore_topics_keyboard() # Оставляем меню лора
        )
    await callback.answer()

# Обработка кнопки "Иные Тайны" (показывает меню тайн)
@router.callback_query(F.data == "action:mysteries_menu")
async def cq_mysteries_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        f"<i>{generators.get_lore_snippet('mysteries_select')}</i>",
        reply_markup=keyboards.mysteries_menu_keyboard()
    )
    await callback.answer()

# --- Обработчики для меню "Иные Тайны" ---

@router.callback_query(F.data == "action:mystery:artifact")
async def cq_mystery_artifact(callback: types.CallbackQuery):
    await callback.answer("Осматриваем хранилище...")
    artifact_desc = generators.generate_artifact_description()
    await callback.message.edit_text(
        f"<i>{generators.get_lore_snippet('artifact')}</i>\n\n🏺 {hitalic(artifact_desc)}",
        reply_markup=keyboards.mysteries_menu_keyboard() # Возвращаем меню тайн
    )

@router.callback_query(F.data == "action:mystery:numerology")
async def cq_mystery_numerology(callback: types.CallbackQuery, state: FSMContext):
    # Переводим в состояние ожидания ввода
    await state.set_state(UserInput.waiting_for_numerology)
    await callback.message.edit_text(
        f"<i>{generators.get_lore_snippet('numerology_prompt')}</i>",
        reply_markup=keyboards.back_to_main_menu_keyboard() # Кнопка назад/отмены
    )
    await callback.answer()

@router.callback_query(F.data == "action:mystery:tarot")
async def cq_mystery_tarot(callback: types.CallbackQuery):
    await callback.answer("Тасуем колоду...")
    card = generators.get_random_tarot_card()
    await callback.message.edit_text(
        f"<i>{generators.get_lore_snippet('tarot')}</i>\n\n🃏 {hbold(card)}",
        reply_markup=keyboards.mysteries_menu_keyboard()
    )

# --- Обработчики состояний FSM ---

# Ловим сообщение, когда бот в состоянии ожидания слова для нумерологии
@router.message(UserInput.waiting_for_numerology, F.text)
async def process_numerology_word(message: types.Message, state: FSMContext):
    word = message.text
    number, interpretation = generators.calculate_numerology(word)
    await message.answer(
        f"Слово: {hcode(word)}\nЧисло Судьбы: {hbold(str(number))}\nВибрация: <i>{interpretation}</i>",
        reply_markup=keyboards.mysteries_menu_keyboard() # Возвращаем меню тайн
    )
    await state.clear() # Выходим из состояния

# Ловим сообщение, когда бот в состоянии ожидания темы лора
@router.message(UserInput.waiting_for_lore_topic, F.text)
async def process_lore_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip().lower()
    lore_text = generators.get_lore_snippet(topic) # Пытаемся найти лор
    if lore_text == generators.get_lore_snippet("unknown_command"): # Если не нашли
        lore_text = generators.get_lore_snippet("unknown_lore")

    await message.answer(
        f"Запрос: {hitalic(topic)}\n\n<i>{lore_text}</i>",
        reply_markup=keyboards.lore_topics_keyboard() # Возвращаем меню лора
    )
    await state.clear() # Выходим из состояния


# --- Обработчик для неизвестных команд или текста (если нужно) ---
# Можно раскомментировать, если хотите реакцию на любой текст вне FSM
# @router.message(F.text)
# async def handle_any_text(message: types.Message):
#     await message.reply(generators.get_lore_snippet("unknown_command"))