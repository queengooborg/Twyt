# -*- encoding: utf8 -*-

import os
import time

import discord
import asyncio

from apiclient.discovery import build as build_yt
from apiclient.errors import HttpError

DEVELOPER_KEY = "AIzaSyALcVh_MfoJwlSUNMg1HKRrhA2X0hHwCxA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build_yt(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
discord = discord.Client()

channel_id = "UCme0nLOCBquY0OxIGvtnREQ"

def video_list(channelid):
	print("video_list start")
	channel = youtube.channels().list(
		part='contentDetails',
		id=channelid
	).execute()

	playlist = youtube.playlistItems().list(
		part='snippet,contentDetails',
		maxResults=5,
		playlistId=channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
	).execute()

	print("video_list done")
	return playlist['items']


async def on_results(fu):
	items=fu.result()
	await discord.send_message('The most recent upload is %s, published on %s.' %
		(items[0]['snippet']['title'],
		items[0]['snippet']['publishedAt']))


@discord.event
async def on_ready():
	print('Logged in as')
	print(discord.user.name)
	print(discord.user.id)
	print('------')

@discord.event
async def on_message(message):
	if message.content.startswith('!test'):
		counter = 0
		tmp = await discord.send_message(message.channel, 'Calculating messages...')
		async for log in discord.logs_from(message.channel, limit=100):
			if log.author == message.author:
				counter += 1
		await discord.edit_message(tmp, 'You have {} messages.'.format(counter))

	elif message.content.startswith("!latest"):
		loop = asyncio.get_event_loop()
		fu = loop.run_in_executor(None, video_list, channel_id)
		print("Foo!")
		fu.add_done_callback(on_results)

	elif message.content.startswith('!sleep'):
		await asyncio.sleep(5)
		await discord.send_message(message.channel, 'Done sleeping')

discord.run('NDMyMzQzMDI2NjgyMTY3Mjk4.Dar6Ww.Q04lUPATCplg98Fo22ipn-n7Ry4')