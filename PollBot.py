import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
from random import *

bot = commands.Bot(description="Indecisive's slave", command_prefix="!", pm_help = True)
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

	if len(ctx.message.content) > len("!ynpoll "):
		await bot.say("How long do you want the poll to be open? (in minutes) \nEnter 0 to to leave poll open indefinitely.")
		wait = await get_poll_time(ctx, max_wait_time)
		poll_message = await bot.say("= = =**POLL**= = =\n❓**:** " + ctx.message.content[len("!ynpoll "):])
		await bot.add_reaction(poll_message, '👍')
		await bot.add_reaction(poll_message, '👎')

		if wait.content == "0":
			await bot.say("*!closepoll to close the poll and post the results.\n!checkpoll to check current poll results*")
			message = await bot.wait_for_message(author = ctx.message.author)
			while message.content != "!closepoll":
				if message.content == "!checkpoll":
					await post_ynresults(ctx, poll_message, reactions)
					message = await bot.wait_for_message(author = ctx.message.author)
				else:
					message = await bot.wait_for_message(author = ctx.message.author)
		else:
			await asyncio.sleep(int(wait.content)*60) # TODO: CHANGE BACK TO MINUTES
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

	await bot.say("Give me the poll options. Enter x when you're done.")
	reply = await bot.wait_for_message(author = ctx.message.author)
	var = 0
	options = ""
	replies = []
	reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
	while reply.content != 'x' and var < max_options:
		replies.append(reply.content)
		options += reactions[var] + "  " + reply.content + "\n"
		var += 1
		reply = await bot.wait_for_message(author = ctx.message.author)
	if len(replies) <= 1:
		await bot.say("You can't have a poll with less than 2 options. Start over.")
		return

	await bot.say("How long do you want the poll to be open? (in minutes) \nEnter 0 to create an untimed poll.")
	wait = await get_poll_time(ctx, max_wait_time)

	poll_message = await bot.say("= = =**POLL**= = =\n❓**:** " + ctx.message.content[len("!poll "):] + "\n\n" + options)
	for reaction in reactions[:var]:
		await bot.add_reaction(poll_message, reaction)

	if wait.content == "0":
		await bot.say("*!closepoll to close the poll and post the results.\n!checkpoll to check current poll results*")
		message = await bot.wait_for_message(author = ctx.message.author)
		while message.content != "!closepoll":
			if message.content == "!checkpoll":
				await post_results(ctx, poll_message, replies, reactions)
				message = await bot.wait_for_message(author = ctx.message.author)
			else:
				message = await bot.wait_for_message(author = ctx.message.author)
	else:
		await asyncio.sleep(int(wait.content)*60) # TODO: CHANGE BACK TO MINUTES
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
			results += reactions[var1] + "  " + replies[var1] + " - **" + str(counts[var1]) + "** votes  :white_check_mark:" + "\n"
		elif counts[var1] == highest and counts[var1] == 1:
			results += reactions[var1] + "  " + replies[var1] + " - **" + str(counts[var1]) + "** vote  :white_check_mark:" + "\n"
		elif counts[var1] != highest and counts[var1] == 1:
			results += reactions[var1] + "  " + replies[var1] + " - **" + str(counts[var1]) + "** vote\n"
		else:
			results += reactions[var1] + "  " + replies[var1] + " - **" + str(counts[var1]) + "** votes\n"
		var1 += 1

	await bot.say("\n= = =**POLL RESULTS** created by <@" + str(ctx.message.author.id) + ">= = =\n❓**:** " + ctx.message.content[len("!poll "):] + "\n\n" + results)

async def get_poll_time(ctx, max_wait_time):
	""" Returns the message containing amount of time for poll to stay open """
	wait = await bot.wait_for_message(author = ctx.message.author)
	while not wait.content.isdigit() or int(wait.content) > max_wait_time:
		if not wait.content.isdigit():
			await bot.say("Numbers only.")
			wait = await bot.wait_for_message(author = ctx.message.author)
		elif int(wait.content) > max_wait_time:
			await bot.say("Keep it under a day.")
			wait = await bot.wait_for_message(author = ctx.message.author)
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
			await bot.say(":feelsThinking: You fucked it up. Try again. Maybe a little slower this time.")
	else:
		await bot.say(":feelsThinking: You fucked it up. Try again. Maybe a little slower this time.")


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
