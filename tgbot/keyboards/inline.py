from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import localization
from tgbot.keyboards.callback import Settings, Faculties, FacultiesActions
from tgbot.models.database import Faculty, SelectedFaculty, User

settings = InlineKeyboardBuilder()
for settings_key, settings_value in localization.SETTINGS_MENU.items():
    settings.add(
        InlineKeyboardButton(
            text=settings_value,
            callback_data=Settings(action=settings_key).pack()
        )
    )
settings.adjust(1)

return_settings = InlineKeyboardBuilder()
return_settings.add(
    InlineKeyboardButton(
        text=localization.RETURN_SETTINGS,
        callback_data=Settings(action='return_settings').pack()
    )
)


async def faculties(user_id: int, offset: int = 0, limit: int = 10) -> InlineKeyboardBuilder:
    faculties_count = await Faculty.all().count()
    faculties_data = await Faculty.all().offset(offset).limit(limit)

    user = await User.get(id=user_id)
    selected_faculties = await SelectedFaculty.filter(user=user).all()\
        .prefetch_related('faculty').values_list('faculty__id', flat=True)

    keyboard = InlineKeyboardBuilder()
    for faculty in faculties_data:
        if faculty.id not in selected_faculties:
            keyboard.row(
                InlineKeyboardButton(
                    text=f'{localization.UNSELECTED_FACULTY} | {faculty.code} {faculty.name}',
                    callback_data=Faculties(type='select', id=faculty.id, offset=offset).pack()
                )
            )
        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=f'{localization.SELECTED_FACULTY} | {faculty.code} {faculty.name}',
                    callback_data=Faculties(type='unselect', id=faculty.id, offset=offset).pack()
                )
            )

    if offset != 0:
        keyboard.row(
            InlineKeyboardButton(
                text=localization.FACULTIES_ACTIONS['back'],
                callback_data=FacultiesActions(action='back', offset=offset - limit).pack()
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text=localization.FACULTIES_ACTIONS['confirm'],
                callback_data=FacultiesActions(action='confirm', offset=offset).pack()
            )
        )
    else:
        keyboard.row(
            InlineKeyboardButton(
                text=localization.FACULTIES_ACTIONS['confirm'],
                callback_data=FacultiesActions(action='confirm', offset=offset).pack()
            )
        )

    if offset + limit < faculties_count:
        keyboard.add(
            InlineKeyboardButton(
                text=localization.FACULTIES_ACTIONS['next'],
                callback_data=FacultiesActions(action='next', offset=offset + limit).pack()
            )
        )
    return keyboard
