
# Facebook friends grapher

Tool for visualizing your Facebook friends.

![example-1](examples/example_1.png)

A node represents one of your friend

An edge means that your two friends are also friends between them.

THe size of each friend is proportionnal to the number of mutual friends between you and him.

Each color represents one community inside your network (maybe a a city, a sport, a school, a friend group,...).

## Usage

This tool will scrape your Facebook friends and their mutual friends and create a graph document.

This document can then be analyzed and visualized using [Gephi](https://gephi.org).

```bash
python3 grapher.py
```

## References
- https://www.databentobox.com/2019/07/28/facebook-friend-graph/
- http://allthingsgraphed.com/2014/08/28/facebook-friends-network/
