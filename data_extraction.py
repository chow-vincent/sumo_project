"""Module with helper functions for processing information extracted from html tags using scraping libraries (e.g.
Beautiful Soup). Raw information typically comes as strings, which are cleaned up for later storage into DataFrames.

Ideally final variable names used to store into DataFrames are English, NOT Japanese. These functions are intended to
remove as much Japanese vocabulary as possible.

Example Usage: from data_extraction import extract_rank

"""

import re
from datetime import datetime


# ---------------- EXTRACT HIGHEST RANK --------------- #

def extract_rank(rank):
    """Function to process the highest rank a sumo wrestler has attained during his career. Eliminates whitespace and
    irrelevant date of achievement information.

    :param rank: unicode rank, with possible date of achievement, e.g. 'Yokozuna (March 2017)' or 'Sekiwake'
    :return: unicode rank, e.g. 'Yokozuna' or 'Maegashira 5'
    """

    parse_list = rank.split(' (')
    highest_rank = parse_list[0]  # eliminate ' (MONTH YEAR)'

    return highest_rank


# ---------------- EXTRACT YEAR INFO  --------------- #

def extract_years(birth_date, hatsu_dohyo, intai):
    """Function to process the birth date, debut, and retirement information for a sumo.

    NOTE: age returned is either current age or retirement age (assumes sumo is retired if retirement exists)

    Possible birth_date inputs: '1757', 'January 1757', 'January 27, 1757', 'January 28, 1757 (200 years)'

    Possible hatsu_dohyo/intai inputs: '2001.03', '2001.03 (Makushita)', 'unknown'

    :param birth_date: raw unicode birth date
    :param hatsu_dohyo: raw unicode debut (when sumo debuted professionally)
    :param intai: raw unicode retirement date
    :return: datetime object bday, float age, float active_years, datetime object debut, unicode entry_rank,
    datetime object retirement
    """
    
    # initialize return variables
    age = None
    active_years = None
    entry_rank = None
    
    # initialize datetime variables
    bday = None
    debut = None
    retirement = None
    retirement_known = True  # known retirement date flag
    
    # using this reg_exp to match on hatsu dohyo and retirement
    # group 1: date, group 2: rank (does not exist for retirement), group 3: unknown (status)
    reg_exp = re.compile('^([0-9.]+)(?:\s)?(?:\()?(\w+)?(?:\))?$|^(unknown)$')
    
    # match on birth year
    parse_list = birth_date.split(' (')
    clean_date = parse_list[0]  # eliminate ' (X years)'
    # try the three formats that show up
    for fmt in ('%B %d, %Y', '%B %Y', '%Y'):
        try:
            bday = datetime.strptime(clean_date, fmt)
            # cannot store dates in dataframes older than 1678 b/c of 64 bit overflow (time stored in nanosec)
            # reset to None if this is true
            if bday.year < 1700:
                bday = None
        except ValueError:
            pass

    # match on hatsu dohyo
    debut_result = reg_exp.match(hatsu_dohyo)  # regexp
    if debut_result:

        # 1st group: date, 2nd group: entry rank (if exists), 3rd group: unknown status
        debut_data = debut_result.groups()
        if debut_data[2] != u'unknown':
            try:
                debut = datetime.strptime(debut_data[0], '%Y.%m')
                entry_rank = debut_data[1]
            except ValueError:
                pass
        
    # match on retirement
    retirement_result = reg_exp.match(intai)
    if retirement_result:

        # 1st group: date, 2nd group: entry rank (if exists), 3rd group: unknown status
        retirement_data = retirement_result.groups()
        if retirement_data[2] == u'unknown':
            retirement_known = False  # set flag for if retirement age is unknown
        else:
            try:
                retirement = datetime.strptime(retirement_data[0], '%Y.%m')
            except ValueError:
                pass

    # given above info, calculate age and active years
    if retirement:
        
        # calculate retirement age
        if bday:  # if bday exists, calculate age
            tdelta = retirement - bday
            age = float(tdelta.days)/365.25
            
        # calculate active years
        if debut:  # if debut date exists, calculate active years
            tdelta = retirement - debut
            active_years = float(tdelta.days)/365.25

    # COMBINE retirement_known flag into this else statement
    else:  # if no retirement date, assume currently active or check for unknown
        
        # calculate current age
        if bday and retirement_known:
            tdelta = datetime.now() - bday
            age = float(tdelta.days)/365.25

        # calculate active years as long as start date exists & retirement is KNOWN
        # problem now is that I am checking retirement_data when it doesn't even exist!

        if debut and retirement_known:
            tdelta = datetime.now() - debut
            active_years = float(tdelta.days)/365.25

    return bday, age, active_years, debut, entry_rank, retirement


# ---------------- EXTRACT PLACE OF ORIGIN  --------------- #

def extract_birthplace(shusshin):
    """Function to process birth place/country of origin of sumo wrestler.

    Note that sumo wrestlers from Japan will not have their country specified, only the province they are from.

    :param shusshin: raw unicode birth place/country of origin
    :return: unicode birth place
    """
    
    birth_place = None

    if shusshin and (shusshin != u'-'):
        birth_place = shusshin

    return birth_place


# ---------------- EXTRACT BODY SPECS --------------- #

def extract_body_specs(ht_wt):
    """Function to process height (cm) and weight (kg) of sumo wrestlers.

    Example input: '192 cm 159.2 kg'

    :param ht_wt: raw unicode with height and weight
    :return: float height, float weight
    """
    
    height = None
    weight = None

    reg_exp = re.compile('^([0-9.]+)\scm\s([0-9.]+)\skg$')
    result = reg_exp.match(ht_wt)
    
    if result:
        stats = result.groups()
    
        try:
            height = float(stats[0])
        except TypeError:
            pass
        
        try:
            weight = float(stats[1])
        except TypeError:
            pass
    
    return height, weight


# ---------------- EXTRACT SUMO STABLE (HEYA)  --------------- #

def extract_stable(heya):
    """Function to process stable sumo wrestler is from.

    :param heya: raw unicode heya (sumo stable)
    :return: unicode sumo stable
    """
    
    sumo_stable = None

    if heya and (heya != u'-'):
        sumo_stable = heya

    return sumo_stable


# ---------------- EXTRACT RECORDS --------------- #

def extract_record(record):
    """Function to extract all the records of a sumo wrestler's performance from his basic profile.

    Possible record inputs:
    '10-1-5/16 (2 basho)'         <--- wins-losses-withdrawals/appearances (tourney participations)
    '10-1/11 (2 basho)'           <--- no withdrawals
    '10-1-1-1d-4a-6o/23'          <--- d's, a's, and o's: various forms of draws (ties) in the past with different rules
    '10-1-5/16 (2 basho), 37 Yusho, 21 Jun-Yusho, 2 Gino-Sho, 3 Shukun-Sho, 1 Kanto-Sho, 1 Kinboshi'

    Yusho: tournament win
    Jun-Yusho: tournament 2nd place
    Gino-Sho: prize for technique
    Shukun-Sho: prize for outstanding performance
    Kanto-Sho: prize for fighting spirit
    Kinboshi: win as a Maegashira (lowest-ranked sumo in Makuuchi division) over a Yokozuna (highest rank possible)

    7 possible groups are returned during regular expression matching of input record:
    (0): wins
    (1): losses
    (2): withdrawals
    (3): extra stats for 1800s rikishi (to denote draws)
    (4): appearances
    (5): number of tournament participations
    (6): awards
    e.g. (u'2', u'54', u'96', u'-4a-6o', u'163', u'29', u'37 Yusho, 21 Jun-Yusho')

    :param record: raw unicode with record information
    :return: dict with information stored in 11 possible keys
    """

    wins = None
    losses = None
    withdrawals = None
    appearances = None
    tourneys = None  # number of tourneys participated, NOT wins (see yusho)

    yusho = None
    jun_yusho = None
    gino_sho = None
    shukun_sho = None
    kanto_sho = None
    kinboshi = None
    
    # new reg_exp
    reg_exp = re.compile('^(\d+)-(\d+)(?:-)?(\d+)?(-[a-zA-Z0-9-]+)?/(\d+)\s\((\d+)\sbasho\)(?:,\s)?(.+)?$', re.UNICODE)
    result = reg_exp.match(record)

    # if there is a result, parse further, else if empty string or no matching, continue
    if result:
        stats = result.groups()

        # if any of the stats has TypeError will keep 'None' value
        try:
            wins = int(stats[0])
        except TypeError:
            pass

        try:
            losses = int(stats[1])
        except TypeError:
            pass

        try:
            withdrawals = int(stats[2])
        except TypeError:
            pass

        try:
            appearances = int(stats[4])
        except TypeError:
            pass

        try:
            tourneys = int(stats[5])
        except TypeError:
            pass

        # if there are awards, parse and save
        if stats[6]:
            parse_list = stats[6].split(', ')  # if just 1 item, will return list with that item
            
            # loop through parse_list and find awards
            for award in parse_list:

                if 'Yusho' in award and 'Jun-Yusho' not in award:  # 1st place
                    yusho = int(re.findall('\d+', award)[0])  # findall returns list, index to 1st elem, convert to int

                if 'Jun-Yusho' in award:  # runner-up
                    jun_yusho = int(re.findall('\d+', award)[0])

                if 'Gino-Sho' in award:  # technique prize
                    gino_sho = int(re.findall('\d+', award)[0])

                if 'Shukun-Sho' in award:  # outstanding performance (relative to rank)
                    shukun_sho = int(re.findall('\d+', award)[0])

                if 'Kanto-Sho' in award:  # fought to best of abilities
                    kanto_sho = int(re.findall('\d+', award)[0])

                if 'Kinboshi' in award:  # when maegashira-ranked rikishi defeats yokozuna
                    kinboshi = int(re.findall('\d+', award)[0])

    record_dict = {u'wins': wins, u'losses': losses, u'withdrawals': withdrawals,
                   u'appearances': appearances, u'tourneys': tourneys,
                   u'yusho': yusho, u'jun_yusho': jun_yusho, u'gino_sho': gino_sho,
                   u'shukun_sho': shukun_sho, u'kanto_sho': kanto_sho, u'kinboshi': kinboshi}

    return record_dict


# ---------------- EXTRACT BOUT TITLE TAGS --------------- #

def extract_bout_title_tags(rikishi_title):
    """Function to process info in the title attribute of 'a href' tags associated with a sumo wrestler (on html pages
    with head-to-head bout info). This information is used to lookup the ID of a sumo wrestler in the all_rikishi.pkl
    DataFrame.

    Only sumo stable, birthday, and debut are returned, b/c (1) these are sufficient for looking up the unique ID for a
    sumo wrestler, and (2) this information is guaranteed to exist for relevant sumo wrestlers (other info may be
    missing).

    Example Input: 'Japanese_name_here, Ajigawa, Mongolia, 17.11.1983, 2001.01, 2009.01, 177.5 cm 94 kg, Jd51'

    To see examples of this information, go to: http://sumodb.sumogames.de/Rikishi_opp.aspx?r=1123
    and inspect source html.

    :param rikishi_title: raw unicode with title tags
    :return: unicode sumo stable, datetime object birthday, datetime object debut
    """

    sumo_stable = None
    bday = None
    debut = None

    parse_list = rikishi_title.split(', ')

    if len(parse_list) == 8:  # shikona, heya, shusshin, bday, debut, retirement, weight, rank
        # may have missing info (e.g. missing heya and shusshin)
        # if parse_list is less than eight elements, than skip

        heya = parse_list[1]
        birth_date = parse_list[3]
        hatsu_dohyo = parse_list[4]
        # intai = parse_list[5]  # sumo may not have retired yet, leave out for now

        for fmt in ('%d.%m.%Y', '%m.%Y', '%Y'):  # add relevant formats
            try:
                bday = datetime.strptime(birth_date, fmt)
                # cannot store dates in dataframes older than 1678 b/c of 64 bit overflow (time stored in nanosec)
                # reset to None if this is true
                if bday.year < 1700:
                    bday = None
            except ValueError:
                pass

        for fmt in ('%Y.%m', '%Y'):
            try:
                debut = datetime.strptime(hatsu_dohyo, fmt)
            except ValueError:
                pass

        sumo_stable = extract_stable(heya)

    else:
        print " Not enough tags to reliably extract information (8 pieces of info required). Moving on..."

    return sumo_stable, bday, debut


# ------------- EXTRACT H2H RECORD DATE ---------- #

def extract_date(date_raw):
    """Function to extract date of a h2h match from bout data. NOTE: if only year and month provided, assumes tourney
    took place on the first day of the month.

    :param date_raw: unicode date from bs4 scrape, e.g. u'2001.11'
    :return: h2h date in Python datetime format, e.g. datetime.datetime(2001, 11, 1, 0, 0)
    """

    date = datetime.strptime(date_raw.strip(), '%Y.%m')  # strip whitespace, turn into datetime format

    return date


# ------------- EXTRACT H2H RECORD TOURNEY DAY ---------- #

def extract_tourney_day(day_raw):
    """Function to extract tourney day on which h2h match from bout data happened.

    :param day_raw: unicode day from bs4 scrape, e.g. u'Day 4'
    :return: int tourney day
    """

    day_raw = day_raw.strip()                  # strip whitespace
    tourney_day = int(day_raw.strip(u'Day '))  # strip Day and space

    return tourney_day


# ------------- EXTRACT H2H RECORD SUMO RANK ---------- #

def extract_h2h_rank(rank_raw):
    """Function to extract h2h rank of sumo at the time of the bout.
    Ranking legend:

    * Note, sometimes extra letters exist, e.g. Y1eHD *

    Y1e --> Yokozuna 1 East
    O3w --> Ozeki 3 West
    S1e --> Sekiwake 1 East
    K1e --> Komusubi 1 East
    M9w --> Maegashira 9 West

    J4w --> Juryo 4 West

    Fixed 42 Makuuchi sumos, typical breakdown: 10 San'yaku, 32 Maegashira
    Fixed 28 Juryo sumos (J1 --> J14, East & West)
    Fixed 120 Makushita sumos (Ms1 --> MS60, East & West)
    Fixed 200 Sandanme sumos (Sd1 --> Sd100, East & West)
    200-250 Jonidan sumos (Jd1 --> Jd125), East & West)
    40-90 Jonokuchi sumos (Jk1 --> Jk45, East & West)

    :param rank_raw: unicode rank from bs4 scrape, e.g. u'Ms4e Hakuho'
    :return: unicode rank (fully spelled out), e.g. u'Makushita 4'; convert to int rank during feature generation
    """
    rank = None  # keep as None in case we don't have complete info, e.g. u'Ms' or u'Mz'

    rank_raw = rank_raw.strip()            # strip whitespace
    rank_string = rank_raw.split(u' ')[0]  # split by space, only take rank info, e.g. u'Ms1e'

    reg_exp = re.compile('^([a-zA-z]+)(\d+)(?:[a-zA-Z]+)$')  # define regular exp
    rank_results = reg_exp.match(rank_string)          # match on rank info

    if rank_results:  # if a result exists
        rank_name = rank_results.groups()[0]  # obtain rank title, e.g. u'Ms', u'Jk'

        rank_num = rank_results.groups()[1]   # obtain rank number, e.g. u'1', u'99'

        abbrev_list = [u'Y', u'O', u'S', u'K', u'M', u'J', u'Ms', u'Sd', u'Jd', u'Jk']  # 2 lists of SAME order

        full_list = [u'Yokozuna', u'Ozeki', u'Sekiwake', u'Komusubi', u'Maegashira',
                     u'Juryo', u'Makushita', u'Sandanme', u'Jonidan', u'Jonokuchi']

        ind = abbrev_list.index(rank_name)  # obtain index of rank title
        full_rank = full_list[ind]          # search for full title at that index

        rank = unicode(full_rank + u' ' + rank_num)  # concatenate, e.g. u'Makushita 10'

    return rank


# ------------- EXTRACT H2H RECORD BOUT OUTCOMES  ---------- #

def extract_outcome(outcome_raw):
    """Function to extract outcome of h2h record from bout data.

    Possible outcomes to deal with:

    shiro(boshi) - victory, denoted by white circle
    kuro(boshi) - loss, denoted by black circle

    fusensho - victory by default, absence of opponent due to injury/retirement, denoted by white square
    fusenpai - loss by default, absence due to injury/retirement, denoted by black square

    http://www.sumoforum.net/forums/topic/32691-draws-in-sumo/
    * It appears that all forms of draws are denoted as hikiwake for h2h record outcomes. *
    azukari - draw (match too close to call), denoted by white triangle & letter "a"
    hikiwake - draw (match too long, rikishi exhausted), denoted by white triangle & letter "d"
    itamiwake - draw (one/both rikishi injured, unable to continue), denoted by ? & letter "d"
    mushobu - draw (match too close to call, gyoji abstains from calling), denoted by ? & letter "o", obsolete 1860's

    :param outcome_raw: string (not unicode) outcome from bs4 scrape, e.g. 'img/hoshi_kuro.gif'
    :return: unicode outcome of the match, e.g. u'fusen_win', u'fusen_loss'
    """

    reg_exp = re.compile('^(?:img/hoshi_)([a-z]+)(?:.gif)$')
    outcome_result = reg_exp.match(outcome_raw.strip())

    outcome = unicode(outcome_result.groups()[0])  # cast as unicode

    # possible outcomes: shiro, kuro, fusensho, fusenpai, hikiwake
    outcome_list = [u'shiro', u'kuro', u'fusensho', u'fusenpai', u'hikiwake']

    if outcome not in outcome_list:
        raise Exception('Unknown match outcome: ' + str(outcome))

    return outcome


# ------------- EXTRACT H2H RECORD BOUT OUTCOMES  ---------- #

def extract_kimarite(kimarite_raw):
    """Function to extract kimarite from h2h data.

    There are 82 (+4) recognized kimarite, https://en.wikipedia.org/wiki/Kimarite. It is possible to see any of these
    in the h2h record, along with the different types of draws that can occur (see extract_outcome for details).

    For now, assume that raw kimarite are correct. There are too many possible kimarite from previous
    eras (in addition to the current 82+4) to hold a complete list with which to check.

    :param kimarite_raw: unicode kimarite from bs4 scrape, e.g. u'uwatenage'
    :return: unicode kimarite
    """

    if kimarite_raw.strip() == u'':  # strip any whitespace, e.g. u'\xa0'
        kimarite = None
    else:
        kimarite = unicode(kimarite_raw.strip())  # typecasting gets rid of bs4 recursive storage info

    # 82 (+4) kimarite, along with possible draw types
    # since there are so many kimarite from previous eras, assume spellings are correct and store all kimarite

    # obsolete list of possible kimarite below, leave commented for now

    # kimarite_list = [None,
    #                  u'abisetaoshi', u'oshidashi', u'oshitaoshi', u'tsukidashi', u'tsukitaoshi',
    #                  u'yorikiri', u'yoritaoshi', u'ipponzeoi', u'kakenage', u'koshinage', u'kotenage', u'kubinage',
    #                  u'nichonage', u'shitatedashinage', u'shitatenage', u'sukuinage', u'tsukaminage',
    #                  u'uwatedashinage', u'uwatenage', u'yaguranage', u'ashitori', u'chongake', u'kawazugake',
    #                  u'kekaeshi', u'ketaguri', u'kirikaeshi', u'komatasukui', u'kozumatori', u'mitokorozeme',
    #                  u'nimaigeri', u'omata', u'sotogake', u'sotokomata', u'susoharai', u'susotori', u'tsumatori',
    #                  u'uchigake', u'watashikomi', u'amiuchi', u'gasshohineri', u'harimanage', u'kainahineri',
    #                  u'katasukashi', u'kotehineri', u'makiotoshi', u'osakate', u'sabaori', u'sakatottari',
    #                  u'shitatehineri', u'sotomuso', u'tokkurinage', u'tottari', u'tsukiotoshi', u'uchimuso',
    #                  u'uwatehineri', u'zubuneri', u'izori', u'kakezori', u'shumokuzori', u'sototasukizori',
    #                  u'tasukizori', u'tsutaezori', u'hatakikomi', u'hikiotoshi', u'hikkake', u'kimedashi',
    #                  u'kimetaoshi', u'okuridashi', u'okurigake', u'okurihikiotoshi', u'okurinage', u'okuritaoshi',
    #                  u'okuritsuridashi', u'okuritsuriotoshi', u'sokubiotoshi', u'tsuridashi', u'tsuriotoshi',
    #                  u'ushiromotare', u'utchari', u'waridashi', u'yobimodoshi', u'fumidashi', u'isamiashi',
    #                  u'koshikudake', u'tsukihiza', u'tsukite',
    #                  u'fusen',
    #                  u'azukari', u'hikiwake', u'itamiwake', u'mushobu']  # also include names of draw outcomes
    #
    # if kimarite not in kimarite_list:
    #     raise Exception('Unknown kimarite: ' + str(kimarite))

    return kimarite
