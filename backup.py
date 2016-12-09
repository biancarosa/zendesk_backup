# encoding: utf-8
import requests
import os
import datetime
import validators
from io import open
import base64
from HTMLParser import HTMLParser


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
sections = {}
endpoint = zendesk + \
    '/api/v2/help_center/{locale}/sections.json'.format(
        locale=language.lower())
while endpoint:
    response = session.get(endpoint)
    if response.status_code != 200:
        log.append('Failed to retrieve sections with error {}. URL: {}'.format(
            response.status_code, endpoint))
    data = response.json()
    for section in data['sections']:
        sections[section['id']] = section['name']
    endpoint = data['next_page']

endpoint = zendesk + \
    '/api/v2/help_center/{locale}/articles.json'.format(
        locale=language.lower())
while endpoint:
    response = session.get(endpoint)
    if response.status_code != 200:
        log.append('Failed to retrieve articles with error {}. URL: {}'.format(
            response.status_code, endpoint))
    data = response.json()

    for article in data['articles']:
        title = '<h1>' + article['title'] + '</h1>'
        name = article['name'].encode('ascii', 'ignore').decode(
            'ascii').replace('/', ' ').strip().replace('?', '').replace(
            '"',"").replace("*", '').replace(':','')
        filename = '{name}.html'.format(name=name)
        sid = article['section_id']
        section_name = sections.get(sid, sid).encode(
            'ascii', 'ignore').decode('ascii').replace(
                '/', ' ').strip().replace('?', '').replace(
            '"',"").replace("*", '').replace(':','')
        path = os.path.join(
            backup_path, '{section}'.format(section=section_name),
            '{article}'.format(article=article['id']))

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

                count = 0
                images_path = os.path.join(path, 'images')
                if len(parser.urls) > 0:
                    if not os.path.exists(images_path):
                        os.makedirs(images_path)

                print('----Article-----')
                print(article['id'])
                body = article['body']
                for url in parser.urls:
                    try:
                        count += 1
                        image_name = '{article}-{count}.jpg'.format(
                            article=article['id'], count=count)
                        body = body.replace(
                            url, os.path.join('images', image_name))
                        if validators.url(url) is True:
                            f = open(os.path.join(images_path, image_name), 'wb')
                            content = requests.get(url).content
                        else:
                            f = open(os.path.join(images_path, image_name), 'wb')
                            content = base64.b64decode(url.split(",")[1])
                        f.write(content)
                        f.close()
                    except Exception as e:
                        log.append('Couldnt get picture url {url} for article {article}'.format(
                            url=url, article=article['id']))

                f = open(os.path.join(path, filename), 'w', encoding='utf-8')
                f.write(title + '\n')
                f.write(body)
                f.close()

    endpoint = data['next_page']

urls_file_path = os.path.join(backup_path, 'images')
if not os.path.exists(urls_file_path):
    os.makedirs(urls_file_path)
f = open(os.path.join(urls_file_path, 'urls.txt'), 'w', encoding='utf-8')
for url in image_urls:
    f.write(url + '\n')
f.close()

f = open(os.path.join(backup_path, 'log.txt', 'w', encoding='utf-8'))
for log in logs:
    f.write(log + '\n')
f.close()
