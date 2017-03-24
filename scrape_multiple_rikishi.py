"""Script to scrape basic profile data for multiple sumo wrestlers. Takes in a sumo datbase url and scrapes
basic profile info (e.g. name, shikona, shusshin, height, weight, etc.).

Usage:
(1) Set up database url
(2) Set up final pickle file save name (bottom of script)
(3) Run scrape_multiple_rikishi.py

"""

# ----------------- Scrape Basic Data for Multiple Rikishi ------------------ #
# last time, took 3.25 hours (requests > urllib2)

import urllib2
# import requests
import bs4  # this is beautiful soup
import pandas as pd
import time
from rikishi_scrape import basic_scrape  # custom helper functions
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 100)

# ----------------- Beautiful Soup Setup ------------------ #

# all yokozuna
# db_url = "http://sumodb.sumogames.de/Rikishi.aspx?shikona=&heya=-1&shusshin=-1&b=-1&high=1&hd=-1&entry=-1&intai=-1&sort=4"

# three current yokozuna
# db_url = "http://sumodb.sumogames.de/Rikishi.aspx?shikona=&heya=-1&shusshin=-1&b=201701&high=1&hd=-1&entry=-1&intai=-1&sort=4"

# all makushita
# db_url = "http://sumodb.sumogames.de/Rikishi.aspx?shikona=&heya=-1&shusshin=-1&b=-1&high=7&hd=-1&entry=-1&intai=-1&sort=4"

# Asahimatsu
# db_url = "http://sumodb.sumogames.de/Rikishi.aspx?shikona=Asahimatsu&heya=-1&shusshin=-1&b=-1&high=-1&hd=-1&entry=-1&intai=-1&sort=6"

# all rikishi
# sorted by birth_date (sort=4)
db_url = "http://sumodb.sumogames.de/Rikishi.aspx?shikona=&heya=-1&shusshin=-1&b=-1&high=-1&hd=-1&entry=-1&intai=-1&sort=4"


# source = requests.get(rikishi_url).text
source = urllib2.urlopen(db_url).read()
soup = bs4.BeautifulSoup(source, 'lxml')  # turn into soup

print 'done'


# ----------------- Create Database of Basic Rikishi Stats & Info ------------------ #

right_td = soup.findAll('td', {'class': 'layoutright'})
rows = right_td[0].findAll('tr')  # take first td with layoutright class

# initialize pandas dataframe
cols = [u'shikona', u'highest_rank', u'bday', u'age', u'birth_place', u'height', u'weight', u'sumo_stable',
        u'active_years', u'debut', u'entry_rank', u'retirement', u'career_record', u'makuuchi_record',
        u'yokozuna_record', u'ozeki_record', u'sekiwake_record', u'komusubi_record', u'maegashira_record',
        u'juryo_record', u'makushita_record', u'sandanme_record', u'jonidan_record', u'jonokuchi_record']
rikishi_df = pd.DataFrame(columns=cols)  # initialize empty dataframe


start = time.time()
for ind, row in enumerate(rows):
    if ind:  # skip first headers row
        links = row.findAll('a', href=True)
        extension = links[0]['href']  # access link inside href
        rikishi_url = "http://sumodb.sumogames.de/" + extension
        compiled_stats = basic_scrape(rikishi_url)
        rikishi_df.loc[len(rikishi_df.index)] = compiled_stats
        print "Iter: %d, " % ind + compiled_stats[0]
    if ind % 1000 == 0:
        # save pickle file
        print "Saving rikishi_df @ length: " + str(len(rikishi_df.index))
        rikishi_df.to_pickle('data/temp_all_rikishi.pkl')

end = time.time()
exec_time = end - start
print "SCRAPING DONE"
print "Execution Time: %2.2f (s)" % exec_time


# store index as the unique rikishi ID
rikishi_df[u'rikishi_ID'] = rikishi_df.index
cols.insert(0, u'rikishi_ID')  # insert rikishi_ID as first column for viewing convenience
rikishi_df = rikishi_df[cols]  # reassign

# --- CHANGE FILENAME BELOW DEPENDING ON SOURCE --- #
# make sure not to overwrite existing pickle files
# rikishi_df.to_pickle('data/all_rikishi.pkl')

rikishi_df.tail()
