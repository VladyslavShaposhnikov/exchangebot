import os

from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram import types
import requests
import json
from datetime import datetime, timedelta, date
from config import API_KEY
from create_bot import bot
from database import postgresql
import matplotlib.pyplot as plt
import pandas as pd


list_of_carrencies = 'USDAED,USDARS,USDAUD,USDBRL,BTCUSD,USDCAD,USDCHF,USDCLP,USDCNY,USDCOP,USDCZK,USDDKK,USDEUR,USDGBP,USDHKD,USDHUF,USDHRK,USDIDR,USDILS,USDINR,USDISK,USDJPY,USDKRW,USDKWD,USDMXN,USDMYR,USDMAD,USDNOK,USDNZD,USDPEN,USDPHP,USDPLN,USDRON,USDRUB,USDSEK,USDSGD,USDTHB,USDTRY,USDTWD,USDXAG,USDXAU,USDZAR'

#@dp.message_handler(commands=['start', 'help'])
async def commands_start(message : types.message):
    await message.answer('Добро пожаловать {}!'.format(message.from_user.full_name))

#@dp.message_handler(commands=['list', 'lst'])
async def command_list(message : types.message):
    id = await postgresql.max_id()
    z = await postgresql.get_data(id)
    timestamp_db = z[1]['timestamp']
    utc_timestamp_db = datetime.utcfromtimestamp(timestamp_db)
    time_for_now = datetime.utcnow()
    from_now_10_min_early = time_for_now - timedelta(minutes=10)
    if from_now_10_min_early <= utc_timestamp_db == True:
        # from db
        currency_list = z[1]['price']
    else:
        # from server
        res = requests.get('https://fxmarketapi.com/apilive', params={'currency': list_of_carrencies, 'api_key': API_KEY})
        data = json.dumps(res.json())
        await postgresql.insert_value(data)
        currency_list = res.json()['price']

    for key, value in currency_list.items():
        currency_name = key.replace('USD', '')
        currency_value = round(value, 2)
        await bot.send_message(chat_id=message.chat.id, text=f'{currency_name}: {currency_value}')

#@dp.message_handler(commands=['exchange'])
async def exchange(message : types.message):
    args = message.get_args()
    if args:
        new_args = args.split()
        print(new_args)
        amount = ''
        if 'USD' in new_args:
            amount = new_args[0]
        elif 'USD' not in new_args:
            amount = new_args[0].replace('$', '')
        else:
            await message.answer('incorrect data')
        convert_to = new_args[-1]
        convert_from = 'USD'
        params_data = {'amount': amount, 'from': convert_from, 'to': convert_to, 'api_key': API_KEY}
        res = requests.get('https://fxmarketapi.com/apiconvert', params=params_data)
        total = res.json()['total']
        result = round(total, 2)
        await bot.send_message(chat_id=message.chat.id, text=f'${amount} = {result} {convert_to}')
    else:
        await bot.send_message(chat_id=message.chat.id, text='You must give parameters after "/exchange" command.\nAllow parametrs:\n$(your amount) to (your currency)\nor\n(your amount) USD to (your currency)\nFor get list of currencies use /list or /lst')

#@dp.message_handler(commands=['history'])
async def history(message : types.message):
    args = message.get_args()
    if args:
        x = []
        y = []
        new_args = args.split()
        if int(new_args[2]) > 31 or int(new_args[2]) <= 1:
            return await bot.send_message(message.chat.id, 'Try choose any date which more than 1 and less than 31')
        currency = new_args[0].replace('/', '')
        print(currency)
        date_now = date.today()
        x_days_ago = date_now - timedelta(days=int(new_args[2]))
        start_date = date_now
        saturday = 0
        sunday = 0
        for singl_date in (start_date + timedelta(n) for n in range(int(new_args[2]))):
            if singl_date.weekday() == 5:
                saturday += 1
            elif singl_date.weekday() == 6:
                sunday += 1
        x_days_ago = x_days_ago - timedelta(days=saturday+sunday+1)
        if x_days_ago.weekday() == 5:
            x_days_ago = x_days_ago + timedelta(days=2)
        elif x_days_ago.weekday() == 6:
            x_days_ago = x_days_ago + timedelta(days=1)
        params_data = {'currency': currency, 'start_date': x_days_ago, 'end_date': date_now, 'format': 'close', 'api_key': API_KEY}
        res = requests.get('https://fxmarketapi.com/apitimeseries', params=params_data)
        req = res.json()
        try:
            for key, value in req['price'].items():
                x.append(key.replace(key[:8], ''))
                y.append(value['USDCAD'])
            plt.plot(x, y)
            plt.xlabel('Date')
            plt.ylabel('Currency amount')
            plt.title(f'Currency amount from {x_days_ago} to {date_now}')
            plt.savefig('plots/1.png')
            im = open('plots/1.png', 'rb')
            await bot.send_photo(message.chat.id, im, 'This chart show currency amount for every weekdays (without weekends and without current day if not value yet)')
            os.remove('plots/1.png')
        except:
            await bot.send_message(message.chat.id, 'No exchange rate data is available for the selected currency')
    else:
        await bot.send_message(chat_id=message.chat.id, text='You must give parameters after "/history" command.\nAllow parametrs:\nUSD/(your currency) for (number of days)\nFor get list of currencies use /list or /lst')


def register_hendlers(dp: Dispatcher):
    dp.register_message_handler(commands_start, commands=['start', 'help'])
    dp.register_message_handler(command_list, commands=['list', 'lst'])
    dp.register_message_handler(exchange, commands=['exchange'])
    dp.register_message_handler(history, commands=['history'])