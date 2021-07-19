import re
import asyncio
from os import getenv
from dotenv import load_dotenv
from pyrogram.errors import PeerIdInvalid
from pyrogram import Client, filters, idle
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

API_ID = int(getenv('API_ID', 12345))
API_HASH = str(getenv('API_HASH', ''))
BOT_TOKEN = getenv('BOT_TOKEN')
LOG_GROUP = int(getenv('LOG_GROUP'))
POST_CHANNEL = getenv('POST_CHANNEL')
DB_URI = getenv('DB_URI').replace('postgres', 'postgresql')

loop = asyncio.get_event_loop()

AniMemeBot = Client(
    "postbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

class DataBase:
    def __init__(self) -> scoped_session:
        engine = create_engine(DB_URI)
        self.BASE = declarative_base()
        self.BASE.metadata.bind = engine
        self.BASE.metadata.create_all(engine)
        self.session =  scoped_session(sessionmaker(bind=engine, autoflush=False))

    def is_banned(self, user_id):
        try:
            return self.session.query(BannedUsers).filter(BannedUsers.user_id == str(user_id)).one()
        except BaseException:
            return None
        finally:
            self.session.close()

    def ban(self, user_id):
        adder = BannedUsers(str(user_id))
        self.session.add(adder)
        self.session.commit()

    def unban(self, user_id):
        rem = self.session.query(BannedUsers).get(str(user_id))
        if rem:
            self.session.delete(rem)
            self.session.commit()

db = DataBase()

class BannedUsers(db.BASE):
    __tablename__ = "banned"
    user_id = Column(String(14), primary_key=True)

    def __init__(self, user_id):
        self.user_id = str(user_id)

BannedUsers.__table__.create(checkfirst=True)

@AniMemeBot.on_message(filters.private, group=-100)
async def checkban(_, m: Message):
    if db.is_banned(m.from_user.id):
        await m.stop_propagation()

@AniMemeBot.on_callback_query(group=-100)
async def _(_, c: CallbackQuery):
    if db.is_banned(c.from_user.id):
        await c.answer('🚫 You\'re banned!')
        await c.stop_propagation()

@AniMemeBot.on_message(filters.command(['start', 'help']) & filters.private)
async def say_hi(_, m: Message):
    await m.reply('Send your meme here!')

@AniMemeBot.on_message((filters.photo|filters.video|filters.audio|filters.animation|filters.document) & filters.private)
async def ask_confirm(_, m: Message):
    await m.reply('Are you sure you want to forward this to admin?',
    reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton('yes', 'yes'),
        InlineKeyboardButton('no', 'no'),
    ]]),
    quote=True)

@AniMemeBot.on_callback_query(filters.regex(pattern=r'^(yes|no)$'))
async def confirmation(_, c: CallbackQuery):
    cb = c.matches[0].group(1)
    await c.answer('alright!')
    if cb == 'yes':
        await c.message.reply_to_message.copy(LOG_GROUP, reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton('post', f'post_{c.from_user.id}'),
            InlineKeyboardButton('🗑', f'dump_{c.from_user.id}'),
        ]]))
        await c.edit_message_text('Done!')
    else:
        await c.edit_message_text('If you say so..')

@AniMemeBot.on_callback_query(filters.regex(pattern=r'^(post|dump)_(\d+)$'))
async def post_or_dump(_, c: CallbackQuery):
    cb = c.matches[0].group(1)
    cb_user = c.matches[0].group(2)
    await c.answer('alright!')
    if cb == 'post':
        await c.message.copy(POST_CHANNEL, caption=re.sub(r'🗑 \.\.was dumped((.|\n)*)', '', c.message.caption, flags=re.MULTILINE) if c.message.caption else None,reply_markup=None)
        await c.edit_message_caption(f'#Posted by {c.from_user.mention(style="md")}')
    else:
        await c.message.edit_caption(f'{c.message.caption if c.message.caption else ""}🗑 ..was dumped to the place where this meme was supposed to be in!\n\n#Dumped by: {c.from_user.mention(style="md")}',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('no, post it', f'post_{cb_user}')]]))


@AniMemeBot.on_message(filters.command('ban') & filters.chat(LOG_GROUP))
async def ban(b: Client, m: Message):
    status = await m.reply('`on it..`')
    if not m.reply_to_message:
        await status.edit('`Reply to a post to ban the posted user from using the bot`')
        return
    replied_post = m.reply_to_message.reply_markup
    if not replied_post:
        await status.edit('`This ain\'t a draft post!`')
        return
    try:
        reason = m.text.split(' ', 1)[1]
    except IndexError:
        reason = None
    try:
        user_id = replied_post.inline_keyboard[0][0].callback_data.split('_', 1)[1]
        if db.is_banned(user_id):
            await status.edit('🚫 `This user is already banned!`')
            return
        await b.send_message(user_id, f'Sir, due to your **holy actions**, You\'ve been **banned**{f" for the following reason: __{reason}__" if reason else "."} 🚫')
        await status.edit(f'🚫 The [user](tg://user?id={user_id}) was banned')
    except PeerIdInvalid:
        await status.edit('🚫 __The user blocked the bot.. nvm, will ban him anyways.__')
    except AttributeError:
        await status.edit('`This ain\'t a draft post!`')
        return
    db.ban(user_id)

@AniMemeBot.on_message(filters.command('unban') & filters.chat(LOG_GROUP))
async def unban(b: Client, m: Message):
    status = await m.reply('`on it..`')
    if not m.reply_to_message:
        await status.edit('`Reply to a post to unban a banned user`')
        return
    replied_post = m.reply_to_message.reply_markup
    if not replied_post:
        await status.edit('`This ain\'t a draft post!`')
        return
    try:
        reason = m.text.split(' ', 1)[1]
    except IndexError:
        reason = None
    try:
        user_id = replied_post.inline_keyboard[0][0].callback_data.split('_', 1)[1]
        if not db.is_banned(user_id):
            await status.edit('💠 `This user is not banned in the first place!`')
            return
        await b.send_message(user_id, f'Heyya, You\'ve been **unbanned**{f" with the following mod message: __{reason}__" if reason else "."}')
        await status.edit(f'💠 The [user](tg://user?id={user_id}) was #unbanned')
    except PeerIdInvalid:
        await status.edit('💠 `The user blocked the bot.. nvm, will unban him anyways.`')
    except AttributeError:
        await status.edit('`This ain\'t a draft post!`')
        return
    db.unban(user_id)

async def start_bot():
    await AniMemeBot.start()
    bot = await AniMemeBot.get_me()
    try:
        logchat = await AniMemeBot.get_chat(chat_id=LOG_GROUP)
        if not (logchat.type == "supergroup") or (logchat.type == "group"):
            print("The log chat is not a group.. exitting!")
            exit()
        print(f'pyrogram started on @{bot.username} in chat {logchat.title}!')
    except PeerIdInvalid:
        print(f'pyrogram started on @{bot.username}!')
    await idle()

if __name__ == "__main__":
    loop.run_until_complete(start_bot())
