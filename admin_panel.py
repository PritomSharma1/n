from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from read_write_files import read_json, write_json, read_user_ids
from pyrogram import filters
import pyrogram, os, zipfile
# from custom_filters import filter_allowed_only_admins, filter_allowed_users
from Bot import Bot

app = Bot().bot

users = read_json('users.json')

async def show_admin_panel(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:
    chat_id = str(message.chat.id)
    admins = read_json('info.json')['admins']
    if chat_id not in admins:
        message.reply_text('You are not admin')
        return


    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("Welcome"), KeyboardButton("Admin")],
        [KeyboardButton('Block | Unblock'), KeyboardButton('Accounts')],
        [KeyboardButton('Country - status'), KeyboardButton('Show Country Status')],
        [KeyboardButton('Broadcast'), KeyboardButton('Send Message')],
        [KeyboardButton('Acc Zip'), KeyboardButton('Delete Acc From Bot')],
        [KeyboardButton('Join Channel'), KeyboardButton('Session Channel')],
        [KeyboardButton('Remove User Info'), KeyboardButton('Set Time')],
    ])

    text = 'Welcome back choose an option:'

    await message.reply(text, reply_markup=keyboard)

@app.on_message(filters.regex('Welcome'))
async def welcome_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:
    global users
    chat_id = str(message.chat.id)
    users[chat_id] = {}
    users[chat_id]['stage'] = 'welcome'
    await message.reply("Send your new welcome message: ")


@app.on_message(filters.regex('Admin'))
async def admin_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:
    global users
    chat_id = str(message.chat.id)
    users[chat_id] = {}
    users[chat_id]['stage'] = 'admin'
    await message.reply("Send new admin user id: ")

@app.on_message(filters.regex('Block | Unblock'))
async def block_unblock_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:
    global users
    chat_id = str(message.chat.id)
    users[chat_id] = {}
    users[chat_id]['stage'] = 'block_unblock'
    await message.reply("Send user id to block or unblock: ")


@app.on_message(filters.regex('Accounts'))
async def accounts_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:
    accounts = get_accounts()

    accounts_numbers = get_account_numbers(accounts)

    if accounts_numbers:
        text = '\n'.join(accounts_numbers)
    else:
        text = 'There is no account.'

    await message.reply(text)

# get all available accounts
def get_accounts() -> list[str]:

    accounts = os.listdir('sessions')

    return accounts

# send all accounts number to the user
def get_account_numbers(accounts: list[str]) -> list[str]:

    accounts_numbers = []

    for i in range(0, len(accounts), 2):
        account = accounts[i]
        accounts_numbers.append(account.split('.')[0])
    
    return accounts_numbers

@app.on_message(filters.regex('Country - status'))
async def country_status_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users
    chat_id = str(message.chat.id)
    users[chat_id] = {}
    users[chat_id]['stage'] = 'country_code'
    await message.reply("Send the country code: ")


@app.on_message(filters.regex('Show Country Status'))
async def show_country_status_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    info = read_json('info.json')

    country_codes = info['country_codes']
    
    capacities = info['capacity']

    prices = info['price']

    times = info['time']
    
    text = ''
    
    for country_code, capacity, price, time in zip(country_codes, capacities, prices, times):
        text += f'{country_code}: {capacity} : {price} Toman : {time}seconds\n'

    if not text:
        text = 'There is no country code.'

    await message.reply(text)


@app.on_message(filters.regex('Broadcast'))
async def broadcast_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users

    chat_id = str(message.chat.id)

    users[chat_id] = {}

    users[chat_id]['stage'] = 'broadcast'

    await message.reply("Forward your message here: ")


@app.on_message(filters.regex('Send Message'))
async def send_message_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users

    chat_id = str(message.chat.id)

    users[chat_id] = {}

    users[chat_id]['stage'] = 'send_message'

    await message.reply("Send your message here: ")


@app.on_message(filters.regex('Acc Zip'))
async def acc_zip_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users

    chat_id = str(message.chat.id)

    users[chat_id] = {}

    users[chat_id]['stage'] = 'acc_zip'

    await message.reply('How many accounts do you want: ')

@app.on_message(filters.regex('Delete Acc From Bot'))
async def delete_accounts_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    delete_all_accounts()

    await message.reply('All accounts has been deleted.')

def delete_all_accounts() -> None:

    for file in os.listdir('sessions'):

        os.remove(f'sessions/{file}')

@app.on_message(filters.regex('Join Channel'))
async def join_channel_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users

    chat_id = str(message.chat.id)

    users[chat_id] = {}

    users[chat_id]['stage'] = 'join_channel'

    await message.reply('Send channel public link(e.g @test): ')

@app.on_message(filters.regex('Session Channel'))
async def session_channel_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users

    chat_id = str(message.chat.id)

    users[chat_id] = {}

    users[chat_id]['stage'] = 'session_channel'

    await message.reply('Send channel private id(e.g -10013123123): ')

@app.on_message(filters.regex('Remove User Info'))
async def remove_users_information_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    try:
        os.remove('users.json')
    except FileNotFoundError:
        pass

    await message.reply('All users information has been deleted.')

@app.on_message(filters.regex('Set Time'))
async def set_time_button_handler(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users

    chat_id = str(message.chat.id)

    users[chat_id] = {}

    users[chat_id]['stage'] = 'set_time'

    await message.reply('Send country code which you have added before: ')

@app.on_message(filters.text & filters.private)
async def handle_messages(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):

    global users

    chat_id = str(message.chat.id)

    if chat_id not in read_json('info.json')['admins']:
        return

    try:
        stage = users[chat_id]['stage']
    except KeyError:
        stage = ''
        users[chat_id] = {}
        users[chat_id]['stage'] = ''

    
    text = message.text
    is_found = await find_right_command(text, client, message)

    if is_found:
        return
    
    elif stage == 'welcome' and message.text != 'Welcome':
        await update_welcome_text(message)
        users[chat_id]['stage'] = ''

    elif stage == 'admin':
        await add_new_admin(message)
        users[chat_id]['stage'] = ''

    elif stage == 'block_unblock':
        
        await update_blocks_list(message)
        users[chat_id]['stage'] = ''

    elif stage == 'country_code' and is_country_code(message.text):
        await update_country_code(message)

    elif stage == 'capacity':
        await handle_capacity_list(message)

    elif stage == 'price':

        await handle_price_list(message)
        users[chat_id]['stage'] = ''
    
    elif stage == 'broadcast' and message.text != 'Broadcast':

        await send_message_all(message.text, client)

        await message.reply('Broadcast sent successfully!')

        users[chat_id]['stage'] = ''
    
    elif stage == 'send_message' and message.text != 'Send Message':

        await send_message_all(message.text, client)

        await message.reply('Message was sent successfully!')

        users[chat_id]['stage'] = ''
    
    elif stage == 'acc_zip' and message.text.isnumeric():

        await handle_acc_zip(client, message)

        users[chat_id]['stage'] = ''

    elif stage == 'join_channel' and message.text[0] == '@':

        await toggle_public_channel_link(message)

        users[chat_id]['stage'] = ''

    elif stage == 'session_channel' and message.text[0] == '-' and message.text[1:].isnumeric():
        
        await toggle_private_channel_link(message)

        users[chat_id]['stage'] = ''

    elif stage == 'set_time' and is_country_code(message.text):
        await handle_set_time(message)

    elif stage == 'set_minutes' and message.text.isnumeric():
        await handle_set_minutes(message)

        users[chat_id]['stage'] = ''



async def find_right_command(command: str, client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> bool:
    if command == 'Welcome':
        await welcome_button_handler(client, message)
        return True
    elif command == 'Admin':
        await admin_button_handler(client, message)
        return True
    elif command == 'Block | Unblock':
        await block_unblock_button_handler(client, message)
        return True
    elif command == 'Accounts':
        await accounts_button_handler(client, message)
        return True
    elif command == 'Country - status':
        await country_status_button_handler(client, message)
        return True
    elif command == 'Show Country Status':
        await show_country_status_button_handler(client, message)
        return True
    elif command == 'Broadcast':
        await broadcast_button_handler(client, message)
        return True
    elif command == 'Send Message':
        await send_message_button_handler(client, message)
        return True
    elif command == 'Acc Zip':
        await acc_zip_button_handler(client, message)
        return True
    elif command == 'Delete Acc From Bot':
        await delete_accounts_button_handler(client, message)
        return True
    elif command == 'Join Channel':
        await join_channel_button_handler(client, message)
        return True
    elif command == 'Session Channel':
        await session_channel_button_handler(client, message)
        return True
    elif command == 'Remove User Info':
        await remove_users_information_button_handler(client, message)
        return True
    elif command == 'Set Time':
        await set_time_button_handler(client, message)
        return True
    
    return False

async def handle_set_minutes(message: pyrogram.types.messages_and_media.message.Message) -> None:

    minutes = message.text

    chat_id = str(message.chat.id)

    add_time(minutes, chat_id)

    await message.reply('The time was set successfully.')

def add_time(minutes: str, chat_id: str) -> None:

    info = read_json('info.json')

    index = info['time'].index(chat_id)

    info['time'][index] = minutes

    write_json('info.json', info)

async def handle_set_time(message: pyrogram.types.messages_and_media.message.Message):
    
    global users

    country_code = message.text

    chat_id = str(message.chat.id)

    if is_country_code_exist(country_code):

        mark_the_time(country_code, chat_id)

        users[chat_id]['stage'] = 'set_minutes'

        await message.reply('Perfect, now send me the time in minutes: ')
    else:

        users[chat_id]['stage'] = ''

        await message.reply('First, you need to add this country code.')

def mark_the_time(country_code: str, mark: str|int) -> None:

    info = read_json('info.json')

    country_code_index = get_country_code_index(country_code)

    info['time'][country_code_index] = mark

    write_json('info.json', info)

def get_country_code_index(country_code: str) -> int:

    info = read_json('info.json')

    return info['country_codes'].index(country_code)

def is_country_code_exist(country_code: str) -> bool:
    info = read_json('info.json')
    return country_code in info['country_codes']

async def toggle_private_channel_link(message: pyrogram.types.messages_and_media.message.Message) -> None:

    channel_link = message.text[1:]

    info = read_json('info.json')

    if channel_link in info['private_channel']:

        info = await remove_private_channel_link(info, message)
    else:

        info = await add_private_channel_link(info, message)

    write_json('info.json', info)

async def remove_private_channel_link(info: dict, message: pyrogram.types.messages_and_media.message.Message) -> dict:

    channel_link = message.text

    info['private_channel'].remove(channel_link)

    await message.reply('The private link has been deleted.')

    return info

async def add_private_channel_link(info: dict, message: pyrogram.types.messages_and_media.message.Message) -> dict:

    channel_link = message.text

    info['private_channel'].append(channel_link)

    await message.reply('The private link has been added.')

    return info

async def toggle_public_channel_link(message: pyrogram.types.messages_and_media.message.Message) -> None:

    channel_link = message.text[1:]

    info = read_json('info.json')

    if channel_link in info['public_channel']:

        info = await remove_public_channel_link(info, message)
    else:

        info = await add_public_channel_link(info, message)

    write_json('info.json', info)

async def remove_public_channel_link(info: dict, message: pyrogram.types.messages_and_media.message.Message) -> dict:

    channel_link = message.text[1:]

    info['public_channel'].remove(channel_link)

    await message.reply('The public link has been deleted.')

    return info

async def add_public_channel_link(info: dict, message: pyrogram.types.messages_and_media.message.Message) -> dict:

    channel_link = message.text[1:]

    info['public_channel'].append(channel_link)

    await message.reply('The public link has been added.')

    return info


async def handle_acc_zip(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message) -> None:

    chat_id = int(message.chat.id)

    if message.text.isnumeric():

        zip_accounts(int(message.text))

        await client.send_document(chat_id, f'sessions.zip')

        os.remove('sessions.zip')

        return
    
    await message.reply('It is not a number')



def zip_accounts(number_of_accounts: int) -> None:

    base_path = os.getcwd()
    # create a file with zip format
    zip = zipfile.ZipFile("sessions.zip", "w", zipfile.ZIP_DEFLATED)

    counter = 0

    os.chdir('sessions')

    files = os.listdir()

    # add account files to zip file with number limit 
    for i in range(0, len(files), 2):
        
        json_file = files[i]
        sessions_file = files[i+1]

        zip.write(json_file)
        zip.write(sessions_file)

        counter += 1

        if counter == number_of_accounts:
            break
    
    zip.close()

    os.chdir(base_path)

async def send_message_all(text: str, client: pyrogram.client.Client) -> None:

    users = get_users()
    
    for user in users:
        if user:
            await client.send_message(int(user), text)        


def get_users() -> set[str]:

    try:
        users = read_user_ids()
        # users = read_json('users.json')
        # users = set(users.keys())
        
    except FileNotFoundError:
        users = set()

    return users

async def handle_price_list(message: pyrogram.types.messages_and_media.message.Message) -> None:
    text = message.text
    if text.isnumeric():
        add_price(text)
        await message.reply('The country code with its info added successfully.')
    else:
        await message.reply('It must be a number.')

def add_price(price: str) -> None:
    info = read_json('info.json')
    info['price'].append(price)
    write_json('info.json', info)


async def handle_capacity_list(message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users

    chat_id = str(message.chat.id)

    capacity = message.text

    if capacity.isnumeric():

        add_capacity(capacity)

        await message.reply('Now send me the price of this country code in Toman')

        users[chat_id]['stage'] = 'price'

    else:

        await message.reply('Capacity must be a number.')

def add_capacity(capacity: str) -> None:

    info = read_json('info.json')

    info['capacity'].append(capacity)

    info['time'].append(0)

    write_json('info.json', info)

async def update_country_code(message: pyrogram.types.messages_and_media.message.Message) -> None:

    country_code = message.text

    info = read_json('info.json')

    if country_code not in info['country_codes']:
        
        await add_country_code(info, message)

    else:

        await remove_country_code(info, message)

async def add_country_code(info: dict, message: pyrogram.types.messages_and_media.message.Message) -> None:

    global users

    country_code = message.text

    info = read_json('info.json')

    chat_id = str(message.chat.id)

    info['country_codes'].append(country_code)

    await message.reply('Enter capacity: ')

    users[chat_id]['stage'] = 'capacity'

    write_json('info.json', info)

async def remove_country_code(info: dict, message: pyrogram.types.messages_and_media.message.Message) -> None:

    info['country_codes'].pop()

    info['capacity'].pop()

    info['time'].pop()

    write_json('info.json', info)

    await message.reply('This country code is off now.')

def is_country_code(text: str) -> bool:

    return text[0] == '+' and text[1:].isnumeric()


async def update_blocks_list(message: pyrogram.types.messages_and_media.message.Message) -> None:

    user_id = message.text

    if user_id.isnumeric():

        info = read_json('info.json')

        if user_id in info['blocks']:
            await unblock_user(info, message)
        else:
            await block_user(info, message)
        # update info file
        write_json('info.json', info)

        return
    
    await message.reply('The user id must be numeric')

async def unblock_user(info: dict, message: pyrogram.types.messages_and_media.message.Message) -> dict|None:
    try:
        user_id = message.text
        info['blocks'].remove(user_id)
        await message.reply('User unblocked successfully')
        return info
    except:
        await message('The user id is wrong.')
async def block_user(info: dict, message: pyrogram.types.messages_and_media.message.Message) -> dict|None:
    try:
        user_id = message.text
        info['blocks'].append(user_id)
        await message.reply('User blocked successfully')
        return info
    except Exception as e:
        print(e)
        await message.reply('The user id is wrong.')
async def add_new_admin(message: pyrogram.types.messages_and_media.message.Message) -> None:

    new_admin_chat_id = message.text
    if new_admin_chat_id.isnumeric():
        update_admins_list(new_admin_chat_id)
        await message.reply('New admin added successfully')
        return
    
    await message.reply('The user id must be numeric')

def update_admins_list(new_admin_chat_id: str|int) -> None:

    info = read_json('info.json')
    info['admins'].append(new_admin_chat_id)
    write_json('info.json', info)


async def update_welcome_text(message: pyrogram.types.messages_and_media.message.Message) -> None:
    welcome_text = message.text
    info = read_json('info.json')
    if welcome_text.lower() == 'default':
        welcome_text = None
    info['welcome'] = welcome_text
    write_json('info.json', info)
    await message.reply('Welcome message saved successfully')

