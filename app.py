from flask import Flask, request, Response, render_template, jsonify, make_response
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Regexp
import re
import string

class WordForm(FlaskForm):
    avail_letters = StringField("Letters", validators= [
        Regexp(r'^$|^[a-z]+$', message="must contain letters only")
    ])
    submit = SubmitField("Go")


csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/index')
def index():
    form = WordForm()
    return render_template("index.html", form=form, name = "Isaac Skorseth")


@app.route('/words', methods=['POST','GET'])
def letters_2_words():
    form = WordForm()
    select = request.form.get('count')
    regex = request.form.get('pattern')
    if(regex != ""):
        if(int(select) != int(len(regex))):
            return("Character Count Doesn't Match Pattern Size")
    pattern = re.compile(regex)
    if form.validate_on_submit():
        letters = form.avail_letters.data
    else:
        return render_template("index.html", form=form)

    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = set()
    if(letters == ""):
        if(regex == ""):
            return("No Letters Or Pattern Specified")
        else:
            count = int(select)
            letters = string.ascii_lowercase
    else:
        count = len(letters)
    for l in range(3,count+1):
        for word in itertools.permutations(letters,l):
            w = "".join(word)
            if(pattern.match(w)):
                if w in good_words:
                    if(select == ""):
                        word_set.add(w)
                    elif(len(w) == int(select)):
                        word_set.add(w)
                    else:
                        continue

    return render_template('wordlist.html',
        wordlist = sorted(sorted(word_set), key=len),
        name="Isaac Skorseth")


@app.route('/api', methods=["GET"])
def api():
    url = "https://dictionaryapi.com/api/v3/references/collegiate/json/"
    key = "e51d9655-d28b-40b3-a743-f807bc42b130"
    if request.method == "GET":
        word = request.args.get('word')
        fullURL = url + word + "?key=" + key
        response = requests.get(fullURL)
        res = make_response()
        data = response.json()
        dic = data[0]
        definition = dic['shortdef']
        stuff = definition[0].encode('ascii', "ignore")
        res.headers['data'] = stuff 
        return res

@app.route('/proxy')
def proxy():
    result = requests.get(request.args['url'])
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp


