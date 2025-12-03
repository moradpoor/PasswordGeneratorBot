from aiogram.types import ReplyKeyboardMarkup,KeyboardButton



def ShowPasswordSTitle(passwords):
    buttons = []
    for password in passwords:
        title = password[3]
        buttons.append(
            [
                KeyboardButton(text=title)
            ]
        )
    return ReplyKeyboardMarkup(keyboard=buttons,resize_keyboard=True)
        
