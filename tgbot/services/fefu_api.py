import aiohttp
from tortoise.expressions import Q

import localization
from tgbot.config import load_config
from tgbot.models.database import Faculty, Agreement

config = load_config('.env')

params = {
    'mode': 'class',
    'c': 'dvfu:admission.spd'
}


async def save_faculties() -> int:
    """
    Получение списка факультетов и добавление новых в базу данных, если таковые имеются.

    :return: Количество добавленных факультетов.
    """
    params['action'] = 'getTrainingDirectionList'
    payload = {
        'admissionCampaignType': 'Прием на обучение на бакалавриат/специалитет',
        'financingSource': 'Бюджетная основа',
        'studyForm': 'Очная',
        'implementationPlace': 'Владивосток'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(config.misc.base_url, params=params, data=payload) as response:
            count = 0
            for faculty in (await response.json())['data']:
                code, name = faculty.split(maxsplit=1)
                if await Faculty.filter(Q(code=code) & Q(name=name)).first() is None:
                    await Faculty.create(code=code, name=name)
                    count += 1
    return count


async def check_faculty(snils: str, faculty: Faculty, agreement: bool) -> dict:
    """
    Получение места в списке абитуриентов для определенного факультета.

    :param snils: СНИЛС абитуриента.
    :param faculty: Факультет для которого совершаем поиск.
    :param agreement: Проверка наличия согласия.
    :return: Категорию приема, место в списках и общее количество мест в категории на факультете
    """
    params['action'] = 'getStudents'
    payload = {
        'admissionCampaignType': 'Прием на обучение на бакалавриат/специалитет',
        'financingSource': 'Бюджетная основа',
        'studyForm': 'Очная',
        'implementationPlace': 'Владивосток',
        'trainingDirection': f'{faculty.code} {faculty.name}',
        'consent': str(agreement).lower()
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(config.misc.base_url, params=params, data=payload) as response:
            agreements = await Agreement.filter(~Q(faculty=faculty) & ~Q(snils=snils)).values_list('snils', flat=True)

            data = []
            count = 0
            for enrollee in (await response.json())['data']:
                if enrollee['name'] == snils:
                    category = enrollee['category']
                    if category != 'Целевой прием':
                        place = int(float(enrollee['GENERALORDER']))
                        data.append({
                            'category': category,
                            'user_place': place - count,
                            'places': enrollee[localization.CATEGORIES[category]]
                        })
                elif enrollee['name'] in agreements:
                    count += 1
            if not data:
                return {'status': False, 'description': 'Не найден в списках'}
            return {'status': True, 'data': data}


async def save_agreements() -> None:
    """
    Сохранение списка абитуриентов, подавших согласие
    """
    params['action'] = 'getStudents'
    for faculty in await Faculty.all():
        payload = {
            'admissionCampaignType': 'Прием на обучение на бакалавриат/специалитет',
            'financingSource': 'Бюджетная основа',
            'studyForm': 'Очная',
            'implementationPlace': 'Владивосток',
            'trainingDirection': f'{faculty.code} {faculty.name}',
            'consent': 'true'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(config.misc.base_url, params=params, data=payload) as response:
                fefu_agreements = set(map(lambda x: x['name'], (await response.json())['data']))
                db_agreements = set(await Agreement.filter(faculty=faculty).values_list('snils', flat=True))
                for snils in fefu_agreements.difference(db_agreements):
                    await Agreement.create(snils=snils, faculty=faculty)
                for snils in db_agreements.difference(fefu_agreements):
                    agreement = await Agreement.get(Q(snils=snils) & Q(faculty=faculty))
                    await agreement.delete()
