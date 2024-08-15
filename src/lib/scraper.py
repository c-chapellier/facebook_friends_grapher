import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# class to scrape Facebook
class FacebookScraper:

    def __init__(self, fb_bot_username, fb_bot_password):
        self.driver = None
        self.fb_bot_username = fb_bot_username
        self.fb_bot_password = fb_bot_password

    def _start(self):
        # launch browser
        chrome_options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_setting_values.notifications': 2}
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option('detach', True)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=650,900')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get('http://www.facebook.com/')

        # authenticate into Facebook
        elem = self.driver.find_element('id', 'email')
        elem.send_keys(self.fb_bot_username)
        elem = self.driver.find_element('id', 'pass')
        elem.send_keys(self.fb_bot_password)
        elem.send_keys(Keys.RETURN)
        time.sleep(5)

    # load, expand and return a page
    def get_page(self, page_url):
        if self.driver is None:
            self._start()

        time.sleep(5)
        self.driver.get(page_url)

        last_height = self.driver.execute_script('return document.body.scrollHeight')
        print('last_height:', last_height)

        while True:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            new_height = self.driver.execute_script('return document.body.scrollHeight')
            print('new_height:', new_height)

            if new_height == last_height:
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(4)
                new_height = self.driver.execute_script('return document.body.scrollHeight')
                print('new_height:', new_height)

                if new_height == last_height:
                    break

            last_height = new_height

        return self.driver.page_source
    
    def close(self):
        if self.driver is not None:
            self.driver.quit()
