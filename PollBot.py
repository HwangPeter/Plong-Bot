#!/usr/bin/python3
import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
from random import *

from pprint import pprint
from googleapiclient import discovery
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

bot = commands.Bot(description="Indecisive's slave", command_prefix="!", pm_help = True)

class member(object):
	ign = ""
	discord_id = ""
	def __init__(self, ign, discord_id):
		self.ign = ign
		self.discord_id = discord_id

def make_member(ign, discord_id = None):
	if discord_id is None:
		Member = member(ign, "")
	else:
		Member = member(ign, discord_id)
	return Member

def get_credentials():
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


async def spreadsheet_task():
	await bot.wait_until_ready()
	Indecisive_server_id = "317150426103283712"
	VT_role_id = "381753872206790659"
	BTA_role_id = "395774727257325568"
	BTB_role_id = "395784674674475009"
	update_date = None


	while(True):
		credentials = get_credentials()

		service = discovery.build('sheets', 'v4', credentials=credentials)

		# The ID of the spreadsheet to retrieve data from.
		spreadsheet_id = '1O5naOP-Ir--2GjgNsWmAGv-lnDkOz00f5TdHdKsE7_Y'

		# The A1 notation of the values to retrieve.
		range_ = ''

		# How values should be represented in the output.
		# The default render option is ValueRenderOption.FORMATTED_VALUE.
		value_render_option = 'FORMATTED_VALUE'

		# How dates, times, and durations should be represented in the output.
		# This is ignored if value_render_option is
		# FORMATTED_VALUE.
		# The default dateTime render option is [DateTimeRenderOption.SERIAL_NUMBER].
		date_time_render_option = 'SERIAL_NUMBER'


		#Checking last edit date
		range_ = 'BT Weekends!B2'
		request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
		edit_date = request.execute()
		if update_date == edit_date: # Roster and roles are up to date.
			pass
		else: # Roster has changed since last update.
			update_date = edit_date
			#Creating roster list
			range_ = 'Clan Roster!D4:D'
			request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
			response_ign = request.execute()
			range_ = 'Clan Roster!I4:I'
			request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
			response_id = request.execute()
			roster = await create_roster(response_ign, response_id, Indecisive_server_id)


			#BTA / Saturday Raid
			range_ = 'BT Weekends!E7:E12' # Party 1
			request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
			response_BT1 = request.execute()
			server = bot.get_server(Indecisive_server_id)
			role = discord.utils.get(server.roles, id = BTA_role_id)
			await remove_role(roster, server, BTA_role_id)
			await add_role(roster, server, BTA_role_id, role, response_BT1)

			range_ = 'BT Weekends!E14:E19' # Party 2
			request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
			response_BT2 = request.execute()
			await add_role(roster, server, BTA_role_id, role, response_BT2)

			#BTB / Sunday Raid
			range_ = 'BT Weekends!O7:O12' # Party 1
			request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
			response_BT1 = request.execute()
			role = discord.utils.get(server.roles, id = BTB_role_id)
			await remove_role(roster, server, BTB_role_id)
			await add_role(roster, server, BTB_role_id, role, response_BT1)

			range_ = 'BT Weekends!O14:O19' # Party 2
			request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
			response_BT2 = request.execute()
			await add_role(roster, server, BTB_role_id, role, response_BT2)

		await asyncio.sleep(20) #Waits 20 seconds before checking for roster updates

async def create_roster(response_ign, response_id, server_id):
	roster = []
	index = 0
	for entry in response_ign['values']:
		if index < len(response_id['values']) and entry and response_id['values'][index]:
			member = make_member(str(entry)[2:-2], str(response_id['values'][index])[2:-2]) #[2:-2] removes brackets and quotes from each entry
			roster.append(member)
			index += 1
		elif index < len(response_id['values']) and entry and not response_id['values'][index]:
			member = make_member(str(entry)[2:-2])
			roster.append(member)
			server = bot.get_server(server_id)
			schlong = discord.utils.get(server.members, id = '217513859412525057')
			await bot.send_message(schlong, "Missing discord ID for " + str(entry))
			index += 1
		elif index >= len(response_id['values']):
			member = make_member(str(entry)[2:-2])
			roster.append(member)
			server = bot.get_server(server_id)
			schlong = discord.utils.get(server.members, id = '217513859412525057')
			await bot.send_message(schlong, "Missing discord ID for " + str(entry))
			index += 1
		else:
			index += 1
	return roster

async def remove_role(roster, server, raid_role_id):
	""" Removes the role passed for all users in roster """
	for guildie in roster:
		if guildie.discord_id:
			raider = discord.utils.get(server.members, id = guildie.discord_id)
			if raider: # Checks if this user was found in the server.
				for roles in raider.roles:
					if raid_role_id == roles.id:
						await bot.remove_roles(raider, roles)
			else:
				schlong = discord.utils.get(server.members, id = '217513859412525057')
				await bot.send_message(schlong, "Couldn't find " + guildie.ign + " in server. Could have left guild.")

async def add_role(roster, server, raid_role_id, role, response_raid):
	try: # Checks for empty raid roster.
		for BT in response_raid['values']:
			member = make_member(str(BT)[2:-2]) #[2:-2] removes brackets and quotes from each entry
			found = False
			for guildie in roster:
				if BT and member.ign == guildie.ign and guildie.discord_id:
					raider = discord.utils.get(server.members, id = guildie.discord_id)
					await bot.add_roles(raider, role)
					found = True
					break
			if found == False:
				schlong = discord.utils.get(server.members, id = '217513859412525057')
				await bot.send_message(schlong, "On the roster, but couldn't add role for " + str(BT))
	except:
		pass

@bot.event
async def on_ready():
	print('Logged in as '+bot.user.name+' (ID:'+bot.user.id+') | Connected to '+str(len(bot.servers))+' servers | Connected to '+str(len(set(bot.get_all_members())))+' users')
	print('--------')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
	print('--------')
	print('Use this link to invite {}:'.format(bot.user.name))
	print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(bot.user.id))
	print('--------')


@bot.command(name = "ynpoll", pass_context = True)
async def ynpoll(ctx):
	"""!ynpoll [poll question] to create a simple yes/no poll"""
	max_wait_time = 1440
	reactions = ['👍', '👎']
	# await bot.delete_message(ctx.message)

	if len(ctx.message.content) > len("!ynpoll "):
		prompt1 = await bot.say("How long do you want the poll to be open? (in minutes) \nEnter 0 to to leave poll open indefinitely.")
		wait = await get_poll_time(ctx, max_wait_time)
		poll_message = await bot.say("= = =**POLL**= = =\n❓**:** " + ctx.message.content[len("!ynpoll "):])
		await bot.add_reaction(poll_message, '👍')
		await bot.add_reaction(poll_message, '👎')
		await bot.delete_message(prompt1)
		await bot.delete_message(ctx.message)

		if wait.content == "0":
			await bot.say("*!closepoll to close the poll and post the results.\n!checkpoll to check current poll results*")
			message = await bot.wait_for_message(author = ctx.message.author)
			while message.content != "!closepoll":
				if message.content == "!checkpoll":
					await bot.delete_message(message)
					await post_ynresults(ctx, poll_message, reactions)
					message = await bot.wait_for_message(author = ctx.message.author)
				else:
					message = await bot.wait_for_message(author = ctx.message.author)
			await bot.delete_message(message)
		else:
			await asyncio.sleep(int(wait.content)*60)
		await post_ynresults(ctx, poll_message, reactions)
	else:
		await bot.say("Give me the poll question together with the !ynpoll command.")

async def post_ynresults(ctx, poll_message, reactions):
	""" Posts poll results. Requires context, the poll_message """
	cache_msg = discord.utils.get(bot.messages, id = poll_message.id)
	counts = []
	var1 = 0
	for reaction in cache_msg.reactions:
		reactors = await bot.get_reaction_users(reaction)
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
			results += reactions[var1] + "  "  + " - **" + str(counts[var1]) + "** votes  :white_check_mark:" + "\n\n"
		elif counts[var1] == highest and counts[var1] == 1:
			results += reactions[var1] + "  "  + " - **" + str(counts[var1]) + "** vote  :white_check_mark:" + "\n\n"
		elif counts[var1] != highest and counts[var1] == 1:
			results += reactions[var1] + "  " + " - **" + str(counts[var1]) + "** vote\n\n"
		else:
			results += reactions[var1] + "  " + " - **" + str(counts[var1]) + "** votes\n\n"
		var1 += 1

	await bot.say("\n= = =**POLL RESULTS** created by <@" + str(ctx.message.author.id) + ">= = =\n❓**:** " + ctx.message.content[len("!ynpoll "):] + "\n\n" + results)

@bot.command(name = "poll", pass_context = True)
async def poll(ctx):
	"""!poll [poll question] to create poll with your specified options"""
	max_options = 10
	max_wait_time = 1440 #Max time for bot to post results. 1440 is 1 day.

	prompt1 = await bot.say("Give me the poll options.")
	reply = await bot.wait_for_message(author = ctx.message.author)
	var = 0
	options = ""
	replies = []
	reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
	while reply.content != 'x' and var < max_options:
		replies.append(reply)
		options += reactions[var] + "  " + reply.content + "\n"
		var += 1
		reply = await bot.wait_for_message(author = ctx.message.author)
	if len(replies) <= 1:
		await bot.say("You can't have a poll with less than 2 options. Start over.")
		return

	prompt2 = await bot.say("How long do you want the poll to be open? (in minutes) \nEnter 0 to create an untimed poll.")
	wait = await get_poll_time(ctx, max_wait_time)

	poll_message = await bot.say("= = =**POLL**= = =\n❓**:** " + ctx.message.content[len("!poll "):] + "\n\n" + options)
	for reaction in reactions[:var]:
		await bot.add_reaction(poll_message, reaction)
	await bot.delete_message(reply)
	for reply in replies:
		await bot.delete_message(reply)
	await bot.delete_message(ctx.message)
	await bot.delete_message(prompt1)
	await bot.delete_message(prompt2)

	if wait.content == "0":
		await bot.say("*!closepoll to close the poll and post the results.\n!checkpoll to check current poll results*")
		message = await bot.wait_for_message(author = ctx.message.author)
		while message.content != "!closepoll":
			if message.content == "!checkpoll":
				await bot.delete_message(message)
				await post_results(ctx, poll_message, replies, reactions)
				message = await bot.wait_for_message(author = ctx.message.author)
			else:
				message = await bot.wait_for_message(author = ctx.message.author)
		await bot.delete_message(message)
	else:
		await asyncio.sleep(int(wait.content)*60) #
	await post_results(ctx, poll_message, replies, reactions)


async def post_results(ctx, poll_message, replies, reactions):
	""" Posts poll results. Requires context, the poll_message, and the options to that poll """
	cache_msg = discord.utils.get(bot.messages, id = poll_message.id)
	counts = []
	var1 = 0
	for reaction in cache_msg.reactions:
		reactors = await bot.get_reaction_users(reaction)
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

	await bot.say("\n= = =**POLL RESULTS** created by <@" + str(ctx.message.author.id) + ">= = =\n❓**:** " + ctx.message.content[len("!poll "):] + "\n\n" + results)

async def get_poll_time(ctx, max_wait_time):
	""" Returns the message containing amount of time for poll to stay open """
	wait = await bot.wait_for_message(author = ctx.message.author)
	while not wait.content.isdigit() or int(wait.content) > max_wait_time:
		if not wait.content.isdigit():
			ans = await bot.say("Numbers only.")
			await bot.delete_message(wait)
			wait = await bot.wait_for_message(author = ctx.message.author)
			await bot.delete_message(ans)
		elif int(wait.content) > max_wait_time:
			ans = await bot.say("Keep it under a day.")
			await bot.delete_message(wait)
			wait = await bot.wait_for_message(author = ctx.message.author)
			await bot.delete_message(ans)
	await bot.delete_message(wait)
	return wait



@bot.command(name = "roll", pass_context = True)
async def roll(ctx):
	"""!roll [min optional]-[max] to return a random roll"""
	if len(ctx.message.content) > len("!roll ") and "-" in ctx.message.content:
		bounds = ctx.message.content[len("!roll "):]
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
				await bot.say("You did it wrong, try again.")
				return
		if int(lower_bound) > int(upper_bound):
			await bot.say("The lower number goes first.")
		result = str(randint(int(lower_bound), int(upper_bound)))
		await bot.say("🎲 You rolled **" + result + "**.")
	elif len(ctx.message.content) > len("!roll "):
		upper_bound = ctx.message.content[len("!roll "):]
		lower_bound = "1"
		if upper_bound.isdigit():
			result = str(randint(int(lower_bound), int(upper_bound)))
			await bot.say("🎲 You rolled **" + result + "**.")
		else:
			await bot.say("Try again.")
	else:
		await bot.say("Try again.")


@bot.command(name = "coin", pass_context = True)
async def flipcoin(ctx):
	"""!coin to flip a coin"""
	result = randint(1, 2)
	if result == 1:
		await bot.say("You got **heads**.")
	else:
		await bot.say("You got **tails**.")


@bot.command(name = "8ball", pass_context = True)
async def magic8ball(ctx):
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

	"No.",
	"Not looking good. But you're used to that aren't you?",
	"Not today. Well... not ever.",
	"Outlook not so good",

	"Reply hazy try again.",
	"Ask again later",
	"Better not tell you now",
	"Cannot predict now" ]
	answer = randint(0, len(results)-1)
	if len(ctx.message.content) > len("!8ball "):
		await bot.say("🎱 " + results[answer])
	else:
		await bot.say("Try asking an actual question.")



bot.run('Token-here')
