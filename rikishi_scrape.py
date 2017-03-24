"""Module with functions used for scraping data with Beautiful Soup. Functions are used when scraping data from
multiple html pages/sumo wrestlers. Example information gathered includes: basic sumo wrestler stats (e.g. height), as
well as head-to-head records among sumo wrestlers.

Example Usage: from rikishi_scrape import basic_scrape

"""

import urllib2
import bs4
from data_extraction import extract_rank, extract_years, extract_birthplace, \
                            extract_body_specs, extract_stable, extract_record, extract_bout_title_tags, \
                            extract_date, extract_tourney_day, extract_h2h_rank, extract_outcome, extract_kimarite
from database_ops import match_ID


# ---------------- SCRAPE BASIC DATA FOR ONE RIKISHI  --------------- #

def basic_scrape(rikishi_url):
    """Function to scrape basic information for a sumo wrestler.

    Example rikishi_url: http://sumodb.sumogames.de/Rikishi.aspx?r=1111

    :param rikishi_url: url to basic profile
    :return: list of compiled basic statistics from a sumo wrestler
    """

    source = urllib2.urlopen(rikishi_url).read()  # read in url and turn html page into bs4 soup
    soup = bs4.BeautifulSoup(source, 'lxml')

    tables = soup.find_all('table', {'class': 'rikishidata'})
    rows = tables[1].find_all('tr')  # there are two tables with the same class, pick 2nd table

    # initialize desired cell values
    # apart from shikona, raw strings are captured with Japanese variables, but stored in English for readability
    shikona = u''
    rank = u''
    birth_date = u''
    shusshin = u''
    ht_wt = u''
    heya = u''
    hatsu_dohyo = u''
    intai = u''

    career_record = u''
    makuuchi_record = u''
    yokozuna_record = u''
    ozeki_record = u''
    sekiwake_record = u''
    komusubi_record = u''
    maegashira_record = u''
    juryo_record = u''
    makushita_record = u''
    sandanme_record = u''
    jonidan_record = u''
    jonokuchi_record = u''

    # collect details & career record
    for row in rows:  # iterate through rows
        cells = row.find_all('td')

        # --- Look for Desired Information --- #
        if (cells[0].text.strip() == u'Shikona') & (len(cells) == 2):  # sumo name
            shikona = cells[1].text.strip()  # extract text, and strip leading/ending whitespace for consistency
        if (cells[0].text.strip() == u'Highest Rank') & (len(cells) == 2):
            rank = cells[1].text.strip()
        if (cells[0].text.strip() == u'Birth Date') & (len(cells) == 2):
            birth_date = cells[1].text.strip()
        if (cells[0].text.strip() == u'Shusshin') & (len(cells) == 2):  # place of origin
            shusshin = cells[1].text.strip()
        if (cells[0].text.strip() == u'Height and Weight') & (len(cells) == 2):
            ht_wt = cells[1].text.strip()
        if (cells[0].text.strip() == u'Heya') & (len(cells) == 2):
            heya = cells[1].text.strip()
        if (cells[0].text.strip() == u'Hatsu Dohyo') & (len(cells) == 2):  # career start date
            hatsu_dohyo = cells[1].text.strip()
        if (cells[0].text.strip() == u'Intai') & (len(cells) == 2):  # retirement date
            intai = cells[1].text.strip()

        if (cells[0].text.strip() == u'Career Record') & (len(cells) == 2):
            career_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'In Makuuchi') & (len(cells) == 2):  # &nbsp; converted to unicode space
            makuuchi_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'As Yokozuna') & (len(cells) == 2):
            yokozuna_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'As Ozeki') & (len(cells) == 2):
            ozeki_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'As Sekiwake') & (len(cells) == 2):
            sekiwake_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'As Komusubi') & (len(cells) == 2):
            komusubi_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'As Maegashira') & (len(cells) == 2):
            maegashira_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'In Juryo') & (len(cells) == 2):
            juryo_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'In Makushita') & (len(cells) == 2):
            makushita_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'In Sandanme') & (len(cells) == 2):
            sandanme_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'In Jonidan') & (len(cells) == 2):
            jonidan_record = cells[1].text.strip()
        if (cells[0].text.strip() == u'In Jonokuchi') & (len(cells) == 2):
            jonokuchi_record = cells[1].text.strip()

    # --- Process Beautiful Soup Information into Storable Data --- #
    highest_rank = extract_rank(rank)
    bday, age, active_years, debut, entry_rank, retirement = extract_years(birth_date, hatsu_dohyo, intai)
    birth_place = extract_birthplace(shusshin)
    height, weight = extract_body_specs(ht_wt)
    sumo_stable = extract_stable(heya)
    
    career_record_dict = extract_record(career_record)
    makuuchi_record_dict = extract_record(makuuchi_record)
    yokozuna_record_dict = extract_record(yokozuna_record)
    ozeki_record_dict = extract_record(ozeki_record)
    sekiwake_record_dict = extract_record(sekiwake_record)
    komusubi_record_dict = extract_record(komusubi_record)
    maegashira_record_dict = extract_record(maegashira_record)
    juryo_record_dict = extract_record(juryo_record)
    makushita_record_dict = extract_record(makushita_record)
    sandanme_record_dict = extract_record(sandanme_record)
    jonidan_record_dict = extract_record(jonidan_record)
    jonokuchi_record_dict = extract_record(jonokuchi_record)

    # store data
    compiled_stats = [shikona, highest_rank, bday, age, birth_place, height, weight, sumo_stable,
                      active_years, debut, entry_rank, retirement, career_record_dict, makuuchi_record_dict,
                      yokozuna_record_dict, ozeki_record_dict, sekiwake_record_dict, komusubi_record_dict,
                      maegashira_record_dict, juryo_record_dict, makushita_record_dict, sandanme_record_dict,
                      jonidan_record_dict, jonokuchi_record_dict]

    return compiled_stats


# ---------------- SCRAPE JUST SHIKONA FOR ONE RIKISHI  --------------- #

def shikona_scrape(rikishi_url):
    """Function to strictly lookup the full shikona (Japanese sumo name) for a sumo wrestler.

    Example rikishi_url: http://sumodb.sumogames.de/Rikishi.aspx?r=1111

    :param rikishi_url: url to basic profile
    :return: unicode full shikona
    """

    source = urllib2.urlopen(rikishi_url).read()
    soup = bs4.BeautifulSoup(source, 'lxml')

    tables = soup.find_all('table', {'class': 'rikishidata'})
    rows = tables[1].find_all('tr')  # there are two tables with the same class, pick 2nd table

    shikona = u''  # initialize empty shikona

    for row in rows:  # iterate through rows
        cells = row.find_all('td')
        if (cells[0].text.strip() == u'Shikona') & (len(cells) == 2):  # sumo name
            shikona = cells[1].text.strip()

    return shikona


# ---------------- SCRAPE H2H DATA FOR ONE RIKISHI  --------------- #

def full_h2h_scrape(shikona1, ID1, bout_url, filtered_df):
    """Function to scrape all h2h bouts for one sumo wrestler. Unlike h2h_scrape(), this fxn stores more information:

    - date of h2h match
    - tourney day
    - rank of each sumo
    - outcome for each sumo
    - kimarite (move used by winning sumo)

    :param shikona1: unicode shikona name of sumo1
    :param ID1: int ID of sumo1
    :param bout_url: unicode? url to the h2h bout page for sumo1
    :param filtered_df: pandas df, filtering out rows without enough info to uniquely identify sumo
    :return: list of dicts, with each row representing one h2h match
    """

    all_rows = []  # list of dictionaries, where each dict is a row in df

    source = urllib2.urlopen(bout_url).read()
    soup = bs4.BeautifulSoup(source, 'lxml')  # turn into soup

    # head-to-head record containing rikishi names and win-loss data are located in "spans" in html
    h2h_records = soup.find_all('span', {'class': 'rb_basho'})

    print " Number of Records: " + str(len(h2h_records))

    # if h2h_records empty, then data will not be added to h2h_df and no error raised

    for record in h2h_records:

        h2h_rows = []  # to store rows for one sumo to sumo match-up

        # initialize ID2
        ID2 = u''

        # --- Extract Tag Info --- #
        span_text = record.find_all(text=True)             # get all text in span tag
        links = record.find_all('a', href=True)            # one row
        ext = links[1]['href']                             # only extract second link (2nd rikishi)
        rikishi_title = links[1]['title']                  # extract title attribute text
        rikishi_url = "http://sumodb.sumogames.de/" + ext  # link to second rikishi as backup identification info

        # --- Find 2nd Rikishi ID --- #
        shikona2 = span_text[2]
        print shikona2
        sumo_stable, bday, debut = extract_bout_title_tags(rikishi_title)  # if cannot extract tags, move on

        if (sumo_stable is not None) and (bday is not None) and (debut is not None):

            ID2 = match_ID(shikona2, sumo_stable, bday, debut, filtered_df, rikishi_url)

            # --- Obtain Raw Info from Tables --- #
            table = record.find_next('table')
            rows = table.find_all('tr')

            for row in rows:

                # --- Initialize Variables --- #
                date = None
                tourney_day = None
                rank1 = None
                rank2 = None
                outcome1 = None
                outcome2 = None
                kimarite = None
                flag = False  # turn on flag if there is inconsistency in data

                data_dict = {}  # initialize a dict to store one row of df

                cells = row.find_all('td')

                date_raw = cells[0].text  # extract text from list of cells

                day_cell = row.find_all('td', {'class': 'rb_day'})[0]  # find rb_day cell from list of cells
                day_raw = day_cell.text                                  # extract tourney day

                sumo_ranks = row.find_all('td', {'class': 'rb_opp'})   # find list of rb_opp CELLS
                rank1_raw = sumo_ranks[0].text                           # extract sumo1 rank
                rank2_raw = sumo_ranks[1].text                           # extract sumo2 rank

                outcomes = row.find_all('td', {'class': 'tk_kekka'})   # find list of h2h results
                outcome1_raw = outcomes[0].find_all('img')[0]['src']     # extract outcome (in form of url string)
                outcome2_raw = outcomes[1].find_all('img')[0]['src']

                kim_cell = row.find_all('td', {'class': 'rb_kim'})     # find list of kimarite
                kimarite_raw = kim_cell[0].text                          # extract kimarite

                # --- Prepare Raw Info for Storing --- #
                date = extract_date(date_raw)
                tourney_day = extract_tourney_day(day_raw)

                rank1 = extract_h2h_rank(rank1_raw)
                rank2 = extract_h2h_rank(rank2_raw)

                outcome1 = extract_outcome(outcome1_raw)
                outcome2 = extract_outcome(outcome2_raw)

                kimarite = extract_kimarite(kimarite_raw)

                # --- Store Data --- #
                # explicit typecasting, navigable bs4 elements lead to pickling problems (recursive unicode elmts)
                data_dict.update({u'date': date, u'tourney_day': int(tourney_day),
                                  u'ID1': int(ID1), u'shikona1': unicode(shikona1), u'rank1': unicode(rank1),
                                  u'outcome1': unicode(outcome1),

                                  u'kimarite': unicode(kimarite),

                                  u'ID2': int(ID2), u'shikona2': unicode(shikona2), u'rank2': unicode(rank2),
                                  u'outcome2': unicode(outcome2),
                                  u'flag': flag})

                h2h_rows.append(data_dict)

            all_rows.extend(h2h_rows)  # add h2h data from a sumo-to-sumo match-up to entire data collection of dicts

        else:
            "Not sufficient info for matching sumo with filtered_df. Moving on..."

    return all_rows


# ---------------- SCRAPE SHIKONA, ID, AND BOUT URL FOR ONE RIKISHI --------------- #
# called in scrape_multiple_h2h.py

def bouturl_scrape(rikishi_url):
    """Function to scrape full shikona, ID, and bout url for one sumo wrestler.

    For example, when generating features, this function is used to obtain the url to the bout html page containing
    all head-to-head bout information for a sumo wrestler.

    :param rikishi_url: url to basic profile
    :return: unicode shikona, unicode sumo_stable, url to bout info
    """

    # if this fxn returns None for sumo_stable, then safe to assume that sumo has useless data
    shikona = u''
    heya = u''

    source = urllib2.urlopen(rikishi_url).read()
    soup = bs4.BeautifulSoup(source, 'lxml')

    # -- Extract Shikona --- #
    tables = soup.find_all('table', {'class': 'rikishidata'})
    rows = tables[1].find_all('tr')  # there are two tables with the same class, pick 2nd table
    for row in rows:  # iterate through rows
        cells = row.find_all('td')
        if (cells[0].text.strip() == u'Shikona') & (len(cells) == 2):  # sumo name
            shikona = cells[1].text.strip()
        if (cells[0].text.strip() == u'Heya') & (len(cells) == 2):
            heya = cells[1].text.strip()

    # --- Extract Bout URL --- #
    links = soup.find_all('a', href=True, text='Show all bouts by opponent')
    extension = links[0]['href']
    bout_url = "http://sumodb.sumogames.de/" + extension

    # --- Extract Sumo Stable -- #
    sumo_stable = extract_stable(heya)

    # --- Raise Exceptions --- #
    if shikona == u'':
        raise Exception('Not able to extract shikona from: ' + rikishi_url)
    if bout_url == u'':
        raise Exception('No bout url exists for: ' + shikona)
    # allow NoneType for sumo_stable, b/c we will check for this in main h2h script

    return shikona, sumo_stable, bout_url
