import asyncio
import logging
import sys
import sqlite3
import datetime
import os
import time

from dotenv import load_dotenv, set_key

from aiogram.exceptions import TelegramForbiddenError
from colorama import Fore, Style
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


# Config logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

# Если TOKEN не существует, записываем его
if not os.getenv("TOKEN"):
    print("Для запуска вставьте токен:")
    token = input(">> ")
    set_key('.env', 'TOKEN', token)
    logging.info("Токен был записан в .env файл\nДалее будет перезагрузка")


_Bot = Bot(token=os.getenv("TOKEN"))


dp = Dispatcher()
CHAT_ID = -1002038329653
admins = [2123919405]

class AddWordBList(StatesGroup):
    word = State()
    reason = State()

class DelWordBList(StatesGroup):
    word = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, bot: _Bot):
    if message.from_user.id in admins:
        await message.answer("Привет! Я отправил сообщение в группу.")
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
    else:
        await message.answer("Привет\nЯ бот для созданный для контроля сообщений в группе https://t.me/vapefleaNN\nК сожаления у меня нет никакого функционала для обычных пользователей\nПриношу свои извенения")

@dp.message(Command("tell"))
async def tell(message: Message, command: CommandObject, bot: _Bot):
    if message.from_user.id:
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
    if message.from_user.id:
        print(message.from_user.id, "\n", type(message.from_user.id))
        answ = input("Желаете принять этот id как администратора?")
        if answ == "y" or answ == "Y" or answ == "Д" or answ == "д" or answ == "да" or answ == "yes" or answ == "Да" or answ == "Yes":
            admins.append(message.from_user.id)
        else:
            pass


@dp.message(Command("id_group"))
async def id_group(message: Message, bot: _Bot):
    if message.from_user.id:
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
    if message.from_user.id in admins:
        await state.set_state(AddWordBList.word)
        await message.reply('Напишите слово которое хотите занести в черный список')
    else:
        await state.clear()
        print(Fore.RED + f"{'':!>3}{'':->3} Попытка использования прав админа {'':->3}{'':!>3}", Style.RESET_ALL)



@dp.message(AddWordBList.word)
async def add_blacklist(message: Message, state: FSMContext):
    text = message.text.lower()
    await state.update_data(word=text)
    con = sqlite3.connect('blacklist.db')
    cursor = con.cursor()
    SearchWord = cursor.execute("SELECT Word FROM Words WHERE Word = ?", (text,)).fetchone()
    if SearchWord:
        await message.answer("Данное вами слово уже существует")
    else:
        await message.answer("Теперь введите причину запрета этого слова")
        await state.set_state(AddWordBList.reason)

@dp.message(AddWordBList.reason)
async def add_blacklist_two(message: Message, state: FSMContext):
    data = await state.get_data()
    reason = message.text
    con = sqlite3.connect('blacklist.db')
    cursor = con.cursor()
    cursor.execute("INSERT INTO Words (Word, reason) VALUES (?, ?)", (data.get("word"), reason))
    await message.reply(f'Слово {data["word"]} добавлено в черный список с причиной {reason}')
    print(f"{'':->10}\nСлово {data["word"]} добавлено в черный список с причиной {reason}")
    con.commit()
    con.close()
    await state.clear()

@dp.message(Command('del_blacklist'))
async def del_blacklist(message: Message, state: FSMContext):
    if message.from_user.id in admins:
        await state.set_state(DelWordBList.word)
        await message.reply('Напишите слово которое хотите удалить из черного списка')
    else:
        await state.clear()
        print(Fore.RED + f"{'':!>3}{'':->3} Попытка использования прав админа {'':->3}{'':!>3}", Style.RESET_ALL)

@dp.message(DelWordBList.word)
async def del_blacklist(message: Message, state: FSMContext):
    text = message.text.lower()
    con = sqlite3.connect('blacklist.db')
    cursor = con.cursor()
    cursor.execute("DELETE FROM Words WHERE Word = ?", (text,))
    cursor.execute("DELETE FROM reason WHERE Word = ?", (text,))
    con.commit()
    con.close()
    await message.reply(f'Слово {message.text} удалено из черного списка')
    await state.clear()

@dp.message()
async def check_blacklist(message: Message, bot: _Bot):
    datetime_date = datetime.datetime.now()
    _date_and_time = datetime_date.strftime("%d-%m-%Y || %H:%M")
    con = sqlite3.connect('blacklist.db')
    cursor = con.cursor()
    if message.from_user.id not in admins:
        print(f"\n\n{'':->10}{_date_and_time}{'':->10}\nЮзер не админ")
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
                        reason = cursor.execute("SELECT Word, reason FROM Words WHERE Word = ?", (i,)).fetchone()
                        await bot.send_message(
                            chat_id=message.from_user.id,
                            text="В вашем сообщение было обнаружено нарушение правил группы\nЗафиксированное нарушение:\n" + reason[0],
                        )
                        break
                    print(Fore.GREEN + f"Совпадений не найдено в цикле: {i}", Style.RESET_ALL, '\n\n')
                    pass
        else:
            print(Fore.RED + f"Фото не прикреплено\nСообщение автоматически удаляется\nТекст сообщения:", Style.RESET_ALL + message.text,
                  '\n\n')
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            try:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text="Ваше сообщение было удалено по причине отсутствия прикреплённого фото!",
                )
                print("Сообщение юзеру отправлено")
            except TelegramForbiddenError:
                print()
    else:
        print(Fore.GREEN + f"{'':*>3}Получено сообщение от админа!{'':*>3}", Style.RESET_ALL, '\n\n')
    con.close()



async def main():
    try:
        datetime_date = datetime.datetime.now()
        _date_and_time = datetime_date.strftime("%d-%m-%Y || %H:%M")
        print(Fore.GREEN + f"\n  {'':->6}Бот запущен в {_date_and_time}{'':->6}", Style.RESET_ALL, '\n')
        await dp.start_polling(_Bot)
    except Exception as ex:
        logging.error(ex)
    finally:
        for i in range(3):
            await _Bot.send_message(text=f"Внимание!!!", chat_id=admins[0])
            time.sleep(1)
        await _Bot.send_message(text=f"Бот завершил работу в {_date_and_time.replace("||", ":")}",
                                chat_id=admins[0]
                                )


if __name__ == "__main__":
    logging.getLogger("aiogram").setLevel(logging.WARNING)  # или logging.ERROR
    asyncio.run(main())