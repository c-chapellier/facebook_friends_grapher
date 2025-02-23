import os
import pickle

import matplotlib.pyplot as plt
import networkx as nx
from dotenv import load_dotenv

from lib.profile_url_to_username_or_id import profile_url_to_username_or_id

load_dotenv()

FB_PROFILE_LINK: str = os.getenv('FB_PROFILE_LINK') # type: ignore

FB_USERNAME_OR_ID = profile_url_to_username_or_id(FB_PROFILE_LINK)

class FriendsGraph:

    def __init__(self):
        self._load_connections()
        self._create_edges()

        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.connections.keys())
        self.graph.add_edges_from(self.edges)
        print(f'Added {len(self.edges)} edges')

    def _load_connections(self):
        with open(f'data/{FB_USERNAME_OR_ID}/data.pickle', 'rb') as f:
            friends_connections = pickle.load(f)
        print('friends:', len(list(friends_connections.keys())))

        self.connections = {}
        for friend, friend_connections in friends_connections.items():
            self.connections[friend] = friend_connections

    def _create_edges(self):
        self.edges = []
        n_none = 0
        connections_cp = self.connections.copy()

        for friend, friend_connections in connections_cp.items():
            if friend is None:
                n_none += 1
                self.connections.pop(friend)
            for connection in friend_connections:
                if connection in self.connections:
                    self.edges.append((friend, connection))

        print('None:', n_none)

    def preview(self):
        pos = nx.kamada_kawai_layout(self.graph)
        plt.rcParams['figure.figsize'] = [10, 10]
        nx.draw_networkx(
            self.graph, pos=pos, with_labels=False, node_size=15,
            width=0.3, node_color='blue', edge_color='grey'
        )
        plt.axis('off')

    # save for external Gephi visualization
    def save(self):
        nx.write_gexf(self.graph, f'data/{FB_USERNAME_OR_ID}/graph_{FB_USERNAME_OR_ID}.gexf')

    # get the graph
    def get(self):
        return self.graph


friends_graph = FriendsGraph()
# friends_graph.preview()
friends_graph.save()
