# Import libraries
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

# Declare headers for the requests agent
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
  'Accept-Language': 'en-US,en;q=0.9',
  'Accept-Encoding': 'gzip, deflate, br',
  'Connection': 'keep-alive'
}

def extract_article_data(link):
  """
  Extracts data from an article based on the provided link.

  Parameters:
    link (str): The URL of the article.

  Returns:
    list: A list containing the extracted article details in the following order:
      - title (str): The title of the article.
      - date (str): The date the article was published.
      - link (str): The URL of the article.
      - text (str): The content of the article.
  """
  # Make a GET request for the article URL
  r = requests.get(link, headers=headers)

  # Parse the HTML
  soup = BeautifulSoup(r.content, 'html.parser')

  # Retrieve doc title
  title = soup.title.text.strip()

  # IF NOT WITH RAPPLER ARTICLE, CHANGE THIS XOXO
  # Retrieve doc date
  date = soup.find("time", {"datetime": True})['datetime']

  # IF NOT WITH RAPPLER ARTICLE, CHANGE THIS XOXO
  # Retrieve article content
  text = ''
  tagged_lines = soup.find("div", {"class": "post-single__content entry-content"}).find_all('p')
  for line in tagged_lines:
    untagged_line = line.get_text()
    text += untagged_line + '\n'

  # Create list containing doc details
  # Append to dataset
  doc_details = [title, date, link, text]                                             
  return doc_details

mother_url = "https://www.rappler.com/wp-json/rappler/v1/ontology-topics/2653920/latest-news?page="
page = 1
page_limit = 5
corpus = pd.DataFrame(columns=['title', 'link', 'date_published', 'text'])

while True:
  page_str = str(page)
  page_url = mother_url + page_str
  print('Working on ' + page_url)

  time.sleep(random.randint(1, 5))

  page_r = requests.get(page_url, headers=headers)
  page_soup = BeautifulSoup(page_r.content, 'html.parser')

  article_container = page_soup.find('div', {'id': 'ontology-topic-latest-news-container'})
  if article_container is None:
    continue

  article_previews = article_container.find_all('article')
  print(article_previews)
  number_of_articles = len(article_previews)
  print(number_of_articles)

  if number_of_articles < 1:
    print('Extraction Finished!')
    break

  for article_id in range(number_of_articles):
    article = article_previews[article_id]
    article_title = article.find("h3")

    if article_title is None:
      continue

    try:
      tmp = extract_article_data(article_title.find("a")['href'])
      print(tmp)
      corpus.loc[len(corpus)] = tmp
    except:
      continue

  if page >= page_limit:
    break

  page += 1

file_name = 'rappler_corpus.xlsx'
corpus.to_excel(file_name)
print(f'File saved to {file_name}')