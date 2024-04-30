# Korean general election ForeCasting
import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class SearchVolumeCrawler:
    def __init__(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
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

    def get_main_rsv(self, keywords, date_range):
        # Open date pick window
        self.click_xpath_element('//*[@id="compare-pickers-wrapper"]/div/custom-date-picker')
        self.click_xpath_element('//*[@id="select_option_24"]')

        self.sleep_random()

        # Input date range and confirm
        for i, name in enumerate(['from', 'to']):
            date_input_elem = self.driver.find_element(By.CSS_SELECTOR, f'.custom-date-picker-dialog-range-{name} input')
            date_input_elem.clear()
            date_input_elem.click()
            self.sleep_random()
            self.action.send_keys(date_range[i]).perform()
            self.sleep_random()

        self.driver.find_element(By.CSS_SELECTOR, '.custom-date-picker-dialog-button:last-child').click()
        self.sleep_random()

        # Enter keywords
        self.click_xpath_element('//*[@id="input-29"]')

        for word in keywords:
            self.action.send_keys(word).perform()
            time.sleep(0.1 + random.random() * 0.1)
            self.action.send_keys(Keys.ENTER).perform()
            self.sleep_random(3)

            self.click_xpath_element('//*[@id="explorepage-content-header"]/explore-pills/div/button')

        # Download csv file
        self.sleep_random(3)
        self.driver.find_element(By.CSS_SELECTOR, '.widget-container-wrapper div:first-child .widget-actions-item-flatten button:first-child').click()
        time.sleep(1)

if __name__ == '__main__':
    keywords = ['이재명', '윤석열', '조국']
    date_range = ('2023-3-15', '2023-4-15')

    crawler = SearchVolumeCrawler()
    crawler.get_main_rsv(keywords, date_range)
