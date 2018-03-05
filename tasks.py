import discord
import asyncio
from discord.ext import commands

from random import * # Used for roll, coin, and 8ball

from pprint import pprint
from googleapiclient import discovery
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime #Used for post_dailies() function.
from datetime import date
from datetime import datetime
import calendar
import time

import aiohttp
from re import finditer
import re
import copy

import pickle #Used for backing up favorites.

#GLOBALS
favorites_dict = {}
alert_dict = {}
cookie = {'commonWebPath':'/web',
'localWebPath':'/english/web',
'language':'en', 'GPVLU':'6187d9c913cf5283d676c3e68aea987e42e4e6804b83d5d78598fe035613d53f6d05c48cc001b6ef530b756b44c469c66c11240bb36528624a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d24a1a222355efd1d2e65c752e0aed4114c1863113b5812c1ec33040840c6f226181e2a8484d1a405133f9f92265f3d85d5b38ec544a8ec704e6c02f49d380d3f86e5e0be669742462e41c10af7941cfa99ad3bf300b8b34db',
'SessionIndex':'1'
}

class tasks:
	""" All PlongBot's background tasks. """
	def __init__(self, bot):
		self.bot = bot


	#All functions and classes needed for background tasks start here.
	class member(object):
		ign = ""
		discord_id = ""
		def __init__(self, ign, discord_id):
			self.ign = ign
			self.discord_id = discord_id

	def make_member(self, ign, discord_id = None):
		if discord_id is None:
			Member = self.member(ign, "")
		else:
			Member = self.member(ign, discord_id)
		return Member


	def get_credentials(self):
		"""Gets valid user credentials from storage.

		If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain the new credentials.

		Returns:
			Credentials, the obtained credential.
		"""
		home_dir = os.path.expanduser('~')
		credential_dir = os.path.join(home_dir, '.credentials')
		if not os.path.exists(credential_dir):
			os.makedirs(credential_dir)
		credential_path = os.path.join(credential_dir,
									   'sheets.googleapis.com-python-quickstart.json')

		store = Storage(credential_path)
		credentials = store.get()
		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
			flow.user_agent = APPLICATION_NAME
			if flags:
				credentials = tools.run_flow(flow, store, flags)
			else: # Needed only for compatibility with Python 2.6
				credentials = tools.run(flow, store)
			print('Storing credentials to ' + credential_path)
		return credentials


	async def get_favorites_dict(self):
		try: #Lazy way to prevent crashes when favorites_dict.txt hasnt been made yet.
			with open('favorites_dict.txt', 'rb') as handle:
				global favorites_dict
				favorites_dict = pickle.loads(handle.read())
		except Exception as e:
			print("Couldnt get favorites_dict")
			print(e)

	async def backup_favs(self):
		with open('favorites_dict.txt', 'wb') as backup:
			pickle.dump(favorites_dict, backup)

	async def scheduled_price_alerts(self):
		refresh_interval = 60 #Checks every minute
		URL = "http://na-bnsmarket.ncsoft.com/bns/bidder/home.web?npc=false"

		while True:
			if alert_dict: #Check if dict has any entries for price alerts to do.
				try:
					async with aiohttp.ClientSession(cookies=cookie) as session:
						async with session.get(URL) as resp:
							if resp.status == 200:
								data = await resp.text()
				except Exception as e:
					print("Failed send price request.")
					print(e)
					return ""

				found = False
				if '<td class="price' in data:
					prices = []
					found = True
					price_lines = []
					item_names = []
					for line in data.splitlines():
						if """<dd class="price"><span class='""" in line:
							price_lines.append(line)
						if '","name":"' in line:
							item_names.append(line)

					index = 0
					names_list = []
					item_nums_list = []
					for line in item_names:
						search = re.search('","name":"(.*)","mainInfo"', line)
						name = search.group(1)
						names_list.append(name)
						#checking alert_dict to remove favorites
						search = re.search('"item":"(.*)","name"', line)
						item_num = search.group(1)
						item_nums_list.append(item_num)
						await self.validate_dict(item_num)

					price_list = []
					for line in price_lines:
						price_entry = ""
						if "gold" in line:
							amt = re.search("class='gold'>(.*) <span>금", line)
							gold = amt.group(1)
							price_entry += gold
						else:
							price_entry += "00"
						if "silver" in line:
							amt = re.search("class='silver'>(.*) <span>은", line)
							silver = amt.group(1)
							price_entry += silver.zfill(2)
						else:
							price_entry += "00"
						if "bronze" in line:
							amt = re.search("class='bronze'>(.*) <span>동", line)
							copper = amt.group(1)
							price_entry += copper.zfill(2)
						else:
							price_entry += "00"
						price_list.append(price_entry)

						prices.append((item_nums_list[index], names_list[index], price_list[index]))
						index += 1

					alert_dict_copy = copy.deepcopy(alert_dict)
					for listing in prices:
						if listing[0] in alert_dict: # If there exist any alerts for this item
							for alert in alert_dict_copy[listing[0]]:
								if await self.price_found(alert, listing):
									server = alert[2]
									price_alert_user = discord.utils.get(server.members, id = alert[0])
									gold = listing[2][:-4] + "<:gold_coin:402993867844222977> "
									silver = listing[2][-4:-2] + "<:silver_coin:402993901293666306> "
									copper = listing[2][-2:] + "<:copper_coin:402993919505203200>"
									price = gold + silver + copper
									await self.bot.send_message(price_alert_user, "Good news! Found a listing for " + listing[1] + " at " + price)
									alert_dict[listing[0]].remove((alert[0], alert[1], alert[2], alert[3]))
									await self.validate_dict(listing[0])


				elif found == False and "No search results found for" in data:
					print("No search results found")
					await self.bot.send_message(schlong, "No search results found.")
				elif found == False and "We apologize for the inconvenience. Please try again later." in data:
					print("Session ID expired.")
					await self.bot.send_message(schlong, "Can't search marketplace at the moment.")
				else:
					print("Error: no internet?")

				await asyncio.sleep(refresh_interval)
			else:

				await asyncio.sleep(refresh_interval)

	async def price_found(self, alert, listing):
		# if ((listing price <= alert_price) and lower_than is true) OR if ((listing price >= alert_price) and lower_than is false)
		if ((int(listing[2]) <= int(alert[1])) and alert[3]) or ((int(listing[2]) >= int(alert[1])) and not alert[3]):
			return True
		else:
			return False

	async def validate_dict(self, item_num):
		""" Checks the alert_dict for a specific item entry. If no users have an alert for this item, it is removed from alert_dict and favorites. """
		try:
			if alert_dict[item_num]:
				#contains other entries for that item.
				pass
			else:
				#Evaluated to False instead of error, which means key exists but has no entries.
				alert_dict.pop(item_num, None)
				await self.delete_favorite(item_num)
		except KeyError:
			await self.delete_favorite(item_num)

	async def get_price(self, price):
		gold = "00"
		silver = "00"
		copper = "00"
		leftover_silver = 0 # Used for decimal places. Ex. 1.5g = 1g and 50 leftover silver
		leftover_copper = 0

		for index, char in enumerate(price):
			if char == "g" and price[index-1].isdigit(): #contains gold
				index2 = index-1
				while price[index2].isdigit() or price[index2] == ".":
					index2 -= 1
				if price[index2+1:index].find(".") == -1: #searches for decimal in "gold section" of price.
					gold = price[index2+1:index]
				else:
					gold, after_decimal = price[index2+1:index].split(".")
					leftover_silver += int(after_decimal[:2].ljust(2,"0"))
					leftover_copper += int(after_decimal[2:4].ljust(2,"0"))
		for index, char in enumerate(price):
			if char == "s" and price[index-1].isdigit(): #contains silver
				index2 = index-1
				while price[index2].isdigit() or price[index2] == ".":
					index2 -= 1
				if price[index2+1:index].find(".") == -1: #searches for decimal in "silver section" of price.
					silver = price[index2+1:index]
				else:
					silver, after_decimal = price[index2+1:index].split(".")
					leftover_copper += int(after_decimal[:2].ljust(2,"0"))
		for index, char in enumerate(price):
			if char == "c" and price[index-1].isdigit(): #contains copper
				index2 = index-1
				while price[index2].isdigit():
					index2 -= 1
				copper = price[index2+1:index]

		#Adding on leftover silvers and coppers
		silver = str(int(silver) + leftover_silver)
		copper = str(int(copper) + leftover_copper)
		#Converting coppers and silvers to higher denominations if they exceed 100
		if int(copper) >= 100:
			silver = str(int(int(silver) + int(copper)/100))
			copper = str(int(copper)%100)
		if int(silver) >= 100:
			gold = str(int(int(gold) + int(silver)/100))
			silver = str(int(silver)%100)

		price = gold + silver.zfill(2) + copper.zfill(2)
		return price


	async def spreadsheet_task(self):
		""" Grabs values from raid rosters on Google Sheets and updates discord roles for their specific raid. """
		server_id = "317150426103283712"
		VT_role_id = "381753872206790659"
		BTA_role_id = "395774727257325568"
		BTB_role_id = "395784674674475009"
		update_range = 'BT Weekends!B2'
		roster_ign_range = 'Clan Roster!D4:D'
		roster_id_range = 'Clan Roster!I4:I'
		raid1_ids_range = 'BT Weekends!AC6:AC18'
		raid2_ids_range = 'BT Weekends!AD6:AD18'
		update_check_delay = 30
		spreadsheet_id = '1O5naOP-Ir--2GjgNsWmAGv-lnDkOz00f5TdHdKsE7_Y'
		value_render_option = 'FORMATTED_VALUE'
		date_time_render_option = 'SERIAL_NUMBER'


		update_date = None
		credentials = await self.bot.loop.run_in_executor(None, self.get_credentials)
		while True:
			try: #Due to potential 503 error.
				service = discovery.build('sheets', 'v4', credentials=credentials)
				break
			except Exception as e:
				print(e)
				await asyncio.sleep(10)
		while(True):
			#Checking last edit date
			try:
				request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=update_range, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
				edit_date = await self.bot.loop.run_in_executor(None, self.request_execute, request)
			except Exception as e:
				print("Grabbing latest edit_date failed.")
				print(e)
				await asyncio.sleep(10)
			if update_date == edit_date: # Roster and roles are up to date.
				pass
			else: # Roster has changed since last update.
				update_date = edit_date
				#Creating roster list
				try:
					request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=roster_ign_range, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
					response_ign = await self.bot.loop.run_in_executor(None, self.request_execute, request)
				except :
					print("Grabbing response_ign for roster failed.")
					await asyncio.sleep(10)
				try:
					request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=roster_id_range, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
					response_id = await self.bot.loop.run_in_executor(None, self.request_execute, request)
				except Exception as e:
					print("Grabbing response_id for roster failed.")
					print(e)
					await asyncio.sleep(10)
				roster = await self.create_roster(response_ign, response_id, server_id)


				#BTA / Saturday Raid
				range_ = 'BT Weekends!E7:E12' # Party 1
				try:
					request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=raid1_ids_range, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
					response_BT1 = await self.bot.loop.run_in_executor(None, self.request_execute, request)
				except Exception as e:
					print("Grabbing response_BT1 values for Saturday failed.")
					print(e)
					await asyncio.sleep(10)
				server = self.bot.get_server(server_id)
				await self.remove_role(roster, server, BTA_role_id)
				await self.add_role(roster, server, BTA_role_id, response_BT1)


				#BTB / Sunday Raid
				range_ = 'BT Weekends!O7:O12' # Party 1
				try:
					request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=raid2_ids_range, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
					response_BT1 = await self.bot.loop.run_in_executor(None, self.request_execute, request)
				except Exception as e:
					print("Grabbing response_BT1 values for Sunday failed.")
					print(e)
					await asyncio.sleep(10)
				await self.remove_role(roster, server, BTB_role_id)
				await self.add_role(roster, server, BTB_role_id, response_BT1)


			await asyncio.sleep(update_check_delay) #Waits seconds before checking for roster updates

	#Used for run_in_executor, since Google Sheets API is synchronous
	def request_execute(self, request):
		while True:
			try:
				response = request.execute()
				return response
			except Exception as e:
				print("Grabbing response values failed.")
				print(e)
				time.sleep(10)


	async def create_roster(self, response_ign, response_id, server_id):
		roster = []
		index = 0
		for entry in response_ign['values']:
			if index < len(response_id['values']) and entry and response_id['values'][index]:
				member = self.make_member(str(entry)[2:-2], str(response_id['values'][index])[2:-2]) #[2:-2] removes brackets and quotes from each entry
				roster.append(member)
				index += 1
			elif index < len(response_id['values']) and entry and not response_id['values'][index]:
				member = self.make_member(str(entry)[2:-2])
				roster.append(member)
				server = self.bot.get_server(server_id)
				schlong = discord.utils.get(server.members, id = '217513859412525057')
				await self.bot.send_message(schlong, "Missing discord ID for " + str(entry))
				index += 1
			elif index >= len(response_id['values']):
				member = self.make_member(str(entry)[2:-2])
				roster.append(member)
				server = self.bot.get_server(server_id)
				schlong = discord.utils.get(server.members, id = '217513859412525057')
				await self.bot.send_message(schlong, "Missing discord ID for " + str(entry))
				index += 1
			else:
				index += 1
		return roster

	async def remove_role(self, roster, server, raid_role_id):
		""" Removes the role passed for all users in roster """
		for guildie in roster:
			if guildie.discord_id:
				raider = server.get_member(guildie.discord_id)
				if raider: # Checks if this user was found in the server.
					for roles in raider.roles:
						if raid_role_id == roles.id:
							await self.bot.remove_roles(raider, roles)
				else:
					schlong = discord.utils.get(server.members, id = '217513859412525057')
					await self.bot.send_message(schlong, "Couldn't find " + guildie.ign + " in server. Could have left guild.")
		return True

	async def add_role(self, roster, server, raid_role_id, response_raid):
		""" Adds role passed for all users in response_raid """
		try: # Checks for empty raid roster.
			role = discord.utils.get(server.roles, id = raid_role_id)
			for BT in response_raid['values']:
				member = str(BT)[2:-2] #[2:-2] removes brackets and quotes from each entry
				found = False
				for guildie in roster:
					if BT and guildie.discord_id and member == guildie.discord_id:
						raider = discord.utils.get(server.members, id = guildie.discord_id)
						print("ADDING ROLE FOR " + guildie.ign + " " + role.id)
						await self.bot.add_roles(raider, role)
						found = True
						break
				if found == False:
					schlong = discord.utils.get(server.members, id = '217513859412525057')
					await self.bot.send_message(schlong, "On the roster, but couldn't add role for " + str(BT) + "Raid ID: " + raid_role_id)
		except:
			print("Empty raid roster or response_raid wasn't requested correctly.")
		return True


	async def post_dailies(self):
		dailies_channel_id = "370276401615732736"
		server_id = "317150426103283712"
		bot_id = "393162340234952715"
		dailies = [
		#Sunday
		"\nAvalanche Den\nGloomdross Incursion\nNaryu Foundry\nNaryu Sanctum\nHollow's Heart\nDrowning Deeps\nTower of Infinity\nOutlaw Island\nMidnight Skypetal Plains\n",
		#Monday
		"\nGloomdross Incursion\nEbondrake Citadel\nDesolate Tomb\nNaryu Sanctum\nEbondrake Lair\nStarstone Mines\n- - - -\nTag Match\nBeluga Lagoon\n",
		#Tuesday
		"\nCold Storage\nLair of the Frozen Fang\nSogun's Lament\nNaryu Foundry\nIronTech Forge\nHollow's Heart\nTower of Infinity\n- - - -\nOne on One Match\nWhirlwind Valley\n",
		#Wednesday
		"\nHeaven's Mandate\nAvalanche Den\nThe Shattered Masts\nDesolate Tomb\nNaryu Sanctum\nEbondrake Lair\nOutlaw Island\n- - - -\nTag Match\nNova Core\n",
		#Thursday
		"\nLair of the Frozen Fang\nEbondrake Citadel\nNaryu Foundry\nIrontech Forge\nStarstone Mines\nMushin's Tower 20F\nTower of Infinity\n- - - -\nOne on One Match\nBeluga Lagoon\n",
		#Friday
		"\nCold Storage\nThe Shattered Masts\nDesolate Tomb\nEbondrake Lair\nHollow's Heart\nDrowning Deeps\nOutlaw Island\n- - - -\nTag Match\nWhirlwind Valley\n",
		#Saturday
		"\nHeaven's Mandate\nSogun's Lament\nEbondrake Citadel\nIrontech Forge\nStarstone Mines\nMidnight Skypetal Plains\nMushin's Tower 20F\n- - - -\nOne on One Match\nNova Core\n"
		]
		img_dailies = [
		#Sunday
		"https://i.imgur.com/BtcJZl9.png",
		#Monday
		"https://i.imgur.com/pFw6UZ9.png",
		#Tuesday
		"https://i.imgur.com/4n1Ru1B.png",
		#Wednesday
		"https://i.imgur.com/Iep8Rwq.png",
		#Thursday
		"https://i.imgur.com/nuRBu29.png",
		#Friday
		"https://i.imgur.com/6S9Opg0.png",
		#Saturday
		"https://i.imgur.com/WAfH7Lo.png"
		]

		server = self.bot.get_server(server_id)
		botto = discord.utils.get(server.members, id = bot_id)
		dailies_channel = self.bot.get_channel(dailies_channel_id)
		dailies_found = False
		async for message in self.bot.logs_from(dailies_channel, limit = 6):
			try:
				if message.author == botto and calendar.day_name[date.today().weekday()] in message.embeds[0]['fields'][0]['name']:
					dailies_found = True
					break
			except:
				print("Not an embed.")
		if dailies_found == False:
			link = img_dailies[int(datetime.today().strftime('%w'))]
			embed = discord.Embed(color=0x4e5f94)
			#embed.set_image(url = link) #Retired image dailies.
			embed.add_field(name = "📆 " + str(datetime.now().month) + "/" + str(datetime.now().day) + " " + calendar.day_name[date.today().weekday()] + " Dailies", value = dailies[int(datetime.today().strftime('%w'))], inline=True)
			try:
				await self.bot.send_message(ctx.message.channel, embed=embed)
			except Exception as e:
				await self.bot.say("I need embed permissions to reply properly.")
				print("Failed !hello command.")
				print(e)
		#await self.bot.send_message(dailies_channel, "📆 **" + str(datetime.now().month) + "/" + str(datetime.now().day) + " " + calendar.day_name[date.today().weekday()]+ "**\n")


	async def schedule_dailies(self):
		check_interval = 25 #25 will check at least twice per minute
		one_day_minus_two_min = 86280
		post_time = "04:00"

		await self.post_dailies()
		while True:
			now = datetime.now().strftime('%H:%M')
			if now == post_time:
				await self.post_dailies()
				print("Posted dailies at: " + now)
				await asyncio.sleep(one_day_minus_two_min)
			else:
				await asyncio.sleep(check_interval)

	async def schedule_session_refresh(self):
		refresh_interval = 1800 # Refreshes every half hour
		server_id = "317150426103283712"
		server = discord.utils.get(self.bot.servers, id = server_id)
		schlong = discord.utils.get(server.members, id = '217513859412525057')
		numbering = ["<:1_:403077593513066496>", "<:2_:403077593273991170>", "<:3_:403077593198362627>"]

		URL = "http://na-bnsmarket.ncsoft.com/bns/bidder/home.web?npc=false"

		while True:
			# sending get request and saving the response as response object
			try:
				async with aiohttp.ClientSession(cookies=cookie) as session:
					async with session.get(URL) as resp:
						if resp.status == 200:
							data = await resp.text()
			except Exception as e:
				print("Failed send price request.")
				print(e)
				await asyncio.sleep(10)

			found = False
			if '<td class="price' in data:
				prices = ""
				found = True
				price_lines = []
				item_names = []
				for line in data.splitlines():
					if """<dd class="price"><span class='""" in line:
						price_lines.append(line)
					if '","name":"' in line:
						item_names.append(line)

				index = 0
				names_list = []
				for line in item_names:
					search = re.search('","name":"(.*)","mainInfo"', line)
					name = search.group(1)
					names_list.append(name)

				price_list = []
				for line in price_lines:
					price_entry = ""
					if "gold" in line:
						amt = re.search("class='gold'>(.*) <span>금", line)
						gold = amt.group(1) + "<:gold_coin:402993867844222977> "
						price_entry += gold
					if "silver" in line:
						amt = re.search("class='silver'>(.*) <span>은", line)
						silver = amt.group(1) + "<:silver_coin:402993901293666306> "
						price_entry += silver
					if "bronze" in line:
						amt = re.search("class='bronze'>(.*) <span>동", line)
						copper = amt.group(1) + "<:copper_coin:402993919505203200>"
						price_entry += copper
					price_list.append(price_entry)

					prices += str(index + 1) + ". **" + names_list[index] + " / " + price_list[index] + "**\n"
					index += 1

				image_url = re.search('iconImg" src="(.*)" alt="', data)
				embed = discord.Embed(color=0x72eab0)
				embed.add_field(name="Listings", value=prices, inline=True)
				await self.bot.send_message(schlong, embed=embed)
			elif found == False and "No search results found for" in data:
				print("No search results found") # change to found for "item"
				await self.bot.send_message(schlong, "No search results found.")
			elif found == False and "We apologize for the inconvenience. Please try again later." in data:
				print("Session ID expired.")
				await self.bot.send_message(schlong, "Can't search marketplace at the moment.")
			else:
				print("Error: no internet?")

			await asyncio.sleep(refresh_interval)

	async def add_favorite(self, item_num):
		URL = "http://na-bnsmarket.ncsoft.com/bns/favorite/insert.web"
		payload = {'item':item_num}
		data = ""

		try:
			async with aiohttp.ClientSession(cookies=cookie) as session:
				async with session.post(URL, data=payload) as resp:
					if resp.status == 200:
						data = await resp.text()
		except Exception as e:
			print("Failed to send POST request")
			print(e)
			await asyncio.sleep(10)
		if "success" in data:
			print("Successfully added favorite.")
			return True
		elif "already been added in data:":
			print("Already in favorites.")
			return True
		else:
			print("Failed to add favorite.")
			return False

	async def delete_favorite(self, item_num):
		URL = "http://na-bnsmarket.ncsoft.com/bns/favorite/delete.web"
		payload = {'item':item_num}
		data = ""

		try:
			async with aiohttp.ClientSession(cookies=cookie) as session:
				async with session.post(URL, data=payload) as resp:
					if resp.status == 200:
						data = await resp.text()
		except Exception as e:
			print("Failed to send POST request")
			print(e)
			await asyncio.sleep(10)
		if "success" in data:
			print("Successfully deleted favorite.")
			return True
		else:
			print("Failed to delete favorite.")
			return False

	async def sonny_emotes(self):
		server_id = "317150426103283712"
		sonny_id = "171018837142142977"
		reactions = ["sonnyThump:335165940469727242", "tsunny:336453298385059840"]


		server = self.bot.get_server(server_id)
		sonny = discord.utils.get(server.members, id = sonny_id)
		while True:
			message = await self.bot.wait_for_message(author = sonny)
			for reaction in reactions:
				await self.bot.add_reaction(message, reaction)


	async def on_ready(self):
		self.bot.loop.create_task(self.get_favorites_dict())
		self.bot.loop.create_task(self.scheduled_price_alerts())
		self.bot.loop.create_task(self.schedule_session_refresh())
		self.bot.loop.create_task(self.spreadsheet_task())
		self.bot.loop.create_task(self.sonny_emotes())
		self.bot.loop.create_task(self.schedule_dailies())

def setup(bot):
	bot.add_cog(tasks(bot))
