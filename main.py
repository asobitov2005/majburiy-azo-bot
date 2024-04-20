import asyncio
import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
from database import add_user, add_group, get_stat, add_channel, del_channel, close_connection

logging.basicConfig(level=logging.INFO)

TOKEN = ''

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if message.chat.type == 'private':
        await add_user(message.chat.id)
        start_group_link = f"https://t.me/{(await bot.get_me()).username}?startgroup=true"
        menu = types.InlineKeyboardMarkup()
        menu.add(types.InlineKeyboardButton(text="👥 Guruhga qo'shish ↗️", url=start_group_link))
        await send_message(message.chat.id,
                           "Xush kelibsiz! Meni guruhga qo'shish uchun quyidagi havoladan foydalaning:",
                           reply_markup=menu)
    else:
        await add_group(message.chat.id)
        await send_message(message.chat.id,
                           "Salom! Men kanal obunalarni boshqaruvchi botman. Men bilan faqat adminlar muloqot qila oladi.\n\nFoydalanish:\nKanal qo'shish: /setchannel @username\nO'chirish: /delchannel")


@dp.message_handler(commands=['setchannel'])
async def set_channel_command(message: types.Message):
    if message.chat.type in ['group', 'supergroup', 'private']:
        if await is_chat_member(message.chat.id, message.from_user.id) in ['creator', 'administrator']:
            channel_username = message.text.replace('/setchannel', '').strip()
            if await add_channel(message.chat.id, channel_username):
                await send_message(message.chat.id, "Kanal muvaffaqiyatli qo'shildi!")
            else:
                await send_message(message.chat.id,
                                   "Kanal qo'shishda xatolik yuz berdi. Iltimos, kanal nomini tekshirib qayta urinib ko'ring.")


@dp.message_handler(commands=['delchannel'])
async def del_channel_command(message: types.Message):
    if message.chat.type in ['group', 'supergroup', 'private']:
        if await is_chat_member(message.chat.id, message.from_user.id) in ['creator', 'administrator']:
            if await del_channel(message.chat.id):
                await send_message(message.chat.id, "Kanal o'chirildi!")
            else:
                await send_message(message.chat.id, "O'chirish uchun kanal topilmadi.")


@dp.message_handler(commands=['stat'])
async def stat_command(message: types.Message):
    if message.chat.type == 'private':
        stat = await get_stat()
        user_count = stat['user_count']
        group_count = stat['group_count']
        await send_message(message.chat.id, f"Foydalanuvchilar: {user_count}\nGuruhlar: {group_count}")


@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    message_id = message.message_id

    if message.chat.type in ['group', 'supergroup', 'private']:
        if await is_not_channel_member(chat_id, user_id):
            await delete_message(chat_id, message_id)
            invite_link = await get_channel_invite_link(chat_id)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="Kanalga qo'shish", url=invite_link))
            sent_message = await send_message(chat_id,
                                              f"<b>Kechirasiz, <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>, guruhda yozish uchun bizning kanalga a'zo bo'lishingiz shart.</b>",
                                              reply_markup=keyboard)
            await asyncio.sleep(15)
            await delete_message(chat_id, sent_message.message_id)


async def is_chat_member(chat_id, user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return chat_member.status
    except Exception as e:
        logging.error(f"Error checking chat membership: {e}")
        return 'unknown'


async def delete_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.error(f"Error deleting message: {e}")


async def send_message(chat_id, text, reply_markup=None):
    try:
        return await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error sending message: {e}")


async def is_not_channel_member(chat_id, user_id):
    try:
        chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return chat_member.status not in ['creator', 'administrator', 'member']
    except Exception as e:
        logging.error(f"Error checking chat membership: {e}")
        return True


async def get_channel_invite_link(chat_id):
    try:
        chat_info = await bot.get_chat(chat_id)
        return chat_info.invite_link
    except Exception as e:
        logging.error(f"Error getting channel invite link: {e}")
        return None


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        close_connection()
