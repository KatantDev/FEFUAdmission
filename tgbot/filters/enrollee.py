from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message

from tgbot.models.database import User


class EnrolleeFilter(BaseFilter):
    enrollee: str = 'enrollee'

    async def __call__(self, obj: Message) -> bool:
        return (await User.get(id=obj.from_user.id)).status == self.enrollee
