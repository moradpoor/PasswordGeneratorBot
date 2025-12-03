from aiogram import Dispatcher, Bot 
from aiogram.types import Message,ReplyKeyboardRemove,BotCommand
from aiogram.enums import ParseMode,ChatAction
from aiogram.types import FSInputFile
from jdatetime import datetime
from db_helper import DBHelper
import config
import string
import random
import text_helper
import button_helper
import asyncio
import logging
import xlsxwriter
import os
import pytz

logging.basicConfig(level=logging.INFO)
iran_tz = pytz.timezone('Asia/Tehran')
bot = Bot(config.TOEKN)
dp = Dispatcher()
db = DBHelper()
db.setup()



async def SendBackup(message: Message):
    chat_id = message.chat.id
    passwords = db.GetMyPasswords(chat_id)
    if not passwords:
        await message.reply(
            '<b>شما هنوز پسوردی ذخیره نکرده اید .</b>',
            parse_mode=ParseMode.HTML
        )
        return
    await bot.send_chat_action(chat_id,ChatAction.TYPING)
    excel_name = 'passwords_'+str(chat_id)+'.xlsx'

    file_path = config.path+excel_name
    print(file_path)
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()
    
    worksheet.write("A1", "عنوان پسورد")
    worksheet.write("B1", "پسورد")
    index = 2
    for item in passwords :
        title = item[3]
        password = item[2]
        
        worksheet.write(f"A{index}", title)
        worksheet.write(f"B{index}", password)
        index += 1
    workbook.close()
    date = str(datetime.now(iran_tz)).split('.')[0]
    caption = f'بکاپ از پسوردها : {date}\n{config.BOT_USERNAME}'
    await bot.send_chat_action(chat_id,ChatAction.UPLOAD_DOCUMENT)
    file = FSInputFile(file_path)
    await bot.send_document(chat_id,document=file,caption=caption,reply_to_message_id=message.message_id)
    os.remove(file_path)


@dp.message()
async def text_message_handler(message: Message):
    chat_id = message.chat.id
    msgid = message.message_id
    if message.text:
        msg = message.text.lower()
        if msg == '/start':
            await message.reply(text_helper.START,parse_mode=ParseMode.MARKDOWN_V2)
            db.AddNewUser(
                message.chat.id,
                str(datetime.now()),
                
            )
            await bot.send_message(config.DEV,f'User {message.from_user.first_name} {message.chat.id} Started Bot')
        elif msg == "/del_all_passwords":
            db.DeleteAllPasswords(chat_id)
            await message.reply(
                "تمام پسوردهای شما حذف شد ",
                reply_markup=ReplyKeyboardRemove()
            )




        elif msg == '/newpassword': 
            words = string.ascii_letters + string.digits 
            newPassword = "".join(random.choices(words,k=6)) + "-"
            newPassword += "".join(random.choices(words,k=6)) + "-"
            newPassword += "".join(random.choices(words,k=6)) 
  
            await message.reply(text_helper.NEW_PASSWORD.format(newPassword),parse_mode=ParseMode.HTML)
        
        
        elif msg == '/mypasswords':
            my_passwords = db.GetMyPasswords(chat_id)
            if not my_passwords :
                await message.reply(
                    '<b>هنوز پسوردی ذخیره نکرده اید .</b>',
                    parse_mode=ParseMode.HTML,
                    reply_markup=ReplyKeyboardRemove()
                )
                return
            await message.reply(
                '<b>برای دیدن پسورد نامش رو از منوی پایین انتخاب کنید .</b>',
                parse_mode=ParseMode.HTML,
                reply_markup=button_helper.ShowPasswordSTitle(my_passwords)
            )
        elif msg == '/help':
            await message.reply(
                text_helper.HELP,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        elif msg == '/backup':
            await SendBackup(message)
        elif message.reply_to_message:
            if 'پسورد جدید با موفقیت ایجاد شد ✅' in message.reply_to_message.text:
                my_passwords = db.GetMyPasswords(chat_id)
                passwords = [x[2] for x in my_passwords]
                titles = [x[3] for x in my_passwords]
                password = message.reply_to_message.text.split('\n')[2]
                title = msg
                

                if any(x==password for x in passwords):
                    return await message.reply('<b>⚠️ شما قبلا این پسورد رو ذخیره کردید.</b>',parse_mode=ParseMode.HTML)
                    
                if any(x==title for x in titles):
                    return await message.reply('<b>⚠️ شما قبلا این نام رو برای پسورد دیگری انتخاب کردید.</b>',parse_mode=ParseMode.HTML)
                    
                db.NewPassword(chat_id,password,title,description=None)
                await message.reply('پسورد با موفقیت ذخیره شد ✅')
            elif msg == 'حذف':
                passwords = [x[2] for x in db.GetMyPasswords(chat_id)]
                print('PASSWORDS :',passwords)
                password = message.reply_to_message.text
                print('PASSWORD:',password)
                if password not in passwords:
                    await message.reply('<b>پسورد یافت نشد ⚠️</b>',parse_mode=ParseMode.HTML)
                    return
                db.DeletePassword(chat_id,password)
                await bot.send_message(chat_id,
                    '<b>پسورد حذف شد ✅</b>',parse_mode=ParseMode.HTML,
                    reply_to_message_id=message.reply_to_message.message_id
                )
        elif msg in [x[3] for x in db.GetMyPasswords(chat_id)]:
            await bot.send_chat_action(chat_id,ChatAction.TYPING)
            password = db.GetPasswordByTitle(chat_id,msg)
            if not password:
                await message.reply(
                    '<b>⚠️ پسورد پیدا نشد</b>',parse_mode=ParseMode.HTML
                )
                return
            password = password[0][0]
            await message.reply(
                f'<code>{password}</code>',parse_mode=ParseMode.HTML
            )
        
async def main():
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start",description="شروع ⭐️"),
            BotCommand(command="newpassword",description="ایجاد پسورد جدید 🔑"),
            BotCommand(command="mypasswords",description="پسوردهای من 🗃"),
            BotCommand(command="backup",description="ایجاد بکاپ از پسوردها 💾"),
            BotCommand(command="del_all_passwords",description="حذف همه پسورد ها")
        ]
    )
    await dp.start_polling(bot)
    await bot.delete_webhook()

asyncio.run(main=main())





