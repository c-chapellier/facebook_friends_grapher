import os
import pickle
import sys
import time

from dotenv import load_dotenv

from lib.parser import FriendsURLsParser
from lib.profile_url_to_username_or_id import profile_url_to_username_or_id
from lib.scraper import FacebookScraper

load_dotenv()

FB_BOT_USERNAME: str = os.getenv('FB_BOT_USERNAME') # type: ignore
FB_BOT_PASSWORD: str = os.getenv('FB_BOT_PASSWORD') # type: ignore
FB_PROFILE_LINK: str = os.getenv('FB_PROFILE_LINK') # type: ignore

FB_USERNAME_OR_ID = profile_url_to_username_or_id(FB_PROFILE_LINK)

# create directory
if not os.path.isdir('data/' + FB_USERNAME_OR_ID):
    os.mkdir('data/' + FB_USERNAME_OR_ID)

FRIENDS_PAGE_FILENAME = 'data/' + FB_USERNAME_OR_ID + '/friends_page.html'
FRIENDS_URLS_FILENAME = 'data/' + FB_USERNAME_OR_ID + '/friends.pickle'
GRAPH_DATA_FILENAME = 'data/' + FB_USERNAME_OR_ID + '/data.pickle'


scraper = FacebookScraper(FB_BOT_USERNAME, FB_BOT_PASSWORD)

OWN_ACCOUNT = False


# scrap friends if needed
if not os.path.isfile(FRIENDS_URLS_FILENAME):

    if not os.path.isfile(FRIENDS_PAGE_FILENAME):
        friends_page = scraper.get_page(f'{FB_PROFILE_LINK}/friends')
        with open(FRIENDS_PAGE_FILENAME, 'w') as f:
            f.write(friends_page)
    
    with open(FRIENDS_PAGE_FILENAME, 'r') as f:
        friends_page = f.read()

    parser = FriendsURLsParser()
    parser.feed(friends_page)

    if not OWN_ACCOUNT and parser.only_shows_mutual_friends:
        print('Main profile only shows mutual friends')
        sys.exit(1)

    while not 'https://' in parser.urls[len(parser.urls) - 1]:
        parser.urls.pop()
        parser.names.pop()

    if not OWN_ACCOUNT:
        parser.urls = [url.replace('_mutual', '') for url in parser.urls]

    with open(FRIENDS_URLS_FILENAME + '.orig', 'wb') as f:
        pickle.dump(dict(zip(parser.names, parser.urls)), f)

    with open(FRIENDS_URLS_FILENAME, 'wb') as f:
        pickle.dump(dict(zip(parser.names, parser.urls)), f)

    print(f'We saved {len(parser.names)} friends')


# load friends
with open(FRIENDS_URLS_FILENAME, 'rb') as f:
    friends = pickle.load(f)

for name, url in friends.items():
       print(f'{name}: \'{url}\'')
print(f'We loaded {len(friends)} friends')


# init graph
connections = {}

if os.path.isfile(GRAPH_DATA_FILENAME):
    with open(GRAPH_DATA_FILENAME, 'rb') as f:
        connections = pickle.load(f)
    print(f'Loaded existing graph, found {len(connections.keys())} keys')


# find main profile name
account_name = None
for name, url in friends.items():
    if url == 'Main profile':
        account_name = name

if account_name is None:
    print('Main profile not found')
    sys.exit(1)


# get mutual friends
count = 0
for name, url in friends.items():

    if name in connections.keys():
        continue

    print(f'{len(connections.keys())}/{len(friends.items())}: {name}: \'{url}\'')

    if name == account_name:
        connections[account_name] = list(friends.keys())
        connections[account_name].remove(account_name)
        continue

    if url == 'No mutual friends':
        connections[name] = [account_name]
        continue

    try:
        mutual_friends_page = scraper.get_page(url)
    except Exception as e:
        print('Error getting page:', e)
        if 'invalid argument' in str(e):
            with open(FRIENDS_URLS_FILENAME, 'wb') as f:
                pickle.dump(friends.copy().pop(name), f)
            continue
        if 'invalid session id' in str(e):
            print('Invalid session id, trying to restart scrapper, ...')
            scraper.close()
            time.sleep(1200)
            scraper = FacebookScraper(FB_BOT_USERNAME, FB_BOT_PASSWORD)
            mutual_friends_page = scraper.get_page(url)
        continue

    connections[name] = [account_name]

    parser = FriendsURLsParser()
    parser.feed(mutual_friends_page)

    if not OWN_ACCOUNT and parser.only_shows_mutual_friends:
        print('Friends not available')
        with open(FRIENDS_URLS_FILENAME, 'wb') as f:
            pickle.dump(friends.copy().pop(name), f)
        continue

    print(f'Found {len(parser.urls)} mutual friends')

    mutual_friends = dict(zip(parser.names, parser.urls))
    for mutual_friend_name, _ in mutual_friends.items():
        connections[name].append(mutual_friend_name)

    with open(GRAPH_DATA_FILENAME, 'wb') as f:
        pickle.dump(connections, f)

    count += 1
    if count % 50 == 0:
        print ('Too many queries, pause for a while...')
        time.sleep(1200)
