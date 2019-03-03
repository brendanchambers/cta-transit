'''
CTA TRACKER
cta_lcd.py
3/2019
'''
##################################################

import adafruit_character_lcd.character_lcd as LCD
import board
import digitalio
import time

import json
import requests
import pandas as pd

##################################################
# LCD INITIALIZATION

# Raspberry Pi pin configuration:
# Based on: https://pimylifeup.com/raspberry-pi-lcd-
lcd_rs = digitalio.DigitalInOut(board.D25) # 25
lcd_en = digitalio.DigitalInOut(board.D24) # 24
lcd_d7 = digitalio.DigitalInOut(board.D22) # 22
lcd_d6 = digitalio.DigitalInOut(board.D18) # 18
lcd_d5 = digitalio.DigitalInOut(board.D17) # 17
lcd_d4 = digitalio.DigitalInOut(board.D23) # 23
lcd_backlight = digitalio.DigitalInOut(board.D4) # 4


# Define columns and rows of a 20x4 LCD.
lcd_columns = 20
lcd_rows    = 4

# Initialise the lcd class
lcd = LCD.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

lcd.backlight = True

##################################################
# SEND URL REQUEST FOR CHICAGO TRANSIT AUTHORITY DATA VIA BUS TIME
# Add credentials and parameters
config_path = "config.json"
with open(config_path,'r') as configfile:
    config = json.load(configfile)
api_key = config['auth']['api-key']


# 10566 - 55th & HP Blvd Westbound
# 1654 - 55 & HP Blvd  Southbound
# 1518 - 55 & HP Blvd Northbound

stop_ids = [10566,1654,1518]
route_ids = [6,55,171]

##################################################
# Construct query for the API Prediction call

# prefix for predictions request
prediction_url = 'http://www.ctabustracker.com/bustime/api/v2/getpredictions'

# add apikey
prediction_url += '?key=' + api_key

# add arguments containing stop id(s)
prediction_url += '&stpid='
for idx,stpid in enumerate(stop_ids):
    if idx > 0:
         prediction_url += ','
    prediction_url += str(stpid)

# and route arguments
prediction_url += '&rt='
for idx,rtid in enumerate(route_ids):
    if idx > 0:
         prediction_url += ','
    prediction_url += str(rtid)
    
prediction_url += '&format=json'

##################################################

while True:
    # Make a request, convert data to json
    response = requests.get(url=prediction_url) # , params=params)
    try:
        data = response.json() # Check the JSON Response Content documentation below
    except:
        print("Warning, JSON Decode Error")
        print(response)
        
    data = pd.DataFrame(data['bustime-response']['prd'])
    ##################################################
    # Print out data

    routes_running = data['rt'].unique()

    for iRoutes in routes_running:
        #initialize and clear LCD message
        lcd.clear()
        text = "Route {}\n".format(iRoutes)
        
        # get data subset
        rt_data = data.loc[data['rt']==iRoutes]
        
        #get unique directions
        directions = rt_data['rtdir'].unique()
        
        for iDirection in directions:
            dir_data = rt_data.loc[rt_data['rtdir']==iDirection]
            
            # set time string
            times = ""
            
            for iTime in dir_data['prdctdn']:
                times += " {},".format(iTime)

            text += "{}: ".format(iDirection[:-5]) + times + '\n'

        lcd.message = text
        time.sleep(5.0)

    time.sleep(60000) #update every 10 minutes

