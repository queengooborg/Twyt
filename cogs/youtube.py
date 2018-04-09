# -*- coding: utf-8 -*-

import asyncio

from discord.ext import commands

from discordbot.bot_utils import config, checks
from discordbot.bot_utils.paginator import Pages

from apiclient.discovery import build as build_yt
from apiclient.errors import HttpError

class YouTube:
	"""All YouTube-based commands."""

	def __init__(self, bot):
		self.bot = bot

		DEVELOPER_KEY = self.bot.config.get('credentials', {}).get('youtube_developer_key')
		YOUTUBE_API_SERVICE_NAME = "youtube"
		YOUTUBE_API_VERSION = "v3"

		self.youtube = build_yt(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

		self.channel_id = "UCme0nLOCBquY0OxIGvtnREQ"

	def video_list(self, channelid):
		channel = self.youtube.channels().list(
			part='contentDetails',
			id=channelid
		).execute()

		playlist = self.youtube.playlistItems().list(
			part='snippet,contentDetails',
			maxResults=5,
			playlistId=channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
		).execute()

		return playlist['items']

	@commands.command(pass_context=True)
	async def latest(self, ctx):
		"""Obtains the latest DubstepHorror release."""

		loop = asyncio.get_event_loop()
		items = await loop.run_in_executor(None, self.video_list, self.channel_id)
		latest = items[0]['snippet']
		await self.bot.send_message(ctx.message.channel, 'The most recent upload is {title}, published on {date}.  {url}'.format(
			title = latest['title'],
			date = latest['publishedAt'],
			url = "https://youtu.be/" + latest['resourceId']['videoId'])
		)

def setup(bot):
	bot.add_cog(YouTube(bot))
