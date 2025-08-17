from googleapiclient.discovery import build
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

youtube = build('youtube', 'v3', developerKey= os.getenv('api_key'))

def extract_youtube_comments(video_id):
  comments = []

  #Response for comment related information.
  comment_response = youtube.commentThreads().list(
    videoId=video_id, part='snippet,replies', maxResults=50,
    order='time', moderationStatus='published'
  ).execute()

  #Response for video related information. Added this to know what video and channel the comments are from.
  video_response = youtube.videos().list(
    part = "snippet, statistics", id = video_id
  ).execute()

  video = video_response['items'][0]

  #Added various information about the video itself for better identification and additional information to consider.
  video_publishedAt = video['snippet'].get('publishedAt')
  video_channelId = video['snippet'].get('channelId')
  video_title = video['snippet'].get('title')
  video_views = video['statistics'].get('viewCount')
  video_likes = video['statistics'].get('likeCount')

  while True:
    for item in comment_response['items']:
      comment = item['snippet']['topLevelComment']['snippet']

      comments.append([
        video_publishedAt,
        video_channelId,
        video_title,
        video_views,
        video_likes,
        comment['textDisplay'],
        f'https://www.youtube.com/watch?v={video_id}&lc={item["snippet"]["topLevelComment"]["id"]}',
        comment['publishedAt'],
        comment['textOriginal'],
        comment['likeCount'],
        np.nan
      ])

      total_reply_count = item['snippet']['totalReplyCount']

      if total_reply_count > 0:
        parent_id = item["snippet"]["topLevelComment"]["id"]

        replies = youtube.comments().list(
          part='snippet',
          parentId=parent_id
        ).execute()

        for reply in replies['items']:

          replyBody = reply['snippet']
          comments.append([
            video_publishedAt,
            video_channelId,
            video_title,
            video_views,
            video_likes,
            replyBody['textDisplay'],
            f"https://www.youtube.com/watch?v={video_id}&lc={reply['id']}",
            replyBody['publishedAt'],
            replyBody['textOriginal'],
            replyBody['likeCount'],
            replyBody['parentId']
          ])

    print(str(len(comments)) + ' comments in list')

    if 'nextPageToken' in comment_response:
      print('Next comment page found. Now extracting data. \n')

      comment_response = youtube.commentThreads().list(
        videoId=video_id, part='snippet,replies', maxResults=50,
        order='time', pageToken=comment_response['nextPageToken'],
        moderationStatus='published'
      ).execute()
    else:
      print('No more comment pages left.\n')
      break

  return pd.DataFrame(
    comments, columns=['video_publishedAt', 'video_channelId', 'video_title', 'video_views', 'video_likes','title', 'link', 'date_published', 'text', 'like_count', 'reply_parent_id']
  )

#All youtube videos are about Leni Robredo.
rappler_links = [
  '8uAgdruPhqA',  
  'MGV3u_2wldg',
  '01NiV2oSmPI',
  'kQfFe2ywY0c',
  'Otf3JHqsrc4'
]

gma_links = [
  'APXtHcRuhOM',
  'jrXVkte_RgA',
  '45uhxDVegc4',
  'woKpGLyH7Qc',
  '95W380l4qhY'
]

abs_links = [
  'y5svE0g9HW4',
  'MRAZ12L5SAk',
  'iy52bLTGj9k',
  'R-e6v1Rp3cI',
  'VWqaXPX9rug'
]

anc_links = [
  'wliI3IhPmEU',
  'VWGbzEWrAbs',
  '1Jq42ZKivWk',
  'vEcu49VFY9g',
  'dlvkFq-oD6w'
]

leni_links = [
  'xfMSWTaFLkw',
  'wEAvcaieVFA',
  'ZQFagpnmbZ4',
  '0klBShshBwU',
  'jfj159wtxzA'
]

channels = [rappler_links, gma_links, abs_links, anc_links, leni_links]

leni_youtube_corpus = None

for channel in channels:
  for video_link in channel:
    print(f'Extracting comments from video: {video_link}')
    if leni_youtube_corpus is None:
      leni_youtube_corpus = extract_youtube_comments(video_link)
    else:
      leni_youtube_corpus = pd.concat([
        leni_youtube_corpus, extract_youtube_comments(video_link)
      ])

file_name = 'leni_youtube.xlsx'
leni_youtube_corpus.to_excel(file_name)
print(f'File saved to {file_name}')