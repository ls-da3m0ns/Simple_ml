import time
import os
from textblob import TextBlob

import flask 
from flask import Flask,request,url_for
from flask import render_template

from tempfile import NamedTemporaryFile
import cv2
import easyocr
import pandas as pd
import random 
from utils import *

app = Flask(__name__)

reader = None
generated_dir = ""

def populate_reader():
    global reader
    reader = easyocr.Reader(['en'])

def paragraph_prediction(paragraph):
    data = dict()
    blob = TextBlob(paragraph)

    overall_polarity = blob.sentiment.polarity
    overall_subjectivity = blob.sentiment.subjectivity

    sentences = []
    for sentence in blob.sentences:
        sentences.append([str(sentence),
                f"{sentence.sentiment.polarity:.4f}",
                f"{sentence.sentiment.subjectivity:.4f}",
                sentence.sentiment_assessments.assessments])

    for i in range(len(sentences)):
        for j in range(len(sentences[i][-1])):
            ahem = sentences[i][-1][j]
            sentences[i][-1][j] = (ahem[0], f"{ahem[1]:.4f}", f"{ahem[2]:.4f}")

    return {
        "polarity": f"{overall_polarity:.4f}",
        "subjectivity": f"{overall_subjectivity:.4f}",
        "sentences": sentences
    }



@app.route('/ocr', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        print(request.files)
        start_time = time.time()
        if 'tmp_filename' not in request.files:
            return 'there is no tmp_filename in form!'

        file1 = request.files['tmp_filename']
        extention = os.path.splitext(file1.filename)
        with NamedTemporaryFile() as temp:
            iname = "".join([str(temp.name), extention[-1]])
            file1.save(iname)
            result = reader.readtext(iname)

        text_chunks = []
        for res in result:
            text_chunks.append(res[1])

        text = " ".join(text_chunks)
        prediction = paragraph_prediction(text)
        #print(prediction)
        all_sentences = prediction["sentences"]

        sentencess = []
        polara = []
        subjec = []
        key_words_fordecision = []

        for pair in all_sentences:
            sen = pair[0]
            pola = pair[1]
            subj = pair[2]

            #print(pair)
            if len(pair[3]) > 0:
                key_words = ' '.join([str(elem) for elem in pair[3][0][0]]) 
            else:
                key_words = "No keywords"

            sentencess.append(sen)
            polara.append(pola)
            subjec.append(subj)
            key_words_fordecision.append(key_words)
        
        df = pd.DataFrame({"Sentence": sentencess,
            "polarity": polara,
            "subjectivity": subjec,
            "key_words": key_words_fordecision})


        return render_template("outputs_ocr.html",
        sentences= text,
         polarity = prediction["polarity"],
         subjectivity = prediction["subjectivity"],
         time_taken=str(time.time() - start_time),
         tables=[df.to_html(classes='data',index=False)], titles=df.columns.values
         )

@app.route('/home', methods=['POST'])
def upload_text():
    if request.method == 'POST':
        #print(request.values)
        start_time = time.time()
        text = request.form['text']
        prediction = paragraph_prediction(text) 
        #print(prediction)#call your model here
        #text_sentence = prediction["text"]
        all_sentences = prediction["sentences"]

        sentencess = []
        polara = []
        subjec = []
        key_words_fordecision = []

        for pair in all_sentences:
            sen = pair[0]
            pola = pair[1]
            subj = pair[2]

            print(pair)
            if len(pair[3]) > 0:
                key_words = ' '.join([str(elem) for elem in pair[3][0][0]]) 
            else:
                key_words = "No keywords"

            sentencess.append(sen)
            polara.append(pola)
            subjec.append(subj)
            key_words_fordecision.append(key_words)
        
        df = pd.DataFrame({"Sentence": sentencess,
            "polarity": polara,
            "subjectivity": subjec,
            "key_words": key_words_fordecision})
        
        #print(df.head())
        #print(sentencess,polara,subjec,key_words_fordecision)
        actual_text = " ".join(sentencess)


        return render_template("outputs_sentiment_analysis.html",
        polarity = prediction["polarity"],
        actual_text = actual_text,
        subjectivity = prediction["subjectivity"],
        time_taken=str(time.time() - start_time),
        tables=[df.to_html(classes='data',index=False)], titles=df.columns.values
        )

@app.route('/document',methods=['POST'])
def upload():
    if request.method == 'POST':
        print(request.files)
        start_time = time.time()
        if 'tmp_filename2' not in request.files:
            return 'there is no tmp_filename in form!'

        file1 = request.files['tmp_filename2']
        extention = os.path.splitext(file1.filename)
        iname = ""
        with NamedTemporaryFile(dir="/home/home/simpleml/static/") as temp:
            iname = "".join([str(temp.name), extention[-1]])
            file1.save(iname)
        message = []
        
        output, flag = image(iname)
        sharp_image = sharpen(output)
        super_resoluted_img = super_resolution(sharp_image)
        smooth(iname)

        return render_template("document.html",
            output_image = iname
        )

@app.route("/",methods=["GET"])
def start_page():
    return render_template("index.html")

@app.route("/home",methods=["GET"])
def home_page():
    return render_template("home.html")

@app.route("/liveaudio",methods=["GET"])
def audio():
    return render_template("liveaudio.html")

if __name__ == "__main__":
    populate_reader()
    app.run(debug=True)
