
# Facebook friends grapher

Tool for visualizing your Facebook network.

![Loading Video...](https://github.com/c-chapellier/facebook_friends_grapher/blob/main/examples/demo-visualizer-1080p.mov)

A node represents one of your friend.

An edge between two nodes indicate a friendship.

The size of each friend is proportionnal to the number of mutual friends between you and him.

Each color represents one community inside your network (maybe a a city, a sport, a school, a friend group,...).

## Usage

This tool will scrape your Facebook friends and their mutual friends and create a graph document.

This document can then be analyzed and visualized using either the included 3d rendering tool or [Gephi](https://gephi.org) for an amazing 2d vizualisation.

### 1. Specified your Facebook credentials

Create a file named `.env` in the root directory of the project and fill it with your Facebook credentials.

The file should look like this:

```txt
FB_BOT_USERNAME = 'FacebookUsername'
FB_BOT_PASSWORD = 'FacebookPassword'
FB_PROFILE_LINK = 'https://www.facebook.com/FacebookUsername'
```

The bot will use these credentials to log in to your Facebook account and scrape the data about the `FB_PROFILE_LINK`.

> ***It is recommended to use the same account for both the bot and the profile link. It will be able to gather far more data.***

### 2. Gather your data

Run the following Python script to webscrap your data. It will open a chrome window and start browsing automatically.

> ***This process can take a while depending on the number of friends you have. If you have 800 friends, it can take up to 12 hours.***

```bash
python3 src/get_data.py
```

> ***Tip***: You can resize the chrome window to a small size to speed up the process. In order to maximize the number of friends displayed on one page.

It will store your data in the `data` directory.

### 3. Create the graph document

Run the following Python script to create the graph `.gexf` document.

```bash
python3 src/create_graph.py
```

### 4. Visualize the graph

#### 4.1. Using Gephi (2d)

[Gephi](https://gephi.org) is an amazing tool for visualizing 2d graphs. It is very powerful and can create beautiful visualizations.

#### 4.2. Using the 3d rendering tool

This tool will launch a small web server that will display a 3d interactive visualization of your graph.

```bash
python 3d/server.py <gexf file>
```

## References
- https://www.databentobox.com/2019/07/28/facebook-friend-graph/
- http://allthingsgraphed.com/2014/08/28/facebook-friends-network/
- https://github.com/vasturiano/force-graph?tab=readme-ov-file
