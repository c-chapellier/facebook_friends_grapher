
import networkx as nx


def community_detection(graph):

    G = nx.Graph()
    for node in graph['nodes']:
        G.add_node(node['id'], name=node['name'])
    for link in graph['links']:
        G.add_edge(link['source'], link['target'])
    
    communities = nx.community.louvain_communities(G, seed=123) # type: ignore
    for i, community in enumerate(communities):
        for node in community:
            for n in graph['nodes']:
                if n['id'] == node:
                    n['community'] = i
                    break

    # add degree to nodes
    for node in graph['nodes']:
        node['val'] = len([n for n in graph['links'] if n['source'] == node['id'] or n['target'] == node['id']])/2

    return graph
