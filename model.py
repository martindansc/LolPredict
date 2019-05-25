import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing

def select_features(data, features):
    ret = []
    for obj in data:
        ret.append({ key: obj[key] for key in features })

    return ret


def convert_to_np(data):
    target = [d['wins'] for d in data]
    [d.pop('wins') for d in data]
    data = [np.array(list(d.values())) for d in data]
    return (np.array(data), np.array(target))


def get_column(data, column):
    ret = []
    for i in data:
        ret.append(i[column])
    return ret


def evaluate(test_target, predictions):
    ((tn, fp), (fn, tp)) = confusion_matrix(test_target, predictions)
    score = (tp + tn) / len(test_target)

    return score

def feature_correlation(data, target):
    ret = []
    for i in range(len(data[0])):
        column_data = get_column(data, i)
        ret.append(np.corrcoef(column_data, target)[0,1])
    return ret

def split_data(data, target):
    return train_test_split(data, target, test_size = 0.25, random_state = 1)

def build(model_class, data, target, features, scale = False, extra_params = None):
    
    if(scale):
        data = preprocessing.scale(data)
    
    train_data, test_data, train_target, test_target = split_data(data, target)
    
    if extra_params != None:
        model = globals()[model_class](train_data, test_data, train_target, test_target, extra_params)
    else:
        model = globals()[model_class](train_data, test_data, train_target, test_target)
    
    predictions = model.predict(test_data)
    score = evaluate(test_target, predictions)
    return (model, score)


def cbuild(model_class, data, features, scale = False, extra_params = None):
    selected_features = select_features(data, features)
    (data, target) = convert_to_np(data)
    return build(model_class, data, target, selected_features, scale, extra_params)


# Model functions

def random_forest(train_data, test_data, train_target, test_target, params = {"n_estimators":10, "random_state" : 42}):
    rf = RandomForestClassifier(**params)
    rf.fit(train_data, train_target)
    return rf
   

def support_vector_machine(train_data, test_data, train_target, test_target, params = {"gamma" : "scale"}):
    svc = svm.SVC(**params)
    svc.fit(train_data, train_target)
    return svc


def logistic_regression(train_data, test_data, train_target, test_target, params = {"max_iter":1000, "random_state":189, "solver":'liblinear'}):
    lr = LogisticRegression(**params)
    lr.fit(train_data, train_target)
    return lr