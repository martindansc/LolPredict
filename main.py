import settings
import api
import transforms
import model
import sys
import numpy as np
import json
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from scipy.stats import binom

# features
team_summary_features = transforms.transform_team_features(["min_winrate", "max_winrate" ,"avg_winrate"])
team_other_features = transforms.transform_team_features(["num_matches", "num_wins"])
roles = transforms.transform_team_features(["TOP", "JUNGLE", "MIDDLE", "BOTTOM"])
roles_diff = ["TOP_DIFF", "JUNGLE_DIFF", "MIDDLE_DIFF", "BOTTOM_DIFF"]

team_selected = transforms.transform_team_features(["min_winrate", "avg_winrate"])
other_selected = ["TOP_DIFF", "JUNGLE_DIFF"]

features = {
    "all" : team_summary_features + team_other_features + roles + roles_diff,
    "basic" : team_summary_features,
    "selected" : team_selected + other_selected
}

# always add win
for feature in features.values():
    feature.append("wins")

model_names = ["random_forest", "support_vector_machine", "logistic_regression"]

def all_models_with_features(selected_features = features["all"]):
    data = transforms.get_players_match_data(0, 550)
    data = model.select_features(data, selected_features)
    (tdata, target) = model.convert_to_np(data)
    for model_name in model_names:
        (_, score) = model.build(model_name, tdata, target, selected_features)
        print("Model: " + model_name + " - " + "{0:.2f}".format(score))


def basic_model():
    data = transforms.get_players_match_data(0, 100)
    (_, score) = model.cbuild("random_forest", data, features["basic"])
    print("(random_forest, basic, 550) - " + "{0:.2f}".format(score))


def all_model():
    data = transforms.get_players_match_data(0, 550)
    (_, score) = model.cbuild("random_forest", data, features["all"])
    print("(random_forest, all, 550) - " + "{0:.2f}".format(score))
    return score

def single_model(name, selected_features, scale = False, params = None):
    data = transforms.get_players_match_data(0, 550)
    (mod, score) = model.cbuild(name, data, features[selected_features], scale, params)
    print("(" + name + "," + selected_features + ", 550) - " + "{0:.2f}".format(score))
    return (mod, score)

def feature_selection():
    # check the correlation of each feature with winning
    data = transforms.get_players_match_data(0, 550)
    data  = model.select_features(data, features["all"])
    (data, target) = model.convert_to_np(data)
    correlations = model.feature_correlation(data, target)
    for i in range(len(correlations)):
        print("Feature: " + features["all"][i] + " - " + "{0:.2f}".format(correlations[i]))


def roc_curve_model(cmodel, selected_features):
    data = transforms.get_players_match_data(0, 550)

    selected_features = model.select_features(data, features[selected_features])
    (data, target) = model.convert_to_np(data)
    _, test_data, _, test_target = model.split_data(data, target)

    scores = model.get_column(cmodel.predict_proba(test_data), 1)
    
    (fpr, tpr, _) = roc_curve(test_target, scores)
    roc_auc = auc(fpr, tpr)

    return (fpr, tpr, roc_auc)

def plot_curve(fpr, tpr, roc_auc, names):
    plt.figure()
    lw = 2

    colors = ['aqua', 'darkorange', 'cornflowerblue']
    for i in range(len(roc_auc)):
        plt.plot(fpr[i], tpr[i], color=colors[i], lw=lw,
                label='ROC curve of model {0} (area = {1:0.2f})'.format(names[i], roc_auc[i]))
    
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()


def get_roc_curves(cmodels, names, selected_features):

    fprs = []
    tprs = []
    roc_acus = []

    for cmodel in cmodels:
        fpr, tpr, roc_auc = roc_curve_model(cmodel, selected_features)
        fprs.append(fpr)
        tprs.append(tpr)
        roc_acus.append(roc_auc)

    plot_curve(fprs,tprs, roc_acus, names)

def print_match_data():
    matches = api.get_matches()
    team_data = transforms.get_team_data(matches[0], 0)
    print(json.dumps(team_data, indent=4))

def print_team_data():
    data = transforms.get_players_match_data(0, 1)
    print(json.dumps(data[0], indent=4))

def get_acuracity_interval(p):
    n = int(550*0.25)
    rv = binom(n, p)
    (low, high) = rv.interval(0.95)
    
    low_rate = low / n
    high_rate = high / n

    print("Interval for probability {0:.2f}".format(p))
    print("{0:.2f} - {1:.2f} ".format(low_rate, high_rate))
    

if __name__ == '__main__':

    if(len(sys.argv) > 1 ):
        # shortcut to run the specific passed function
        globals()[sys.argv[1]]()
    else:
        (selected_logistic, best_score_logistic) = single_model("logistic_regression", "selected")
        (forest_selected, best_score_forest) = single_model("random_forest", "selected")
        get_roc_curves([forest_selected, selected_logistic], ["forest", "logistic"], "selected")

