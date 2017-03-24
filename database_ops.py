"""Module with helper functions to perform various operations with DataFrames.

Example Usage: from database_ops import match_ID

"""

from datetime import timedelta
import rikishi_scrape


# -- Helper Function to Match Record Title Attribute Info with Sumo ID --- #

def match_ID(shikona, sumo_stable, bday, debut, filtered_df, rikishi_url):
    """Function used to lookup unique ID associated with sumo wrestler. Input info comes from the title attribute of
    'a href tags' associated with a sumo wrestler (on html pages with head-to-head bout info).

    Function is used to in scripts storing head-to-head data. Unique ID's are located in the all_rikishi.pkl DataFrame.

    :param shikona: unicode Japanese sumo name
    :param sumo_stable: unicode stable sumo wrestler is from
    :param bday: datetime object birth day
    :param debut: datetime object debut (hatsu dohyo)
    :param filtered_df: Pandas DataFrame with sumos yielding fruitful information for machine learning purposes
    :param rikishi_url: url to a sumo wrestler's basic profile
    :return: int ID.
    """

    ID = None  # initialize ID

    # match on shikona, bday, and debut
    # bday and debut date must both be within a year of the stored dates in all_rikishi.pkl

    # --- Check Shikona & Sumo Stable First (quickest filter) --- #
    logical = filtered_df['shikona'].apply(lambda x: shikona in x) & \
              filtered_df['sumo_stable'].apply(lambda x: sumo_stable in x)
    ID_df = filtered_df[logical]

    if len(ID_df) == 1:
        ID = int(ID_df['rikishi_ID'].item())
    elif len(ID_df) > 1:

        # --- Check All Conditions If First Filter Fails --- #
        logical = filtered_df['shikona'].apply(lambda x: shikona in x) & \
                  filtered_df['sumo_stable'].apply(lambda x: sumo_stable in x) & \
                  filtered_df['bday'].apply(
                      lambda x: abs((bday - x).total_seconds()) <= timedelta(days=365).total_seconds()) & \
                  filtered_df['debut'].apply(
                      lambda x: abs((debut - x).total_seconds()) <= timedelta(days=365).total_seconds())
        ID_df = filtered_df[logical]

        if len(ID_df) == 1:
            ID = int(ID_df['rikishi_ID'].item())
        elif len(ID_df) > 1:

            # --- Go to Sumo Basic Profile URL If Previous Filters Fail --- #
            # try to match on as many basic data as possible to minimize probability of this failing
            print " Forced to go to basic rikishi profile for better ID matching"

            compiled_stats = rikishi_scrape.basic_scrape(rikishi_url)
            shikona = compiled_stats[0]
            highest_rank = compiled_stats[1]
            bday = compiled_stats[2]
            # age = compiled_stats[3]
            # birth_place = compiled_stats[4]
            height = compiled_stats[5]
            weight = compiled_stats[6]
            sumo_stable = compiled_stats[7]
            # active_years = compiled_stats[8]
            debut = compiled_stats[9]
            # entry_rank = compiled_stats[10]
            # retirement = compiled_stats[11]
            logical = (filtered_df['shikona'] == shikona) & (filtered_df['bday'] == bday) & \
                      (filtered_df['height'] == height) & (filtered_df['weight'] == weight) & \
                      (filtered_df['sumo_stable'] == sumo_stable) & (filtered_df['debut'] == debut)
            ID = int(filtered_df.loc[logical, 'rikishi_ID'].item())

    if ID is None:
        raise Exception('Could not find sumo ID for: ' + shikona)

    return ID
