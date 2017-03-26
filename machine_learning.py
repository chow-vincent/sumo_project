""" Script for doing various machine learning tasks, including model evaluation & predicting outcomes of new bouts.

Head-to-head matches are imported by placing Excel match-ups into text files in the 'tourneys/schedules' folder.
Results (including outcomes and probabilities) are also printed to text files in the 'tourneys/results' folder, for
quick transfer into Excel spreadsheets.

Usage:
(1) Set up pickle file from which to load generated features (from feature_generation.py)
(2) Set up file names from which to load tourney schedules and save tourney results (bottom of script)
(3) Decide to do model evaluation (Option A), or predict outcomes of new bouts (Option B). Comment in desired code.

Option A:
(4) Run machine_learning.py


Option B:
(4) Set up list of sumo wrestlers, their abbreviated names, and their ranks for this tourney
(5) Run machine_learning.py

"""

from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split  # used if performing model evaluation/cross-validation
from sklearn.metrics import precision_recall_fscore_support
import pandas as pd
from ml_fxns import predict_outcome, read_schedule
pd.set_option('display.width', 500)
pd.set_option('display.max_columns', 100)


# --- Load Generated Features --- #
feature_df = pd.read_pickle('data/recent_feature_df.pkl')  # features for all sumo wrestlers debuting after 2000


# --- Setup Feature Vectors for SkLearn Library --- #
# features are inherently symmetric (e.g. difference in height, difference in rank)
# hence no need to subtract mean

X = feature_df.loc[:, ['height_diff', 'weight_diff', 'age_diff', 'active_diff', 'rank_diff', 'h2h_diff']]
scaler = StandardScaler(copy=True, with_mean=False, with_std=True)
X_scaled = scaler.fit_transform(X)
X_scaled[:, 5] = feature_df['h2h_diff']  # make sure h2h_diff NOT standardized

y = feature_df.loc[:, 'label']  # labels, outcomes for first sumo (1 for wins, 0 for losses)


# --- Initialize Model --- #
# NO bias unit, b/c if two values of a feature are the same, we expect 50% probability when features are ZERO in value
logistic = linear_model.LogisticRegression(fit_intercept=False)


# ========== OPTION A: MODEL EVALUATION (Comment Out For Testing New Predictions) ========== #
# X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.33, random_state=42)
#
# logistic.fit(X_train, y_train)
# y_pred = logistic.predict(X_test)
#
# precision, recall, fbeta_score, _ = precision_recall_fscore_support(y_test, y_pred, beta=1.0, labels=[1])
#
# print "Precision: %0.3f" % precision
# print "Recall   : %0.3f" % recall
# print "F1 Score : %0.3f" % fbeta_score  # F1 score for predicting wins (similar result to predicting losses)


# print('LogisticRegression score: %f'
#       % logistic.fit(X_train, y_train).score(X_test, y_test))  # reports mean accuracy


# ========== OPTION B: PREDICT OUTCOMES FOR FUTURE HEAD-TO-HEAD MATCHES (Comment Out for Model Evaluation) ========= #

logistic.fit(X_scaled, y)  # fit on all STANDARDIZED data


# ------ SINGLE PREDICTION SECTION ------ #
# shikona1 = u'Takanishi Hayato - Daishoei Hayato - Daieisho Hayato'
# shikona2 = u'Motoi Miyohito - Chiyoo Miyohito'
#
# rank1 = u'Maegashira 11'
# rank2 = u'Maegashira 15'
#
# prediction, prob_win1, prob_win2 = predict_outcome(shikona1, shikona2, rank1, rank2, logistic)


# ------- FULL DAY PREDICTION SECTION ------- #

# --- List of Shikonas, Abbreviations, and Rankings --- #

shikona_list = {u'Hakuho Sho': u'Yokozuna', u'Kakuryu Rikisaburo': u'Yokozuna',
                u'Ama Kohei - Harumafuji Kohei': u'Yokozuna', u'Hagiwara Yutaka - Kisenosato Yutaka': u'Yokozuna',
                u'Sawai Gotaro - Goeido Gotaro': u'Ozeki',
                u'Wakamisho Yoshiaki - Wakamisho Noriaki - Wakamisho Yoshiaki - Terunofuji Yoshiaki - Terunofuji Haruo': u'Ozeki',
                u'Tamawashi Ichiro': u'Sekiwake', u'Takayasu Akira': u'Sekiwake', u'Kotokikutsugi Kazuhiro - Kotoshogiku Kazuhiro': u'Sekiwake',
                u'Mitakeumi Hisashi': u'Komusubi', u'Shodai Naoya': u'Komusubi',
                u'Narita Akira - Takekaze Akira': u'Maegashira 1', u'Toguchi Shota - Ikioi Shota': u'Maegashira 1',
                u'Sokokurai Eikichi': u'Maegashira 2', u'Takanoiwa Yoshimori': u'Maegashira 2',
                u'Matsutani Yuya - Shohozan Yuya': u'Maegashira 3', u'Takarafuji Daisuke': u'Maegashira 3',
                u'Onishi Masatsugu - Yoshikaze Masatsugu': u'Maegashira 4', u'Arawashi Tsuyoshi': u'Maegashira 4',
                u'Endo Shota': u'Maegashira 5', u'Daiki Akimichi - Hokutofuji Daiki': u'Maegashira 5',
                u'Sawada Toshiki - Chiyonokuni Toshiki': u'Maegashira 6', u'Aoiyama Kiyohito - Aoiyama Kosuke': u'Maegashira 6',
                u'Ichinojo Takashi': u'Maegashira 7', u'Shoma Fujio - Chiyoshoma Fujio': u'Maegashira 7',
                u'Kaisei Ichiro': u'Maegashira 8', u'Fukuoka Ayumi - Okinoumi Ayumi - Fukuoka Ayumi - Okinoumi Ayumi': u'Maegashira 8',
                u'Tatsu Ryoya - Kagayaki Taishi': u'Maegashira 9', u'Kotoenomoto Yuki - Kotoyuki Kazuyoshi': u'Maegashira 9',
                u'Tochinoshin Tsuyoshi': u'Maegashira 10', u'Kageyama Yuichiro - Tochiozan Yuichiro': u'Maegashira 10',
                u'Takanishi Hayato - Daishoei Hayato - Daieisho Hayato': u'Maegashira 11', u'Ishiura Masakatsu': u'Maegashira 11',
                u'Matsumura Kaname - Sadanoumi Kaname - Sadanoumi Takashi': u'Maegashira 12', u'Ura Kazuki': u'Maegashira 12',
                u'Sato Takanobu - Takakeisho Mitsunobu': u'Maegashira 13', u'Kawabata Shogo - Daishomaru Shogo': u'Maegashira 13',
                u'Miyamoto Yasunari - Myogiryu Yasunari': u'Maegashira 14', u'Kyokushuho Yuji - Kyokushuho Koki': u'Maegashira 14',
                u'Motoi Miyohito - Chiyoo Miyohito': u'Maegashira 15', u'Aoki Makoto - Tokushoryu Makoto': u'Maegashira 15',
                u'Kumagai Tetsuya - Nishikigi Tetsuya': u'Maegashira 16', u'Meigetsuin Hidemasa - Chiyotairyu Hidemasa': u'Juryo 1',
                u'Onosho Fumiya': u'Juryo 2', u'Okinoshita Yuki - Chiyootori Yuki': u'Juryo 1',
                u'Gagamaru Taro - Gagamaru Masaru': u'Juryo 2'}

shikona_abbrevs = {u'Hakuho': u'Hakuho Sho', u'Kakuryu': u'Kakuryu Rikisaburo', u'Harumafuji': u'Ama Kohei - Harumafuji Kohei',
                   u'Kisenosato': u'Hagiwara Yutaka - Kisenosato Yutaka', u'Goeido': u'Sawai Gotaro - Goeido Gotaro',
                   u'Terunofuji': u'Wakamisho Yoshiaki - Wakamisho Noriaki - Wakamisho Yoshiaki - Terunofuji Yoshiaki - Terunofuji Haruo',
                   u'Tamawashi': u'Tamawashi Ichiro', u'Takayasu': u'Takayasu Akira', u'Kotoshogiku': u'Kotokikutsugi Kazuhiro - Kotoshogiku Kazuhiro',
                   u'Mitakeumi': u'Mitakeumi Hisashi', u'Shodai': u'Shodai Naoya', u'Takekaze': u'Narita Akira - Takekaze Akira',
                   u'Ikioi': u'Toguchi Shota - Ikioi Shota', u'Sokokurai': u'Sokokurai Eikichi', u'Takanoiwa': u'Takanoiwa Yoshimori',
                   u'Shohozan': u'Matsutani Yuya - Shohozan Yuya', u'Takarafuji': u'Takarafuji Daisuke',
                   u'Yoshikaze': u'Onishi Masatsugu - Yoshikaze Masatsugu', u'Arawashi': u'Arawashi Tsuyoshi',
                   u'Endo': u'Endo Shota', u'Hokutofuji': u'Daiki Akimichi - Hokutofuji Daiki',
                   u'Chiyonokuni': u'Sawada Toshiki - Chiyonokuni Toshiki', u'Aoiyama': u'Aoiyama Kiyohito - Aoiyama Kosuke',
                   u'Ichinojo': u'Ichinojo Takashi', u'Chiyoshoma': u'Shoma Fujio - Chiyoshoma Fujio', u'Kaisei': u'Kaisei Ichiro',
                   u'Okinoumi': u'Fukuoka Ayumi - Okinoumi Ayumi - Fukuoka Ayumi - Okinoumi Ayumi',
                   u'Kagayaki': u'Tatsu Ryoya - Kagayaki Taishi', u'Kotoyuki': u'Kotoenomoto Yuki - Kotoyuki Kazuyoshi',
                   u'Tochinoshin': u'Tochinoshin Tsuyoshi', u'Tochiozan': u'Kageyama Yuichiro - Tochiozan Yuichiro',
                   u'Daieisho': u'Takanishi Hayato - Daishoei Hayato - Daieisho Hayato', u'Ishiura': u'Ishiura Masakatsu',
                   u'Sadanoumi': u'Matsumura Kaname - Sadanoumi Kaname - Sadanoumi Takashi', u'Ura': u'Ura Kazuki',
                   u'Takakeisho': u'Sato Takanobu - Takakeisho Mitsunobu', u'Daishomaru': u'Kawabata Shogo - Daishomaru Shogo',
                   u'Myogiryu': u'Miyamoto Yasunari - Myogiryu Yasunari', u'Kyokushuho': u'Kyokushuho Yuji - Kyokushuho Koki',
                   u'Chiyoo': u'Motoi Miyohito - Chiyoo Miyohito', u'Tokushoryu': u'Aoki Makoto - Tokushoryu Makoto',
                   u'Nishikigi': u'Kumagai Tetsuya - Nishikigi Tetsuya', u'Chiyotairyu': u'Meigetsuin Hidemasa - Chiyotairyu Hidemasa',
                   u'Onosho': u'Onosho Fumiya', u'Chiyootori': u'Okinoshita Yuki - Chiyootori Yuki',
                   u'Gagamaru': u'Gagamaru Taro - Gagamaru Masaru'}


# -- Setup Input and Output Files --- #
tourney_day = 'haru2017_day15'

match_list = read_schedule('tourneys/schedules/' + tourney_day + '.txt')  # input file

export_file = open('tourneys/results/' + tourney_day + '_results.txt', 'w')  # output file


for item in match_list:  # loop over h2h lineups

    abbrev1 = item[0]
    abbrev2 = item[1]

    shikona1 = shikona_abbrevs[abbrev1]
    shikona2 = shikona_abbrevs[abbrev2]

    rank1 = shikona_list[shikona1]
    rank2 = shikona_list[shikona2]
    prediction, prob_win1, prob_win2 = predict_outcome(shikona1, shikona2, rank1, rank2, logistic)

    print >>export_file, (str(prob_win1) + '\t' + str(prob_win2) + '\t' + str(prediction) + '\t' + str(prediction ^ 1))


print "\nFinished predicting h2h results."
export_file.close()
