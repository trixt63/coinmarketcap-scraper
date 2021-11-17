import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
# parse.py function to parse time
from parse import parse_time, parse_price, parse_vol24h
# This scraper is for web=crawling on Chromium web browsers. My chromedriver is located at /usr/bin/chromedriver
driver = webdriver.Chrome('/usr/bin/chromedriver')  

# Constants
coin_name = 'oraichain-token'
pace = -1 # pace to move the cursor on the chart
lag_days = 30 # the number of days that we want to crawl
# list of available intervals for scraping:
intervals = {
    '1D': '//*[@id="react-tabs-0"]',
    '7D': '//*[@id="react-tabs-2"]',
    '1M': '//*[@id="react-tabs-4"]',
    '3M': '//*[@id="react-tabs-6"]',
    '1Y': '//*[@id="react-tabs-8"]'
}
selected_interval = '1M'

# URL for the web that you want to crawl
my_url = 'https://coinmarketcap.com/currencies/{}/'.format(coin_name)
driver.get(my_url)
driver.maximize_window()

# Click to move to the desired interval tab that you want to scrape (1D, 7D, etc)
selected_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, intervals[selected_interval])))
selected_tab.click()

# The 'action' object, which we'll use to move cursor on screen
action = webdriver.ActionChains(driver)
# find chart element, and get its size & location on the page
element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[3]/div[1]/div[2]/div/table/tr[1]')))
loc = element.location
size = element.size
print(loc)
print(size)

# move the cursor near to the current time 
action.move_to_element_with_offset(element, size['width']-5, 0).perform()
# check the first data point
day_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[1]/span[1]').text
hour_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[1]/span[2]').text
price_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[2]/span[3]').text
vol24h_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[3]/span[2]').text
# parse the scraped data
time_index = parse_time(day_str, hour_str)
price = parse_price(price_str)
vol24h = parse_vol24h(vol24h_str)

print("Time index:", time_index, "; Price: ", price, "; Volume 24h: ", vol24h)

# lists to save crawled data
indexes = []
indexes.append(time_index)
prices = []
prices.append(price)
vols = []
vols.append(vol24h)
# While Loop to crawl data from the last 30 days 
stop_time = dt.now() - timedelta(days = lag_days)
while True:
    action.move_by_offset(pace, 0).perform()

    day_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[1]/span[1]').text
    hour_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[1]/span[2]').text
    price_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[2]/span[3]').text
    vol24h_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[3]/span[2]').text

    time_index = parse_time(day_str, hour_str)
    indexes.append(time_index)
    price = parse_price(price_str)
    prices.append(price)
    vol24h = parse_vol24h(vol24h_str)
    vols.append(vol24h)
    if not (time_index.day > stop_time.day or time_index.month > stop_time.month):
        break

time.sleep(3)
driver.quit()

# save the data crawled to a dictionary, then to a dataframe
dictionary = {'index': indexes, 'price':prices, 'volume_24h':vols}
df = pd.DataFrame(data=dictionary)
print(df)
# output the data
df.to_csv('{}_{}_to_{}.csv'.format(coin_name, stop_time.strftime("%b%d"), dt.now().strftime("%b%d")))
