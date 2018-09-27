import Queue
import operator
from data_structures import history
from bottle import Bottle, route, run, template, get, post, request

history = history()

# ask for keywords from user 
@get('/') # or @route('/')
def submit_form():
    return '''
        <form action="/" method="post">
            <input name="keywords" type="text" />            
            <input value="Search" type="submit" />
        </form>
    '''

# show search results, word count, and search history
@post('/') # or @route('/', method='POST')
def show_results():
    # http get recorded keyword
    keywords = request.forms.get('keywords')
    history.add_new_keyword(keywords)
    
    # split keyword string into words and count them
    # store them in a dictionary
    words_list = keywords.split()
    words_count = {word:words_list.count(word) for word in words_list}

    #TEMPLATE_PATH.append('/nfs/ug/homes-0/y/yanggan/csc326/frontend')

   
    return template('results_page_template', keywords=keywords, words_count=words_count, history=history.items())


# run server
run(host='localhost', port=8081, debug=True)


