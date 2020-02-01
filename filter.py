import time
from os.path import join, dirname
import pandas as pd
import requests

path = dirname(__file__)
data_dir = join(path, 'data')


class Filter:
    def __init__(self, path):
        self.df = pd.read_csv(path)
        self.base_url = 'https://api.github.com/repos/apache/activemq/commits/'

    @staticmethod
    def get_commit(url):
        headers = {'content-type': 'application/json',
                   'accept': 'application/vnd.github.v3.patch'}
        with open(join(path, 'auth.conf'), 'r') as file:
            lines = file.readlines()
        username = lines[0].split('\n')[0]
        password = lines[1].split('\n')[0]
        session = requests.Session()
        session.auth = (username, password)
        response = session.get(url, headers=headers)
        time.sleep(1)
        return response

    def remove_duplicated(self):
        keys = []
        texts = []
        ids = []
        for i, row in self.df.iterrows():
            key = row['Issue key']
            sha = row['SHA']
            response = self.get_commit(self.base_url + sha)
            try:
                index = texts.index(response.text)
            except:
                keys.append(key)
                texts.append(response.text)
                ids.append(sha)
                continue
            if keys[index] == key:
                print(sha, 'is the same as', ids[index], 'and both are associated with', key)
                self.df = self.df[self.df.SHA != sha]
            else:
                keys.append(key)
                texts.append(response.text)
                ids.append(sha)
        return self.df


if __name__ == '__main__':
    filter = Filter(path=join(data_dir, 'issue_commit.csv'))
    df = filter.remove_duplicated()
    df.to_csv(join(data_dir, 'issue_commit_refined.csv'), index=False)
