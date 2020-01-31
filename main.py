from os.path import join, dirname
import pandas as pd
import requests
import json

path = dirname(__file__)
data_dir = join(path, 'data')


class Miner:
    def __init__(self, file_name):
        self.df = pd.read_csv(join(data_dir, file_name))
        self.issue_keys = list(self.df['Issue key'].values)
        self.base_url = 'https://api.github.com/search/commits?q=repo:apache/activemq+'

    def find_commits(self):
        headers = {'content-type': 'application/json',
                   'accept': 'application/vnd.github.cloak-preview'}
        keys = []
        ids = []
        messages = []
        for issue in self.issue_keys:
            response = requests.get(self.base_url+issue, headers=headers)
            response_dict = json.loads(response.text)
            print(response_dict)
            commits = response_dict.get('items')
            for commit in commits:
                if not self.remove_modify_commit(commit):
                    keys.append(issue)
                    ids.append(commit.get('sha'))
                    messages.append(commit.get('commit').get('message'))
        commit_df = pd.DataFrame({'Issue key': keys,
                                  'sha': ids,
                                  'message': messages})
        df = commit_df.join(self.df.set_index('Issue key'), on='Issue key')
        return df

    @staticmethod
    def remove_modify_commit(commit):
        pass


if __name__ == '__main__':
    miner = Miner(file_name='issues.csv')
    df = miner.find_commits()
    df.to_csv('issue_commit.csv', index=False)
