import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
# parse.py function to parse time
from parse import parse_time, parse_money
# This scraper is for web=crawling on Chromium web browsers. My chromedriver is located at /usr/bin/chromedriver
driver = webdriver.Chrome('/usr/bin/chromedriver')  

# Constants
coin_name = 'ethereum'
pace = -1 # pace to move the cursor on the chart
lag_days = 29 # the number of days that we want to crawl
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
selected_tab = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, intervals[selected_interval])))
selected_tab.click()

# time period to crawl
stop_time = dt.now() - timedelta(days = lag_days) # stop time

# The 'action' object, which we'll use to move cursor on screen
action = webdriver.ActionChains(driver)

# Crawl price and volume

# find chart element, and get its size & location on the page
prices_table = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[3]/div[1]/div[2]/div/table/tr[1]')))
loc = prices_table.location
size = prices_table.size
print(loc)
print(size)
# lists to save crawled data
indexes = []
prices = []
vols = []
action.move_to_element_with_offset(prices_table, size['width']-5, 0).perform() # move the cursor near to the current time 
# While Loop to crawl data from the last 30 days 
while True:
    # date
    day_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[1]/span[1]').text
    hour_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[1]/span[2]').text
    time_index = parse_time(day_str, hour_str)
    if not (time_index.day > stop_time.day or time_index.month > stop_time.month):
        break 
    indexes.append(time_index)
    # price and volume
    price_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[2]/span[3]').text
    vol24h_str = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[3]/span[2]').text
    price = parse_money(price_str)
    prices.append(price)
    vol24h = parse_money(vol24h_str)
    vols.append(vol24h)
    # move the cursor
    action.move_by_offset(pace, 0).perform()

# save the data crawled to a dictionary, then to a dataframe
dictionary_price = {'date': indexes, 'price':prices, 'volume_24h':vols}
df_price = pd.DataFrame(data=dictionary_price)
print(df_price.head(10))

# Crawl Market Cap
# move the cursor to the "Market Cap" tab
market_cap_tab = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/button[2]/span')))
market_cap_tab.click()
# detect the marketcap tab
marketcaps_table = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[3]/div[1]/div[2]/div/table/tr[1]')))
loc = marketcaps_table.location
size = marketcaps_table.size
print(loc)
print(size)
# lists to save crawled data
indexes2 = []
market_caps = []
action.move_to_element_with_offset(marketcaps_table, size['width']-5, 0).perform() # move the cursor near to the current time 
# While Loop to crawl data from the last 30 days 
while True:
    # date
    day_str = driver.find_element_by_xpath('/html/body/div/div[1]/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[1]/span[1]').text
    hour_str = driver.find_element_by_xpath('/html/body/div/div[1]/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[1]/span[2]').text
    time_index = parse_time(day_str, hour_str)
    if not (time_index.day > stop_time.day or time_index.month > stop_time.month):
        break
    indexes2.append(time_index)
    # market cap
    marketcap_str = driver.find_element_by_xpath('/html/body/div/div[1]/div/div[2]/div/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div/div[1]/div/div/div[1]/div[2]/span[3]').text
    market_cap = parse_money(marketcap_str)
    market_caps.append(market_cap)
    # move the cursor
    action.move_by_offset(pace, 0).perform()

dictionary_marketcap = {'date': indexes2, 'market cap': market_caps}
df_marketcap = pd.DataFrame(data = dictionary_marketcap)
print(df_marketcap.head(10))

time.sleep(3)
driver.quit()

# concat two dictionaries
df = pd.merge(left=df_price, right=df_marketcap, how='left', left_on='date', right_on='date')

print(df)
# output the data to a csv file
df.to_csv('{}_{}_to_{}.csv'.format(coin_name, stop_time.strftime("%b%d"), dt.now().strftime("%b%d")))
