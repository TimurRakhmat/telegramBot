from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_kb():
    kb_list = [
        [KeyboardButton(text="📝 Добавить место"),
         KeyboardButton(text="🎯 Выбрать место"),]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def stop_fsm():
    kb_list = [
        [KeyboardButton(text="❌ Остановить сценарий")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Для того чтоб остановить сценарий FSM нажми на одну из двух кнопок👇"
    )


def add_place_check():
    kb_list = [
        [KeyboardButton(text="✅ Все верно"), KeyboardButton(text="❌ Отменить")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def add_rate_kb():
    kb_list = [
        [KeyboardButton(text="1️⃣"),
         KeyboardButton(text="2️⃣"),
         KeyboardButton(text="3️⃣"),
         KeyboardButton(text="4️⃣"),
         KeyboardButton(text="5️⃣")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def main_visit_kb():
    kb_list = [
        [KeyboardButton(text="📝 хочу посетить"), KeyboardButton(text="📋 давай дальше")],
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )