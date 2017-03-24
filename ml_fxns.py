"""Module with helper functions for various machine learning tasks. Could include data pre-processing tasks, prediction
tasks, etc.

Example Usage: from ml_fxns import check_makuuchi

"""

import numpy as np
import pandas as pd
import re
from datetime import datetime


# --- Filter Out Non-Makuuchi Sumo Wrestlers --- #

def check_makuuchi(current_rank):
    """Function to check if sumo wrestler currently is in or retired in the Makuuchi division.

    :param current_rank: unicode rank (e.g. u'Makushita 1')
    :return: boolean True if the rikishi is Makuuchi division, else false
    """

    check = False  # burden should fall on the code to turn True

    rank_list = [u'Yokozuna', u'Ozeki', u'Sekiwake', u'Komusubi', u'Maegashira']

    if any(item in current_rank for item in rank_list):
        check = True

    return check


# --- Map Categorical Rank to Numerical Value --- #

def map_rank(current_rank):
    """Function to map a rank title into a numerical value. For example, u'Yokozuna' is mapped to an int equal to 1.
    Used in generating features. There can be multiple rikishi at the same rank in a tournament.
    See the following for details: https://en.wikipedia.org/wiki/Professional_sumo_divisions

    Yokozuna --> 1
    Ozeki --> 2
    ...
    Maegashira 1 --> 5, no. of Maegashira ranks ranges from 15-17. Thus, rank range = 5 to 21.
    ...
    Juryo 1 --> 22, no. of Juryo rikishi fixed at 28. Thus, rank range = 22 to 35.
    ...
    Makushita 1 --> 36, no. of Makushita rikishi fixed at 120. Thus, rank range = 36 to 95.
    ...
    Sandanme 1 --> 96, no. of Sandanme rikishi fixed at 200. Thus, rank range = 96 to 195.
    ...
    Jonidan 1 --> 196, no. of Jonidan rikishi ranges from 200-250. Thus, rank range = 196 to 320.
    ...
    Jonokuchi 1 --> 321, no. of Jonokuchi rikishi ranges from 40-90. Thus, rank range = 321 to 365.

    :param current_rank: unicode rank title, e.g. u'Maegashira 5' or 'Jonidan 10'
    :return: int rank
    """

    num_rank = None

    if u'Yokozuna' in current_rank:
        num_rank = 1
    if u'Ozeki' in current_rank:
        num_rank = 2
    if u'Sekiwake' in current_rank:
        num_rank = 3
    if u'Komusubi' in current_rank:
        num_rank = 4

    title_list = [u'Maegashira', u'Juryo', u'Makushita', u'Sandanme', u'Jonidan', u'Jonokuchi']
    offset_list = [4, 21, 35, 95, 195, 320]

    for title in title_list:                        # loop through title_list
        if title in current_rank:                   # if a title is in the current rank
            ind = title_list.index(title)           # lookup offset
            offset = offset_list[ind]
            parse_list = current_rank.split(' ')
            num_rank = int(parse_list[1]) + offset  # and add offset to title number
            break

    if num_rank is None:
        raise Exception('Unable to map categorical rank to numerical value.')

    return num_rank


# --- Calculate Age of Sumo At the Time of a H2H Match --- #

def calculate_age(date, bday):
    """Function to calculate age at the time of a h2h match. Used when generating features.

    :param date: datetime object representing year & month in which tourney happened
    :param bday: datetime object representing birth date of sumo
    :return: float age of sumo, calculated by time from sumo bday to time of tourney
    """

    tdelta = date - bday
    age = float(tdelta.days) / 365.25

    return age


# --- Calculate a Sumo's Active Years At the Time of a H2H Match --- #

def calculate_active_years(date, debut):
    """Function to calculate number of years a sumo has been active at the time of a h2h match. Used when generating
    features.

    :param date: datetime object representing year & month in which tourney happened
    :param debut: datetime object representing sumo's debut (hatsu dohyo)
    :return: float active years of sumo, calculated by time from debut to time of tourney
    """

    tdelta = date - debut
    active_years = float(tdelta.days) / 365.25

    return active_years


# ---- Time Discounting: Calculate Weight to Assign Historical Match --- #

def discount_weight(current_date, previous_date, discount_factor):
    """Function to calculate the weight for a historical h2h match. Uses time discounting, where the weight is the
    minimum of (discount_factor^years_since_match, discount_factor). Thus, any matches within a year are
    assigned a weight equal to the discount factor, and matches beyond a year drop in value exponentially.

    Used for generating features, such as h2h win percentage.

    :param current_date: datetime object, date of h2h match being analyzed
    :param previous_date: datetime object, date of a previous h2h match
    :param discount_factor: float, how much to discount older matches
    :return: float, the weight to assign a h2h match in the past
    """

    # create a lookup table
    N = 100
    time = np.linspace(0, 10, N)

    exp_curve = np.power(np.ones(N)*discount_factor, time)

    discount_weights = np.minimum(exp_curve, discount_factor)

    # calculate time between tourney dates
    tdelta = current_date - previous_date
    years_since = float(tdelta.days) / 365.25

    # interpolate to find weight
    if years_since <= 1:
        weight = discount_factor
    else:
        ind = np.abs(time - years_since).argmin()  # find closest value
        weight = discount_weights[ind]

    return weight


# ---- Calculate H2H WP From Historical Data & Using Time Discounting --- #

def calculate_h2h_wp(current_date, rel_df, ID1):
    """Function to estimate a head-to-head win percentages between two sumo wrestlers, using a weighted average over all
    prior matches, weighted by time discounting. If there is no head-to-head history, then the default win percentages
    are 50/50.

    NOTE: rel_df could have switched orientations (e.g. 1st sumo switched with 2nd sumo for some rows), and this code
    takes this into account.

    :param current_date: datetime object representing "current date" of match that we are predicting
    :param rel_df: Pandas DataFrame containing data of all previous matches between the two sumo wrestlers
    :param ID1: int representing ID of the first sumo for ensuring correct orientation of sumo wrestlers
    :return: two floats, representing the sumo wrestlers' head-to-head win percentages
    """

    if rel_df.empty:
        h2h_wp1 = 0.5
        h2h_wp2 = 0.5
    else:

        weight_list = []
        numerator1 = []
        numerator2 = []

        # weighted sum calculation: (w1*x1 + w2*x2 + ... + wn*xn)/(w1 + ... + wn)

        for _, row in rel_df.iterrows():

            previous_date = row['date']
            weight = discount_weight(current_date, previous_date, discount_factor=0.8)
            weight_list.append(weight)

            if row['ID1'] == ID1:  # if ID1 matches sumo 1, proceed normally

                if (row['outcome1'] == u'shiro') and (row['outcome2'] == u'kuro'):  # win by sumo 1, loss by sumo 2
                    numerator1.append(weight)  # add weight multiplied by 1 (win)
                    numerator2.append(0.)       # add weight multiplied by 0 (loss)

                elif (row['outcome1'] == u'kuro') and (row['outcome2'] == u'shiro'):  # win by sumo 2, loss by sumo 1
                    numerator1.append(0.)
                    numerator2.append(weight)

            elif row['ID2'] == ID1:  # if ID2 matches sumo 1, proceed with things switched

                if (row['outcome1'] == u'shiro') and (row['outcome2'] == u'kuro'):  # win by sumo 2, loss by sumo 1
                    numerator1.append(0.)  # add weight multiplied by 1 (win)
                    numerator2.append(weight)       # add weight multiplied by 0 (loss)

                elif (row['outcome1'] == u'kuro') and (row['outcome2'] == u'shiro'):  # win by sumo 1, loss by sumo 2
                    numerator1.append(weight)
                    numerator2.append(0.)

            else:
                print "Not matching proper criteria!!!"

        h2h_wp1 = float(sum(numerator1))/float(sum(weight_list))
        h2h_wp2 = float(sum(numerator2))/float(sum(weight_list))

    return h2h_wp1, h2h_wp2


# ------ Predict Outcome for an Upcoming H2H Match ------ #

def predict_outcome(shikona1, shikona2, rank1, rank2, model):
    """Function to predict the outcome of a single head-to-head sumo match. Provides the outcome of sumo 1 vs. sumo 2,
    as well as the associated probabilities/certainty of the model

    :param shikona1: unicode full shikona name of sumo 1, e.g. u'Hakuho Sho'
    :param shikona2: unicode full shikona name of sumo 2
    :param rank1: unicode title rank of sumo 1, e.g. u'Maegashira 5'
    :param rank2: unicode title rank of sumo 2
    :param model: sklearn model (e.g. logistic regression))
    :return: int outcome for sumo 1 (1 for win, 0 for loss), and float probabilities of sumo 1 & 2 winning
    """

    # ----- Load Requisite Data ---- #

    rikishi_df = pd.read_pickle('data/all_rikishi.pkl')
    h2h_df = pd.read_pickle('data/recent_full_h2h.pkl')
    feature_df = pd.read_pickle('data/recent_feature_df.pkl')

    # --- Apply Requisite Conditions Used to Extract H2H Data --- #
    logical = rikishi_df['shikona'].map(lambda x: x is not None) & \
              rikishi_df['sumo_stable'].map(lambda x: x is not None) & \
              rikishi_df['bday'].map(lambda x: pd.notnull(x)) & \
              rikishi_df['debut'].map(lambda x: pd.notnull(x))
    filtered_df = rikishi_df[logical]

    # ----- Remove Rows Without Requisite Features ----- #

    logical = (pd.notnull(filtered_df['height'])) & (pd.notnull(filtered_df['weight'])) & \
              (pd.notnull(filtered_df['bday'])) & (pd.notnull(filtered_df['debut'])) & \
              (~filtered_df['highest_rank'].isnull())

    filtered_df = filtered_df[logical]

    # --- Extract Stored Info, Prepare Feature Vector --- #
    date = datetime.now()

    sumo1_df = filtered_df[filtered_df['shikona'] == shikona1]
    sumo2_df = filtered_df[filtered_df['shikona'] == shikona2]

    ID1 = sumo1_df['rikishi_ID'].item()
    ID2 = sumo2_df['rikishi_ID'].item()

    height_diff = sumo1_df['height'].item() - sumo2_df['height'].item()
    weight_diff = sumo1_df['weight'].item() - sumo2_df['weight'].item()

    bday1 = sumo1_df['bday'].item()
    bday2 = sumo2_df['bday'].item()
    age_diff = calculate_age(date, bday1) - calculate_age(date, bday2)

    debut1 = sumo1_df['debut'].item()
    debut2 = sumo2_df['debut'].item()
    active_diff = calculate_active_years(date, debut1) - calculate_active_years(date, debut2)

    rank_diff = map_rank(rank1) - map_rank(rank2)

    logical = ((h2h_df['ID1'] == ID1) & (h2h_df['ID2'] == ID2)) | \
              ((h2h_df['ID1'] == ID2) & (h2h_df['ID2'] == ID1))
    rel_df = h2h_df[logical]

    logical = (h2h_df['date'] < date)  # h2h date is less than current date
    rel_df = rel_df[logical]

    h2h_wp1, h2h_wp2 = calculate_h2h_wp(date, rel_df, ID1)  # if rel_df is empty, then say h2h_wp is 50/50
    h2h_diff = h2h_wp1 - h2h_wp2

    feature_vector = [{'height_diff': height_diff, 'weight_diff': weight_diff, 'age_diff': age_diff,
                       'active_diff': active_diff, 'rank_diff': rank_diff, 'h2h_diff': h2h_diff}]

    # --- Predict Outcome --- #
    # scale feature vector & reshape for 1D array
    predict_df = pd.DataFrame(feature_vector)

    X = predict_df.loc[:, ['height_diff', 'weight_diff', 'age_diff', 'active_diff', 'rank_diff', 'h2h_diff']]

    stdevs = feature_df.std()

    X_scaled = X.copy()

    # --- Standardize Features --- #
    # keep h2h_diff as is
    X_scaled['height_diff'] = X['height_diff'] / stdevs['height_diff']
    X_scaled['weight_diff'] = X['weight_diff'] / stdevs['weight_diff']
    X_scaled['age_diff'] = X['age_diff'] / stdevs['age_diff']
    X_scaled['active_diff'] = X['active_diff'] / stdevs['active_diff']
    X_scaled['rank_diff'] = X['rank_diff'] / stdevs['rank_diff']

    prediction = int(model.predict(X_scaled)[0])
    pred_prob = model.predict_proba(X_scaled)

    print "\nPrediction for Sumos: " + str(shikona1) + ", " + str(shikona2)
    print "Outcome: %2d" % prediction
    print "Probability that Sumo 1 Wins: %0.3f" % pred_prob[0][1]
    print "Probability that Sumo 2 Wins: %0.3f" % pred_prob[0][0]

    print "Feature Vector: "
    print "height_diff: %2.3f" % height_diff
    print "weight_diff: %2.3f" % weight_diff
    print "age_diff: %2.3f" % age_diff
    print "active_diff: %2.3f" % active_diff
    print "rank_diff: %2.3f" % rank_diff
    print "h2h_diff: %2.3f\n" % h2h_diff

    prob_win1 = float(pred_prob[0][1])
    prob_win2 = float(pred_prob[0][0])

    return prediction, prob_win1, prob_win2


# --- Read In Text Files of Match Schedules --- #

def read_schedule(match_file):
    """Function to read in h2h match schedule for 1 day of tournament.

    :param match_file: filename pointing to text file with h2h matchups (copied from excel spreadsheet)
    :return: list of tuples, with each tuple a head-to-head match
    """

    with open(match_file) as input_file:
        match_list = []
        for line in input_file:
            test = re.split('\s+', line.strip())
            h2h = (unicode(test[0]), unicode(test[1]))
            match_list.append(h2h)

    return match_list
