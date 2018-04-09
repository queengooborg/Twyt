# -*- coding: utf-8 -*-

# Sample Python code for user authorization

import os

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyALcVh_MfoJwlSUNMg1HKRrhA2X0hHwCxA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

channel_id = "UCme0nLOCBquY0OxIGvtnREQ"

def video_list(channelid):
	channel = youtube.channels().list(
		part='contentDetails',
		id=channelid
	).execute()
	
	# print('This channel\'s ID is %s. Its title is %s, and it has %s views.' %
	# 		 (channel['items'][0]['id'],
	# 			channel['items'][0]['snippet']['title'],
	# 			channel['items'][0]['statistics']['viewCount']))

	playlist = youtube.playlistItems().list(
		part='snippet,contentDetails',
		maxResults=5,
		playlistId=channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
	).execute()

	return playlist['items']

	# print(playlist['items'][0])

if __name__ == '__main__':
	items = video_list(channel_id)
	print('The most recent upload is %s, published on %s.' %
			(items[0]['snippet']['title'],
			items[0]['snippet']['publishedAt'])
)