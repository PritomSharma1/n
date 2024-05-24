import pyrogram
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from read_variables import *
from read_write_files import read_json, write_json
    


async def show_my_account(message: pyrogram.types.messages_and_media.message.Message) -> None:
    users = read_json('users.json')

    chat_id = str(message.chat.id)
    try:
        user = users[chat_id]
    except:
        user = users[chat_id] = {}

    info = read_json('info.json')
    country_codes = info['country_codes']
    prices = info['price']
    is_valid = user.get('is_valid', False)

    price_text = ''
    for price, country in zip(prices, country_codes):
        price_text += f'AC..{country}: {price} Toman\n'

    receipt = ''
    for price, country in zip(prices, country_codes):
        if is_valid:
            receipt += f'AC..{country}: {user.get(country, 0)} Number\n'
        else:
            receipt += f'AC..{country}: 0 Number\n'
    total_balance = user.get('balance', 0) if is_valid else 0

    card_number = user.get('card_number', 'Not Set')

    text =f"""
Your ID User: {chat_id}

Rate per account:
    {price_text}
NumberOfAccounts:
    {receipt}

balance:{total_balance}
CardNumber: {card_number}"""
    # Prompt the user to select an option
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳Set Card Name", callback_data="set_bank_card")],
        [InlineKeyboardButton("📤Checkout", callback_data="checkout")],
        [InlineKeyboardButton("🔙Back To Menu", callback_data="back")],
    ])

    await message.edit_text(text, reply_markup=keyboard)

async def set_new_card_bank(message: pyrogram.types.messages_and_media.message.Message) -> None:
    users = read_json('users.json')
    chat_id = str(message.chat.id)
    user = users[chat_id]
    text = message.text

    # if is_card_number(text):
    #     user['card_number'] = text
    #     write_json('users.json', users)
    #     await message.reply('Your card number has saved successfully ')

    if message.from_user and 'ID User' not in text:
        user['card_number'] = text
        write_json('users.json', users)
        await message.reply('Your card name has saved successfully ')
    
    else:
        await message.reply('Send Your Card Name: ')
    


def is_card_number(text: str) -> bool:
    return len(text) == 16 and text.isdigit()

async def checkout(query: pyrogram.types.bots_and_keyboards.callback_query.CallbackQuery, client: pyrogram.client.Client) -> None:
    users = read_json('users.json')
    message = query.message
    chat_id = str(message.chat.id)
    try:
        user = users[chat_id]
    except KeyError:
        await client.answer_callback_query(query.id,'You have not registered yet.')
        return
    if user.get('card_number', 'Not Set') == 'Not Set':
        await client.answer_callback_query(query.id,'The card number is not set yet')
         
    if user.get('balance', 0) == 0:
        await client.answer_callback_query(query.id,'The balance is 0.')
        
    else:

        await message.reply('Your order is complete and the money will be transferred to your bank account')

        data = {
            'chat_id': chat_id,
            'card_number': user.get('card_number', 'Not Set'),
            'balance': user['balance']
        }

        write_json('checkout.json', data)

        country_codes = read_json('info.json')['country_codes']

        for country in country_codes:
            if country in list(user.keys()):
                user[country] = 0

        user['balance'] = 0

        user['stage'] = ''

        write_json('users.json', users)
