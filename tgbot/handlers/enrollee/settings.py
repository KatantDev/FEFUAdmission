import asyncio

from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import localization
from tgbot.keyboards import inline
from tgbot.keyboards.callback import FacultiesActions, Faculties
from tgbot.misc.states import Snils
from tgbot.models.database import User, SelectedFaculty, Faculty


async def generate_settings_message(user_id: int) -> str:
    """
    Генерация сообщения для модуля настроек на основе информации из Базы Данных.

    :param user_id: ID пользователя для которого требуется сгенерировать сообщение.
    :return: Итоговое сообщение, готовое к отправке
    """
    user = await User.get(id=user_id).prefetch_related('selected_faculties')
    selected_faculties = await user.selected_faculties.all().prefetch_related('faculty')
    if len(selected_faculties):
        faculties = ''
        for selected_faculty in selected_faculties:
            faculties += f'\n{selected_faculty.faculty.name} ({selected_faculty.faculty.code})'
    else:
        faculties = 'Не указаны'

    return localization.SETTINGS.format(
        snils=user.snils if user.snils else 'Не указан',
        faculties=faculties,
        check_agreement='Да' if user.check_agreement else 'Нет',
        notifications='Включены' if user.notifications else 'Отключены'
    )


async def generate_faculties_message(user_id: int) -> str:
    """
    Генерация сообщения для модуля выбора факультетов на основе информации из Базы Данных.

    :param user_id: ID пользователя для которого требуется сгенерировать сообщение.
    :return: Итоговое сообщение, готовое к отправке
    """
    user = await User.get(id=user_id)
    selected_faculties = await SelectedFaculty.filter(user=user).all().prefetch_related('faculty')
    if len(selected_faculties):
        faculties = ''
        for selected_faculty in selected_faculties:
            faculties += f'\n{selected_faculty.faculty.name} ({selected_faculty.faculty.code})'
    else:
        faculties = 'Не указаны'

    return localization.FACULTIES.format(faculties=faculties)


async def settings(message: Message, state: FSMContext):
    await state.clear()

    message_text = await generate_settings_message(message.from_user.id)
    await message.answer(message_text, reply_markup=inline.settings.as_markup())


async def agreement(query: CallbackQuery):
    user = await User.get(id=query.from_user.id)
    user.check_agreement = not user.check_agreement
    await user.save()

    message_text = await generate_settings_message(query.from_user.id)
    await query.message.edit_text(message_text, reply_markup=inline.settings.as_markup())


async def notifications(query: CallbackQuery):
    user = await User.get(id=query.from_user.id)
    user.notifications = not user.notifications
    await user.save()

    message_text = await generate_settings_message(query.from_user.id)
    await query.message.edit_text(message_text, reply_markup=inline.settings.as_markup())


async def enter_snils(query: CallbackQuery, state: FSMContext):
    await state.set_state(Snils.wait_for_ans)
    await state.update_data(message=query.message)

    await query.message.edit_text(
        f'{localization.ENTER_SNILS}\n{localization.SNILS_EXAMPLE}',
        reply_markup=inline.return_settings.as_markup()
    )


async def change_snils(message: Message, state: FSMContext):
    user = await User.get(id=message.from_user.id)
    user.snils = message.text.strip()
    await user.save()

    msg = (await state.get_data())['message']
    await state.clear()

    message_text = await generate_settings_message(message.from_user.id)
    await msg.edit_text(message_text, reply_markup=inline.settings.as_markup())
    await message.delete()


async def incorrect_snils(message: Message, state: FSMContext):
    msg = (await state.get_data())['message']

    await msg.edit_text(
        f'{localization.INCORRECT_SNILS}\n{localization.SNILS_EXAMPLE}',
        reply_markup=inline.return_settings.as_markup()
    )

    await asyncio.sleep(2)
    await message.delete()


async def return_settings(query: CallbackQuery, state: FSMContext):
    await state.clear()

    message_text = await generate_settings_message(query.from_user.id)
    await query.message.edit_text(message_text, reply_markup=inline.settings.as_markup())


async def change_faculties(query: CallbackQuery):
    message_text = await generate_faculties_message(query.from_user.id)
    keyboard = await inline.faculties(user_id=query.from_user.id)
    await query.message.edit_text(
        message_text, reply_markup=keyboard.as_markup()
    )


async def faculties_paginate(query: CallbackQuery, callback_data: FacultiesActions):
    keyboard = await inline.faculties(user_id=query.from_user.id, offset=callback_data.offset)
    await query.message.edit_reply_markup(keyboard.as_markup())


async def select_faculty(query: CallbackQuery, callback_data: Faculties):
    faculty = await Faculty.get(id=callback_data.id)
    user = await User.get(id=query.from_user.id)
    if await SelectedFaculty.filter(user=user).count() < 3:
        if not (await SelectedFaculty.exists(user=user, faculty=faculty)):
            await SelectedFaculty.create(user=user, faculty=faculty)

        message_text = await generate_faculties_message(query.from_user.id)
    else:
        message_text = await generate_faculties_message(query.from_user.id)
        message_text += f'\n{localization.INCORRECT_FACULTIES_COUNT}'
    keyboard = await inline.faculties(user_id=query.from_user.id, offset=callback_data.offset)
    await query.answer()
    await query.message.edit_text(message_text, reply_markup=keyboard.as_markup())


async def unselect_faculty(query: CallbackQuery, callback_data: Faculties):
    faculty = await Faculty.get(id=callback_data.id)
    user = await User.get(id=query.from_user.id)
    selected_faculty = await SelectedFaculty.get(user=user, faculty=faculty)
    await selected_faculty.delete()

    message_text = await generate_faculties_message(query.from_user.id)
    keyboard = await inline.faculties(user_id=query.from_user.id, offset=callback_data.offset)
    await query.message.edit_text(message_text, reply_markup=keyboard.as_markup())
