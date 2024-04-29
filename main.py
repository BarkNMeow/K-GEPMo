# Korean general election ForeCasting
import time
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

keywords = ['이재명', '윤석열', '조국']

def sleep_random():
    time.sleep(0.5 + random.random())

def click_xpath_element(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    sleep_random()

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get('https://trends.google.com')

click_xpath_element(driver, '//*[@id="gb"]/div[2]/div[1]/div[1]')
click_xpath_element(driver, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div[3]/gm-raised-drawer/div/div[2]/div/ul/li[2]')

action = ActionChains(driver)
time.sleep(1 + random.random())

for word in keywords:
    action.send_keys(word).perform()
    time.sleep(0.1 + random.random() * 0.1)
    action.send_keys(Keys.ENTER).perform()

    click_xpath_element(driver, '//*[@id="explorepage-content-header"]/explore-pills/div/button')

time.sleep(4 + random.random())
click_xpath_element(driver, '/html/body/div[2]/div[2]/div/md-content/div/div/div[1]/trends-widget/ng-include/widget/div/div/div/widget-actions/div/button[1]')

while input() != '':
    pass

driver.quit()