from enum import Enum

from aiogram.dispatcher.filters.callback_data import CallbackData


class SettingsAction(str, Enum):
    snils = 'snils'
    faculties = 'faculties'
    check_agreement = 'check_agreement'
    notifications = 'notifications'
    return_settings = 'return_settings'


class FacultiesAction(str, Enum):
    back = 'back'
    confirm = 'confirm'
    next = 'next'


class FacultiesType(str, Enum):
    select = 'select'
    unselect = 'unselect'


class Settings(CallbackData, prefix='settings'):
    action: SettingsAction


class FacultiesActions(CallbackData, prefix='f_actions'):
    action: FacultiesAction
    offset: int


class Faculties(CallbackData, prefix='faculties'):
    type: FacultiesType
    id: int
    offset: int

