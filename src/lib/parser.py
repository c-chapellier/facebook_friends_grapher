from html.parser import HTMLParser


# filter the page to get the friends URLs
class FriendsURLsParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.urls = []
        self.names = []
        
        self.is_friend_name_active = False
        self.is_account_name_active = False
        # self.mutual_friends_active = False

        self.last_item_added = ''
        self.only_shows_mutual_friends = False # True


    def handle_starttag(self, tag, attrs):
    
        # if tag == 'a':
        #     a_class_name_1 = 'x1i10hfl xe8uvvx xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz xjyslct xjbqb8w x18o3ruo x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1heor9g x1ypdohk xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg x1vjfegm x3nfvp2 xrbpyxo x1itg65n x16dsc37'
        #     class_ok = False
        #     selected_ok = False
        #     for name, value in attrs:
        #         if name == 'class' and value == a_class_name_1:
        #             class_ok = True
        #         if name == 'aria-selected' and value == 'true':
        #             selected_ok = True
        #     if class_ok and selected_ok:
        #         self.mutual_friends_active = True
        
        if tag == 'a':
            friend_url_classname = 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1sur9pj xkrqix3 xi81zsa xo1l8bm'
            good_class = False
            for name, value in attrs:
                if name == 'class' and value == friend_url_classname:
                    good_class = True
                if good_class and name == 'href':
                    self.urls.append(value)
                    # print('add url:', value)
                    self.last_item_added = 'url'

        if tag == 'span':
            account_name_classname = 'x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1ill7wo x1g2y4wz x579bpy xjkpybl x1xlr1w8 xzsf02u x2b8uid'
            for name, value in attrs:
                if name == 'class' and value == account_name_classname:
                    self.is_account_name_active = True

        if tag == 'div':
            friend_name_classname = 'x1iyjqo2 x1pi30zi'
            for name, value in attrs:
                if name == 'class' and value == friend_name_classname:
                    self.is_friend_name_active = True

    def handle_data(self, data):
        
        # if self.mutual_friends_active:
        #     if data == 'Tous les amis':
        #         self.only_shows_mutual_friends = False
        #     self.mutual_friends_active = False
        
        if self.is_friend_name_active:
            if self.last_item_added == 'name':
                self.urls.append('No mutual friends')
            self.names.append(data)
            self.last_item_added = 'name'
            self.is_friend_name_active = False
        
        if self.is_account_name_active:
            self.names.append(data)
            self.urls.append('Main profile')
            self.is_account_name_active = False
