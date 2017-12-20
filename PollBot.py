import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform

bot = commands.Bot(description="PollBot", command_prefix="!", pm_help = True)
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
	""" Creates a poll by adding thumbs up and thumbs down emojis added as reactions """
	poll_message = await bot.say(ctx.message.content[len("!ynpoll "):])
	await bot.add_reaction(poll_message, '👍')
	await bot.add_reaction(poll_message, '👎')

@bot.command(name = "poll", pass_context = True)
async def poll(ctx):
	""" Creates a poll with up to 10 options. Adds as many reactions as there are options"""
	await bot.say("Give me the poll options. Enter x when finished.")
	reply = await bot.wait_for_message(author = ctx.message.author)
	var = 0
	options = ""
	while reply.content != 'x' and var < 10:
		var += 1
		options += str(var) + ". " + reply.content + "\n"
		reply = await bot.wait_for_message(author = ctx.message.author)
	poll_message = await bot.say(ctx.message.content[len("!poll "):] + "\n\n" + options)
	reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
	for reaction in reactions[:var]:
		await bot.add_reaction(poll_message, reaction)




bot.run('Token_here')
