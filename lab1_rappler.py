import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import json

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
  'Accept-Language': 'en-US,en;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br',
  'Connection': 'keep-alive'
}

rappler = pd.DataFrame(
    columns=['title', 'link', 'date_published', 'text', 'related_topics']
)

def extract_article_data(link):
  r = requests.get(link, headers=headers)

  soup = BeautifulSoup(r.content, 'html.parser')

  title = soup.title.text.strip()

  date = soup.find("time", {"datetime": True})['datetime']

  text = ''
  tagged_lines = soup.find("div", {"class": "post-single__content entry-content"}).find_all('p')
  for line in tagged_lines:
    untagged_line = line.get_text()
    text += untagged_line + '\n'

  related_topics = ''
  extracted_topics = soup.find("div", {"class": "related-topics-links"})
  for topic in extracted_topics:
    related_topics += ' ' + topic.get_text()

  doc_details = [title, date, link, text, related_topics]                                             
  return doc_details

#Retrieve Articles from Leni Robredo's People Page
mother_url = "https://www.rappler.com/wp-json/rappler/v1/ontology-topics/2653920/latest-news?page="
page = 1
page_limit = 5
rappler_corpus = pd.DataFrame(columns=['title', 'link', 'date_published', 'text', 'related_topics'])

while page <= page_limit:
  page_str = str(page)
  page_url = mother_url + page_str
  print('Working on ' + page_url)

  time.sleep(random.randint(1, 5))

  page_r = requests.get(page_url)
  page_soup = page_r.json()

  number_of_articles = len(page_soup)

  for article in page_soup:
    if article.get('title') is None:
        continue
    else:
      try:
          tmp = extract_article_data(article['permalink'])
          rappler_corpus.loc[len(rappler_corpus)] = tmp
      except:
        continue

  page += 1

file_name = 'rappler_corpus.xlsx'

rappler_corpus.to_excel(file_name)
print(f'File saved to {file_name}')
