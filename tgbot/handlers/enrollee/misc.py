from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

import localization
from tgbot.keyboards import reply


async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        localization.ENROLLEE_START, reply_markup=reply.main.as_markup(resize_keyboard=True)
    )
