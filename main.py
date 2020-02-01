import re
import time
from os.path import join, dirname
import pandas as pd
import requests
import json

path = dirname(__file__)
data_dir = join(path, 'data')


class Miner:
    def __init__(self, path):
        self.df = pd.read_csv(path)
        self.issue_keys = list(self.df['Issue key'].values)
        self.base_url = 'https://api.github.com/search/commits?q=repo:apache/activemq+'

    def find_commits(self):
        headers = {'content-type': 'application/json',
                   'accept': 'application/vnd.github.cloak-preview'}
        keys = []
        ids = []
        messages = []
        for issue in self.issue_keys:
            print(issue)
            with open(join(path, 'auth.conf'), 'r') as file:
                lines = file.readlines()
            username = lines[0].split('\n')[0]
            password = lines[1].split('\n')[0]
            session = requests.Session()
            session.auth = (username, password)
            response = session.get(self.base_url + issue, headers=headers)
            time.sleep(1)
            response_dict = json.loads(response.text)
            commits = response_dict.get('items')
            for commit in commits:
                if not self.remove_modify_commit(commit):
                    keys.append(issue)
                    ids.append(commit.get('sha'))
                    messages.append(commit.get('commit').get('message'))
                    with open(join(data_dir, 'issue_commit.txt'), 'a') as file:
                        file.write(str(keys[-1]) + ', ' +
                                   str(ids[-1]) + ', ' +
                                   str(messages[-1]) + '\n')
                    print('\tfor', issue, ' commit', ids[-1], ' added.')
        commit_df = pd.DataFrame({'Issue key': keys,
                                  'SHA': ids,
                                  'Message': messages})
        df = commit_df.join(self.df.set_index('Issue key'), on='Issue key')
        return df

    @staticmethod
    def remove_modify_commit(commit):
        headers = {'content-type': 'application/json',
                   'accept': 'application/vnd.github.v3.patch'}
        url = commit.get('url')
        with open(join(path, 'auth.conf'), 'r') as file:
            lines = file.readlines()
        username = lines[0].split('\n')[0]
        password = lines[1].split('\n')[0]
        session = requests.Session()
        session.auth = (username, password)
        response = session.get(url, headers=headers)
        time.sleep(1)
        if response.text == '':
            return True
        text = response.text.split('\n')
        p = re.compile(', [0-9]+ deletion(s{0,1})\(-\)')
        for line in text:
            if bool(p.search(line)):
                return True
        return False


if __name__ == '__main__':
    miner = Miner(path=join(data_dir, 'issues.csv'))
    df = miner.find_commits()
    df.to_csv(join(data_dir, 'issue_commit.csv'), index=False)
