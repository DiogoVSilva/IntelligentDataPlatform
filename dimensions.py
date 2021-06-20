from itertools import combinations
import pandas as pd
import numpy as np
# from app import colored


def colored(r, g, b, text):
    '''
    Function to color text in the terminal.
    '''

    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def check_perc(p, min_perc, max_perc):
    '''
    Checks whether the percentage meets the minimum and maximum.
    Returns True if fulfilled.
    '''

    if (p >= min_perc) and (p <= max_perc):
        return True
    return False


def integrity(dataframe, min_perc, max_perc):
    '''
    Output: res1,res2
    '''

    dataframe = dataframe.replace(r'^\s*$', np.NaN, regex=True)  # replace " " with NaN

    # INTE1:
    res1 = []

    for column in dataframe.columns:

        valores = dataframe[column].dropna().drop_duplicates().tolist()  # remove repeated, move to list

        if len(valores) > 1:
            valores2 = valores[0:len(valores) - 1]  # the last value, it's just to print

            not_null = len(dataframe[column].dropna())
            total = len(dataframe[column])

            percentagem = not_null / total * 100
            res = "" + column + " is equal to " + ', '.join(str(v) for v in valores2) + " or " \
                  + str(valores[-1]) + ": " + str(percentagem) + "%"

        else:
            res = "" + column + " is equal to " + str(valores[0]) + ": 100%"
            percentagem = 100

        if check_perc(percentagem, min_perc, max_perc):
            res1.append(res)

    # INTE2:
    res2 = []

    column_combinations = list(combinations(dataframe, 2))  # all 2-column combinations

    for combination in column_combinations:
        column1, column2 = combination
        df = dataframe[[column1, column2]]

        count = (dataframe[column1] == dataframe[column2]).sum()

        p = count / len(df) * 100
        res = "" + column1 + " is equal to " + column2 + ": " + str(p) + "%"

        if check_perc(p, min_perc, max_perc):
            res2.append(res)

    return res1, res2


def completeness(dataframe, min_perc, max_perc):  #
    '''
    Output: res1,res2,res3
    '''

    dataframe = dataframe.replace(r'^\s*$', np.NaN, regex=True)

    res1 = []

    total_rows = len(dataframe)

    for column in dataframe.columns:

        notna = dataframe[column].notna().sum()

        p = notna / total_rows * 100
        res = "" + column + " is populated: " + str(p) + "%"
        if check_perc(p, min_perc, max_perc):
            res1.append(res)

    res2 = []
    res3 = []

    column_combinations = list(combinations(dataframe, 2))  # all 2-column combinations
    cc = []

    for combination in column_combinations:
        column1, column2 = combination
        cc.append((column1, column2))
        cc.append((column2, column1))

    for column1, column2 in cc:  # COMP2:

        # COMP2:
        df1 = dataframe[[column1, column2]]
        values = df1[column1].drop_duplicates().dropna().tolist()

        for value in values:

            df = df1[df1[column1] == value]
            n_values = len(df)

            notna = df[column2].notna().sum()

            p = notna / n_values * 100
            res = "" + "When " + column1 + " is " + str(value) + " then " + column2 + \
                  " is populated: " + str(p) + "%"
            if check_perc(p, min_perc, max_perc):
                res2.append(res)

        # COMP3:
        missing_values_c1 = dataframe[column1].isnull().sum()

        if missing_values_c1 == 0:
            number_values_c2 = dataframe[column2].count()

            p = number_values_c2 / total_rows * 100
            res = "When " + column1 + " is populated then " + column2 + " is populated: " + str(p) + "%"
            if check_perc(p, min_perc, max_perc):
                res3.append(res)

    return res1, res2, res3


# auxiliary function for consistency and uniqueness
def getUniqueColumns(dataframe):
    '''
    Returns columns that only have single values.
    '''

    uniques = []
    for column in dataframe.columns:
        if dataframe[column].is_unique:
            uniques.append(column)
    return uniques


def consistency(dataframe, min_perc, max_perc):
    '''
    Output: res1
    '''

    # CONS1:
    res1 = []

    dataframe = dataframe.replace(r'^\s*$', np.NaN, regex=True)  # replace " " with NaN

    # remove columns that only have single values
    uniques = getUniqueColumns(dataframe)
    dfWithoutUniques = dataframe.drop(columns=uniques)
    column_combinations = list(combinations(dfWithoutUniques, 2))  # all 2-column combinations
    cc = []

    for column1, column2 in column_combinations:
        cc.append((column1, column2))
        cc.append((column2, column1))

    for column1, column2 in cc:
        df1 = dataframe[[column1, column2]]

        values_c1 = (dataframe[column1].drop_duplicates().dropna().tolist())
        values_c2 = (dataframe[column2].drop_duplicates().dropna().tolist())

        values_c2 = list(combinations(values_c2, int(np.ceil(0.50 * len(values_c2)))))

        for value_c1 in values_c1:

            df = df1[df1[column1] == value_c1]
            total = len(df)

            for value_c2 in values_c2:

                count = 0
                for i in value_c2:
                    count += (df[column2].values == i).sum()

                if count == 0:
                    p = 0
                else:
                    p = count / total * 100

                res = "" + "When " + column1 + " is " + str(value_c1) + " then " + column2 + " is "

                end = len(value_c2)
                for i, v in enumerate(value_c2):
                    if i == end - 1:
                        res += str(v)
                    elif i == end - 1 - 1:
                        res += str(v) + " or "
                    else:
                        res += str(v) + ", "

                res += ": " + str(p) + "%"

                if check_perc(p, min_perc, max_perc):
                    res1.append(res)

    return res1


def uniqueness(dataframe, min_perc, max_perc):
    '''
    Output: res1,res2
    '''

    # UNIQ1:
    res1 = []

    for column in dataframe.columns:

        if dataframe[column].is_unique:
            p = 100
            res = "" + column + " is unique: 100%"
            if check_perc(p, min_perc, max_perc):
                res1.append(res)
        else:
            comp1 = len(dataframe[column])  # number of lines
            comp2 = len(dataframe[column].drop_duplicates(keep=False))

            p = comp2 / comp1 * 100
            res = "" + column + " is unique: " + str(p) + "%"
            if check_perc(p, min_perc, max_perc):
                res1.append(res)

    # UNIQ2:
    res2 = []

    # remove columns that only have single values
    uniques = getUniqueColumns(dataframe)

    dfWithoutUniques = dataframe.drop(columns=uniques)

    # nr_columns = len(dfWithoutUniques.columns)

    column_combinations = list(combinations(dfWithoutUniques.columns, 2))

    for i in range(len(column_combinations)):
        combination = list(column_combinations[i])  # it must go to the list because column_combinations[i] is
        # a tuple

        comp1 = len(dfWithoutUniques[combination])  # number of lines
        comp2 = len(dfWithoutUniques[combination].drop_duplicates(keep=False))  # number of unrepeated lines
        # keep=False to keep one of the repeated

        if comp1 == comp2:

            p = 100
            res = "" + "Unique combination:" + str(combination)
            if check_perc(p, min_perc, max_perc):
                res2.append(res)

        else:
            comb = combination[0:len(combination) - 1]

            p = comp2 / comp1 * 100
            res = "" + "Combination of " + (', '.join(str(c) for c in comb)) + " and " \
                  + str(combination[-1]) + " is unique: " + str(p) + "%"
            if check_perc(p, min_perc, max_perc):
                res2.append(res)

    return res1, res2


def relevancy(dataframe1, dataframe2, table_name, table_name_2, min_perc, max_perc):
    '''
    Output: res1,res2
    '''

    columns_intersection = (dataframe1.columns).intersection(dataframe2.columns)
    columnUNIQUE = getUniqueColumns(dataframe1[columns_intersection])[0]

    # REL1:
    res1 = []

    n_rows = len(dataframe1)  # número de linhas
    values1 = dataframe1[columnUNIQUE]
    values2 = dataframe2[columnUNIQUE]

    v1_in_v2 = values1.isin(values2).sum()  # see how many values v1 are in v2

    p = v1_in_v2 / n_rows * 100
    res = "" + "All records in one table exists in the other: " + str(p) + '%'
    if check_perc(p, min_perc, max_perc):
        res1.append(res)

    # REL2:
    res2 = []

    dataframe1 = dataframe1.replace(r'^\s*$', 'blank', regex=True)
    columns = dataframe1.columns.drop(columnUNIQUE)

    for column in columns:
        values = (dataframe1[column].drop_duplicates().tolist())

        for value in values:
            fvalues1 = dataframe1[(dataframe1[column] == value)][columnUNIQUE]  # dataframe that only has value
            # value in column
            fn_rows = len(fvalues1)  # number of lines
            fv1_in_v2 = fvalues1.isin(values2).sum()  # see how many values of v1 are in v2

            if fv1_in_v2 == 0:  # gave an error in the division
                p = 0

            else:
                p = fv1_in_v2 / fn_rows * 100

            res = "" + "When " + column + " is " + str(value) + " then all records in " \
                  + table_name + " also exist in " + table_name_2 + ": " + str(p) + "%"
            if check_perc(p, min_perc, max_perc):
                res2.append(res)

    return res1, res2


# auxiliary functions for conformity
def long_substr(data):
    '''
    Returns the longest common substring in a string list.
    '''

    substrs = lambda x: {x[i:i + j] for i in range(len(x)) for j in range(len(x) - i + 1)}
    s = substrs(data[0])
    for val in data[1:]:
        s.intersection_update(substrs(val))
    return max(s, key=len)


def convert(word):
    '''
    Takes a word and converts it to a string of C's and N's.
    '''

    word = str(word)
    result = list(word)
    for i in range(len(result)):
        if ord(result[i]) >= 48 and ord(result[i]) <= 57:
            result[i] = "N"
        else:
            result[i] = "C"
    return "".join(result)


def divideList(lst):
    '''
    Takes a list and divides it into sublists in which the elements have the same length.
    '''

    dct = {}

    for element in lst:
        if len(element) not in dct:
            dct[len(element)] = [element]
        elif len(element) in dct:
            dct[len(element)] += [element]

    res = []
    for key in sorted(dct):
        res.append(dct[key])

    return res


def list_pattern(patterns):
    '''
    Takes a list of possible regular expressions and returns a generalized regular expression.
    '''
    res = list(patterns[0])
    size = len(res)
    for pattern in patterns:
        pattern = list(pattern)
        for i in range(size):
            if res[i] != pattern[i]:
                res[i] = "*"
    return "".join(res)


def check_pattern(column_values, miss_values, reg_exp):
    '''
    Returns which \% of column values that match the regular expression reg_exp.
    '''

    reg_exp = reg_exp.replace("{", "")
    reg_exp = reg_exp.replace("}", "")

    count = 0  # number of words that match the expression in the column
    for value in column_values:
        check_letter = 0  # number of right letters in the word value
        value = list(value)  # convert value into analysis into a list
        r = list(reg_exp)  # *123C -> [*,1,2,3,C]

        if len(value) == len(r):  # it only checks if the value matches the regular expression if they have the
            # same size

            for i in range(len(value)):  # compare letter by letter to regular expression and column value

                if ord(value[i]) >= 48 and ord(value[i]) <= 57:  # se for um número entre 0 e 9
                    if value[i] == r[i] or r[i] == "N" or r[i] == "*":
                        check_letter += 1

                if (ord(value[i]) >= 65 and ord(value[i]) <= 90) or (ord(value[i]) >= 97 and ord(value[i]) <= 122):
                    if value[i] == r[i] or r[i] == "C" or r[i] == "*":
                        check_letter += 1

            if check_letter == len(value):
                count += 1

    percentage = count / (len(column_values) + miss_values) * 100
    return percentage


def conf(dataframe, min_perc, max_perc):
    '''
    Receives a dataframe and returns a list of tuples (column, regular expression).
    '''

    dataframe = dataframe.astype(str)  # to be able to compare when values are numbers
    dataframe = dataframe.replace(r'^\s*$', np.NaN, regex=True)
    rules = []
    lines = []

    for column in dataframe.columns:
        missing_values = dataframe[column].isna().sum()
        dataframe = dataframe.dropna(how='any', subset=[column])
        values = dataframe[column].to_list()  # column values
        pattern = long_substr(values)  # common pattern for the entire column

        patterns = []  # list that stores all possible patterns of each column at each iteration

        for value in values:  # create the word pattern
            value = str(value)

            if len(pattern) > 1:  # only if the pattern has at least two letters is it relevant
                begin = value.find(pattern)  # index where the pattern starts
                end = begin + len(pattern)  # index where the pattern ends

                res = "" + convert(value[:begin])
                res += "{" + pattern + "}"
                res += convert(value[end:])

            else:
                res = "" + convert(value)

            patterns.append(res)

        patterns = divideList(list(set(patterns)))

        for hipoteses in patterns:

            if len(hipoteses) > 1:  # if there is more than one possible pattern
                r = list_pattern(hipoteses)

            else:
                r = hipoteses[0]

            percentage = check_pattern(values, missing_values, r)
            line = "" + column + " has pattern " + str(r) + ": " + str(percentage) + "%"
            if check_perc(percentage, min_perc, max_perc):
                lines.append(line)
                rules.append((column, r))

    return rules, lines


def conformity(dataframe, min_perc, max_perc):
    '''
    Output: res1,res2,res3,res4,res5
    '''

    # CONF1:
    d, res1 = conf(dataframe, min_perc, max_perc)

    # CONF2:
    res2 = []
    dataframe2 = dataframe.astype(str)
    dataframe2 = dataframe2.replace(r'^\s*$', 'blank', regex=True)  # replace " " with blank

    # remove columns that only have single values
    uniques = getUniqueColumns(dataframe2)
    dfWithoutUniques = dataframe2.drop(columns=uniques)

    for column1 in dfWithoutUniques.columns:
        column1_values = list(set(dfWithoutUniques[column1].tolist()))

        for par in d:
            column2 = par[0]
            exp = par[1]

            if column1 != column2:
                for valor in column1_values:
                    df = dataframe2[dataframe2[column1] == valor]
                    mv = df[column2].isna().sum()
                    df = df.dropna(how='any', subset=[column2])
                    column2_values = df[column2].tolist()

                    p = check_pattern(column2_values, mv, exp)
                    res = "" + "When " + column1 + " equal to " + str(valor) + " then " \
                          + column2 + " has pattern " + str(exp) + ": " + str(p) + "%"
                    if check_perc(p, min_perc, max_perc):
                        res2.append(res)

    # CONF3:
    res3 = []

    for column in dataframe.columns:
        values = dataframe[column].tolist()
        lengths = [len(str(value)) for value in values]
        minimum = min(lengths)
        maximum = max(lengths)

        p = 100
        res = "" + column + " length ranges between " + str(minimum) + " & " + str(maximum) + ": 100 %"
        if check_perc(p, min_perc, max_perc):
            res3.append(res)

    # CONF4:
    res4 = []

    df = dataframe.select_dtypes(include=['number'])  # dataframe whose attributes are numeric

    if len(df) > 0:

        for column in df.columns:
            values = dataframe[column].tolist()
            minimum = min(values)
            maximum = max(values)

            p = 100
            res = "" + column + " value ranges between " + str(minimum) + " & " + str(maximum) + ": 100 %"
            if check_perc(p, min_perc, max_perc):
                res4.append(res)

    else:
        res = "This dataframe doesn't contain columns with numeric values."
        res4.append(res)

    # CONF5:
    res5 = []

    for column in dataframe.columns:

        if dataframe[column].dtypes == 'object':
            a = pd.to_numeric(dataframe[column], errors='coerce').isna().sum()  # we add the values that cannot
            # be passed to numeric
            b = len(dataframe[column])

            if a == b:  # so there are no numeric values, they are all nominal
                res = "" + column + " contains nominal values: 100 %"
                p = 100
                if check_perc(p, min_perc, max_perc):
                    res5.append(res)

            elif a >= (b / 2):  # half or more than half of the values are nominal
                res = "" + column + " contains nominal values: " + str(a / b * 100) + "%"
                if check_perc(a / b * 100, min_perc, max_perc):
                    res5.append(res)

            else:  # more than half of the values are numeric
                res = "" + column + " contains numeric values: " + str((b - a) / b * 100) + "%"
                if check_perc((b - a) / b * 100, min_perc, max_perc):
                    res5.append(res)

        elif dataframe[column].dtypes == 'int64':
            res = "" + column + " contains numeric values: 100%"
            p = 100
            if check_perc(p, min_perc, max_perc):
                res5.append(res)

    return res1, res2, res3, res4, res5


def display_results(dimension_name, rule_number, results):
    '''
    Takes the name of the dimension, a list of rule numbers and a list of the results of that rule, and
    prints the results.
    '''

    n = len(rule_number)
    colored_text = colored(0, 128, 0, "\nRules generated after dimension " \
                           + dimension_name + " is applied to the chosen table.")
    print(colored_text)

    j = 0
    for i in range(n):
        string = str("\n" + rule_number[i])
        colored_text = colored(255, 171, 0, string)
        print(colored_text, '\n')
        for result in results[i]:
            print(str(j) + ": ", result)
            j += 1