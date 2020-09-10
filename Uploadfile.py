import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import pyreadstat
import numpy as np
import requests

from Code_update import Check

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Upload.html')

@app.route('/uploader', methods=['POST'])
def upload_file():
    filename = request.form['fnname']
    Brand_fromUser = request.form['Brand']
    Second_Brand_fromUser = request.form['Brand2']
    Other = request.form['Other']
    NoneVal = request.form['NoneVal']
    Dont = request.form['Dont']
    Prefer = request.form['Prefer']
    uploaded_file1 = request.form['path']
    #BrandQ = request.form['BrandQ']
    MergeStr = request.form['merge']
    result = list(Check(uploaded_file1,filename,Brand_fromUser,Other,NoneVal,Dont,Prefer,MergeStr,Second_Brand_fromUser))
    if len(result) > 0:
        return render_template('sucsess.html',path=uploaded_file1,lab=result[1],tables1=len(result[1].index),tables=len(result[0].index),Message=[result[0].loc[x,2] for x in range(len(result[0].index))],Qnumber=[result[0].loc[x,0] for x in range(len(result[0].index))],Created_Label=[result[0].loc[x,1] for x in range(len(result[0].index))])
    else:
        return render_template('sucsess.html',path=uploaded_file1)    

    

@app.errorhandler(500) 
def not_found(e): 
  return render_template("500.html")   

@app.route('/uploader1', methods=['POST'])
def upload_file1():
    uploaded_file = request.files['file']
    uploaded_file1 = request.form['text']
    filename = secure_filename(uploaded_file.filename)
    ab=os.path.join(uploaded_file1,filename)
    uploaded_file.save(os.path.join(uploaded_file1,filename))
    fn = os.path.join(uploaded_file1, filename)
    Updated_path = fn.replace('\\', '/') 
    (df, meta) = pyreadstat.read_sav(Updated_path)
    meta_data = meta.column_names_to_labels
    col = meta.column_names
    Value_label = meta.variable_value_labels
    with_dot=[]
    for i in col:
        if "." in i:
            val = i.split(".")[-1]
            with_dot.append(val)
    if len(with_dot)>0:
        return render_template('index.html',file1=uploaded_file1,fnname=filename,colname=int(with_dot[-1]),Merge_check=Value_label)
    else:
        return render_template('index.html',file1=uploaded_file1,fnname=filename,Merge_check=Value_label)    

    