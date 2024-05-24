from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
from read_variables import *
import pyrogram, time
from read_write_files import read_json, write_user_id
from Bot import Bot
import asyncio
# Create a Pyrogram Client

import logging
logging.basicConfig(level=logging.INFO)



app: pyrogram.client.Client = Client("bot", api_hash=read_api_hash(), api_id=read_api_id(), bot_token='')

Bot(app)



bot_admins = []

stage: str = ''

from sell_account import add_account, validate_account
from my_account import show_my_account, checkout, set_new_card_bank





users = read_json('users.json')



is_back = False

def block_users(user_id: str):
    blocked_user_ids = read_json('info.json')['blocks']
    return user_id in blocked_user_ids


# Define the start command handler
@app.on_message(filters.command('start'))
async def start_command(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global is_back
    # Get the chat ID
    chat_id = message.chat.id


    if block_users(str(chat_id)):
        await message.reply('You has been blocked')
        return


    if not await check_membership(chat_id):
        await invite_to_join(chat_id)
        return
    
    write_user_id(str(chat_id))

    # Get the user's first name
    user_first_name = message.from_user.first_name

    admins = read_json('info.json')['admins']

    if str(chat_id) in admins:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Sell Account", callback_data="sell_account"), InlineKeyboardButton("MyAccount", callback_data="my_account")],
            [InlineKeyboardButton("Admin Panel", callback_data="admin_panel")]
        ])
    else:
        # Prompt the user to select an option
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Sell Account", callback_data="sell_account"), InlineKeyboardButton("MyAccount", callback_data="my_account")],
        ])

    welcome_text = read_json('info.json')['welcome']

    text = f'🖐👽 **--Hi--** **User**: {user_first_name}'

    final_welcome_text = welcome_text if welcome_text else text

    if not is_back:
        await app.send_message(chat_id, final_welcome_text, reply_markup=keyboard)
        
    else:
        await message.edit_text(final_welcome_text, reply_markup=keyboard)
        is_back = False

async def invite_to_join(chat_id: str|int) -> None:
    channels = read_json('info.json')['public_channel']
    channels = list(map(lambda id: '@'+id, channels))
    channels = '\n'.join(channels)
    message = f"""To use bot join these channels
    {channels}"""
    # Prompt the user to select an option
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Check Membership", callback_data="check_membership")],
    ])

    await app.send_message(chat_id, message, reply_markup=keyboard)

async def check_membership(chat_id: str|int) -> bool:

    channels = read_json('info.json')['public_channel']
    for target in channels:
        try:
            await app.get_chat_member(target, chat_id)
        except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:
            return False
    
    return True


    
# Define the callback query handler
@app.on_callback_query()
async def callback_query(client: pyrogram.client.Client, query: pyrogram.types.bots_and_keyboards.callback_query.CallbackQuery) -> None:

    global users, is_back

    chat_id = query.message.chat.id
    message = query.message
    data = query.data
    
    if block_users(str(chat_id)):
        await message.reply('You has been blocked')
        return

    if data == 'sell_account':
        set_stage(chat_id, 'add_account')
        await handle_messages(client, query)
    
    elif data == 'account_validation':
        set_stage(chat_id, 'account_validation')
        await handle_messages(client, query)

    elif data =='my_account':
        set_stage(chat_id, 'my_account')
        await handle_messages(client, query)

    elif data == 'set_bank_card':
        set_stage(chat_id,'set_bank_card')
        await handle_messages(client, query)

    elif data == 'checkout':
        set_stage(chat_id,'checkout')
        await handle_messages(client, query)
    
    elif data == 'check_membership':
        if not await check_membership(chat_id):
            await invite_to_join(chat_id)
        else:
            await start_command(client, message)
    
    elif data == 'back':
        is_back = True
        await start_command(client, message)
    
    elif data == 'admin_panel':
        set_stage(chat_id,'admin_panel')
        await handle_messages(client, query)

def set_stage(chat_id: str|int, stage: str) -> None:
    global users
    users[chat_id] = {}
    users[chat_id]['stage'] = stage



@app.on_message(filters.text & filters.private)
async def handle_messages(client, query):
    from admin_panel import show_admin_panel, handle_messages
    global users

    if isinstance(query, pyrogram.types.bots_and_keyboards.callback_query.CallbackQuery):
        message = query.message
    else:
        message = query
    # Get the chat ID
    chat_id = message.chat.id
    if block_users(str(chat_id)):
        await message.reply('You has been blocked')
        return
    try:
        current_stage = users[chat_id]['stage']
    except KeyError:
        await handle_messages(client, message)
        current_stage = ''


    if current_stage == 'add_account':
        await add_account(message, users)

    elif current_stage == 'account_validation':
        await validate_account(app, message)
    
    elif current_stage == 'my_account':
        await show_my_account(message)

    elif current_stage =='set_bank_card':
        await set_new_card_bank(message)

    elif current_stage == 'checkout':
        await checkout(query, client)
    
    elif current_stage == 'admin_panel':
        
        await show_admin_panel(client, message)
        set_stage(chat_id, '')
    else:

        await handle_messages(client, message)

    



print("Bot is running...")

app.run()
