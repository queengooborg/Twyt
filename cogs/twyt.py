# -*- coding: utf-8 -*-

import asyncio

from discord.ext import commands

from discordbot.bot_utils import config, checks
from discordbot.bot_utils.paginator import Pages

from apiclient.discovery import build as build_yt
from apiclient.errors import HttpError

SAVE_FILE = "./data/twyt.pickle"

SLEEP_MINUTES = 0.25

class YouTubeItem:
	def __init__(self, channel_id, youtube):
		self.channel_id = channel_id
		self.playlist_id = '' #wait for youtube
		self.latest = None
		self.discord_channels = []

		self.youtube = youtube

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
		latest = self.latest
		self.latest = response['publishedAt']
		if self.latest != latest: return response
		else: return None

class DiscordChannel:
	def __init__(self, bot, channel, template = "%(title)s by %(channelTitle)s just published!  %(url)s"):
		self.bot = bot
		self.channel = channel
		self.template = template

	async def send_message(self, data):
		if data: await self.bot.send_message(self.channel, self.template % data)

class Twyt:
	"""All YouTube and Twitch based commands."""

	def __init__(self, bot):
		self.bot = bot

		self.youtube = build_yt("youtube", "v3", developerKey=self.bot.config.get('credentials', {}).get('youtube_developer_key'))

		self.checklist = []
		# self._load()
		self.checklist.append(YouTubeItem("UCme0nLOCBquY0OxIGvtnREQ", self.youtube))

	async def on_ready(self):
		while True:
			await asyncio.sleep(SLEEP_MINUTES*60)
			for item in self.checklist:
				latest = await item.check_latest()
				for channel in item.discord_channels:
					await channel.send_message(latest)

	def _save(self):
		pickle.dump(self.checklist, open(SAVE_FILE, 'wb'))

	def _load(self):
		try:
			data = pickle.load(open(SAVE_FILE, 'rb'))
			if data: self.checklist = data
		except IOError:
			pass

	@commands.command(pass_context=True)
	async def latest(self, ctx):
		"""Obtains the latest DubstepHorror release."""

		self.checklist[0].discord_channels.append(DiscordChannel(self.bot, ctx.message.channel))

		latest = await self.checklist[0].check_latest()
		for channel in self.checklist[0].discord_channels:
			await channel.send_message(latest)
		

def setup(bot):
	bot.add_cog(Twyt(bot))
