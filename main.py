import asyncio
import logging
import sys
import sqlite3
import datetime
from colorama import init, Fore, Back, Style
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ContentType, Message, CallbackQuery, KeyboardButton, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessage


datetime_date = datetime.datetime.now()

_date_and_time = datetime_date.strftime("%d-%m-%Y || %H:%M")


# Config logging
logging.basicConfig(level=logging.INFO)

# BOt token and dispatcher
BOT = Bot(token='7473178796:AAEbEg2wkTTzrnLtQbo-U22rUqhndZzGJzs')
dp = Dispatcher()
CHAT_ID = -1002038329653
admins = [2123919405]

class AddWordBList(StatesGroup):
    word = State()

class DelWordBList(StatesGroup):
    word = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, bot: BOT):
    # Отправляем сообщение в личку пользователю
    await message.answer("Привет! Я отправил сообщение в группу.")

    # Отправляем сообщение в группу
    await bot.send_message(
        chat_id=CHAT_ID,
        text="""Всем привет!
Я — бот, цель которого следить за соблюдением правил в этой группе.

Правила группы:
1. Распространение незаконных товаров запрещено.
2. Реклама без договорённости с администраторами запрещена.
3. Длительная переписка не по теме группы или попытки увлечь пользователей на сторонние ресурсы запрещены.

Рекомендация:
1. Обязательно прикрепляйте фото к своему сообщения в противном случае это будет расцениваться как нарушение правил

Желаю приятного опыта использования нашей группой!"""
    )

@dp.message(Command("tell"))
async def tell(message: Message, command: CommandObject, bot: BOT):
    if not command.args:
        await message.answer("Пожалуйста, напишите сообщение после команды /tell.")
        return

        # Получаем текст сообщения
    text_to_send = command.args

    try:
        # Отправляем сообщение в группу
        await bot.send_message(
            chat_id=CHAT_ID,
            text=text_to_send,
        )
        await message.answer("Сообщение успешно отправлено в группу!")
    except Exception as e:
        await message.answer(f"Ошибка при отправке сообщения: {e}")


@dp.message(Command("Check"))
async def check(message: Message):
    await message.answer(f"Бот запущен\n{message.from_user.id}")


@dp.message(Command("addAdmin"))
async def addAdmin(message: Message):
    print(message.from_user.id, "\n", type(message.from_user.id))
    answ = input("Желаете принять этот id как администратора?")
    if answ == "y" or answ == "Y" or answ == "Д" or answ == "д" or answ == "да" or answ == "yes" or answ == "Да" or answ == "Yes":
        admins.append(message.from_user.id)
    else:
        pass


@dp.message(Command("id_group"))
async def id_group(message: Message, bot: BOT):
    chat_id = message.chat.id
    print(f"ID этого чата: {chat_id}")
    answ = input("Желаете установить значение по умолчанию? (Y or N): ")
    if answ == "y" or answ == "Y" or answ == "Д" or answ == "д" or answ == "да" or answ == "yes" or answ == "Да" or answ == "Yes":
        CHAT_ID = chat_id
        print("Значение установлено!")
    else:
        print("Операция отменена!")

@dp.message(Command('add_blacklist'))
async def add_blacklist(message: Message, state: FSMContext):
    await state.set_state(AddWordBList.word)
    await message.reply('Напишите слово которое хотите занести в черный список')

@dp.message(AddWordBList.word)
async def add_blacklist(message: Message, state: FSMContext):
    text = message.text.lower()
    con = sqlite3.connect('blacklist.db')
    cursor = con.cursor()
    SearchWord = cursor.execute("SELECT Word FROM Words WHERE Word = ?", (text,)).fetchone()
    if SearchWord:
        await message.answer("Данное вами слово уже существует")
    else:
        cursor.execute("INSERT INTO Words (Word) VALUES (?)", (text,))
        await message.reply(f'Слово {message.text} добавлено в черный список')
    con.commit()
    con.close()
    await state.clear()

@dp.message(Command('del_blacklist'))
async def del_blacklist(message: Message, state: FSMContext):
    await state.set_state(DelWordBList.word)
    await message.reply('Напишите слово которое хотите удалить из черного списка')

@dp.message(DelWordBList.word)
async def del_blacklist(message: Message, state: FSMContext):
    text = message.text.lower()
    con = sqlite3.connect('blacklist.db')
    cursor = con.cursor()
    cursor.execute("DELETE FROM Words WHERE Word = ?", (text,))
    con.commit()
    con.close()
    await message.reply(f'Слово {message.text} удалено из черного списка')
    await state.clear()

@dp.message()
async def check_blacklist(message: Message, bot: BOT):
    con = sqlite3.connect('blacklist.db')
    cursor = con.cursor()
    if message.from_user.id not in admins:
        print(f"\n\n{'':->25}{_date_and_time}{'':->25}\nЮзер не админ")
        if message.photo:
            print("\n-> Отправлено фото")
            if message.caption:
                print("---> Имеется прикрепёный текст: ", message.caption.lower())
                text = message.caption.lower().split(" ")
                for i in text:
                    cursor.execute("SELECT Word FROM Words WHERE Word = ?", (i,))
                    data = cursor.fetchall()
                    if data:
                        print(Fore.RED + "Совпадение найдено в цикле: ", Style.RESET_ALL, data[0][0], '\n\n')
                        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                        break
                    else:
                        print(Fore.GREEN + "Совпадений не найдено в цикле", Style.RESET_ALL, '\n\n')
                        pass
        else:
            print(Fore.RED + f"Фото не прикреплено\nСообщение автоматически удаляется\nТекст сообщения:", Style.RESET_ALL + message.text,
                  '\n\n')
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        print(Fore.GREEN + f"{'':*>3}Получено сообщение от админа!{'':*>3}", Style.RESET_ALL, '\n\n')
    con.close()



async def main():
    await dp.start_polling(BOT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())