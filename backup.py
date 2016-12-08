#encoding: utf-8
import requests
import os
import datetime
from io import open

credentials = '', ''
session = requests.Session()
session.auth = credentials

zendesk = 'https://portalstone.zendesk.com'
language = 'pt-br'

date = datetime.date.today()
backup_path = os.path.join('backup', str(date), language)

log = []
endpoint = zendesk + '/api/v2/help_center/{locale}/articles.json'.format(locale=language.lower())
while endpoint:
    response = session.get(endpoint)
    if response.status_code != 200:
        print('Failed to retrieve articles with error {}'.format(response.status_code))
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
            print('{id} is draft!'.format(id=article['id']))
        elif article['body'] is None:
            print('{id} not copied!'.format(id=article['id']))
        else:
            f = open(os.path.join(path, filename), 'w', encoding='utf-8')
            f.write(name + '\n' + title + '\n' + article['body'])
            f.close()

    endpoint = data['next_page']
