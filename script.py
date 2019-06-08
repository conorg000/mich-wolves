# Let's make a web scraper
!pip install requests BeautifulSoup4
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Function to get page from its url
# Got this from https://realpython.com/python-web-scraping-practical-introduction/
def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
    
def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    print(e)
	
	
# This function uses BeautifulSoup to scrape data from
# pages containing Michigan's results
def get_data(url):
    '''
    Get the seasons data for Michigan
    '''
    # Dict to store results (change this to pd later)
    df = pd.DataFrame(columns=['Opponent', 'Net Wins'])
    # List of teams (for checking purposes)
    tms = []
    # Loop through seasons 2010 to 2019
    for n in range(10, 20):
        # Fetch results
        response = simple_get(url.format(n))
        # Parse with BS
        if response is not None:
            html = BeautifulSoup(response, 'html.parser')
            # For each table entry, find ones related to Big Ten Conference
            for tr in html.select('tr'):
                bigtens = tr.find('a', {'title' : 'Big Ten Conference'})
                team = ''
                res = ''
                if bigtens != None:
                    # If it's a Big Ten match, get the team name and result
                    team = tr.find('td', {'data-stat' : 'opp_name'}).find('a').contents[0]
                    res = tr.find('td', {'data-stat' : 'game_result'}).contents[0]
                    # If the team isn't already in the dict, set its value to 0
                    if team not in tms:
                        tms.append(team)
                        df = df.append(pd.DataFrame([[team, 0]], columns=['Opponent', 'Net Wins']), ignore_index=True)
                    # If result is 'W', add 1 to team's value in dictionary
                    # Otherwise, take 1 from team's value
                    if res == 'W':
                        df.loc[df['Opponent'] == team, 'Net Wins'] += 1
                    else:
                        df.loc[df['Opponent'] == team, 'Net Wins'] -= 1
                else:
                    continue
    return(df)
	
# Use the webscraper to collate data from 2010 to 2019
src = 'https://www.sports-reference.com/cbb/schools/michigan/20{}-schedule.html'
data = get_data(src)

# Table listing Wolverines' performance against other teams
data = data.sort_values(by='Net Wins', ascending=False)
data['Xpos'] = 1
data.insert(3,'Ypos', range(1, 1 + len(data)))
names = data.pivot(index='Ypos', columns='Xpos', values='Opponent')
teams = list(names[1])
teams = [str(x) for x in teams]
tser = pd.Series(teams)

# Plot with a seaborn heatmap
plt.clf()
fig, ax = plt.subplots(figsize=(3,8))
title = "Michigan Wolverine's Rivals"
plt.title(title, fontsize=15)
sns.heatmap(res)
ax.axis('off')
ax.set_xticks([])
ax.set_yticks([])
plt.show()