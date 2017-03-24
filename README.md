# Sumo Wrestling Machine Learning Project

## Intro
The goal of this project was to use machine learning to **predict the outcomes of sumo wrestling bouts** in Japan Sumo Grand Tournaments. There are few Western attempts at using sports analytics on Eastern sports, and this is an attempt at filling that gap.

## Process
First, I **built a database by scraping and parsing data** from publicly available information at [Sumo Reference] using [Beautiful Soup]. This website contains data on sumo wrestlers, tournament outcomes, etc. dating back to as early as 1600. I scrape basic profile info (e.g. height, weight, rank) as well as head-to-head matches (outcomes of matches between two sumo wrestlers). The resulting database contains **12,374 unique sumo wrestler profiles**, as well as the outcomes of almost **200,000 head-to-head matches** dating back to the early 2000's.

Next, I **visualized the data to observe interesting trends, clean data, and look for features** to include for machine learning. Plots were generated using [Seaborn] and saved as PNG's.

Finally, I **trained a logistic regression model on this data** to predict the outcomes of new matches during the 2017 March Grand Tournament (Haru Basho). Current features used are **differences** in the following values between two sumo wrestlers:

   - Height
   - Weight
   - Age
   - Active Number of Years
   - Rank
   - Head-to-Head Win Percentage (of previous matches between two sumos, what percentage of them did one sumo win against the other?)

## Results

Results of model pending on completion of tournament.


## Future Work

   - Try different classifiers
   - Gather more features (e.g. Scrape professional sumo's Twitter profiles)
   - Perform more work on feature selection


## Folders and Files

data/  : contains data collected from online, public database using Beautiful Soup Library. Stored as pickle files from pandas dataframes.

plots/ : contains visualizations of data in Seaborn plots saved as png's.

tourneys/ : contains daily tourney head-to-head lineups for March (Haru) Basho 2017.

TODO: document python scripts and jupyter notebooks


[Seaborn]: <https://seaborn.pydata.org/>
[Sumo Reference]: <http://sumodb.sumogames.de/>
[Beautiful Soup]: <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>