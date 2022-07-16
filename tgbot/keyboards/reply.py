import localization
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

main = ReplyKeyboardBuilder()
for text in localization.ENROLLEE_MENU.values():
    main.row(KeyboardButton(text=text))
