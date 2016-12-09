#encoding: utf-8
import requests
import os
import datetime
from io import open
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):

    def __init__(self):
        self.urls = []
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            for attr in attrs:
                if attr[0] == 'src':
                    self.urls.append(attr[1])


credentials = '', ''
session = requests.Session()
session.auth = credentials

zendesk = 'https://portalstone.zendesk.com'
language = 'pt-br'

date = datetime.date.today()
backup_path = os.path.join('backup', str(date), language)

log = []
image_urls = []
endpoint = zendesk + '/api/v2/help_center/{locale}/articles.json'.format(locale=language.lower())
while endpoint:
    response = session.get(endpoint)
    if response.status_code != 200:
        log.append('Failed to retrieve articles with error {}'.format(response.status_code))
        exit()
    data = response.json()

    for article in data['articles']:
        name = '<h1>' + article['name'] + '</h1>'
        title = '<h2>' + article['title'] + '</h2>'
        filename = '{id}.html'.format(id=article['id'])
        path = os.path.join(backup_path, '{section}'.format(section=article['section_id']))

        if not os.path.exists(path):
            os.makedirs(path)
        if article['draft'] is True:
            log.append('{id} is draft!'.format(id=article['id']))
        elif article['body'] is None:
            log.append('{id} not copied!'.format(id=article['id']))
        else:
            parser = MyHTMLParser()
            parser.feed(article['body'])
            image_urls.append(parser.urls)
            # TODO Download images and replace 'em
            f = open(os.path.join(path, filename), 'w', encoding='utf-8')
            f.write(name + '\n' + title + '\n' + article['body'])
            f.close()

    endpoint = data['next_page']

urls_file_path = os.path.join(backup_path, 'images')
if not os.path.exists(urls_file_path):
    os.makedirs(urls_file_path)
f = open(os.path.join(urls_file_path, 'urls.txt'), 'w', encoding='utf-8')
for url in image_urls:
    f.write(url + '\n')
f.close()

f = open(os.path.join(backup_path, 'log.txt', 'w', enconding='utf-8')
for log in logs:
    f.write(log + '\n')
f.close()
