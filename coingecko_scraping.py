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
# list of available intervals for scraping:
intervals = {
    '1D': ('/html/body/div[4]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[1]', 1), 
    '7D': ('/html/body/div[4]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[2]'), 7),
    '14D': ('/html/body/div[4]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[3]', 14),
    '30D': ('/html/body/div[4]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[4]', 30),
    '90D': ('/html/body/div[4]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[5]', 90),
    '180D': ('/html/body/div[4]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[6]', 180),
    '1Y': ('/html/body/div[4]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[7]', 365)
}
selected_interval = '30D'

# URL for the web that you want to crawl
my_url = 'https://www.coingecko.com/en/coins/{}/'.format(coin_name)
driver.get(my_url)

# lag day calculate:
selected_interval_path, lag_days = intervals[selected_interval]

# time period to crawl
stop_time = dt.now() - timedelta(days = lag_days) # stop time

# The 'action' object, which we'll use to move cursor on screen
action = webdriver.ActionChains(driver)

# Click to move to the desired interval tab that you want to scrape (1D, 7D, etc)
selected_tab = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, selected_interval_path)))
selected_tab.click()



# Crawl price and volume

# find chart element, and get its size & location on the page
prices_table = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[6]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/div[1]/div/div[4]/div[2]/svg/rect[1]')))
loc = prices_table.location
size = prices_table.size
print(loc)
print(size)
# lists to save crawled data
indexes = []
prices = []
vols = []
action.move_to_element_with_offset(prices_table, size['width'], 0).perform() # move the cursor near to the current time 
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
