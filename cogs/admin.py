# -*- encoding: utf8 -*-

import argparse
import asyncio
from collections import Counter, defaultdict

import copy
import discord
from discord.ext import commands

import embeds
from bot_utils import checks
from bot_utils import config
from colors import Colors


class Arguments(argparse.ArgumentParser):
	def error(self, message):
		raise RuntimeError(message)


class Admin:
	"""Bot administration commands."""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True, no_pm=True)
	@checks.mod_or_permissions(manage_messages=True)
	async def cleanup(self, ctx, search : int = 100):
		"""Cleans up the bot's messages from the channel.

		If a search number is specified, it searches that many messages to delete.
		If the bot has Manage Messages permissions, then it will try to delete
		messages that look like they invoked the bot as well.

		After the cleanup is completed, the bot will send you a message with
		which people got their messages deleted and their count. This is useful
		to see which users are spammers.

		To use this command you must have Manage Messages permission or have the
		Bot Mod role.
		"""

		spammers = Counter()
		channel = ctx.message.channel
		prefixes = self.bot.command_prefix
		if callable(prefixes):
			prefixes = prefixes(self.bot, ctx.message)

		def is_possible_command_invoke(entry):
			valid_call = any(entry.content.startswith(prefix) for prefix in prefixes)
			return valid_call and not entry.content[1:2].isspace()

		can_delete = channel.permissions_for(channel.server.me).manage_messages

		if not can_delete:
			api_calls = 0
			async for entry in self.bot.logs_from(channel, limit=search, before=ctx.message):
				if api_calls and api_calls % 5 == 0:
					await asyncio.sleep(1.1)

				if entry.author == self.bot.user:
					await self.bot.delete_message(entry)
					spammers['Bot'] += 1
					api_calls += 1

				if is_possible_command_invoke(entry):
					try:
						await self.bot.delete_message(entry)
					except discord.Forbidden:
						continue
					else:
						spammers[entry.author.display_name] += 1
						api_calls += 1
		else:
			predicate = lambda m: m.author == self.bot.user or is_possible_command_invoke(m)
			deleted = await self.bot.purge_from(channel, limit=search, before=ctx.message, check=predicate)
			spammers = Counter(m.author.display_name for m in deleted)

		deleted = sum(spammers.values())
		messages = ['%s %s removed.' % (deleted, 'message was' if deleted == 1 else 'messages were')]
		if deleted:
			messages.append('')
			spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
			messages.extend(map(lambda t: '**%s**: %d' %(t[0], t[1]), spammers))

		await self.bot.delete_message(ctx.message)

		msg = await self.bot.responses.basic(title="Removed Messages:", message='\n'.join(messages))
		await asyncio.sleep(10)
		await self.bot.delete_message(msg)

	@commands.command(pass_context=True, no_pm=True)
	@checks.mod_or_permissions(manage_messages=True)
	async def clear(self, ctx, search : int = 100):
		"""Clears all messages from the chat.

		If a search number is specified, it searches that many messages to delete.
		After the cleanup is completed, the bot will send you a message with
		which people got their messages deleted and their count. This is useful
		to see which users are spammers.

		To use this command you must have Manage Messages permission or have the
		Bot Mod role.
		"""

		spammers = Counter()
		channel = ctx.message.channel
		prefixes = self.bot.command_prefix
		if callable(prefixes):
			prefixes = prefixes(self.bot, ctx.message)

		def is_possible_command_invoke(entry):
			valid_call = any(entry.content.startswith(prefix) for prefix in prefixes)
			return valid_call and not entry.content[1:2].isspace()

		can_delete = channel.permissions_for(channel.server.me).manage_messages

		if not can_delete:
			api_calls = 0
			async for entry in self.bot.logs_from(channel, limit=search, before=ctx.message):
				if api_calls and api_calls % 5 == 0:
					await asyncio.sleep(1.1)

				if entry.author == self.bot.user:
					spammers['Bot'] += 1
					api_calls += 1
				else:
					spammers[entry.author.display_name] += 1
					if is_possible_command_invoke(entry):
						api_calls += 1

				try:
					await self.bot.delete_message(entry)
				except discord.Forbidden:
					continue

		else:
			deleted = await self.bot.purge_from(channel, limit=search, before=ctx.message)
			spammers = Counter(m.author.display_name for m in deleted)

		deleted = sum(spammers.values())
		messages = ['%s %s removed.' % (deleted, 'message was' if deleted == 1 else 'messages were')]
		if deleted:
			messages.append('')
			spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
			messages.extend(map(lambda t: '**%s**: %d' %(t[0], t[1]), spammers))

		await self.bot.delete_message(ctx.message)

		msg = await self.bot.responses.basic(title="Removed Messages:", message='\n'.join(messages))
		await asyncio.sleep(10)
		await self.bot.delete_message(msg)

def setup(bot):
	bot.add_cog(Admin(bot))
