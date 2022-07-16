from aiogram.types import Message

import localization
from tgbot.keyboards import reply
from tgbot.models.database import User


async def start(message: Message):
    await User.create(
        id=message.from_user.id,
        status='enrollee',
        check_agreement=False,
        notifications=False
    )
    await message.answer(
        localization.USER_START, reply_markup=reply.main.as_markup(resize_keyboard=True)
    )
