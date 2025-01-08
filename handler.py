from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import dao
import kb

router = Router()


class AddPlaceStates(StatesGroup):
    content = State()  
    sport = State()
    culture = State()
    night = State()
    check_state = State()  


class CheckVisited(StatesGroup):
    content = State()  
    sport = State()
    culture = State()
    night = State()
    check_state = State()  


@router.message(F.text == '🏠 Главное меню')
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await dao.set_user(tg_id=message.from_user.id,
                          username=message.from_user.username,
                          full_name=message.from_user.full_name)
    greeting = f"Привет, {message.from_user.full_name}! Выбери необходимое действие"
    if user is None:
        greeting = f"Привет, новый пользователь! Выбери необходимое действие"

    await message.answer(greeting, reply_markup=kb.main_kb())


@router.message(F.text == '❌ Остановить сценарий')
async def stop_fsm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Сценарий остановлен. Для выбора действия воспользуйся клавиатурой ниже",
                         reply_markup=kb.main_kb())



@router.callback_query(F.data == 'main_menu')
async def main_menu_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Вы вернулись в главное меню.')
    await call.message.answer(f"Привет, {call.from_user.full_name}! Выбери необходимое действие",
                              reply_markup=kb.main_kb())


@router.message(F.text == '📝 Добавить место')
async def start_add_place(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Отправь картинку и описание места",
                         reply_markup=kb.stop_fsm())
    await state.set_state(AddPlaceStates.content)


@router.message(F.photo, AddPlaceStates.content)
async def start_questionnaire_process(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await state.update_data(caption=message.text or message.caption)
    await message.answer('Оцени место от 1 до 5 как активный/спортивный отдых',
                         reply_markup=kb.add_rate_kb())
    await state.set_state(AddPlaceStates.sport)


def getRate(rateSign: str) -> int:
    match rateSign:
        case "1️⃣" : return 1
        case "2️⃣" : return 2
        case "3️⃣" : return 3
        case "4️⃣" : return 4
        case "5️⃣" : return 5

    return 0
 


@router.message(F.text, AddPlaceStates.sport)
async def start_sport_process(message: Message, state: FSMContext):
    if not getRate(message.text):
        await message.answer('Оцени место от 1 до 5 как активный/спортивный отдых',
                         reply_markup=kb.add_rate_kb())
        return
    
    await state.update_data(sport=getRate(message.text))
    await message.answer('Оцени место от 1 до 5 как культурный отдых',
                         reply_markup=kb.add_rate_kb())
    await state.set_state(AddPlaceStates.culture)


@router.message(F.text, AddPlaceStates.culture)
async def start_culture_process(message: Message, state: FSMContext):
    if not getRate(message.text):
        await message.answer('Оцени место от 1 до 5 как культурный отдых',
                         reply_markup=kb.add_rate_kb())
        return
    
    await state.update_data(culture=getRate(message.text))
    await message.answer('Оцени место от 1 до 5 как ночной/молодежный отдых',
                         reply_markup=kb.add_rate_kb())
    await state.set_state(AddPlaceStates.night)


@router.message(F.text, AddPlaceStates.night)
async def start_night_process(message: Message, state: FSMContext):
    if not getRate(message.text):
        await message.answer('Оцени место от 1 до 5 как ночной/молодежный отдых',
                         reply_markup=kb.add_rate_kb())
        return
    
    await state.update_data(night=getRate(message.text))

    data = await state.get_data()
    caption = f'Пожалуйста, проверьте все ли верно: \n\n' \
              f'<b>описание</b>: {data.get("caption")}\n' \
              f'<b>Спорт</b>: {data.get("sport")}\n' \
              f'<b>Культура</b>: {data.get("culture")}\n' \
              f'<b>Развлечение</b>: {data.get("night")}'

    await message.answer_photo(photo=data.get('photo'), caption=caption, reply_markup=kb.add_place_check())
    await state.set_state(AddPlaceStates.check_state)


@router.message(AddPlaceStates.check_state, F.text == '✅ Все верно')
async def confirm_add_note(message: Message, state: FSMContext):
    place = await state.get_data()
    await dao.add_place(placename=place.get("caption"), 
                        active_recreation=place.get("sport"),
                        cultural_event=place.get("culture"),
                        nightlife=place.get("night"),
                        file_id=place.get("photo"))
    await message.answer('Место успешно добавлено!', reply_markup=kb.main_kb())
    await state.clear()


@router.message(AddPlaceStates.check_state, F.text == '❌ Отменить')
async def cancel_add_note(message: Message, state: FSMContext):
    await message.answer('Добавление места отменено!', reply_markup=kb.main_kb())
    await state.clear()



@router.message(F.text == '🎯 Выбрать место')
@router.message(F.text == "📋 давай дальше")
async def start_visit_check(message: Message, state: FSMContext):
    user_data = await state.get_data()
    offset = user_data.get("offset")
    if not offset:
        offset = 1
    data = await dao.get_place(offset=offset, user_id=message.from_user.id)
    await state.update_data(offset=offset+1)

    if not data:
        await state.update_data(offset=1)
        await message.answer('Все места просмотрены, подождите пока они появяться снова или просмотрите еще раз',
                              reply_markup=kb.main_visit_kb())
        return

    caption = f'Стоит посетить: \n\n' \
              f'<b>описание</b>: {data.placename}\n' \
              f'<b>Спорт</b>: {data.active_recreation}\n' \
              f'<b>Культура</b>: {data.cultural_event}\n' \
              f'<b>Развлечение</b>: {data.nightlife}'

    await state.update_data(place_id=data.id)
    await message.answer_photo(photo=data.img_id, caption=caption, reply_markup=kb.main_visit_kb())
    await state.set_state(CheckVisited.content)


@router.message(F.text == "📝 хочу посетить", CheckVisited.content)
async def start_set_visit_mark(message: Message, state: FSMContext):
    await message.answer('Оцени место после посещения от 1 до 5',
                         reply_markup=kb.add_rate_kb())
    await state.set_state(CheckVisited.sport)


@router.message(F.text, CheckVisited.sport)
async def start_set_visit_rate(message: Message, state: FSMContext):
    if not getRate(message.text):
        await message.answer('Оцени место после посещения от 1 до 5',
                         reply_markup=kb.add_rate_kb())
        return
    
    place = await state.get_data()
    await dao.add_rate(user_id=message.from_user.id, 
                       place_id=place.get("place_id"),
                       rating=getRate(message.text))
    # await state.update_data(sport=getRate(message.text))
    await message.answer('Надеюсь вам все понравилос...',
                         reply_markup=kb.main_kb())