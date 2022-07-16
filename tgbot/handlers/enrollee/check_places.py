from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

import localization
from tgbot.models.database import User, SelectedFaculty
from tgbot.services.fefu_api import check_faculty


async def check_places(message: Message, state: FSMContext):
    await state.clear()

    user = await User.get(id=message.from_user.id)
    selected_faculties = await SelectedFaculty.filter(user=user).all().prefetch_related('faculty')
    if user.snils is None:
        await message.answer(localization.NO_SNILS)
    elif not selected_faculties:
        await message.answer(localization.NO_FACULTIES)
    else:
        selected_faculties = await SelectedFaculty.filter(user=user).all().prefetch_related('faculty')
        if len(selected_faculties):
            faculties = ''
            for selected_faculty in selected_faculties:
                faculties += f'\n{selected_faculty.faculty.name} ({selected_faculty.faculty.code})'
        else:
            faculties = 'Не указаны'
        msg = await message.answer(localization.CHECK_PLACES.format(faculties=faculties))

        for i in range(len(selected_faculties)):
            selected_faculty = selected_faculties[i]
            response = await check_faculty(
                snils=user.snils,
                faculty=selected_faculty.faculty,
                agreement=user.check_agreement
            )

            if response['status']:
                message_text = ''
                for place in response['data']:
                    if place['category'] == 'На общих основаниях':
                        selected_faculty.place = place['user_place']
                        await selected_faculty.save()

                    message_text += localization.FACULTY_RESULT.format(
                        faculty=f'{selected_faculty.faculty.name} ({selected_faculty.faculty.code})',
                        place=place['user_place'],
                        places=place['places'],
                        category=place['category']
                    )
            else:
                message_text = localization.FACULTY_ERROR.format(
                    faculty=f'{selected_faculty.faculty.name} ({selected_faculty.faculty.code})',
                    description=response['description']
                )
            if i:
                message_text = f'{msg.html_text}{message_text}'

            msg = await msg.edit_text(message_text)
