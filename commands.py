import discord
import asyncio
from discord.ext import commands

from random import * # Used for roll, coin, and 8ball

import datetime #Used for post_dailies() function.
from datetime import date
from datetime import datetime
import calendar
import time

import aiohttp # used for
from re import finditer
import re
import copy

import tasks

class commands:
	""" All PlongBot's commands. """
	def __init__(self, bot):
		self.bot = bot

	# BOT COMMANDS START HERE #
	###########################
	@commands.command(aliases = ["hi", "hey"], pass_context = True)
	async def hello(self, ctx):
		embed = discord.Embed(color=0x4e5f94)
		embed.set_image(url = "https://i.imgur.com/6pyIpUT.png")
		embed.add_field(name = "Hi.", value = "Dis me.", inline=True)
		await self.bot.send_message(ctx.message.channel, embed=embed)

	@commands.command(aliases = ["3box", "dailychallenges", "DC"], pass_context = True)
	async def dailies(self, ctx):
		""" !dailies to receive list of today's Blade and Soul daily challenges."""
		dailies = [
		#Sunday
		"\nTower of Infinity\nOutlaw Island\nSogun's Lament\nNaryu Foundry\nGloomdross Incursion\nHollow's Heart\nNaryu Sanctum\nMidnight Skypetal Plains\n- - - -\nBeluga Lagoon\n",
		#Monday
		"\nMushin's Tower (15)\nCold Storage\nAvalanche Den\nStarstone Mines\nEbondrake Citadel\nDesolate Tomb\nEbondrake Lair\n- - - -\nArena Match\nBeluga Lagoon\n",
		#Tuesday
		"\nMushin's Tower (20)\nHeaven's Mandate\nSogun's Lament\nLair of the Frozen Fang\nNaryu Foundry\nHollow's Heart\nIrontech Forge\n- - - -\nArena Match\nWhirlwind Valley\n",
		#Wednesday
		"\nOutlaw Island\nTower of Infinity\nGloomdross Incursion\nThe Shattered Masts\nDesolate Tomb\nEbondrake Lair\nNaryu Sanctum\n- - - -\nArena Match\nBeluga Lagoon\n",
		#Thursday
		"\nMushin's Tower (15)\nCold Storage\nLair of the Frozen Fang\nStarstone Mines\nEbondrake Citadel\nIrontech Forge\nNaryu Foundry\n- - - -\nArena Match\nWhirlwind Valley\n",
		#Friday
		"\nMushin's Tower (20)\nHeaven's Mandate\nAvalanche Den\nHollow's Heart\nEbondrake Lair\nNaryu Sanctum\nMidnight Skypetal Plains\n- - - -\nArena Match\nBeluga Lagoon\n",
		#Saturday
		"\nTower of Infinity\nLair of the Frozen Fang\nThe Shattered Masts\nDesolate Tomb\nStarstone Mines\nIrontech Forge\nMidnight Skypetal Plains\n- - - -\nArena Match\nWhirlwind Valley\n"
		]

		await self.bot.say("📆 **" + str(datetime.now().month) + "/" + str(datetime.now().day) + " " + calendar.day_name[date.today().weekday()]+ "**\n" + dailies[int(datetime.today().strftime('%w'))])



	@commands.command(pass_context = True, hidden=True)
	async def fishbowl(self, ctx):
		"""!fishbowl to start a fishbowl. Outputs a list of all current fish and creates a poll for each fish."""
		server_id = "317150426103283712"
		fish_id = "358344958836736000"
		mod_id = "212404022697656321"
		reactions = ['🐠', '🐟', '👢', '🤷']

		server = self.bot.get_server(server_id)
		mod = discord.utils.get(server.members, id = mod_id)
		if ctx.message.author == mod:
			list_of_fish_msg = "Here's the current list of all fish:\n\n"
			comma_separated_fish = ""
			fish_list = []
			index = 0
			server = self.bot.get_server(server_id)
			for member in server.members:
				for role in member.roles:
					if role.id == fish_id:
						fish_list.append(member.name)
						list_of_fish_msg += str(index + 1) + ". " + member.name + "\n"
						comma_separated_fish += member.name + ", "
						index += 1
			comma_separated_fish = comma_separated_fish[:-2] # Removes ", " from last entry.
			await self.bot.send_message(mod, "You started a fishbowl. Here's the list of all fish:\n" + comma_separated_fish)
			await self.bot.say(list_of_fish_msg + "\n- - - -\nStarting the fishbowl! First up:\n\n")

			for fish in fish_list:
				poll_msg = await self.bot.say(fish + ' - Cast your vote:\n')
				for reaction in reactions:
					await self.bot.add_reaction(poll_msg, reaction)
				message = await self.bot.wait_for_message(timeout = 1440, author = mod, channel = ctx.message.channel) # 1440 is one day
				while True:
					if "done" in message.content.casefold():
						try:
							await self.bot.delete_message(message)
						except Exception as e:
							print("Problem deleteing message.")
							print(e)
						break
					else:
						message = await self.bot.wait_for_message(timeout = 1440, author = mod, channel = ctx.message.channel) # 1440 is one day

			await self.bot.say("<:feelsWow:370363135384879104> That concludes this fishbowl round.")
		else:
			await self.bot.say("You don't have permission to start a fishbowl.")

	@commands.command(pass_context = True)
	async def pricealert(self, ctx, *, content : str = None):
		""" !pricealert [item name], higher or lower than [price] to be notified when any listings are found. Checks every minute for 4 hours or until found. """
		alert_duration = 14400 #How long it will continue to price check their item. 4 hours by default.
		if content:
			try:
				item_name = content[:content.index(",")].strip()
				if not item_name:
					await self.bot.say("You need to specify what item you want me to look for.")
					return
			except:
				await self.bot.say("Ya dun goofed. You need to separate item name and price by a comma.")
				return -1
			price = content[content.find(",")+1:].replace(" ", "")
			alert_price = await tasks.tasks.get_price(tasks, price)
			if alert_price == "000000":
				await self.bot.say("You can't set your price alert at 0.")
				return
			data = await self.send_request(item_name)
			if "topPrice" in data:
				# Checking if they want to check above or below their set price.
				lower_than = True
				if "high" in price: # Notification for set price or higher
					lower_than = False
				elif "low" in price:
					pass
				else:
					await self.bot.say("Sorry, not sure what you mean. Please specify if you want me to look for listings higher or lower than your price.")
					return
				#formatting price for confirmation message
				gold = alert_price[:-4] + "<:gold_coin:402993867844222977> "
				silver = alert_price[-4:-2] + "<:silver_coin:402993901293666306> "
				copper = alert_price[-2:] + "<:copper_coin:402993919505203200>"
				if lower_than:
					await self.bot.say("Okay, I'll let you know if I find " + item_name + " listed for " + gold + silver + copper + " or lower in the next 4 hours.")
				elif not lower_than:
					await self.bot.say("Okay, I'll let you know if I find " + item_name + " listed for " + gold + silver + copper + " or higher in the next 4 hours.")
				search = re.search('"","item":"(.*)","amount', data)
				item_num = search.group(1)
				tasks.alert_dict.setdefault(item_num, []).append((ctx.message.author.id, alert_price, ctx.message.server, lower_than))
				await tasks.tasks.add_favorite(tasks, item_num)
				await asyncio.sleep(alert_duration)
				try:
					tasks.alert_dict[item_num].remove((ctx.message.author.id, alert_price, ctx.message.server, lower_than))
					server = ctx.message.server
					price_alert_user = discord.utils.get(server.members, id = ctx.message.author.id)
					if lower_than:
						await self.bot.send_message(price_alert_user, "Never managed to find a listing for " + item_name + " under " + gold + silver + copper)
					elif not lower_than:
						await self.bot.send_message(price_alert_user, "Never managed to find a listing for " + item_name + " above " + gold + silver + copper)
				except Exception as e:
					print("Already removed from dict")
					print(e)
				#Removes key from dict if user has no other pricealerts active.
				await tasks.validate_dict(item_num)
			else:
				await self.bot.say("Sorry, I couldn't find that item.")

		else:
			await self.bot.say("Ya dun goofed.")


	@commands.command(alises = ["profile"], pass_context = True, hidden=True)
	async def f2(self, ctx, *, username : str = None):
		"""!f2 [username] to receive picture of their f2 profile """
		if username:
			username = username.replace(" ", "+")
			await self.bot.say("🔗 http://na-bns.ncsoft.com/ingame/bs/character/profile?c=" + username)
		else:
			await self.bot.say("Maybe try entering an actual username.")


	@commands.command(alises = ["pricecheck", "checkprice"], pass_context = True)
	async def price(self, ctx, *, item_name : str = None):
		""" !price [item] to receive live market listings of that item. """
		if item_name:
			numbering = ["<:1_:403077593513066496>", "<:2_:403077593273991170>", "<:3_:403077593198362627>"]
			data = await self.send_request(item_name)
			found = False
			prices, found = await self.get_price_info(data, numbering)

			if prices:
				image_url = re.search('iconImg" src="(.*)" alt="', data)
				embed = discord.Embed(color=0x72eab0)
				embed.set_thumbnail(url=image_url.group(1))
				embed.add_field(name="Listings for " + ctx.message.content[len("!price "):], value=prices, inline=True)
				await self.bot.send_message(ctx.message.channel, embed=embed)
			elif found == False and "No search results found for" in data:
				print("No search results found for " + item_name) # change to found for "item"
				await self.bot.say("No search results found for **" + item_name + "**.")
			elif found == False and "We apologize for the inconvenience. Please try again later." in data:
				print("Session ID expired.")
				await self.bot.say("Can't search marketplace at the moment.")
			else:
				print("Error: no internet?")
		else:
			await self.bot.say("Ya dun goofed.")

	async def send_request(self, item_name):
		item_name_url = item_name.strip().replace(" ", "+")
		URL = "http://na-bnsmarket.ncsoft.com/bns/bidder/search.web?ct=&exact=1&grade=&level=&prevq=&q=" + item_name_url + "&sort=&stepper=&type="

		try:
			async with aiohttp.ClientSession(cookies=tasks.cookie) as session:
				async with session.get(URL) as resp:
					if resp.status == 200:
						data = await resp.text()
		except Exception as e:
			print("Failed send price request.")
			print(e)
			return ""
		return data

	async def get_price_info(self, data, numbering):
		found = False
		prices = ""
		if "topPrice" in data:
			found = True
			indexes = []
			for match in finditer('","unitBid"', data):
				indexes.append(match.span()[0])

			index = 0
			for match in finditer('","topPrice"', data):
				if index > 2:
					break
				pos_end = match.span()[0]
				pos_start = pos_end - 1
				while data[pos_start].isdigit():
					pos_start -= 1
				price = data[pos_start+1:pos_end]
				coppers = price[-2:] + "<:copper_coin:402993919505203200>"
				silvers = price[-4:-2] + "<:silver_coin:402993901293666306> "
				gold = price[:-4] + "<:gold_coin:402993867844222977> "
				if gold[:2] == "00":
					gold = ""
				if silvers[:2] == "00":
					silvers = ""
				if coppers[:2] == "00":
					coppers = ""

				pos_end = indexes[index]
				pos_start = pos_end - 1
				while data[pos_start].isdigit():
					pos_start -= 1
				amount = data[pos_start + 1: pos_end]

				u_price = str(int(price)//int(amount))
				u_coppers = u_price[-2:] + "<:copper_coin:402993919505203200>"
				u_silvers = u_price[-4:-2] + "<:silver_coin:402993901293666306> "
				u_gold = u_price[:-4] + "<:gold_coin:402993867844222977> "
				#Removes the coin emojis if 0 of any coin type
				if u_gold[:2] == "<:" or u_gold[:2] == "00":
					u_gold = ""
				if u_silvers[:2] == "<:" or u_silvers[:2] == "00":
					u_silvers = ""
				if u_coppers[:2] == "<:" or u_coppers[:2] == "00":
					u_coppers = ""
				prices += numbering[index] + "  **" + u_gold + u_silvers + u_coppers + "**  Qty: **" + amount + "**\n"
				index += 1

		return prices, found


	@commands.command(alises = ["ynpoll", "yesnopoll", "nypoll", "noyespoll"], pass_context = True)
	async def ynpoll(self, ctx, *, question : str = None):
		"""!ynpoll [poll question] to create a simple yes/no poll"""
		max_wait_time = 1440
		reactions = ['👍', '👎']

		if question:
			prompt1 = await self.bot.say("How long do you want the poll to be open? (in minutes) \nEnter 0 to to leave poll open indefinitely.")
			wait = await self.get_poll_time(ctx, max_wait_time)
			try:
				await self.bot.delete_message(prompt1)
				await self.bot.delete_message(ctx.message)
			except Exception as e:
				print("Problem deleteing message.")
				print(e)

			if wait.content == "0":
				poll_message = await self.bot.say("= = =**POLL**= = =\n❓**:** " + question
				 	+ "\n\n*!closepoll to close the poll and post the results.\n!checkpoll to check current poll results*")
				await self.bot.add_reaction(poll_message, '👍')
				await self.bot.add_reaction(poll_message, '👎')

				message = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
				while message is not None and message.content != "!closepoll":
					if message.content == "!checkpoll":
						try:
							await self.bot.delete_message(message)
						except Exception as e:
							print("Problem deleteing message.")
							print(e)
						await self.post_ynresults(ctx, poll_message, reactions, question)
						message = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
					else:
						message = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
				try:
					await self.bot.delete_message(message)
				except Exception as e:
					print("Problem deleteing message.")
					print(e)
			else:
				poll_message = await self.bot.say("= = =**POLL**= = =\n❓**:** " + question)
				await self.bot.add_reaction(poll_message, '👍')
				await self.bot.add_reaction(poll_message, '👎')
				await asyncio.sleep(int(wait.content)*60)
			await self.post_ynresults(ctx, poll_message, reactions, question)
		else:
			await self.bot.say("Give me the poll question together with the !ynpoll command.")

	async def post_ynresults(self, ctx, poll_message, reactions, question):
		""" Posts poll results. Requires context, the poll_message """
		cache_msg = discord.utils.get(self.bot.messages, id = poll_message.id)
		max_options = 2 # Only thumbs up/down
		counts = []
		var1 = 0
		for reaction in cache_msg.reactions[:max_options]:
			reactors = await self.bot.get_reaction_users(reaction)
			counts.append(-1) #-1 to exclude bot's reaction vote
			for reactor in reactors:
				counts[var1] += 1
			var1 += 1

		highest = 0
		for count in counts:
			if count > highest:
				highest = count

		var1 = 0
		results = ""
		while var1 < max_options:
			if counts[var1] == highest and counts[var1] > 1:
				results += reactions[var1] + "  "  + " - **" + str(counts[var1]) + "** votes  :white_check_mark:" + "\n\n"
			elif counts[var1] == highest and counts[var1] == 1:
				results += reactions[var1] + "  "  + " - **" + str(counts[var1]) + "** vote  :white_check_mark:" + "\n\n"
			elif counts[var1] != highest and counts[var1] == 1:
				results += reactions[var1] + "  " + " - **" + str(counts[var1]) + "** vote\n\n"
			else:
				results += reactions[var1] + "  " + " - **" + str(counts[var1]) + "** votes\n\n"
			var1 += 1

		await self.bot.say("\n= = =**POLL RESULTS** created by <@" + str(ctx.message.author.id) + ">= = =\n❓**:** " + question + "\n\n" + results)

	@commands.command(pass_context = True)
	async def poll(self, ctx, *, question : str = None):
		"""!poll [poll question] to create poll with your specified options"""
		if question:
			max_options = 10
			max_wait_time = 1440 #Max time for bot to post results. 1440 is 1 day.

			prompt1 = await self.bot.say("Give me the poll options. Enter x when you're done.")
			reply = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
			number_of_options = 0
			options = ""
			replies = []
			reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
			while reply.content != 'x' and number_of_options < max_options:
				replies.append(reply)
				options += reactions[number_of_options] + "  " + reply.content + "\n"
				number_of_options += 1
				reply = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
			if number_of_options <= 1:
				await self.bot.say("<:feelsSpecial:356858646812164099> You can't have a poll with less than 2 options. Start over.")
				return

			prompt2 = await self.bot.say("How long do you want the poll to be open? (in minutes) \nEnter 0 to create an untimed poll.")
			wait = await self.get_poll_time(ctx, max_wait_time)


			if wait.content == "0": #Untimed poll
				poll_message = await self.bot.say("= = =**POLL**= = =\n❓**:** " + question + "\n\n" + options
					+ "\n\n*!closepoll to close the poll and post the results.\n!checkpoll to check current poll results*")
				for reaction in reactions[:number_of_options]:
					await self.bot.add_reaction(poll_message, reaction)
				await self.cleanup(reply, replies, ctx, prompt1, prompt2)
				message = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
				while message is not None and message.content != "!closepoll":
					if message.content == "!checkpoll":
						try:
							await self.bot.delete_message(message)
						except Exception as e:
							print("Problem deleteing message.")
							print(e)
						await self.post_results(ctx, poll_message, replies, reactions, number_of_options, question)
						message = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
					else:
						message = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
				try:
					await self.bot.delete_message(message)
				except Exception as e:
					print("Problem deleteing message.")
					print(e)
			else: # Timed poll
				poll_message = await self.bot.say("= = =**POLL**= = =\n❓**:** " + question + "\n\n" + options)
				for reaction in reactions[:number_of_options]:
					await self.bot.add_reaction(poll_message, reaction)
				await self.cleanup(reply, replies, ctx, prompt1, prompt2)
				await asyncio.sleep(int(wait.content)*60)
			await self.post_results(ctx, poll_message, replies, reactions, number_of_options, question)
		else:
			await self.bot.say("Give me the poll question together with the !poll command.")

	async def cleanup(self, reply, replies, ctx, prompt1, prompt2):
		try:
			await self.bot.delete_message(reply)
			for reply in replies:
				await self.bot.delete_message(reply)
			await self.bot.delete_message(ctx.message)
			await self.bot.delete_message(prompt1)
			await self.bot.delete_message(prompt2)
		except Exception as e:
			print("Problem deleting some posts, could have been deleted already.")
			print(e)

	async def post_results(self, ctx, poll_message, replies, reactions, number_of_options, question):
		""" Posts poll results. Requires context, the poll_message, and the options to that poll """
		cache_msg = discord.utils.get(self.bot.messages, id = poll_message.id)
		counts = []
		var1 = 0
		for reaction in cache_msg.reactions[:number_of_options]:
			reactors = await self.bot.get_reaction_users(reaction)
			counts.append(-1) #-1 to exclude bot's reaction vote
			for reactor in reactors:
				counts[var1] += 1
			var1 += 1

		highest = 0
		for count in counts:
			if count > highest:
				highest = count

		var1 = 0
		results = ""
		while var1 < len(counts):
			if counts[var1] == highest and counts[var1] > 1:
				results += reactions[var1] + "  " + replies[var1].content + " - **" + str(counts[var1]) + "** votes  :white_check_mark:" + "\n"
			elif counts[var1] == highest and counts[var1] == 1:
				results += reactions[var1] + "  " + replies[var1].content + " - **" + str(counts[var1]) + "** vote  :white_check_mark:" + "\n"
			elif counts[var1] != highest and counts[var1] == 1:
				results += reactions[var1] + "  " + replies[var1].content + " - **" + str(counts[var1]) + "** vote\n"
			else:
				results += reactions[var1] + "  " + replies[var1].content + " - **" + str(counts[var1]) + "** votes\n"
			var1 += 1

		await self.bot.say("\n= = =**POLL RESULTS** created by <@" + str(ctx.message.author.id) + ">= = =\n❓**:** " + question + "\n\n" + results)

	async def get_poll_time(self, ctx, max_wait_time):
		""" Returns the message containing amount of time for poll to stay open """
		wait = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
		while not wait.content.isdigit() or int(wait.content) > max_wait_time:
			if not wait.content.isdigit():
				ans = await self.bot.say("Numbers only.")
				try:
					await self.bot.delete_message(wait)
				except Exception as e:
					print("Problem deleteing message.")
					print(e)
				wait = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
				try:
					await self.bot.delete_message(ans)
				except Exception as e:
					print("Problem deleteing message.")
					print(e)
			elif int(wait.content) > max_wait_time:
				ans = await self.bot.say("<:feelsRage:329995595857264640> Keep it under a day.")
				try:
					await self.bot.delete_message(wait)
				except Exception as e:
					print("Problem deleteing message.")
					print(e)
				wait = await self.bot.wait_for_message(timeout = max_wait_time, author = ctx.message.author, channel=ctx.message.channel)
				try:
					await self.bot.delete_message(ans)
				except Exception as e:
					print("Problem deleteing message.")
					print(e)
		try:
			await self.bot.delete_message(wait)
		except Exception as e:
			print("Problem deleteing message.")
			print(e)
		return wait


	@commands.command(pass_context = True)
	async def roll(self, ctx, *, bounds : str = None):
		"""!roll [min optional]-[max] to return a random roll"""
		if bounds and "-" in ctx.message.content:
			lower_bound = ""
			upper_bound = ""
			l_bound = True
			for char in bounds:
				if char.isdigit() and l_bound:
					lower_bound += char
				elif char == "-" and lower_bound != "":
					l_bound = False
				elif char.isdigit() and not l_bound:
					upper_bound += char
				else:
					await self.bot.say("<:feelsThinking:356858638318567434> You fucked it up. Try again. Maybe a little slower this time.")
					return
			if int(lower_bound) > int(upper_bound):
				await self.bot.say("The lower number goes first. <:feelsSpecial:356858646812164099>")
			result = str(randint(int(lower_bound), int(upper_bound)))
			if result == "1":
				await self.bot.say("🎲 You rolled **" + result + "**. Nice roll, nerd.")
			elif result == "69":
				await self.bot.say("🎲 You rolled **" + result + "**. <:feelsReceive:388769216343310339>")
			else:
				await self.bot.say("🎲 You rolled **" + result + "**.")
		elif bounds:
			upper_bound = ctx.message.content[len("!roll "):]
			lower_bound = "1"
			if upper_bound.isdigit():
				result = str(randint(int(lower_bound), int(upper_bound)))
				if result == "1":
					await self.bot.say("🎲 You rolled **" + result + "**. Nice roll, nerd.")
				elif result == "69":
					await self.bot.say("🎲 You rolled **" + result + "**. <:feelsReceive:388769216343310339>")
				else:
					await self.bot.say("🎲 You rolled **" + result + "**.")
			else:
				await self.bot.say("<:feelsThinking:356858638318567434> You fucked it up. Try again. Maybe a little slower this time.")
		else:
			await self.bot.say("<:feelsThinking:356858638318567434> You fucked it up. Try again. Maybe a little slower this time.")


	@commands.command(aliases = ["coin", "coinflip", "flip"])
	async def flipcoin(self):
		"""!coin to flip a coin"""
		result = randint(1, 2)
		if result == 1:
			await self.bot.say("You got **heads**.")
		else:
			await self.bot.say("You got **tails**.")


	@commands.command(aliases = ["8ball", "eightball"], pass_context = True)
	async def magic8ball(self, ctx):
		"""!8ball [question] to return a magic 8ball answer"""
		results = [
		"Definitely. It is as certain as you dying alone.",
		"Yes.",
		"Highly likely.",
		"Without a doubt!",
		"Signs point to yes.",
		"Probably. What the fuck do you think?",
		"Looking good :thumbsup:",
		"Obviously, the answer is yes.",
		"Do you really need me to spell it out? Yes.",
		"Almost certainly.",

		"The only thing less likely is your parents loving you.",
		"No, and you're retarded for asking.",
		"No.",
		"Not looking good. But you're used to that aren't you?",
		"Not today. Well... not ever.",

		"Maybe. Maybe one day you'll accomplish something. Who knows?",
		"Indeterminate.",
		"Not sure.",
		"How would I know?",
		"Difficult to say."
		]

		answer = randint(0, len(results)-1)
		if len(ctx.message.content) > len("!8ball "):
			await self.bot.say("🎱 " + results[answer])
		else:
			await self.bot.say("Try asking an actual question, dumbass. <:feelsSpecial:356858646812164099>")



	# def get_item_index(): #retired item lookup.
	# 	credentials = get_credentials()
	# 	service = discovery.build('sheets', 'v4', credentials=credentials)
	# 	spreadsheet_id = '1NZM-UwyUOwUe4iqByAmyNPz6bWVZFianlaj4EmsrXMw'
	# 	range_ = 'C2:C'
	# 	value_render_option = 'FORMATTED_VALUE'
	# 	date_time_render_option = 'SERIAL_NUMBER'
	#
	# 	while True:
	# 		try:
	# 			request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
	# 			item_names = request.execute()
	# 			break
	# 		except:
	# 			print("Requesting item_names from database failed.")
	# 	range_ = 'F2:F'
	#
	# 	while True:
	# 		try:
	# 			request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
	# 			item_ids = request.execute()
	# 			break
	# 		except:
	# 			print("Requesting item_ids from database failed.")
	#
	# 	item_dict = {}
	# 	index = 0
	# 	try:
	# 		for item in item_names['values']:
	# 			item_dict[str(item)[2:-2]] = str(item_ids['values'][index])[2:-2] # [2:-2] removes brackets
	# 			index += 1
	# 	except:
	# 		print("Item index list is empty or problem grabbing values")
	#
	# 	return item_dict

def setup(bot):
	bot.add_cog(commands(bot))
