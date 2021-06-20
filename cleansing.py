
from sklearn.neural_network import MLPClassifier

import pandas as pd
from sklearn.preprocessing import LabelEncoder


################### LABEL ENCODING #######################

def label_encoding(dataframe, column):
    '''
    Applies label enconding to the column defined in the input
    '''
    label_encoder = LabelEncoder()
    data = dataframe.copy(deep=True)
    data[column] = label_encoder.fit_transform(data[column])
    return data



################### ONE-HOT ENCODING #####################

def one_hot_encoding(dataframe, column):
    '''
    Do one hot enconding to the column defined in the input
    '''
    df = dataframe.copy()
    one_hot = pd.get_dummies(df[column])
    df = df.drop(column, axis=1)
    df = df.join(one_hot)
    return df



################### APPLY ENCODING #######################

def encode_all_labels(df, label, option="one-hot encoding"):
    '''
    Applies the function label_encondig or one_hot_enconding (according to the chosen option), to encode all non-numeric columns.
    Options: "label encoding" or "one-hot encoding"
    '''

    data = df.copy(deep=True)
    non_numeric_columns = data.select_dtypes(exclude=['int64','float64']).columns
    if label in non_numeric_columns:
        non_numeric_columns = non_numeric_columns.drop(label)


    if option == "label encoding":
        for column in non_numeric_columns:
            data = label_encoding(data, column)

    elif option == "one-hot encoding":
        for column in non_numeric_columns:
            data = one_hot_encoding(data, column)

    else:
        print("\nInvalid encoding!\n")
        return -1

    return data



################## IDEA TO TREAT THE GENERATED RULES ###############################
import numpy as np
import re


def get_values_consistency(generated_rule):
    '''
    Divides a rule into a tuple with only the relevant info. "When country is PT then city is Braga or Porto" -> (country, PT, city, [Braga,Porto])
    '''
    l = re.split(',|, | |: ', generated_rule) # break rule into words
    ises = [i for i in range(len(l)) if l[i]=="is"]
    # Get only relevant words:
    column1 = l[1]
    value1 = l[3]
    column2 = l[5]
    values2 = l[ises[-1]+1:len(l)-1]
    values2 = [x for x in values2 if x!='or']
    return column1, value1, column2, values2



def get_pass_and_fail_data(dataframe, value1, column, value2):
    '''
    Divides the dataframe in 4 dataframes: X_pass_data,Y_pass_data, X_fail_data, Y_fail_data
    '''

    label_to_predict = column

    df = dataframe.copy(deep=True)
    df = df[df[value1]==1] # df is one hot encoded, so we have to check if the value1 it is equal to 1

    # we want to predict column, that it is not one-hot encoded:
    pass_data = df[df[column].isin(value2)]
    fail_data = df[~df[column].isin(value2)] # ~ = not

    X_pass_data = pass_data.drop([label_to_predict],axis=1)
    Y_pass_data = pass_data[label_to_predict]

    X_fail_data = fail_data.drop([label_to_predict],axis=1)
    Y_fail_data = fail_data[label_to_predict]

    return X_pass_data,Y_pass_data, X_fail_data, Y_fail_data




def cleansing_consistency(dataframe, rule_to_apply):
    '''
    Receives dataframe and the rule chosen by the user (example: rule 27 - WHEN COUNTRY IS PT THEN CITY IS BRAGA or PORTO)
    Returns a dataframe that only has the fail data and the forecasts, and the original updated dataframe
    '''

    df = dataframe.copy(deep=True)
    df = df.replace(" ","blank")

    c1, v1, c2, v2 = get_values_consistency(rule_to_apply)
    label_to_predict = c2

    df = encode_all_labels(df, label_to_predict)

    X_pass_data,Y_pass_data, X_fail_data, Y_fail_data = get_pass_and_fail_data(df, v1, c2, v2)


    clf = MLPClassifier(random_state=1, max_iter=300).fit(X_pass_data, Y_pass_data)

    predictions = clf.predict(X_fail_data)

    nifs = X_fail_data['NIF']
    res = dataframe[dataframe['NIF'].isin(nifs)]

    res.insert(len(res.columns),"PRED",np.array(predictions))


    # create this copy otherwise it spoils the original
    altered_dataframe = dataframe.copy(deep=True)

    altered_dataframe.loc[altered_dataframe['NIF'].isin(res['NIF']), [label_to_predict]] = res['PRED']

    return res, altered_dataframe




def get_values_completeness(generated_rule):
    '''
    Divides a rule into a tuple with only the relevant info. "NIF is populated: 100.0%" -> NIF
    '''
    l = re.split(',|, | |: |%', generated_rule) # break rule into words
    return l[0]


def cleansing_completeness(dataframe, rule_to_apply):
    '''
    Receives dataframe and the rule chosen by the user (example: "NIF is populated")
    Returns a dataframe that only has the fail data and the forecasts, and the original updated dataframe
    '''
    df = dataframe.copy(deep=True)
    df = df.replace(" ","blank")

    label_to_predict = get_values_completeness(rule_to_apply)

    df = encode_all_labels(df, label_to_predict)

    pass_data = df[df[label_to_predict] != "blank"]
    fail_data = df[df[label_to_predict] == "blank"] 

    X_pass_data = pass_data.drop([label_to_predict],axis=1)
    Y_pass_data = pass_data[label_to_predict]

    X_fail_data = fail_data.drop([label_to_predict],axis=1)

    clf = MLPClassifier(random_state=1, max_iter=300).fit(X_pass_data, Y_pass_data)

    predictions = clf.predict(X_fail_data)

    nifs = X_fail_data['NIF']
    res = dataframe[dataframe['NIF'].isin(nifs)]

    res.insert(len(res.columns),"PRED",np.array(predictions))

    # create this copy otherwise it spoils the original
    altered_dataframe = dataframe.copy(deep=True)

    altered_dataframe.loc[altered_dataframe['NIF'].isin(res['NIF']), [label_to_predict]] = res['PRED']

    return res, altered_dataframe
