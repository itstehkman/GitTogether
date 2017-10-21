import unittest
import requests
import pprint

class Tests(unittest.TestCase):

  def test_repo(self):
    r = requests.get('http://localhost:5000/repos/natural+language+processing')
    #print r.json()

  def test_users_for_repos(self):
    r = requests.get('http://localhost:5000/commits/JustFollowUs/Natural-Language-Processing')
    #pprint.pprint(r.json())

  def test_users_for_keyword(self):
    r = requests.get('http://localhost:5000/users/lstm')
    pprint.pprint(r.json())


unittest.main()
