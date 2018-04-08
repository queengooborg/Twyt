from discordbot import DiscordBot
import asyncio

bot = DiscordBot()

bot.load_cogs()

bot.run()