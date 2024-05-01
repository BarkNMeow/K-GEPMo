# Korean general election ForeCasting
import time
import random
import os
import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class SearchVolumeCrawler:
    def __init__(self):
        # define and clear download directory
        download_dir = os.path.dirname(os.path.realpath(__file__)) + '\\tmp'
        try:
            if os.path.exists(download_dir):
                files = os.listdir(download_dir)
                for file in files:
                    file_path = os.path.join(download_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            else:
                os.mkdir(download_dir)

        except OSError:
            print('Error occurred while clearing directory')

        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': download_dir }
        chrome_options.add_experimental_option('prefs', prefs)

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        self.action = ActionChains(self.driver)

        self.driver.get('https://trends.google.com')

        # Navigate to "Explore" Page
        self.click_xpath_element('//*[@id="gb"]/div[2]/div[1]/div[1]')
        self.click_xpath_element('//*[@id="yDmH0d"]/c-wiz/div/div[2]/div[3]/gm-raised-drawer/div/div[2]/div/ul/li[2]')

    def __del__(self):
        self.driver.quit()

    def sleep_random(self, min_time=1):
        time.sleep(min_time + random.random())

    def click_xpath_element(self, xpath):
        element = self.driver.find_element(By.XPATH, xpath)
        element.click()
        self.sleep_random()

    def click_css_element(self, selector):
        flag = True
        while flag:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.click()
            except Exception:
                continue

            self.sleep_random()
            flag = False

    def set_date(self, date_range):
        # Open date pick window
        self.click_xpath_element('//*[@id="compare-pickers-wrapper"]/div/custom-date-picker')
        self.click_css_element('.custom-date-picker-select-option:last-child')

        self.sleep_random(0.5)

        # Input date range and confirm
        while True:
            for i, name in enumerate(['from', 'to']):
                date_input_elem = self.driver.find_element(By.CSS_SELECTOR, f'.custom-date-picker-dialog-range-{name} input')
                date_input_elem.clear()
                date_input_elem.click()
                self.sleep_random(0.25)
                self.action.send_keys(date_range[i]).perform()
                self.sleep_random(0.25)

            confirm_button = self.driver.find_element(By.CSS_SELECTOR, '.custom-date-picker-dialog-button:last-child')
            self.sleep_random()

            if confirm_button.get_dom_attribute('disabled') != 'true':
                print(confirm_button.get_dom_attribute('disabled'))
                confirm_button.click()
                return

    def enter_keyword(self, keywords):
        # Enter keywords
        self.click_css_element('.search-term-wrapper.term-not-selected')

        for word in keywords:
            self.action.send_keys(word).perform()
            self.sleep_random()
            self.action.send_keys(Keys.ENTER).perform()
            self.sleep_random()

            self.click_xpath_element('//*[@id="explorepage-content-header"]/explore-pills/div/button')

    def clear_keyword(self):
        while True:
            try:
                self.driver.find_element(By.CSS_SELECTOR, '.search-term-wrapper:not(.term-not-selected)').click()
                self.sleep_random(0.5)
                self.action.send_keys(Keys.DELETE).perform()
                self.sleep_random(0.5)
                self.action.send_keys(Keys.ENTER).perform()
                self.sleep_random(0.5)
            except Exception:
                return

    def get_main_rsv(self, keywords, date_range):
        self.set_date(date_range)
        self.enter_keyword(keywords)

        # Download csv file
        self.sleep_random(2)
        self.driver.find_element(By.CSS_SELECTOR, '.widget-container-wrapper div:first-child .widget-actions-item-flatten button:first-child').click()
        time.sleep(1)

        result = []
        download_file_path = '.\\tmp\\multiTimeline.csv'

        # Analyze csv file
        with open(download_file_path, encoding='UTF-8') as csvfile:
            for _ in range(3):
                csvfile.readline()

            reader = csv.reader(csvfile)
            for row in reader:
                row_list = []
                row_list.append(row[0]) # date
                row_list.extend(map(int, row[1:])) # rsv

                result.append(row_list)

            csvfile.close()

        # Remove the downloaded file
        if os.path.exists(download_file_path):
            os.remove(download_file_path)
        
        return result
    
    def get_query_rsv(self, keywords, date_range):
        # Get main rsv envelope
        rsv = self.get_main_rsv(keywords, date_range)

        # Initialize the keyword environment
        self.clear_keyword()
        self.sleep_random(0.5)
        flag = True

        # For each date, get related queries and their RSV for each keyword
        for line in rsv:
            date = line[0]
            self.set_date((date, date))
            self.sleep_random()

            for keyword in keywords:
                if flag:
                    self.click_css_element('.search-term-wrapper.term-not-selected')
                    flag = False
                else:
                    self.click_css_element('.search-term-wrapper:not(.term-not-selected)')

                self.action.send_keys(keyword).perform()
                self.sleep_random(0.5)
                self.action.send_keys(Keys.ENTER).perform()
                self.sleep_random(2)

                related_queries_panel = self.driver.find_element(By.CSS_SELECTOR, '.widget-container-wrapper div:last-child .widget-template')
                related_queries_panel.find_element(By.CSS_SELECTOR, 'md-select').click()
                self.sleep_random(0.5)

                self.driver.find_element(By.CSS_SELECTOR, 'md-select-menu md-option:last-child').click()
                self.sleep_random()

        

if __name__ == '__main__':
    keywords = ['이재명']
    date_range = ('2023-3-15', '2023-4-15')

    crawler = SearchVolumeCrawler()
    crawler.get_query_rsv(keywords, date_range)
    