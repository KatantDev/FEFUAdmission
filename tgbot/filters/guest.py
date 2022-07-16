from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message

from tgbot.models.database import User


class GuestFilter(BaseFilter):
    guest: type(None) = None

    async def __call__(self, obj: Message) -> bool:
        return (await User.filter(id=obj.from_user.id).first()) is None
