import json
import codecs
import requests
import re
import subprocess
import random
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
	helpmessage += "`\thdeposit - allows you to obtain an address to send HLIX to use for tips`\n"
	helpmessage += "`\t\t\t\t/hdeposit`\n"
	helpmessage += "`\thtip - allows you to tip another user in HLIX`\n"
	helpmessage += "`\t\t\t\t/htip @user HLIXamount`\n"
	helpmessage += "`\thtipusd - allows you to tip another user in USD`\n"
	helpmessage += "`\t\t\t\t/htipusd @user USDamount`\n"
	helpmessage += "`\thwithdraw - allows you to withdraw HLIX`\n"
	helpmessage += "`\t\t\t\t/hwithdraw HLIXWITHDRAWADDRESS amount`\n"
	helpmessage += "`\thbalance - allows you to check your HLIX balance`\n"
	helpmessage += "`\t\t\t\t/hbalance`\n"
	helpmessage += "`\thbotbalance - allows you to check the bot's HLIX balance`\n"
	helpmessage += "`\t\t\t\t/hbotbalance`\n"
	helpmessage += "`\thprice - allows you to check the current HLIX price`\n"
	helpmessage += "`\t\t\t\t/hprice`\n"
	helpmessage += "`\thmninfo - allows you to check the current Helix masternode data`\n"
	helpmessage += "`\t\t\t\t/hmninfo`\n"
	helpmessage += "`\thmarketcap - allows your to check the current HLIX Market Cap`\n"
	helpmessage += "`\t\t\t\t/hmarketcap`\n"
	helpmessage += "`\thhilo - Double your bet! Bet low to bet on 1-4499 or high to bet on 5501-10000! The house always wins between 4500-5500!`\n"
	helpmessage += "`\t\t\t\t/hhilo <high/low> <amount>`\n"
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
		bot.send_message(chat_id=update.message.chat_id, text="@{0}` your depositing address is:` {1}".format(user,clean),parse_mode='Markdown')
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
		
@run_async
def mninfo(bot,update):
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving Helix Masternode Data")
	r = requests.get('http://explorer.helix-crypto.com/api/getmasternodecount')
	cgapi = json.loads(r.content.decode())
	mncount=cgapi['enabled']
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	rwtime = float(mncount) / 60
	perday =  (24 / float(rwtime)) * 9
	perweek = (168 / float(rwtime)) * 9
	permonth = (720 / float(rwtime)) * 9
	peryear = (8760 / float(rwtime)) * 9
	roi = (peryear / 10000) * 100
	msg=bot.send_message(chat_id=update.message.chat_id, text="*Helix masternode info*\n\n`MNs online: {0}\nCollateral: 10,000 HLIX\n\nIncome:\n{1:.2f} HLIX per day\n{2:.2f} HLIX per week\n{3:.2f} HLIX per month\n{4:.2f} HLIX per year\nROI: {5:.2f}%`".format(mncount, perday, perweek, permonth, peryear, roi),parse_mode='Markdown')
	time.sleep(15)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)


def hilo(bot,update):
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving Helix Market Data")
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['current_price']['usd']
	price=float(usd)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	user = update.message.from_user.username
	command=update.message.text.split()
	bet = command[1]
	rdm = random.randint(0, 10001)
	amount = float(command[2])
	machine = "Helix_crypto_bot"
	if user is None:
		msg=bot.send_message(chat_id=update.message.chat_id, text="Please set a telegram username in your profile settings!")
		time.sleep(5)
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
	else:
			user = update.message.from_user.username
			core = "/usr/local/bin/helix-cli"
			result = subprocess.run([core,"getbalance",user],stdout=subprocess.PIPE)
			balance = float((result.stdout.strip()).decode("utf-8"))
			result2 = subprocess.run([core,"getbalance",machine],stdout=subprocess.PIPE)
			balance2 = float((result2.stdout.strip()).decode("utf-8"))
			amount = round(float(amount),8)
			if balance2 < amount:
				msg=bot.send_message(chat_id=update.message.chat_id, text="Sorry @{0} i dont have enough, my current available funds is {1} HLIX, you can top me up by tipping me!".format(user,balance2))
				time.sleep(10)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif balance < amount:
				msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} you have insufficent funds.".format(user))
				time.sleep(10)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif bet != "high" and bet != "low":
				msg=bot.send_message(chat_id=update.message.chat_id, text="Please choose 'high' or 'low' as bet!")
				time.sleep(10)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif amount < 0:
				msg=bot.send_message(chat_id=update.message.chat_id, text="You can't play with a negative amount, silly.")
				time.sleep(10)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
			elif amount < 1:
				msg=bot.send_message(chat_id=update.message.chat_id, text="You can't play with less than 1 HLIX.")
				time.sleep(10)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

			elif amount > 1000:
				msg=bot.send_message(chat_id=update.message.chat_id, text="Whoa, calm down highroller! Not all of us has such high amounts! Please bet 1000 or lower!")
				time.sleep(15)
				bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

			elif rdm > 4500 and rdm < 5500:
				
				balance = str(balance)
				amount = str(amount)
				tx = subprocess.run([core,"move",user,machine,amount],stdout=subprocess.PIPE)
				msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} Ouch I rolled {1} which is between 4500-5500 and is always won by the house! You lost {2} HLIX".format(user,rdm,amount),parse_mode='Markdown')
#				time.sleep(5)
				#bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

			elif bet == "high" and rdm > 5500:
				
				balance = str(balance)
				amount = str(amount)
				tx = subprocess.run([core,"move",machine,user,amount],stdout=subprocess.PIPE)
				msg=bot.send_message(chat_id=update.message.chat_id, text="@{3} choose {0} and the bot rolled {1}! Congrats you won {2} HLIX!".format(bet,rdm,amount,user),parse_mode='Markdown')
#				time.sleep(30)
				#bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

			elif bet == "low" and rdm < 4500:
				
				balance = str(balance)
				amount = str(amount)
				tx = subprocess.run([core,"move",machine,user,amount],stdout=subprocess.PIPE)
				msg=bot.send_message(chat_id=update.message.chat_id, text="@{3} choose {0} and the bot rolled {1}! Congrats you won {2} HLIX!".format(bet,rdm,amount,user),parse_mode='Markdown')
#				time.sleep(30)
				#bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

			else:
				balance = str(balance)
				amount = str(amount)
				tx = subprocess.run([core,"move",user,machine,amount],stdout=subprocess.PIPE)
				msg=bot.send_message(chat_id=update.message.chat_id, text="@{3} choose {0} and the bot rolled {1}! You lost {2} HLIX".format(bet,rdm,amount,user),parse_mode='Markdown')
#				time.sleep(15)
				#bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

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
		if "@" in target:
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
				bot.send_message(chat_id=update.message.chat_id, text="@{0} `tipped` @{1} `{2:.8f} HLIX (${3:.8f} USD)`".format(user, target, float(amount), usdamount),parse_mode='Markdown')
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
		else:
			msg=bot.send_message(chat_id=update.message.chat_id, text="Error that user is not applicable and probably has to set a telegram username.")
			time.sleep(10)
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
				bot.send_message(chat_id=update.message.chat_id, text="@{0}` tipped `@{1}` ${3:.8f} USD ({2:.8f} HLIX)`".format(user, target, float(amount), amountusd),parse_mode='Markdown')
				bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
		else:
			msg=bot.send_message(chat_id=update.message.chat_id, text="Error that user is not applicable and probably has to set a telegram username.")
			time.sleep(10)
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
		msg=bot.send_message(chat_id=update.message.chat_id, text="@{0} `your current balance is: {1} HLIX ≈  ${2}`".format(user,balance,fiat_balance),parse_mode='Markdown')
		time.sleep(15)
		bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
		bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

def botbalance(bot,update):
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving Helix Market Data")
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['current_price']['usd']
	price=float(usd)
	machine="Helix_crypto_bot"
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	user = update.message.from_user.username
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving HLIX Balance")
	core = "/usr/local/bin/helix-cli"
	result = subprocess.run([core,"getbalance",machine],stdout=subprocess.PIPE)
	clean = (result.stdout.strip()).decode("utf-8")
	balance  = float(clean)
	fiat_balance = balance * usd
	fiat_balance = str(round(fiat_balance,4))
	balance =  str(round(balance,8))
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	msg=bot.send_message(chat_id=update.message.chat_id, text="@{0}`'s current balance is: {1} HLIX ≈  ${2}`".format(machine,balance,fiat_balance),parse_mode='Markdown')
	time.sleep(15)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def price(bot,update):
	msg=bot.send_message(chat_id=update.message.chat_id, text="Retrieving Helix Market Data")
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['current_price']['usd']
	btc=cgapi['market_data']['current_price']['btc']
	change=cgapi['market_data']['price_change_percentage_24h']
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	msg=bot.send_message(chat_id=update.message.chat_id, text="*Helix is valued at:*\n`BTC: {1:.8f}฿\nUSD: ${0:.8f}\n24h change: {2:.5}%`".format(usd, btc, change),parse_mode='Markdown')
	time.sleep(30)
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
					msg=bot.send_message(chat_id=update.message.chat_id, text="`@{0} has successfully withdrawn {2} HLIX to address: {1}`" .format(user,address,amount),parse_mode='Markdown')
					time.sleep(20)
					bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
					bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def marketcap(bot,update):
	r = requests.get('https://api.coingecko.com/api/v3/coins/helix?tickers=false&community_data=false&developer_data=false&sparkline=false')
	cgapi = json.loads(r.content.decode())
	usd=cgapi['market_data']['market_cap']['usd']
	btc=cgapi['market_data']['market_cap']['btc']
	msg=bot.send_message(chat_id=update.message.chat_id, text="*Marketcap:*\n`The current market cap of Helix is valued at ${0} (USD)`".format(int(usd)),parse_mode='Markdown')
	time.sleep(30)
	bot.delete_message(chat_id=update.message.chat_id, message_id=msg.message_id)
	bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

from telegram.ext import CommandHandler

hilo_handler = CommandHandler('hhilo', hilo)
dispatcher.add_handler(hilo_handler)

mninfo_handler = CommandHandler('hmninfo', mninfo)
dispatcher.add_handler(mninfo_handler)

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

botbalance_handler = CommandHandler('hbotbalance', botbalance)
dispatcher.add_handler(botbalance_handler)

help_handler = CommandHandler('hhelp', help)
dispatcher.add_handler(help_handler)

updater.start_polling()
