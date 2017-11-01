import json
import requests
import os

from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE_URL = 'https://api.github.com'
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# Helpers

def _repos_for_keyword(keyword):
  """ Get repos which match the keyword search """

  keyword = keyword.replace('+', ' ')
  params = {'q': '%s in:name,description,readme' % keyword,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET}
  r = requests.get(BASE_URL + '/search/repositories', params)
  print r.url
  print {k:v for k,v in r.headers.iteritems() if 'Rate' in k}
  return [item['full_name'] for item in r.json()['items']]

def _users_for_repo(repo, weeks=400):
  """ Returns users that have commited in a repo in the last N weeks """

  params = {'since': (datetime.now() - timedelta(weeks=weeks)).isoformat(),
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
  return list(users)

# Flask routes

@app.route('/repos/<keyword>', methods=['GET'])
def repos_for_keyword(keyword):
  return jsonify(_repos_for_keyword(keyword))

@app.route('/commits/<path:repo>', methods=['GET'])
def users_for_repo(repo, weeks=400):
  users = _users_for_repo(repo, weeks=weeks)
  return jsonify(users)

@app.route('/users/<keyword>', methods=['GET'])
def users_for_keyword(keyword):
  """ Find the top users who have commited in repositories matching the keyword in the last month """

  repos = _repos_for_keyword(keyword)
  users = set()
  for repo in repos:
    users_list = _users_for_repo(repo, weeks=400)
    for user in users_list:
      users.add(tuple(user))
  return jsonify(list(users))

app.run('0.0.0.0', debug=True)
