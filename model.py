import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

def select_features(data, features):
    return { key: data[key] for key in features }

def convert_to_np(data):
    target = np.array(data['win'])
    data = data.drop('win', axis = 1)
    data = np.array(data)

    return (data, target)

def build(model_class, data, features):
    (data, target) = convert_to_np(data)

    train_data, test_data, train_target, test_target = train_test_split(data, target, test_size = 0.25, random_state = 1)

    locals()[model_class]()

    return True


# Model functions

def RandomForest(train_data, test_data, train_target, test_target):
    rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)
    rf.fit(train_data, train_target)

    predictions = rf.predict(test_data)

    return (rf, predictions)