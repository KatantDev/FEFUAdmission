from aiogram import Router, F
from aiogram.dispatcher.filters import Command

import localization
from tgbot.filters.enrollee import EnrolleeFilter
from tgbot.handlers.enrollee.check_places import check_places
from tgbot.handlers.enrollee.misc import start
from tgbot.handlers.enrollee.settings import settings, agreement, notifications, enter_snils, change_snils, \
    incorrect_snils, return_settings, change_faculties, faculties_paginate, select_faculty, unselect_faculty
from tgbot.keyboards.callback import SettingsAction, Settings, FacultiesActions, FacultiesAction, Faculties, \
    FacultiesType
from tgbot.misc.states import Snils

enrollee_router = Router()
enrollee_router.message.filter(EnrolleeFilter())


enrollee_router.message.register(start, Command(commands='start'), state='*')

enrollee_router.message.register(settings, F.text == localization.ENROLLEE_MENU['settings'], state='*')
enrollee_router.callback_query.register(agreement, Settings.filter(F.action == SettingsAction.check_agreement))
enrollee_router.callback_query.register(notifications, Settings.filter(F.action == SettingsAction.notifications))

enrollee_router.callback_query.register(enter_snils, Settings.filter(F.action == SettingsAction.snils))
enrollee_router.message.register(
    change_snils, F.text.regexp(r'^\d{9}$') | F.text.regexp(r'^\d{3}-\d{3}-\d{3} \d{2}$'), Snils.wait_for_ans
)
enrollee_router.message.register(incorrect_snils, Snils.wait_for_ans)
enrollee_router.callback_query.register(
    return_settings, Settings.filter(F.action == SettingsAction.return_settings), Snils.wait_for_ans
)

enrollee_router.callback_query.register(change_faculties, Settings.filter(F.action == SettingsAction.faculties))
enrollee_router.callback_query.register(return_settings, FacultiesActions.filter(F.action == FacultiesAction.confirm))
enrollee_router.callback_query.register(
    faculties_paginate, FacultiesActions.filter(F.action != FacultiesAction.confirm)
)
enrollee_router.callback_query.register(select_faculty, Faculties.filter(F.type == FacultiesType.select))
enrollee_router.callback_query.register(unselect_faculty, Faculties.filter(F.type == FacultiesType.unselect))


enrollee_router.message.register(check_places, F.text == localization.ENROLLEE_MENU['check_places'])
