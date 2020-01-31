from os.path import join, dirname
import pandas as pd
import requests

path = dirname(__file__)
data_dir = join(path, 'data')
df = pd.read_csv(join(data_dir, 'issues.csv'))

base_url = 'https://api.github.com/search/commits?q=repo:apache/activemq+'
issue_key = 'AMQ-2935'
url = base_url + issue_key
