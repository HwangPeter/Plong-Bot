from discord.ext import commands
import discord
import platform

# this specifies what extensions to load when the bot starts up
startup_extensions = ["tasks", "commands"]

bot = commands.Bot(description="Helpful Plong. For personal background tasks and more.", command_prefix="!", pm_help = True)

@bot.event
async def on_ready():
	print('Logged in as '+bot.user.name+' (ID:'+bot.user.id+') | Connected to '+str(len(bot.servers))+' servers | Connected to '+str(len(set(bot.get_all_members())))+' users')
	print('--------')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
	print('--------')
	print('Use this link to invite {}:'.format(bot.user.name))
	print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(bot.user.id))
	print('--------')
	await bot.change_presence(game=discord.Game(name='with my life'))



if __name__ == "__main__":
	for extension in startup_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			exc = '{}: {}'.format(type(e).__name__, e)
			print('Failed to load extension {}\n{}'.format(extension, exc))

	bot.run('token')
