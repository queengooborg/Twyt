# -*- coding: utf-8 -*-

import asyncio

from discord.ext import commands

from discordbot.bot_utils import config, checks
from discordbot.bot_utils.paginator import Pages

from apiclient.discovery import build as build_yt
from apiclient.errors import HttpError

SLEEP_MINUTES = 0.25

class YouTubeItem:
	def __init__(self, channel_id, youtube):
		self.channel_id = channel_id
		self.playlist_id = '' #wait for youtube
		self.latest = None

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
		return items[0]['snippet']

class Twyt:
	"""All YouTube and Twitch based commands."""

	def __init__(self, bot):
		self.bot = bot

		self.youtube = build_yt("youtube", "v3", developerKey=self.bot.config.get('credentials', {}).get('youtube_developer_key'))

		self.checklist = [YouTubeItem("UCme0nLOCBquY0OxIGvtnREQ", self.youtube)]

	async def on_ready(self):
		while True:
			await asyncio.sleep(SLEEP_MINUTES*60)
			for item in self.checklist:
				await item.check_latest()

	@commands.command(pass_context=True)
	async def latest(self, ctx):
		"""Obtains the latest DubstepHorror release."""

		latest = await self.checklist[0].check_latest()
		await self.bot.send_message(ctx.message.channel, 'The most recent upload is {title}, published on {date}.  {url}'.format(
			title = latest['title'],
			date = latest['publishedAt'],
			url = "https://youtu.be/" + latest['resourceId']['videoId'])
		)

def setup(bot):
	bot.add_cog(Twyt(bot))
