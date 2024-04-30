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
date_from, date_to = '2023-3-15', '2023-4-15' 

def sleep_random():
    time.sleep(0.5 + random.random())

def click_xpath_element(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    sleep_random()

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get('https://trends.google.com')

# Navigate to "Explore" Page
click_xpath_element(driver, '//*[@id="gb"]/div[2]/div[1]/div[1]')
click_xpath_element(driver, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/div[3]/gm-raised-drawer/div/div[2]/div/ul/li[2]')

action = ActionChains(driver)
time.sleep(1 + random.random())

# Pick date
click_xpath_element(driver, '//*[@id="compare-pickers-wrapper"]/div/custom-date-picker')
click_xpath_element(driver, '//*[@id="select_option_24"]')

time.sleep(3)

date_start_elem = driver.find_element(By.CSS_SELECTOR, '.custom-date-picker-dialog-range-from input')
date_start_elem.clear()
sleep_random()
date_start_elem.click()
sleep_random()
action.send_keys(date_from).perform()

date_start_elem = driver.find_element(By.CSS_SELECTOR, '.custom-date-picker-dialog-range-to input')
date_start_elem.clear()
sleep_random()
date_start_elem.click()
sleep_random()
action.send_keys(date_to).perform()
sleep_random()

driver.find_element(By.CSS_SELECTOR, '.custom-date-picker-dialog-button:last-child').click()

time.sleep(5)

# Enter keywords
for word in keywords:
    action.send_keys(word).perform()
    time.sleep(0.1 + random.random() * 0.1)
    action.send_keys(Keys.ENTER).perform()

    click_xpath_element(driver, '//*[@id="explorepage-content-header"]/explore-pills/div/button')

    

time.sleep(3 + random.random())
driver.find_element(By.CSS_SELECTOR, '.widget-container-wrapper div:first-child .widget-actions-item-flatten button:first-child').click()
# click_xpath_element(driver, '/html/body/div[2]/div[2]/div/md-content/div/div/div[1]/trends-widget/ng-include/widget/div')

while input() != '':
    pass

driver.quit()