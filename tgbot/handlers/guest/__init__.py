from aiogram import Router

from tgbot.filters.guest import GuestFilter
from tgbot.handlers.guest.welcome import start


guest_router = Router()
guest_router.message.filter(GuestFilter())


guest_router.message.register(start, commands=['start'])
