import json
import requests
import os

from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_URL = 'https://api.github.com'
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

@app.route('/repos/<keyword>', methods=['GET'])
def sorted_repos(keyword):
  """ Get repos which match the keyword search """

  keyword = keyword.replace('+', ' ')
  params = {'q': '%s in:name,description,readme' % keyword,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET}
  r = requests.get(BASE_URL + '/search/repositories', params)
  print r.url
  print {k:v for k,v in r.headers.iteritems() if 'Rate' in k}

  r_json = r.json()
  items = []
  for item in r_json['items']:
    items.append(item['full_name'])
  return jsonify(items)

@app.route('/commits/<path:repo>', methods=['GET'])
def sorted_users_for_repo(repo):
  """ Get users who have commited in the repo in the last month """

  params = {'since': (datetime.now() - timedelta(weeks=400)).isoformat(),
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET}
  r = requests.get(BASE_URL + '/repos/%s/commits' % repo, params)
  print r.url
  print {k:v for k,v in r.headers.iteritems() if 'Rate' in k}

  r_json = r.json()
  users = set()
  for commit in r_json:
    if 'author' in commit and commit['author'] is not None:
      user = (commit['author']['login'], commit['commit']['author']['email'],
              commit['commit']['author']['name'])
      users.add(user)

  return jsonify(list(users))

@app.route('/users/<keyword>', methods=['GET'])
def sorted_users_for_keyword(keyword):
  """ Find the top users who have commited in repositories matching the keyword in the last month """

  repos = sorted_repos(keyword)
  repos = json.loads(repos.get_data())
  users = set()
  for repo in repos:
    users_list = sorted_users_for_repo(repo)
    users_list = json.loads(users_list.get_data())
    for user in users_list:
      users.add(tuple(user))
  return jsonify(list(users))

app.run('0.0.0.0', debug=True)
