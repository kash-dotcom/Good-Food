import gspread
from google.oauth2.service_account import Credentials

import pandas as pd
import numpy as np
import re
import datetime

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('good_food_network')

inventory = SHEET.worksheet('inventory')
customers = SHEET.worksheet('customers')


def match_and_return():
    """
    Matches the users input in a specific column and returns 
    * uses for dietary requirements
    * login

    Reference
    linking gspread to pandas
    https://medium.com/@vince.shields913/reading-google-sheets-into-a-pandas-dataframe-with-gspread-and-oauth2-375b932be7bf
    
    """

    name = customers.get_all_values()
    user_input = input("What is your name? ")
    
    for row in name:
        if row[0] == user_input:
            membership_no = row[1]
            print(f"Welcome {user_input}, to Good Food Pantry Online. Your membership number {membership_no}\n")
            break
    else:
        print("We can't find your name in the list")

def categories():

    """
    Matches the users input in a specific column and returns 
    * uses for dietary requirements
    * login

    References
    https://builtin.com/data-science/pandas-filter
    https://shecancode.io/filter-a-pandas-dataframe-by-a-partial-string-or-pattern-in-8-ways/
    https://sentry.io/answers/write-a-list-to-a-file-in-python-with-each-item-on-a-new-line/
    """
 
    user_search = input('Would you like to see only vegan or vegetarian foods? \n \n If yes, please write "Vegan" or "Vegetarian" below. \n \n ')
 
    filt = (df['Allegen'].str.contains(user_search, na=False)) & (df['Status'] == 'In stock') 
    filt_df =df.loc[filt]

    if not filt_df.empty:
        in_stock = filt_df[['Item_Name', 'Allegen', 'Status']]
        #in_stock_item_index = in_stock.set_index('Item_Name')
        print(in_stock)
        return in_stock
    else:
        print("Sorry, there are any items that match your request. Please try again")

def selection(search_results):

    """
    User selects an item using the index and it is added to the shopping bag
    """
    shopping_bag = []
    items = 1
    while items < 6:
        user_selects = int(input('\nChose an item:\n \n'))

        try:
            in_the_bag = search_results.loc[user_selects, 'Item_Name']
            shopping_bag.append(in_the_bag)
            shopping_bag_str = '\n'.join(shopping_bag) 
            print(shopping_bag_str)
            items += 1

        except (KeyError):
            print("Sorry, we can't find that item. Please choose another item from the list")

        except (ValueError):
            print("Sorry, we can't find that item. Please choose another item from the list")

        #BUG - ValueError when user doesn't input anything - programme restarts

    
    print("Thank you, would you like to reserve your items or start again? \n")
        

# ---------------------------Manipulation of data of the gspread--------------------


def expired():

    """
    Based on the expiry date

    References
    date
    https://www.geeksforgeeks.org/get-current-date-using-python/ - reminder for using dates in python
    https://www.programiz.com/python-programming/datetime''
    https://strftime.org/ - Python strftime cheatsheet
    https://www.geeksforgeeks.org/convert-the-column-type-from-string-to-datetime-format-in-pandas-dataframe/#pandas-convert-column-to-datetime-using-pdto_datetime-function

    """
    #Takes todays date and changes it into Pandas format
    today = datetime.date.today()
    today_pd = pd.to_datetime(today)

    #imports the data and changes to a data frame for easier viewing 
    inventory_li = inventory.get_all_records()
    inventory_df = pd.DataFrame(inventory_li)

    #Changes the data type of the expiry_date column from string to Pandas format eg datetime64[ns]                 
    inventory_df['Expiry_Date'] = pd.to_datetime(inventory_df['Expiry_Date'], format='%d/%m/%y')
   
    #creates a list of expired food
    expired_status = inventory_df[inventory_df["Expiry_Date"] < today_pd]
    expired_filt = expired_status[['Item_Name', 'Expiry_Date']]   
      
    print(expired_filt)

    # Change every subset of inventory_df into 


   
    



    """
                #today's date written as a string in uk format

    today = datetime.date.today()

    #today_obj = today.strftime('%d/%m/%y')
            #today_obj = today.to_datetime()
                #print(today_obj)

            #import gspread data as a list
    inventory_li = inventory.get_all_records()

                #change to data frame
    inventory_df = pd.DataFrame(inventory_li)


                    #change from str to datatime
                    
    inventory_df['Expiry_Date'] = pd.to_datetime(inventory_df['Expiry_Date'], format='%d/%m/%y')

    expired_filt = inventory_df[['Item_Name', 'Expiry_Date']]

    expired_status = inventory_df["Expiry_Date"] == np.where(inventory_df["Expiry_Date"] < today)
   

    print(expired_status)
    print(expired_filt)
    print(today)

    """

        #filtered_df = inventory_df[inventory_df['Expiry_Date'].dt.strftime('%d/%m/%y') < today_obj]
    #
    
#expired_filt = inventory_df[inventory_df['Expiry_Date'] < datetime.today()]
   #current issue - datetime...(now) is <class 'datetime.date'>
    # - Expiry Date is datetime64[ns]

    #expired_filt = inventory_df['Expiry_Date'] 


    #expired_now = (inventory_df["Expiry_Date"])

    #print(inventory_df)

    #expired_status = inventory_df["Expiry_Date"] == np.where(inventory_df["Expiry_Date"] < today_obj, inventory_df["Status"] == "Expired", inventory_df["Status"] == "In stock")
    #print(expired_filt)

expired()


def sold_out():
    """
    Based on the number of items in the inventory

    """






def in_stock_spreadsheet():
    """
    Based on the expired and sold_out - show customers the available produce

    """
    # set time and date
    # update status when something is out of stock 
        # Sold Out
        # Due to expire
        # Expired

        


    
    
    
    
    
    
    

    
def main():
    match_and_return()
    search_results = categories()
    selection(search_results)
    
#main()




























# Login 
# Left align columns (https://www.geeksforgeeks.org/align-columns-to-left-in-pandas-python/)
# Change what is in stock according to expiry date
# Data validation - invalid data
# search for an excluding e.g. not fish
        # extension 
        # change colour on spreadsheet
        # Password Protect the Membership numbers file
# Select food and put in basket
# Check out update orders











# print(in_stock)

    #choice = in_stock.set_index('Item_Name', inplace=True)

    #print(choice)
    
    
    # return in_stock


    

    #user_select = input("Select an item, e.g. if you would like the '4 British Baking Potates', just write 'potates'")

    #select = filt_df['Item_Name'].str.contains(user_select, na=False)

    #print(select)



   
    #pprint(choice) 













"""
def read_logins():
   
    Common delimiter and remove the new line marker



    with open('logins.txt', 'r') as f:
        contents = f.readlines()

        new_contents = []

        for line in contents:
            fields = line.split(',')
            fields[1] = fields[1].rstrip()
            new_contents.append(fields)

        return new_contents


logins = read_logins()


def login():
    

    login page
    https://www.youtube.com/watch?v=L2i6lELbNI0
    https://github.com/rodbove/console-login-system/blob/master/main.py
    https://docs.gspread.org/en/latest/


   
    #ask_username = str(input('Please enter your full name:  '))
    #ask_password =str(input('Please enter you password:  '))

    
 
    logged_in = False

    for line in logins:
        if line[0] == ask_username and line[1] == ask_password:
            print('Logged in successfully...')
            #main()

    print('Username / Password is incorrect')
    #login()

def main():
    print(f'Welcome')
   

# login()

   #inventory
   # user = inventory.find('Name')
    #user_password = inventory.find('Password')


#pandas trial
    #pd_super_list = pd.DataFrame(inventory)
    #items = inventory.column_value(1)

    #df = pd.DataFrame(super_list, columns=items)

    #print(df)

  

column = 'Item_Name'
    column_index = super_list[1].index(column)
    options = []

    for sublist in super_list:
        for item in sublist:
            if item == user_search:
                for stock in user_search[1]:
                    stocked = stock[column_index]
                    options.append(stocked)
    print(stocked)

Filter
        
    

    if not filter_df.empty:
        for item in filter_df ['Item_Name']:
            print(item)
    else:
        print("No matching items found")



       #filt = (df['Allegen'] == user_search)

    """