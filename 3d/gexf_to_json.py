

import xml.etree.ElementTree as ET


# parse the gexf file and return a json object
def gexf_to_json(gexf_file):

    print('gexf_file:', gexf_file)

    tree = ET.parse(gexf_file)
    root = tree.getroot()

    nodes = []
    for i, item in enumerate(root.findall('./{http://www.gexf.net/1.2draft}graph/{http://www.gexf.net/1.2draft}nodes/{http://www.gexf.net/1.2draft}node')):
        nodes.append({
            'id': i,
            'name': item.attrib['label'],
        })

    links = []
    for item in root.findall('./{http://www.gexf.net/1.2draft}graph/{http://www.gexf.net/1.2draft}edges/{http://www.gexf.net/1.2draft}edge'):
        links.append({
            # get id of source based on node name and id
            'source': [node['id'] for node in nodes if node['name'] == item.attrib['source']][0],
            'target': [node['id'] for node in nodes if node['name'] == item.attrib['target']][0],
        })

    # only send the first n nodes with all their links
    # n = 50
    # nodes = nodes[:n]
    # links = [link for link in links if link['source'] in [node['id'] for node in nodes] and link['target'] in [node['id'] for node in nodes]]

    # print ('nodes:', nodes)
    # print ('links:', links)

    return {'nodes': nodes, 'links': links}
