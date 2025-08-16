from googleapiclient.discovery import build
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

api_key = 'AIzaSyCU4Hj7otWb_yzB5mNzDJ0mXVAkGoRX3Uc'
youtube = build('youtube', 'v3', developerKey=api_key)

def extract_youtube_comments(video_id, no_comments):
  """
  Extracts comments from a YouTube video.

  Args:
    video_id (str): The ID of the YouTube video.
    no_comments (int): The number of comments to extract.

  Returns:
    pandas.DataFrame: A DataFrame containing the extracted comments with the following columns:
      - title (str): The display text of the comment.
      - link (str): The URL of the comment.
      - date_published (str): The date and time when the comment was published.
      - text (str): The original text of the comment.
      - like_count (int): The number of likes the comment has received.
      - reply_parent_id (float): The ID of the parent comment if the comment is a reply, otherwise NaN.
  """
  # re-initialize list of YouTube comments
  comments = []

  # get first page of the comments
  video_response = youtube.commentThreads().list(
    videoId=video_id, part='snippet,replies', maxResults=50,
    order='time', moderationStatus='published'
  ).execute()

  while len(comments) < no_comments:
    # iterate through items
    for item in video_response['items']:
      ##### Parent Comments #####
      # extract comment from each item
      comment = item['snippet']['topLevelComment']['snippet']

      # append comment to list of comments
      comments.append([
        comment['textDisplay'],
        f'https://www.youtube.com/watch?v={video_id}&lc={item["snippet"]["topLevelComment"]["id"]}',
        comment['publishedAt'],
        comment['textOriginal'],
        comment['likeCount'],
        np.nan
      ])

      ##### Reply Comments #####
      # count number of replies
      total_reply_count = item['snippet']['totalReplyCount']

      # if there is at least one reply
      if total_reply_count > 0:
        parent_id = item["snippet"]["topLevelComment"]["id"]

        replies = youtube.comments().list(
          part='snippet',
          parentId=parent_id
        ).execute()

        # iterate through the replies
        for reply in replies['items']:
          # extract text from each reply
          # append reply to list of comments
          replyBody = reply['snippet']
          comments.append([
            replyBody['textDisplay'],
            f"https://www.youtube.com/watch?v={video_id}&lc={reply['id']}",
            replyBody['publishedAt'],
            replyBody['textOriginal'],
            replyBody['likeCount'],
            replyBody['parentId']
          ])

    ##### Next Page #####
    # print number of comments
    print(str(len(comments)) + ' comments in list')

    # if there is a next page to the comment result
    if 'nextPageToken' in video_response:
      # notify that next page has been found
      print('Next comment page found. Now extracting data. \n')

      # get the next page
      video_response = youtube.commentThreads().list(
        videoId=video_id, part='snippet,replies', maxResults=50,
        order='time', pageToken=video_response['nextPageToken'],
        moderationStatus='published'
      ).execute()
    else:
      # notify that no more pages are left
      print('No more comment pages left.\n')
      break

  return pd.DataFrame(
    comments, columns=['title', 'link', 'date_published', 'text', 'like_count', 'reply_parent_id']
  )


video_links = [
  'Zx31bB2vMns',  
  'J1Ip2sC_lss'
]

bini_youtube_corpus = None

for video_link in video_links:
  print(f'Extracting comments from video: {video_link}')
  if bini_youtube_corpus is None:
    aliceguo_youtube_corpus = extract_youtube_comments(video_link, 750)
  else:
    bini_youtube_corpus = pd.concat([
      bini_youtube_corpus, extract_youtube_comments(video_link, 750)
    ])

print(bini_youtube_corpus)