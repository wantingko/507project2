#################################
##### Name: Wan-Ting Ko
##### Uniqname: wtko
#################################

from requests_oauthlib import OAuth1
from bs4 import BeautifulSoup
import requests
import json
import secrets 

url = "https://www.nps.gov"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")


#building cache
CACHE_FILENAME = "nps_cache.json"
CACHE_DICT = {}

client_key = secrets.MAPQUEST_API_KEY
client_secret = secrets.MAPQUEST_API_SECRET
oauth = OAuth1(client_key, client_secret=client_secret)

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

#do we need this part for this assignment?
def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    #TODO Implement function
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)
    return unique_key

def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    #TODO Implement function
    response = requests.get(baseurl, params=params, auth=oauth)
    return response.json()

#Michelle Tao taught me this part
def make_request_with_cache(baseurl, params={}):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search (i.e. "#2020election")
    count: int
        The number of tweets to retrieve
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #TODO Implement function
    CACHE_DICT = open_cache()
    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("Using cache")
        result = CACHE_DICT[request_key] #returns a string?
    else:
        print("Fetching")
        result = requests.get(baseurl, params).text
        CACHE_DICT[request_key] = result
        save_cache(CACHE_DICT)
    return result

#finish building cache 

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone=None, state_url=None):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
        self.state_url = state_url
    def info(self):
        return "{} ({}): {} {}".format(self.name, self.category, self.address, self.zipcode)

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_url_dic = {}
    state_list = []
    url_list = []
    searching_div = soup.find(id = 'HERO')

    child_divs = searching_div.find_all('ul', class_='dropdown-menu SearchBar-keywordSearch')
    for c_div in child_divs:
        c_link = c_div.find_all('a')
        for header in c_link:
            state_name = header.text
            state_list.append(state_name.lower())
        for link in c_link:
            c_path = link['href']
            url_path = 'https://www.nps.gov' + c_path
            url_list.append(url_path)
    state_url_dic = {state_list[i]: url_list[i] for i in range(len(state_list))} 
    return state_url_dic

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    response = requests.get(site_url)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        park_name = soup.find('a', class_='Hero-title').text.strip()
    except:
        park_name = 'No Name'
    try:
        park_category = soup.find('span', class_='Hero-designation').text.strip()
    except:
        park_category = 'No Category'

    try:
        park_address = soup.find('span', itemprop='addressLocality').text.strip()
    except:
        park_address = 'No Address'
    try: 
        park_address_state = soup.find('span', class_='region').text.strip()
    except: 
        park_address_state = 'No State'
    address= park_address + ', ' + park_address_state
    try:
        park_zipcode = soup.find('span', class_='postal-code').text.strip()
    except:
        park_zipcode = 'No Zipcode'
    try:
        park_phone = soup.find('span', itemprop='telephone').text.strip()
    except:
        park_phone = 'No Phone'

    instance_national_site = NationalSite(park_category, park_name, address, park_zipcode, park_phone)
    return instance_national_site

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    instance_list = []
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text.strip(), "html.parser")
    searching_div = soup.find_all('div', class_= 'col-md-9 col-sm-9 col-xs-12 table-cell list_left')

# Xiao-Han taught me this part
    for item in searching_div:
        url_path = 'https://www.nps.gov' + item.find('a')['href'] + 'index.htm'
        site_instance = get_site_instance(url_path)
        instance_list.append(site_instance)
    return instance_list

#part 4
def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    baseurl = 'http://www.mapquestapi.com/search/v2/radius'
    params = {'key': secrets.MAPQUEST_API_KEY, 'origin': site_object.zipcode, 
    'radius': 10, 'maxMatches': 10, 'ambiguities': 'ignore', 'outFormat': 'json'}

    response = requests.get(baseurl, params)
    # print(response)
    results = response.json()['searchResults']
    # print(results)
    for result in results:
        name = result['fields']['name']
        category = result['fields']['group_sic_code_name_ext']
        address = result['fields']['address']
        city = result['fields']['city']
    if category == '':
        return "- {} (no category): no address, no city".format(name)
        # print(f'- {name} (no category): no address, no city')
        # return "{} ({}): {} {}".format(self.name, self.category, self.address, self.zipcode)
    else:
        return "- {} ({}): {}, {}".format(name, category, address, city)
        # print(f'- {name} ({category}): {address}, {city}')

if __name__ == "__main__":

    # input_term = input("Enter a state name (e.g. Michigan, michigan) or 'exit': ")
    # count = 0

    # if input_term == 'exit':
    #     quit()
    # else:
    #     for url in build_state_url_dict():
    #         count += 1
    #         results = get_site_instance(url)
    #         print('[' + str(count) + ']' + results + '\n')
    #Am I on the right track?
    pass