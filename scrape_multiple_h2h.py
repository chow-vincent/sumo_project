"""Script to scrape head-to-head data for multiple sumo wrestlers. Takes in a sumo database url and scrapes
head-to-head information from each sumo wrestler listed in the database. DOES NOT handle duplicate information. See
filter_duplicates script to handle duplicate rows.

NOTE: Best time to scrape info is several days after a tournament, when sumo db has entered complete head-to-head info.

Usage:
(1) Set up pickle file with basic profile info (for ID matching)
(2) Set up database url
(3) Set up final pickle file save name (bottom of script)
(4) Run scrape_multiple_h2h.py

"""

import urllib2
import bs4
import time
import pandas as pd
from rikishi_scrape import bouturl_scrape, full_h2h_scrape
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 100)


# ----------- Import Basic Rikishi Data for ID Matching // Setup Fresh or Continue Existing Scrape ------------ #

rikishi_df = pd.read_pickle('data/all_rikishi.pkl')

# ==== CHOOSE IF STARTING FROM SCRATCH OR LOADING SAVED TEMP FILE === #

h2h_df = None  # uncomment if starting from scratch
# h2h_df = pd.read_pickle('data/temp_full_h2h.pkl')  # load existing data and continue scraping

# =================================================================== #

cols = [u'date', u'tourney_day',
        u'ID1', u'shikona1', u'rank1', u'outcome1',
        u'kimarite',
        u'ID2', u'shikona2', u'rank2', u'outcome2',
        u'flag']

if h2h_df is None:  # initialize DataFrame if starting from scratch
    h2h_df = pd.DataFrame(columns=cols)
    print "# --- Initializing H2H DF to Begin Fresh Scraping --- # "
else:
    print "# --- Existing H2H DataFrame Loaded to Continue Scraping --- #"


# --- Jump Sumo Wrestlers --- #  (must be >=1, jumps over title row)
# row_jump is HTML ROW, NOT SUMO WRESTLER ID

row_jump = 1
# row_jump = 10823  # recent_full_h2h extracts starting at row 10823 (hatsu dohyo in 2000)


# ----------------- Beautiful Soup Setup ------------------ #

# all yokozuna, sorted by hatsu dohyo
# db_url = r"http://sumodb.sumogames.de/Rikishi.aspx?shikona=&heya=-1&shusshin=-1&b=-1&high=-1&hd=-1&entry=-1&intai=-1&sort=6"

# four current yokozuna
db_url = "http://sumodb.sumogames.de/Rikishi.aspx?shikona=&heya=-1&shusshin=-1&b=201701&high=1&hd=-1&entry=-1&intai=-1&sort=4"

# all rikishi
# sorted by birth_date (sort=4)
# db_url = "http://sumodb.sumogames.de/Rikishi.aspx?shikona=&heya=-1&shusshin=-1&b=-1&high=-1&hd=-1&entry=-1&intai=-1&sort=4"


source = urllib2.urlopen(db_url).read()
soup = bs4.BeautifulSoup(source, 'lxml')  # turn into soup

print 'HTML turned into soup'


# ----------------- Obtain Soup Rows from Sumo Database ------------------ #

# obtain rows in database (rikishi to loop over)
right_td = soup.findAll('td', {'class': 'layoutright'})
rows = right_td[0].findAll('tr')  # take first td with layoutright class


# ----------------- Loop Over Multiple Rikishi Profiles ------------------ #

start = time.time()

# data suggest that rikishi_df rows failing the following conditions do not have useful or any bout data
# pd.notnull(x) checks for None, NaN, and NaT
logical = rikishi_df['shikona'].map(lambda x: x is not None) & \
          rikishi_df['sumo_stable'].map(lambda x: x is not None) & \
          rikishi_df['bday'].map(lambda x: pd.notnull(x)) & \
          rikishi_df['debut'].map(lambda x: pd.notnull(x))
filtered_df = rikishi_df[logical]

# important assumptions:
# - sumo wrestlers with viable data will have min viable data available (shikona, sumo stable, bday, debut)
# - skip any sumo wrestlers lacking this info

for ind, row in enumerate(rows):

    # if ind == row_jump:  # uncomment to test just 1 row
    if ind >= row_jump:  # make sure to skip first headers row

        # time.sleep(1)  # may need to pause to prevent server request errors

        ID1 = None

        # --- Obtain Current Rikishi URL --- #
        links = row.findAll('a', href=True)
        extension = links[0]['href']  # access link inside href
        rikishi_url = "http://sumodb.sumogames.de/" + extension  # rikishi1 basic profile

        # --- Obtain Shikona, ID, and Bout URL --- #
        shikona1, sumo_stable, bout_url = bouturl_scrape(rikishi_url)
        print "\n# --- Row: %d, " % ind + shikona1 + " --- #\n"

        if (shikona1 is not None) and (sumo_stable is not None):

            print " Proceeding with ID extraction ..."
            logical = (filtered_df['shikona'] == shikona1) & (filtered_df['sumo_stable'] == sumo_stable)
            ID_df = filtered_df.loc[logical, 'rikishi_ID']

            # only proceed if exactly 1 match on shikona & sumo stable
            # this skips at least 24 rikishi with exact same shikona & sumo stable, but have justifiably useless data
            if len(ID_df.index) == 1:
                print " Successfully obtained Shikona 1's ID ..."
                ID1 = ID_df.item()

                # --- Scrape H2H Bout Data --- #
                start2 = time.time()
                data_rows = full_h2h_scrape(shikona1, ID1, bout_url, filtered_df)
                end2 = time.time()
                print " H2H Scrape Time: %2.3f" + (end2-start2) + "\n"

                # --- Store Data in Overall Dataframe --- #
                if data_rows:  # add rows only if data_rows is full
                    h2h_df = h2h_df.append(data_rows, ignore_index=True)
            else:
                print " Zero or more than One Shikona1 sumo profile(s) matched. Moving on ...\n"
        else:
            print " Shikona1 does not have enough info to scrape bout h2h data. Moving on... "

    if (ind % 100 == 0) & (ind >= row_jump):  # save whole h2h_df every 100 rows

        print "Saving h2h_df @ length: " + str(len(h2h_df.index))
        h2h_df.to_pickle('data/temp_full_h2h.pkl')  # save temp pickle file


h2h_df = h2h_df[cols]  # reorganize columns in desired order

end = time.time()
exec_time = end - start
print "SCRAPING DONE"
print "Execution Time: %2.2f (s)" % exec_time

# --- Save Pandas Dataframe, RENAME EACH TIME, uncomment to save file --- #
# h2h_df.to_pickle('data/recent_full_h2h.pkl')