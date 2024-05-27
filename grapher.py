import os
import pickle
import re
import sys
import time
from html.parser import HTMLParser

import matplotlib.pyplot as plt
import networkx as nx
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

FB_USERNAME = ''
FB_USERID = ''
FB_PASSWORD = ''

FRIENDS_URLS_FILENAME = 'friends_urls.pickle'
GRAPH_FILENAME = 'friend_graph.pickle'


# filter the page to get the friends URLs
class FriendsURLsParser(HTMLParser):
    urls = []

    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            class_name = "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xi81zsa xo1l8bm"
            ok = False
            for name, value in attrs:
                if name == "class" and value == class_name:
                    ok = True
                if name == "href" and ok:
                    self.urls.append(value)  


# filter friend name or id from URL
def find_friend_from_url(url):
    # https://www.facebook.com/profile.php?id=123456789&sk=friends_mutual -> 123456789
    m = re.search(r'profile\.php\?id=(\d+)', url)
    if m:
        return m.group(1)

    # https://www.facebook.com/john.john.3/friends_mutual -> john.john.3
    m = re.search(r'facebook\.com/([^/]+)', url)
    if m:
        return m.group(1)
    return None


class FacebookScraper:
    def __init__(self):
        # launch browser
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.get('http://www.facebook.com/')

        # authenticate into Facebook
        elem = self.driver.find_element("id", "email")
        elem.send_keys(FB_USERNAME)
        elem = self.driver.find_element("id", "pass")
        elem.send_keys(FB_PASSWORD)
        elem.send_keys(Keys.RETURN)
        time.sleep(5)

    # load, expand and return a page
    def get_page(self, url):
        time.sleep(5)
        self.driver.get(url)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        print('last_height:', last_height)

        while True:

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height < last_height:
                print('limit reached')
                sys.exit(1)
        
            print('new_height:', new_height)
            if new_height == last_height:

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(4)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height < last_height:
                    print('limit reached')
                    sys.exit(1)
                
                if new_height == last_height:
                    break
                
            last_height = new_height

        return self.driver.page_source
    

fb_scraper = FacebookScraper()


# scrap friends if needed
if not os.path.isfile(FRIENDS_URLS_FILENAME):
    friends_page = fb_scraper.get_page(f'https://www.facebook.com/{FB_USERID}/friends')

    friends_urls_parser = FriendsURLsParser()
    friends_urls_parser.feed(friends_page)
    friends_urls = set(friends_urls_parser.urls)

    with open(FRIENDS_URLS_FILENAME, 'wb') as f:
        pickle.dump(friends_urls, f)
    
    print(f'We saved {len(friends_urls)} friends')


# load friends
with open(FRIENDS_URLS_FILENAME, 'rb') as f:
    friends_urls = pickle.load(f)

print(f'We loaded {len(friends_urls)} friends')


# init graph
friends_connections = {}

if os.path.isfile(GRAPH_FILENAME):
    with open(GRAPH_FILENAME, 'rb') as f:
        friends_connections = pickle.load(f)
    print('Loaded existing graph, found {} keys'.format(len(friends_connections.keys())))


# get mutual friends
count = 0
for friend_url in tqdm(friends_urls):

    print('friend_url:', friend_url)

    friend_username_or_id = find_friend_from_url(friend_url)

    # refresh all friends with 8 connections (may be a scraper bug)
    #  and (len(friends_connections[friend_username_or_id]) != 8)
    if ((friend_username_or_id in friends_connections.keys()) and len(friends_connections[friend_username_or_id]) > 1):
        continue

    print('friend_username_or_id:', friend_username_or_id)

    friends_connections[friend_username_or_id] = [FB_USERNAME]

    try :
        mutual_friends_page = fb_scraper.get_page(friend_url)
    except:
        print('error')
        continue

    parser = FriendsURLsParser()
    parser.urls = []
    parser.feed(mutual_friends_page)
    mutual_friends_urls = set(parser.urls)
    print(f'Found {len(mutual_friends_urls)} mutual friends')

    for mutual_url in mutual_friends_urls:
        mutual_friend = find_friend_from_url(mutual_url)
        friends_connections[friend_username_or_id].append(mutual_friend)

    with open(GRAPH_FILENAME, 'wb') as f:
        pickle.dump(friends_connections, f)

    count += 1
    # if count % 50 == 0:
    #     print ("Too many queries, pause for a while...")
    #     time.sleep(120)


class FriendsGraph:

    def __init__(self):
        self._load_connections()
        self._create_edges()

        self.G = nx.Graph()
        self.G.add_nodes_from([FB_USERID])
        self.G.add_nodes_from(self.central_friends.keys())
        self.G.add_edges_from(self.edges)

        print('Added {} edges'.format(len(self.edges) ))

    def _load_connections(self):
        with open(GRAPH_FILENAME, 'rb') as f:
            friends_connections = pickle.load(f)
        print('friends:', len(list(friends_connections.keys())))

        self.central_friends = {}
        for k, v in friends_connections.items():
            print('k:', k, 'v:', v)
            # intersection_size = len(np.intersect1d(list(friends_connections.keys()), v))
            # if intersection_size > 2:
            self.central_friends[k] = v

        # print('Firtered out {} items'.format(len(friends_connections.keys()) - len(central_friends.keys())))

    def _create_edges(self):
        self.edges = []
        nodes = [FB_USERID]
        n_none = 0

        central_friends_cp = self.central_friends.copy()

        for k, v in central_friends_cp.items():
            if k == None:
                n_none += 1
                self.central_friends.pop(k)
            for item in v:
                if item in central_friends_cp.keys() or item == FB_USERID:
                    self.edges.append((k, item))

        print('None:', n_none)        

    def preview(self):
        # layout algorithm
        pos = nx.kamada_kawai_layout(self.G)
        plt.rcParams['figure.figsize'] = [10, 10]
        nx.draw_networkx(self.G, pos=pos, with_labels=False, node_size=15, width=0.3, node_color='blue', edge_color='grey')
        limits = plt.axis('off')

    # save for external Gephi visualization
    def save(self):
        nx.write_gexf(self.G, "fb_graph.gexf")

friends_graph = FriendsGraph()
friends_graph.preview()
friends_graph.save()
