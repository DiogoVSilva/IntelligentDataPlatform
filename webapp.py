
from flask import Flask, render_template, url_for, request, redirect, session
import pandas as pd
import csv
from pandas.core.frame import DataFrame
from dimensions import integrity, completeness, consistency, uniqueness, relevancy, conformity
from cleansing import cleansing_completeness, cleansing_consistency
from sklearn.neural_network import MLPClassifier

import pandas as pd
from sklearn.preprocessing import LabelEncoder

df = DataFrame()

pd.options.display.html.border = 0

app = Flask(__name__)
app.secret_key = "hello"


@app.route('/', methods=['GET','POST'])
@app.route('/home',methods=['GET','POST'])
def home():
    return render_template("home.html")


@app.route('/insertData', methods=['GET', 'POST'])
def insertData():
    if request.method == "POST":

        file = request.files["file"]
        df = pd.read_csv(file)
        dict_obj = df.to_dict('list')
        session['data'] = dict_obj

        return render_template("insertData.html", message="Your file was uploaded sucessfully!")
    
    return render_template("insertData.html", message="Upload")


@app.route('/choice1', methods=['GET','POST'])
def choice1(): # choose analyze or correct
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    return render_template("choice1.html", data=df)


@app.route('/analyze', methods=['GET','POST'])
def analyze():
    
    session['min_confidence'] = 0
    session['max_confidence'] = 100

    if request.method=="POST":
        min = request.form.get('min')
        max = request.form.get('max')

        session['min_confidence'] = min
        session['max_confidence'] = max

        return render_template("analyze.html", message="Min value set to " + str(session['min_confidence']) +" and max value set to "+str(session['max_confidence'])+".")
    
    session['min_confidence'] = 0
    session['max_confidence'] = 100
    
    return render_template("analyze.html", message="Min value set to None and max value set to None.")

@app.route('/integrity', methods=['GET', 'POST'])
def integrity_page():
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1,res2 = integrity(df, int(session['min_confidence']), int(session['max_confidence']))

    if len(res1)==0:
        res1.append("No results available.")

    if len(res2)==0:
        res2.append("No results available.") 

    return render_template("integrity.html", res1 = res1, res2= res2)


@app.route('/completeness', methods=['GET', 'POST'])
def completeness_page():
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1,res2,res3 = completeness(df, int(session['min_confidence']), int(session['max_confidence']))

    if len(res1)==0:
        res1.append("No results available.")

    if len(res2)==0:
        res2.append("No results available.") 

    if len(res3)==0:
        res3.append("No results available.")

    return render_template("completeness.html", res1 = res1, res2= res2, res3=res3)


@app.route('/consistency', methods=['GET', 'POST'])
def consistency_page():
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1 = consistency(df, int(session['min_confidence']), int(session['max_confidence']))

    if len(res1)==0:
        res1.append("No results available.")

    return render_template("consistency.html", res1 = res1)


@app.route('/uniqueness', methods=['GET', 'POST'])
def uniqueness_page():
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1,res2 = uniqueness(df, int(session['min_confidence']), int(session['max_confidence']))

    if len(res1)==0:
        res1.append("No results available.")

    if len(res2)==0:
        res2.append("No results available.") 

    return render_template("uniqueness.html", res1 = res1, res2= res2)


@app.route('/relevancy1', methods=['GET', 'POST'])
def relevancy_insertData():
    if request.method == "POST":

        file = request.files["file2"]
        df = pd.read_csv(file)
        dict_obj = df.to_dict('list')
        session['data2'] = dict_obj

        return render_template("relevancy1.html", message="success")
    
    return render_template("relevancy1.html", message="Upload")


@app.route('/relevancy', methods=['GET', 'POST'])
def relevancy_page():
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)

    dict_obj2 = session['data2'] if 'data2' in session else ""  
    df2 = pd.DataFrame(dict_obj2)

    res1,res2 = relevancy(df,df2, "table1", "table2", int(session['min_confidence']), int(session['max_confidence']))

    if len(res1)==0:
        res1.append("No results available.")

    if len(res2)==0:
        res2.append("No results available.") 

    return render_template("relevancy.html", res1 = res1, res2= res2)


@app.route('/conformity', methods=['GET', 'POST'])
def conformity_page():
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1,res2,res3,res4,res5 = conformity(df, int(session['min_confidence']), int(session['max_confidence']))

    if len(res1)==0:
        res1.append("No results available.")

    if len(res2)==0:
        res2.append("No results available.") 

    if len(res3)==0:
        res3.append("No results available.")

    if len(res4)==0:
        res4.append("No results available.") 
    
    if len(res5)==0:
        res5.append("No results available.")


    return render_template("conformity.html", res1 = res1, res2= res2, res3=res3, res4=res4, res5=res5)


@app.route('/correct', methods=['GET','POST'])
def correct():

    session['min_confidence'] = 0
    session['max_confidence'] = 100

    if request.method=="POST":
        min = request.form.get('min')
        max = request.form.get('max')

        session['min_confidence'] = min
        session['max_confidence'] = max

        return render_template("correct.html", message="Min value set to " + str(session['min_confidence']) +" and max value set to "+str(session['max_confidence'])+".")
    
    session['min_confidence'] = 0
    session['max_confidence'] = 100
    
    return render_template("correct.html", message="Min value set to None and max value set to None.")


@app.route('/fix_with_completeness', methods=['GET','POST'])
def fix_with_completeness():
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1,res2,res3 = completeness(df, int(session['min_confidence']), int(session['max_confidence']))

    if len(res1)==0:
        res1.append("No results available.")

    if len(res2)==0:
        res2.append("No results available.") 

    if len(res3)==0:
        res3.append("No results available.")

    if request.method=="POST":
        rule_number = request.form.get('rule_number')
        session['rule_number'] = rule_number
        return render_template('fix_with_completeness.html', res1=res1,res2=res2,res3=res3, message="Rule number set to "+str(session['rule_number'])+".")
    
    

    return render_template('fix_with_completeness.html', res1=res1,res2=res2,res3=res3, message="Rule number set to None.")

@app.route('/completeness_results',methods=['GET','POST'])
def completeness_results():

    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1,res2,res3 = completeness(df, int(session['min_confidence']), int(session['max_confidence']))
    
    rule_number = int(session['rule_number'])-1
    rule = res1[rule_number]
    altered_rows, altered_dataframe = cleansing_completeness(df, rule)

    dict_obj = altered_dataframe.to_dict('list')
    session['data_altered'] = dict_obj

    return render_template('completeness_results.html', rule=rule,altered_rows=altered_rows, altered_dataframe=altered_dataframe)


@app.route('/fix_with_consistency', methods=['GET','POST'])
def fix_with_consistency():
    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1 = consistency(df, int(session['min_confidence']), int(session['max_confidence']))

    if len(res1)==0:
        res1.append("No results available.")


    if request.method=="POST":
        rule_number = request.form.get('rule_number')
        session['rule_number'] = rule_number
        return render_template('fix_with_consistency.html', res1=res1, message="Rule number set to "+str(session['rule_number'])+".")



    return render_template('fix_with_consistency.html', res1=res1, message="Rule number set to None.")


@app.route('/consistency_results',methods=['GET','POST'])
def consistency_results():

    dict_obj = session['data'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    res1 = consistency(df, int(session['min_confidence']), int(session['max_confidence']))
    
    rule_number = int(session['rule_number'])-1
    rule = res1[rule_number]
    altered_rows, altered_dataframe = cleansing_consistency(df, rule)

    dict_obj = altered_dataframe.to_dict('list')
    session['data_altered'] = dict_obj

    return render_template('consistency_results.html', rule=rule,altered_rows=altered_rows, altered_dataframe=altered_dataframe)


@app.route('/change_original_df', methods=['GET','POST'])
def change_original_df():

    dict_obj = session['data_altered'] if 'data' in session else ""  
    df = pd.DataFrame(dict_obj)
    session['data'] = dict_obj

    return render_template('change_original_df.html', altered_dataframe = df)



@app.route('/download', methods=['POST','GET'])
def download():
    if request.method=="POST":
        file_name = request.form.get('file_name')
        dic = session['data']
        df = pd.DataFrame(dic)
        df.to_csv(""+file_name+".csv",index=False)

    return render_template('download.html')

if __name__ == "__main__":
    app.run(debug=True)