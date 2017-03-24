""" Script to generate DataFrame containing feature data and labels.

Each row in the resulting DataFrame contains features and labels. Row only generated if (1) h2h data exists, and (2)
if both sumo wrestlers have the requisite feature info.

Usage:
(1) Set up pickle files with relevant DataFrames (basic profile info, and head-to-head info)
(2) Set up pickle file save name (bottom of script)
(3) Run feature_generation.py


"""

import pandas as pd
import time
import random
from ml_fxns import map_rank, check_makuuchi, calculate_age, calculate_active_years, calculate_h2h_wp


# --- Import Data --- #
rikishi_df = pd.read_pickle('data/all_rikishi.pkl')
h2h_df = pd.read_pickle('data/recent_full_h2h.pkl')


# --- Apply Requisite Conditions Used to Extract H2H Data --- #
# only sumos that satisfied these conditions were used to store head-to-head data into h2h_df DataFrame
logical = rikishi_df['shikona'].map(lambda x: x is not None) & \
          rikishi_df['sumo_stable'].map(lambda x: x is not None) & \
          rikishi_df['bday'].map(lambda x: pd.notnull(x)) & \
          rikishi_df['debut'].map(lambda x: pd.notnull(x))
filtered_df = rikishi_df[logical]


# ----- Remove Rows Without Requisite Features ----- #
# eliminate missing data
logical = (pd.notnull(filtered_df['height'])) & (pd.notnull(filtered_df['weight'])) & \
        (pd.notnull(filtered_df['bday'])) & (pd.notnull(filtered_df['debut'])) & \
        (~filtered_df['highest_rank'].isnull()) & (filtered_df['highest_rank'].apply(check_makuuchi))

filtered_df = filtered_df[logical]

filtered_df[['height', 'weight']] = filtered_df[['height', 'weight']].astype('float64')  # cast correct data types


# --- Pre-process H2H DataFrame: Filter out NoneTypes, Select Win Outcomes, & Sort Chronologically --- #
# NOTE: datatypes (including NoneTypes) for rank/kimarite were cast to unicode for convenience

# remove nonetypes
logical = (h2h_df['rank1'] != u'None') & (h2h_df['rank2'] != u'None') & (h2h_df['kimarite'] != u'None')
h2h_df = h2h_df[logical]

# remove outcomes that were draws or defaults
logical = ((h2h_df['outcome1'] == u'shiro') | (h2h_df['outcome1'] == u'kuro')) & ((h2h_df['outcome2'] == u'shiro') |
          (h2h_df['outcome2'] == u'kuro'))
h2h_df = h2h_df[logical]

# sort chronologically (for easier readability in resulting feature df)
h2h_df = h2h_df.sort_values(by='date', ascending=True)  # debut 2000 to 2017


# ================ Loop Over H2H DF ================ #

checkpoint1 = 0
checkpoint2 = len(h2h_df.index)

compiled_dicts = []  # list for storing all the dicts generated

counter = 1

start = time.time()
for ind, row in h2h_df.iterrows():

    if counter % 1000 == 0:
        print "Counter: %4d" % counter  # print a counter every once in a while to show progress

    # watch out for this 'if' statement; the ind is the DataFrame label, NOT necessarily consecutive index
    if (ind >= checkpoint1) & (ind <= checkpoint2):

        # --- Extract Info --- #
        ID1 = row['ID1']
        ID2 = row['ID2']

        rikishi1 = filtered_df[filtered_df['rikishi_ID'] == ID1]
        rikishi2 = filtered_df[filtered_df['rikishi_ID'] == ID2]

        # possible to get h2h_df rikishi WITHOUT min feature requirements to uniquely identify in filtered_df
        if (not rikishi1.empty) and (not rikishi2.empty):

            print "# --- Generating Features: Row: %2d" % ind + " --- #"

            # --- Continue Extracting Relevant Info --- #
            date = row['date']
            rank1 = row['rank1']
            rank2 = row['rank2']
            outcome1 = row['outcome1']
            outcome2 = row['outcome2']

            # --- Generate Feature Values (ALWAYS Sumo1 Minus Sumo2) --- #
            height_diff = rikishi1['height'].item() - rikishi2['height'].item()  # diff in height (cm)
            weight_diff = rikishi1['weight'].item() - rikishi2['weight'].item()  # diff in weight (kg)

            bday1 = rikishi1['bday'].item()
            bday2 = rikishi2['bday'].item()
            age1 = calculate_age(date, bday1)
            age2 = calculate_age(date, bday2)
            age_diff = age1 - age2  # diff in age in yrs

            debut1 = rikishi1['debut'].item()
            debut2 = rikishi2['debut'].item()
            active_years1 = calculate_active_years(date, debut1)
            active_years2 = calculate_active_years(date, debut2)
            active_diff = active_years1 - active_years2  # difference in active no. of years

            num_rank1 = map_rank(rank1)
            num_rank2 = map_rank(rank2)
            rank_diff = num_rank1 - num_rank2  # difference in rank

            # calculate historical h2h win percentage
            # obtain all previous matches by boolean indexing, date must be less than current_date
            logical = ((h2h_df['ID1'] == ID1) & (h2h_df['ID2'] == ID2)) | \
                      ((h2h_df['ID1'] == ID2) & (h2h_df['ID2'] == ID1))
            rel_df = h2h_df[logical]

            logical = (h2h_df['date'] < date)  # h2h date is less than current date
            rel_df = rel_df[logical]

            h2h_wp1, h2h_wp2 = calculate_h2h_wp(date, rel_df, ID1)  # if rel_df is empty, then say h2h_wp is 50/50
            h2h_diff = h2h_wp1 - h2h_wp2

            # ----------- Generate Feature Vectors and Labels ------------- #
            # order in which sumos are stored must be randomized, else the data would be biased b/c of the order in
            # which head-to-head data were scraped

            order = random.randint(1, 2)  # randomize order in which features and sumos are stored

            feature_dict = {}  # initialize dictionary

            # --- Keep Order of Sumos --- #
            if order == 1:  # keep everything as is (no switching signs)

                if (outcome1 == u'shiro') and (outcome2 == u'kuro'):  # win by 1st sumo, loss by 2nd sumo

                    feature_dict = {'height_diff': height_diff, 'weight_diff': weight_diff, 'age_diff': age_diff,
                                    'active_diff': active_diff, 'rank_diff': rank_diff, 'h2h_diff': h2h_diff,
                                    'ID1': ID1, 'ID2': ID2, 'label': 1}

                elif (outcome1 == u'kuro') and (outcome2 == u'shiro'):  # loss by 1st sumo, win by 2nd sumo

                    feature_dict = {'height_diff': height_diff, 'weight_diff': weight_diff, 'age_diff': age_diff,
                                    'active_diff': active_diff, 'rank_diff': rank_diff, 'h2h_diff': h2h_diff,
                                    'ID1': ID1, 'ID2': ID2, 'label': 0}

            # --- Switch Order of Sumos --- #
            elif order == 2:  # then switch signs of features, order of sumos, but NOT labels

                if (outcome2 == u'shiro') and (outcome1 == u'kuro'):  # win by "1st sumo", loss by 2nd sumo

                    feature_dict = {'height_diff': -height_diff, 'weight_diff': -weight_diff, 'age_diff': -age_diff,
                                    'active_diff': -active_diff, 'rank_diff': -rank_diff, 'h2h_diff': -h2h_diff,
                                    'ID1': ID2, 'ID2': ID1, 'label': 1}

                elif (outcome2 == u'kuro') and (outcome1 == u'shiro'):  # loss by "1st sumo", win by 2nd sumo

                    feature_dict = {'height_diff': -height_diff, 'weight_diff': -weight_diff, 'age_diff': -age_diff,
                                    'active_diff': -active_diff, 'rank_diff': -rank_diff, 'h2h_diff': -h2h_diff,
                                    'ID1': ID2, 'ID2': ID1, 'label': 0}

            # --- Collect Data --- #
            if feature_dict:
                compiled_dicts.append(feature_dict)
            else:
                print "Empty feature dict! Cannot append to compiled dicts..."

    counter += 1


# ----- Store Data into DataFrame ---- #
cols = ['height_diff', 'weight_diff', 'age_diff', 'active_diff', 'rank_diff', 'h2h_diff',
        'ID1', 'ID2', 'label']
feature_df = pd.DataFrame(compiled_dicts, columns=cols)

end = time.time()
print "Time: %2.2f" % (end - start)


# --- Uncomment And Change Filename When Ready to Store --- #
# feature_df.to_pickle('data/recent_feature_df.pkl')
