import json
import codecs
import requests
import re
import subprocess
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater
from html import escape
import time

updater = Updater(token='')
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)
					
def help(bot, update):
	user = update.message.from_user.username
	helpmessage = "*Hi, I am HelixBot, here are some commands you can use to interact with me...*\n\n"
	helpmessage += "`\thdeposit - allows you to obtain an address to send HLIX to use for tips:`\n"
	helpmessage += "`\t\t\t\t/hdeposit`\n"
	helpmessage += "`\thtip - allows you to tip another user in HLIX:`\n"
	helpmessage += "`\t\t\t\t/htip @user HLIXamount`\n"
	helpmessage += "`\thtip - allows you to tip another user in USD:`\n"
	helpmessage += "`\t\t\t\t/htipusd @user USDamount`\n"
	helpmessage += "`\thwithdraw - allows you to withdraw HLIX:`\n"
	helpmessage += "`\t\t\t\t/hwithdraw HLIXWITHDRAWADDRESS amount`\n"
	helpmessage += "`\thbalance - allows you to check your HLIX balance:`\n"
	helpmessage += "`\t\t\t\t/hbalance`\n"
	helpmessage += "`\thprice - allows you to check the current HLIX price:`\n"
	helpmessage += "`\t\t\t\t/hprice`\n"
	helpmessage += "`\thmarketcap - allows your to check the current HLIX Market Cap:`\n"
	helpmessage += "`\t\t\t\t/hmarketcap`\n"
	bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	msg=bot.send_message(chat_id=update.message.chat_id, text=helpmessage, parse_mode='Markdown')

@run_async
def deposit(bot, update):
	user = update.message.from_user.username
	if user is None:
		msg=bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
		time.sleep(5)
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	else:
		address = "/usr/local/bin/helix-cli"
		result = subprocess.run([address,"getaccountaddress",user],stdout=subprocess.PIPE)
		clean = (result.stdout.strip()).decode("utf-8")
		bot.send_message(chat_id=update.message.chat_id, text="@{0} your depositing address is: {1}".format(user,clean))
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
		
@run_async
def tip(bot,update):
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving Helix Market Data")
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['current_price']['usd']
	price=float(usd)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	user = update.message.from_user.username
	command=update.message.text.split()
	amount =  float(command[2])
	usdamount = float(price) * float(amount)
	target =  command[1]
	if user is None:
		msg=bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
		time.sleep(5)
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	else:
		machine = "@Helix_crypto_bot"
		if target == machine:
			bot.send_message(chat_id=update.message.chat_id, text="HODL.")
		elif "@" in target:
			target = target[1:]
			user = update.message.from_user.username
			core = "/usr/local/bin/helix-cli"
			result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
			balance = float((result.stdout.strip()).decode("utf-8"))
			amount = round(float(amount),8)
			if balance < amount:
				msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} you have insufficent funds.".format(user))
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif amount < 0:
				msg=bot.send_message(chat_id=update.message.chat_id, text="You can't tip a negative amount, silly.")
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif amount < 0.00000001:
				msg=bot.send_message(chat_id=update.message.chat_id, text="You can't tip less than 0.00000001.")
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif target == user:
				msg=bot.send_message(chat_id=update.message.chat_id, text="You can't tip yourself, silly.")
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			else:
				balance = str(balance)
				amount = str(amount)
				tx = subprocess.run([core,"move",user,target,amount],stdout=subprocess.PIPE)
				bot.send_message(chat_id=update.message.chat_id, text="@{0} tipped @{1} {2:.8f} HLIX (${3:.8f} USD)".format(user, target, float(amount), usdamount))
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
		else:
			msg=bot.send_message(chat_id=update.message.chat_id, text="Error that user is not applicable.")
			time.sleep(5)
			bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
			bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

def tipusd(bot,update):
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving Helix Market Data")
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['current_price']['usd']
	price=float(usd)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	user = update.message.from_user.username
	command=update.message.text.split()
	amountusd =  float(command[2])
	amount = float(amountusd) / float(price)
	target =  command[1]
	if user is None:
		msg=bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
		time.sleep(5)
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	else:
		machine = "@Helix_crypto_bot"
		if target == machine:
			bot.send_message(chat_id=update.message.chat_id, text="HODL.")
		elif "@" in target:
			target = target[1:]
			user = update.message.from_user.username
			core = "/usr/local/bin/helix-cli"
			result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
			balance = float((result.stdout.strip()).decode("utf-8"))
			amount = round(float(amount),8)
			if balance < amount:
				msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} you have insufficent funds.".format(user))
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif amount < 0:
				msg=bot.send_message(chat_id=update.message.chat_id, text="You can't tip a negative amount, silly.")
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif amount < 0.00000001:
				msg=bot.send_message(chat_id=update.message.chat_id, text="You can't tip less than 0.00000001.")
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif target == user:
				msg=bot.send_message(chat_id=update.message.chat_id, text="You can't tip yourself, silly.")
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			else:
				balance = str(balance)
				amount = str(amount)
				tx = subprocess.run([core,"move",user,target,amount],stdout=subprocess.PIPE)
				bot.send_message(chat_id=update.message.chat_id, text="@{0} tipped @{1} ${3:.8f} USD ({2:.8f} HLIX)".format(user, target, float(amount), amountusd))
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
		else:
			msg=bot.send_message(chat_id=update.message.chat_id, text="Error that user is not applicable.")
			time.sleep(5)
			bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
			bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def balance(bot,update):
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving Helix Market Data")
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['current_price']['usd']
	price=float(usd)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	user = update.message.from_user.username
	if user is None:
		msg=bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
		time.sleep(5)
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	else:
		msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving HLIX Balance")
		core = "/usr/local/bin/helix-cli"
		result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
		clean = (result.stdout.strip()).decode("utf-8")
		balance  = float(clean)
		fiat_balance = balance * usd
		fiat_balance = str(round(fiat_balance,4))
		balance =  str(round(balance,8))
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} your current balance is: {1} HLIX ≈  ${2}".format(user,balance,fiat_balance))
		time.sleep(10)
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def price(bot,update):
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving Helix Market Data")
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['current_price']['usd']
	btc=cgapi['market_data']['current_price']['btc']
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	msg=bot.send_message(chat_id=update.message.chat_id, text="Helix is valued at ${0:.8f} ≈ {1:.8f}".format(usd,btc) + " ฿")
	time.sleep(10)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def withdraw(bot,update):
	user = update.message.from_user.username
	if user is None:
		msg=bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
		time.sleep(5)
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	else:
		invalid=False
		command=update.message.text.split()
		address = command[1]
		target = command[2]
		core = "/usr/local/bin/helix-cli"
		result = subprocess.run([core,"validateaddress",address],stdout=subprocess.PIPE)
		clean = json.loads((result.stdout.strip()).decode("utf-8"))
		if clean['isvalid'] != True:
			msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} That is an invalid HLIX Address".format(user))
			time.sleep(5)
			bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
			bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
		else:
			try:
				amount = float(target)
			except:
				msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} That is not a valid amount!".format(user))
				time.sleep(5)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
				invalid=True
			if invalid!=True:
				result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
				clean = (result.stdout.strip()).decode("utf-8")
				balance = float(clean)
				if balance < amount:
					msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} you have insufficent funds.".format(user))
					time.sleep(5)
					bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
					bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
				else:
					amount = str(amount)
					tx = subprocess.run([core,"sendfrom",user,address,amount],stdout=subprocess.PIPE)
					msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} has successfully withdrawn {2} HLIX to address: {1}" .format(user,address,amount))
					time.sleep(10)
					bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
					bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def marketcap(bot,update):
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['market_cap']['usd']
	btc=cgapi['market_data']['market_cap']['btc']
	msg=bot.send_message(chat_id=update.message.chat_id, text="The current market cap of Helix is valued at ${0} (USD)".format(int(usd)))
	time.sleep(10)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

from telegram.ext import CommandHandler

withdraw_handler = CommandHandler('hwithdraw', withdraw)
dispatcher.add_handler(withdraw_handler)

marketcap_handler = CommandHandler('hmarketcap', marketcap)
dispatcher.add_handler(marketcap_handler)

deposit_handler = CommandHandler('hdeposit', deposit)
dispatcher.add_handler(deposit_handler)

price_handler = CommandHandler('hprice', price)
dispatcher.add_handler(price_handler)

tip_handler = CommandHandler('htip', tip)
dispatcher.add_handler(tip_handler)

tip_handler = CommandHandler('htipusd', tipusd)
dispatcher.add_handler(tip_handler)

balance_handler = CommandHandler('hbalance', balance)
dispatcher.add_handler(balance_handler)

help_handler = CommandHandler('hhelp', help)
dispatcher.add_handler(help_handler)

updater.start_polling()
