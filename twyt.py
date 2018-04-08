# -*- encoding: utf8 -*-

from bot import DiscordBot
import asyncio

bot = DiscordBot()

bot.load_cogs()

bot.run()