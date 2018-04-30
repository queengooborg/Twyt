# -*- coding: utf-8 -*-

__title__ = 'twyt.cog'
__author__ = 'Vinyl Darkscratch'
__license__ = 'GNU GPLv3'
__copyright__ = 'Copyright 2018 Vinyl Darkscratch www.queengoob.org'
__version__ = '0.0.1'

import asyncio

import discord
from discord.ext import commands

from discordbot.bot_utils import config, checks
from discordbot.bot_utils.paginator import Pages

import os
import json

from apiclient.discovery import build as build_yt
from apiclient.errors import HttpError

import opengraph

SAVE_FILE = "./data/twyt.json"

SLEEP_MINUTES = 5

class YouTubeItem:
	def __init__(self, youtube, channel_id, discord_channel = None):
		self.channel_id = channel_id
		self.latest = None
		self.discord_channels = []

		if discord_channel:
			self.discord_channels.append(discord_channel)

		self.youtube = youtube

	@classmethod
	def fromDict(cls, youtube, bot, data):
		self = cls(youtube, data.get('channel_id'))
		self.latest = data.get('latest')
		self.discord_channels = [DiscordChannel.fromDict(bot, discord_channel) for discord_channel in data.get('discord_channels', [])]
		return self

	def toDict(self):
		return dict(channel_id = self.channel_id, latest = self.latest, discord_channels = [c.toDict() for c in self.discord_channels])

	def video_list(self):
		channel = self.youtube.channels().list(
			part='contentDetails',
			id=self.channel_id
		).execute()

		playlist = self.youtube.playlistItems().list(
			part='snippet,contentDetails',
			maxResults=5,
			playlistId=channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
		).execute()

		return playlist['items']

	async def check_latest(self):
		loop = asyncio.get_event_loop()
		items = await loop.run_in_executor(None, self.video_list)
		if not len(items): return None

		response = items[0]['snippet']
		response['url'] = "https://youtu.be/" + response['resourceId']['videoId']
		return response

	async def check_latest_unseen(self):
		response = await self.check_latest()
		print("%s: Livestream?  %s" %(response['url'], response.get('liveBroadcastContent', 'none')))
		if response.get('liveBroadcastContent', 'none') != "none": pass
		latest = self.latest
		self.latest = response['publishedAt']
		if (self.latest == latest or latest == None): return None
		else: return response

class DiscordChannel:
	def __init__(self, bot, channel, template = "%(title)s by %(channelTitle)s just published!  %(url)s"):
		self.bot = bot
		self.channel = channel
		self.template = template

	@classmethod
	def fromDict(cls, bot, data):
		return cls(bot, data.get('channel'), data.get('template'))

	def toDict(self):
		return dict(channel = self.channel, template = self.template)

	async def send_message(self, data):
		if data: await self.bot.send_message(discord.Object(self.channel), self.template % data)

class Twyt:
	"""All YouTube and Twitch based commands."""

	def __init__(self, bot):
		self.bot = bot

		self.youtube = build_yt("youtube", "v3", developerKey=self.bot.config.get('credentials', {}).get('youtube_developer_key'))

		self.checklist = []
		self._load()

	async def on_ready(self):
		while True:
			await asyncio.sleep(SLEEP_MINUTES*60)
			for item in self.checklist:
				latest = await item.check_latest_unseen()
				for channel in item.discord_channels:
					await channel.send_message(latest)

	def _save(self):
		with open(SAVE_FILE, 'w') as save:
			json.dump([c.toDict() for c in self.checklist], save)

	def _load(self):
		try:
			data = json.load(open(SAVE_FILE, 'r'))
			if data: self.checklist = [YouTubeItem.fromDict(self.youtube, self.bot, d) for d in data]
		except IOError:
			pass

	@commands.command(pass_context=True)
	@checks.mod_or_permissions(manage_webhooks=True)
	async def watch(self, ctx, url : str, message = "@everyone New upload!"):
		"""Add a YouTube/Twitch channel to watch for new uploads.

		XXX Only works with YouTube channels right now.
		XXX Sort of works with livestreams on YouTube.  The bot announces new video uploads, and YouTube treats livestreams like videos.
		XXX Doesn't allow you to change the Discord channel.
		XXX IMPORTANT: Videos should be published in the order they were uploaded on this channel to prevent issues with notifications."""

		if not url:
			await self.bot.responses.failure(title="No URL Specified", message="You need to give me a URL!")
			return

		og = opengraph.OpenGraph(url=url)
		channel_url = og.get('url', '')
		if channel_url.startswith("https://www.youtube.com/channel/"):
			self.checklist.append(YouTubeItem(self.youtube, channel_url.replace("https://www.youtube.com/channel/", ""), DiscordChannel(self.bot, ctx.message.channel.id, message + "  %(url)s")))
			await self.bot.responses.basic(message="This YouTube channel has been added!")
		elif False:
			pass
		else:
			await self.bot.responses.failure(title="Not a YouTube/Twitch Channel", message="The URL you have given me is not a YouTube/Twitch channel!")
			return

		self._save()

	@commands.command(pass_context=True)
	@checks.mod_or_permissions(manage_webhooks=True)
	async def unwatch(self, ctx, url : str):
		"""Remove a YouTube/Twitch channel from the watch queue.

		XXX Only works with YouTube channels right now."""

		if not url:
			await self.bot.responses.failure(title="No URL Specified", message="You need to give me a URL!")
			return

		found = False

		og = opengraph.OpenGraph(url=url)
		channel_url = og.get('url', '')
		if channel_url.startswith("https://www.youtube.com/channel/"):
			channel_id = channel_url.replace("https://www.youtube.com/channel/", "")

			for i in range(len(self.checklist)):
				if self.checklist[i].channel_id == channel_id:
					for j in range(len(self.checklist[i].discord_channels)):
						if self.checklist[i].discord_channels[j].channel == ctx.message.channel.id:
							self.checklist[i].discord_channels.pop(j)
							found = True
					if len(self.checklist[i].discord_channels) == 0: self.checklist.pop(i)
					break
		elif False:
			pass
		else:
			await self.bot.responses.failure(title="Not a YouTube/Twitch Channel", message="The URL you have given me is not a YouTube/Twitch channel!")
			return

		if found: await self.bot.responses.basic(message="This channel has been removed!")
		else: await self.bot.responses.failure(title="Channel Never Watched", message="I was never watching this YouTube/Twitch channel in this Discord channel!")

		self._save()

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def latest(self, ctx):
		"""Obtains the latest videos and announces them for every channel.

		This does not just check the latest videos in this particular server.  It will force an announcement across all servers."""

		for item in self.checklist:
			latest = await item.check_latest()
			for channel in item.discord_channels:
				await channel.send_message(latest)
		

def setup(bot):
	bot.add_cog(Twyt(bot))
