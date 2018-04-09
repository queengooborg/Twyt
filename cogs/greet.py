# -*- encoding: utf8 -*-

from discord.ext import commands

from bot_utils import config, checks
from bot_utils.paginator import Pages

class Greet:
	"""Greets the user."""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def greet(ctx):
		"""Greets the user.

		This is additional help text that will only show up if
		help is called on the command itself as opposed to the
		normal short help which shows up in the main help.
		"""
		await self.bot.send_message(ctx.message.channel, "Hi there, {user}, how are you?".format(user=ctx.message.author.mention))

def setup(bot):
	bot.add_cog(Greet(bot))
