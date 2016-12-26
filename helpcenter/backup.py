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
backup_path = 'backup'
backup_images = False
log = []
image_urls = []
data_csv = []
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
        print('----Article-----')
        print(article['id'])
        title = '<h1>' + article['title'] + '</h1>'
        name = article['name'].encode('ascii', 'ignore').decode(
            'ascii').replace('/', ' ').strip().replace('?', '').replace(
            '"',"").replace("*", '').replace(':','')
        filename = '{article}.html'.format(article=article['id'])
        sid = article['section_id']

        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        if article['draft'] is True:
            log.append('{id} is draft!'.format(id=article['id']))
        elif article['body'] is None:
            log.append('{id} not copied!'.format(id=article['id']))
        else:
            body = article['body']

            if backup_images:
                parser = MyHTMLParser()
                parser.feed(article['body'])
                image_urls.append(parser.urls)

                count = 0
                images_path = os.path.join(backup_path, 'images')
                if len(parser.urls) > 0:
                    if not os.path.exists(images_path):
                        os.makedirs(images_path)

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

            fname = os.path.join(backup_path, filename)
            f = open(fname, 'w', encoding='utf-8')
            f.write(title + '\n')
            f.write(body)
            f.close()
            log.append('{id} copied!'.format(id=article['id']))
            data_csv.append(",".join([article['title'], fname]))
            break

    endpoint = False #data['next_page']

f = open('log.txt', 'w', encoding='utf-8')
for line in log:
    f.write(unicode(line + "\n"))
f.close()

f = open('data.csv', 'w', encoding='utf-8')
f.write(unicode("Title,description__c\n"))
for line in data_csv:
    f.write(unicode(line + "\n"))
f.close()
