import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}

params = {
    'mode': 'class',
    'c': 'dvfu:admission.spd',
    'action': 'getStudents'
}

payload = {
    'admissionCampaignType': 'Прием на обучение на бакалавриат/специалитет',
    'financingSource': 'Бюджетная основа',
    'studyForm': 'Очная',
    'implementationPlace': 'Владивосток',
    'trainingDirection': '10.05.01 Компьютерная безопасность',
    'consent': 'true',
    'category': 'Имеющие особое право'
}

response = requests.post(
    'https://www.dvfu.ru/bitrix/services/main/ajax.php', params=params, data=payload, headers=headers
)
print(response.json())
