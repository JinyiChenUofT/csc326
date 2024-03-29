from __future__ import division 
import Queue
import operator
import json
import httplib2
import requests
import os
import urllib
import sqlite3 as lite
from backend.static_variables import StaticVar
from backend.data_structures import UserHistoryIndex, History, UserRecentWordsIndex, RecentWords
from backend.database import MyDatabase
from backend.oxfordDictionaryCrawler import MyDictionary
from bottle import Bottle, route, run, template, get, post, request, static_file, redirect, app, error
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware
from spellchecker import SpellChecker
from autocorrect.nlp_parser import NLP_COUNTS
from autocorrect.word import Word, common, exact, known, get_case

# declare golbal variables
user_history_index = UserHistoryIndex()
user_recent_words_index = UserRecentWordsIndex()

current_page = 'query_page'

keywords = ''
first_word = ''
words_count = []
corrected_keywords = ""
calculation_result = 0.0

num_per_page = 0
page_num_counts = 0
cur_page_num = 0
document = []

SCOPE = StaticVar.SCOPE
REDIRECT_URI = StaticVar.REDIRECT_URI
sessions_opts = StaticVar.sessions_opts
database_file = 'backend/'+StaticVar.database_file
num_per_page = StaticVar.num_per_page

history = History()

# ask for keywords from user
@get('/')  # or @route('/')
def home():
    session = request.environ.get('beaker.session')
    if "user_email" in session:        
        return template('./templates/query_page.tpl', login = True, 
                user_email = session["user_email"], recent_words = user_recent_words_index.get_recent_words(session["user_email"]))
    else:
        return template('./templates/query_page.tpl', login = False)

# show search results, word count, and search history
@post('/')  # or @route('/', method='POST')
def show_results():
    global keywords
    global first_word
    global words_count
    global corrected_keywords
    global calculation_result

    # keyword from http get    
    keywords = request.forms.get('keywords')

    if '+' or '-' or '*' or '/' or '**' or '^' in keywords:
        try:
            calculation_result = eval(keywords)
        except:
            calculation_result = 0.0
    
    # split keyword string into words and count them
    # store words in a dict
    words_list = keywords.split()
    words_count = {word: words_list.count(word) for word in words_list}

    for i in range(len(words_list)):
        words_list[i] = autocorrect(words_list[i])
    corrected_keywords = ' '.join(words_list)
    
    #if input is empty, go back homepage
    if not words_list:
        redirect('/')
    #if there is input words, check in the database
    else:
        first_word = words_list[0]
        # lowercase first keyword
        first_word = first_word.lower()

        # encode url
        quoted_url=''
        if '/' in keywords:
            quoted_url = keywords.replace('/','%')
        else:
            quoted_url = urllib.quote_plus(keywords)
        
        redirect('/keyword/' + quoted_url + '/page_no/1')

        #redirect('/keyword/' + keywords + '/page_no/1')

def autocorrect(misspelled):
    """most likely correction for everything up to a double typo"""
    w = Word(misspelled)
    candidates = (common([misspelled]) or exact([misspelled]) or known([misspelled]) or
                    known(w.typos()) or common(w.double_typos()) or [misspelled])
    correction = max(candidates, key=NLP_COUNTS.get)
    return get_case(misspelled, correction)

# pagination for urls found
@route('/keyword/<keyword>/page_no/<page_no>')
def search_first_word(keyword, page_no):
    # decode url    
    if "%" in keyword:
        keyword = keyword.replace('%','/')
    else:
        keyword = urllib.unquote_plus(keyword)
    
    # split keyword string into words
    words_list = keyword.split()

    # connect to database
    db_conn = lite.connect(database_file)
    myDB = MyDatabase(db_conn)

    # get word ids and crawler ids from lexicon
    word_id_list = myDB.select_word_id_from_lexicon(words_list)
    # get document ids and crawler ids from inverted index
    sorted_document_id = myDB.select_document_id_from_InvertedIndex(word_id_list)    
    
    global num_per_page
    global page_num_counts
    global cur_page_num
    global document

    # get document ids and crawler ids based on page number
    url_counts = len(sorted_document_id)    
    page_num_counts = pagination(url_counts)
    cur_page_num = int(page_no)
    if cur_page_num > 0:
        cur_page_num = cur_page_num -1
    start_num = cur_page_num * num_per_page
    end_num = start_num + num_per_page   
    document = myDB.select_document_from_DocumentIndex(sorted_document_id[start_num:end_num])

    db_conn.close()

    session = request.environ.get('beaker.session')
    if "user_email" in session:
        user_history_index.get_history(session["user_email"]).add_new_keywords(words_list)
        user_recent_words_index.get_recent_words(session["user_email"]).add_new_keywords(words_list)
        return template('./templates/result_page.tpl', keywords = keywords, corrected_keywords=corrected_keywords, words_count = words_count, 
                login = True, user_email = session["user_email"], recent_words = user_recent_words_index.get_recent_words(session["user_email"]),
                history = user_history_index.get_history(session["user_email"]).get_popular(), first_word = first_word, document = document, 
                cur_page_num = cur_page_num+1, num_per_page = num_per_page, page_num_counts = page_num_counts,calculation_result = calculation_result)
    else:
        user_history_index.get_history("anonymous").add_new_keywords(words_list)
        return template('./templates/result_page.tpl', keywords = keywords,corrected_keywords=corrected_keywords, words_count = words_count, 
                login = False, history = user_history_index.get_history("anonymous").get_popular(),first_word = first_word, document = document, 
                cur_page_num = cur_page_num+1, num_per_page = num_per_page, page_num_counts = page_num_counts,calculation_result = calculation_result)

def pagination(url_counts):
    # q for quotient, r for remainder
    q, r = divmod(url_counts, num_per_page)
    if r != 0:
        page_num_counts = q+1
    else:
        page_num_counts = q
    return page_num_counts

@route('/calculator/<result>')
def calculator(result):
    global calculation_result
    calculation_result =  calculation_result
    return template('./templates/calculator.tpl',calculation_result=calculation_result)

@route('/dictionary/<word>')
def dictionary(word):
    MyDict=MyDictionary()
    #look up words in dictionary
    translation=MyDict.translateWords(word)
    return template('./templates/dictionary.tpl',translation=translation,word=word)

@error(404)
def error404(error):
    return template('./templates/error_page.tpl',error=error)

# if user login in the query_page, set the current page to query_page
# and then redirect to Google login
@route('/login', method='GET')
def query_page():
    global current_page
    current_page = 'query_page'
    google_login()

# if user login in the result_page, set the current page to result_page
# and then redirect to Google login
@route('/login/result', method='GET')
def result_page():
    global current_page
    current_page = 'result_page'
    google_login()

# redirect to Google login prompt for user authentication
def google_login():
    flow = flow_from_clientsecrets('client_secrets.json', scope=SCOPE, redirect_uri=REDIRECT_URI)
    uri = flow.step1_get_authorize_url()
    return redirect(str(uri))

def credentials_to_dict(credentials):
    return {'access_token': credentials.access_token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'revoke_uri': credentials.revoke_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

# redirect to Google logout prompt, and then redirect to the query_page
@route('/logout', method='GET')
def google_logout():
    session = request.environ.get('beaker.session')
    requests.post('https://accounts.google.com/o/oauth2/revoke',
                params={'token': session["token"]},
                headers = {'content-type': 'application/x-www-form-urlencoded'})
    session.delete() 
    return redirect('/')


#If user authorizes your application server to access the Google services, an one-time code will be attached
#to the query string when the browser is redirected to the redirect_uri specified in step 2. 
#The one-time code can be retrieved as GET parameter:
@route('/redirect')
def redirect_page():
    code = request.query.get('code', '')

    with open("client_secrets.json", 'r') as load_f:
        load_dict = json.load(load_f)

    flow = OAuth2WebServerFlow(client_id=load_dict['web']['client_id'], client_secret=load_dict['web']['client_secret'],
                               scope=SCOPE, redirect_uri=REDIRECT_URI)
    credentials = flow.step2_exchange(code)

    # acquire refresh tokens for offline access, syncing Google accounts when users are not actively logged in.
    #token = credentials.id_token['sub']
    token = credentials.access_token

    # retrieve user's data
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Get user info
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']    

    # maintain a session for the user
    session = request.environ.get('beaker.session')
    session["user_email"] = user_email
    session['credentials'] = credentials_to_dict(credentials)
    session["token"] = token
    if "name" in user_document.keys():
        session['user_name'] = user_document['name']
    session.save()

    return redirect('/user')

#after user login, they will stay on the same page (query_page || result_page)
@route('/user')
def user_login():
    session = request.environ.get('beaker.session')
    if current_page == 'query_page':
        return template('./templates/query_page.tpl', login = True, 
            user_email = session["user_email"], recent_words = user_recent_words_index.get_recent_words(session["user_email"]))
    else:
        return template('./templates/result_page.tpl', keywords = keywords, words_count = words_count, corrected_keywords=corrected_keywords,
            login = True, user_email = session["user_email"], recent_words = user_recent_words_index.get_recent_words(session["user_email"]),
            history = user_history_index.get_history(session["user_email"]).get_popular(),first_word = first_word, document = document, 
            cur_page_num = cur_page_num, num_per_page = num_per_page, page_num_counts = page_num_counts,calculation_result = calculation_result)

# routes of assets (css, js, images)
@route('/assets/<filename:path>')
def send_assets(filename):
    return static_file(filename, root='./assets')

# route of templates
@route('/templates/<filename:path>')
def send_templates(filename):
    return static_file(filename, root='./templates')

if __name__ == "__main__":
    app = SessionMiddleware(app(), sessions_opts)
    # run server
    run(app=app, host='0.0.0.0', port=80, debug=True)
