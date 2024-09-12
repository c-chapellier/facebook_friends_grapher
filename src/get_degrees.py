
import pickle

from dotenv import load_dotenv

from lib.profile_url_to_username_or_id import profile_url_to_username_or_id

load_dotenv()

FB_PROFILE_LINK: str = os.getenv('FB_PROFILE_LINK') # type: ignore

FB_USERNAME_OR_ID = profile_url_to_username_or_id(FB_PROFILE_LINK)

with open(f'data/{FB_USERNAME_OR_ID}/data.pickle', 'rb') as f:
    friends_connections = pickle.load(f)
    print('friends:', len(list(friends_connections.keys())))

    connections = {}
    for friend, friend_connections in friends_connections.items():
        connections[friend] = friend_connections

    friends = list(connections.keys())
    friends_degrees = {}
    for friend in friends:
        friends_degrees[friend] = len(connections[friend])

    friends_degrees = dict(sorted(friends_degrees.items(), key=lambda item: item[1], reverse=True))
    with open(f'data/{FB_USERNAME_OR_ID}/degrees.txt', 'w') as f:
        for friend, degree in friends_degrees.items():
            f.write(f'{friend} {degree}\n')
