import numpy as np
import pandas as pd
from urllib.parse import urlparse
import re
from tld import get_tld
import pickle

def proc_tld(url):
    if url.startswith('http:'):
        res = get_tld(url, as_object = True, fail_silently=False, fix_protocol=False)
    else:
        res = get_tld(url, as_object = True, fail_silently=False, fix_protocol=True)
    return len(res.subdomain), len(res.domain), len(res.tld), len(res.fld)

def proc_tld_url(entry):
    try:
        if entry['is_ip'] == 0:
            return proc_tld(entry['url'])
        return 'invalid', 'invalid', 'invalid', 'invalid'
    except Exception as e:
        return 'badurl', 'badurl', 'badurl', 'badurl'

def check_url(url):
    match = re.search(str(urlparse(url).hostname), url)
    if match:
        return 1
    else:
        return 0
    
def check_https(url):
    match = str(urlparse(url).scheme)
    if match=='https':
        return 1
    else:
        return 0
    
def count_numbers(url):
    count = 0
    for itr in url:
        if itr.isnumeric():
            count+=1
    return count

def count_alphabets(url):
    count = 0
    for itr in url:
        if itr.isalpha():
            count+=1
    return count

#Taken from @habibmrad notebook from kaggle
def Shortining_Service(url):
    match = re.search('bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                      'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                      'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                      'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                      'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                      'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                      'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|'
                      'tr\.im|link\.zip\.net',
                      url)
    if match:
        return 1
    else:
        return 0

#Taken from @sid321xan notebook from kaggle
def is_url_ip_address(url: str) -> bool:
    match = re.search(
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4
        '(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.'
        '([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|'  # IPv4 with port
        '((0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\.(0x[0-9a-fA-F]{1,2})\\/)' # IPv4 in hexadecimal
        '(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}|'
        '([0-9]+(?:\.[0-9]+){3}:[0-9]+)|'
        '((?:(?:\d|[01]?\d\d|2[0-4]\d|25[0-5])\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d|\d)(?:\/\d{1,2})?)', url)  # Ipv6
    if match:
        return 1
    else:
        return 0

def url_path(url):
    try:
        res = get_tld(url, as_object = True, fail_silently=False, fix_protocol=True)
        path = ''
        if res.parsed_url.query:
            path = res.parsed_url.path + res.parsed_url.query
        else:
            path = res.parsed_url.path
        return len(path.split('/'))
    except:
        return 0


def prepare_input(url):
    data = pd.DataFrame(data={'url':[url],'type':[None]})
    data['length_of_url'] = data['url'].apply(lambda url: len(url) )
    features = ['@','?','-','=','.','#','%','+','$','!','*',',','//']
    for feature in features:
        data[feature] = data['url'].apply(lambda i: i.count(feature))
    data['abnormal_url'] = data['url'].apply(lambda i: check_url(i))
    data['https_scheme'] = data.url.apply(lambda url: check_https(url))
    data['count_numbers'] = data.url.apply(lambda url: count_numbers(url))
    data['count_alphabets'] = data.url.apply(lambda url: count_alphabets(url))
    data['is_ip'] = data['url'].apply(lambda url: is_url_ip_address(url))
    data[['subdomain', 'domain', 'tld', 'fld']] = data.apply(lambda entry: proc_tld_url(entry), axis=1, result_type="expand")   
    data['is_ip'] = data['url'].apply(lambda url: is_url_ip_address(url))
    data['short_url'] = data.url.apply(lambda url: Shortining_Service(url))
    data['url_path_length'] = data.url.apply(lambda url: url_path(url))
    data['numeric_ratio'] = data.apply(lambda entry: entry['count_numbers']/entry['length_of_url'], axis=1)
    data['character_ratio'] = data.apply(lambda entry: entry['count_alphabets']/entry['length_of_url'], axis=1)
    data['fld'] = data['fld'].replace('invalid',-1)
    data['fld'] = data['fld'].replace('badurl',-1)
    data['length_of_url'] = (data['length_of_url'] - 2)/(193)
    data['url_path_length'] = data['url_path_length']/29
    data['numeric_ratio'] = data['numeric_ratio']/0.378571
    data['character_ratio'] = (data['character_ratio']-0.409836)/0.590164

    data['subdomain'] = data['subdomain'].replace('invalid',-1)
    data['subdomain'] = data['subdomain'].replace('badurl',-1)

    data['domain'] = data['domain'].replace('invalid',-1)
    data['domain'] = data['domain'].replace('badurl',-1)

    data['tld'] = data['tld'].replace('invalid',-1)
    data['tld'] = data['tld'].replace('badurl',-1)
    
    return(data)

def make_prediction(input_array):
    #data= input_array.iloc[:,[0,2,3,4,5,6,7,8,12,13,14,16,17,19,20,21,22,23,24,25,26]]
    data = input_array[['length_of_url', '?', '-', '=', '.', '#', '%', '+', ',', '//','abnormal_url', 'count_numbers', 'count_alphabets', 'subdomain','domain', 'tld', 'fld', 'short_url', 'url_path_length', 'numeric_ratio', 'character_ratio']]
    model = pickle.load(open('rfmodel.pkl','rb'))
    pred = model.predict(data)
    return pred
