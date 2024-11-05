import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials


import pandas as pd
import re
import datetime
import numpy as np
from collections import Counter

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

# imports the data and changes to a data frame for easier viewing
inventory_li = inventory.get_all_records()
inventory_df = pd.DataFrame(inventory_li)

# class Customer:
    # def __init__(self, membership, search, bag, order, inventory_update):
        #self.membership = membership
        #self.search = stock
       # self.bag = options
        #self.order = selects
        
def membership_m():
    """
    Matches the users input in a specific column and returns.
    
    * uses for dietary requirements
    * login

    Reference:
    linking gspread to pandas
    https://medium.com/@vince.shields913/reading-google-sheets-into-a-pandas-dataframe-with-gspread-and-oauth2-375b932be7bf
    """
    name = customers.get_all_values()
    user_input = input("What is your name? ")
    for row in name:
        if row[0] == user_input:
            membership_no = row[1]
            print((f"Welcome {user_input}, to Good Food Pantry Online. Your membership number {membership_no}\n"))
            return membership_no
            break
    else:
        print("We can't find your name in the list")

def search():

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

    filt = (inventory_df['Allegen'].str.contains(user_search, na=False)) & (inventory_df['Status'] == 'In stock') 
    filt_df =inventory_df.loc[filt]

    if not filt_df.empty:
        in_stock = filt_df[['Item_Name', 'Allegen', 'Status']]
        print(in_stock)
        return in_stock
    else:
        print("Sorry, there are any items that match your request. Please try again:C")

def bag(search_results):

    """
    User selects an item using the index and it is added to the shopping bag
    """
    shopping_bag = []
    items = 0

    while items < 3:
        user_selects = int(input('\nChose an item: '))

        try:
            in_the_bag = search_results.loc[user_selects, 'Item_Name']
            shopping_bag.append(in_the_bag)
            shopping_bag_str = '\n'.join(shopping_bag) 
            print(shopping_bag_str)
            items += 1  

        except (KeyError):
            print("Sorry, we can't find that item. Please choose another item from the list:KE")

        except (ValueError):
            print("Sorry, we can't find that item. Please choose another item from the list:VE")

        #BUG - ValueError when user doesn't input anything - programme restarts

    print("Thank you, would you like to reserve your items or start again? \n")
    return shopping_bag_str

def start_again():
    pass

def order_amount(shopping):
    """
    Calcuation the number of items the customer has in the shopping basket

        for items in shopping_items:''
        inventory_df.loc[inventory_df['Item_Name'] == items]
        new = pd.join(inventory_df, shopping_items, on='Item_Name', how="inner")
        print(new)
    ref 
    Flatten List
    https://python.shiksha/tips/count-occurrences-of-a-list-item-in-python/
    https://realpython.com/python-flatten-list/

    Turn into dictionary DataFrame 
    https://www.geeksforgeeks.org/how-to-create-dataframe-from-dictionary-in-python-pandas/

    Renaming Columns
    https://www.geeksforgeeks.org/how-to-rename-multiple-column-headers-in-a-pandas-dataframe/

    Inner Joing
    https://www.kdnuggets.com/2023/03/3-ways-merge-pandas-dataframes.html

    Subtract columns
    https://www.tutorialspoint.com/how-to-subtract-two-columns-in-pandas-dataframe 

    NaN
    https://note.nkmk.me/en/python-pandas-nan-fillna/
    https://saturncloud.io/blog/how-to-replace-none-with-nan-in-pandas-dataframe/#:~:text=The%20simplest%20way%20to%20replace,replace%20None%20values%20with%20NaN%20.
    https://www.geeksforgeeks.org/convert-floats-to-integers-in-a-pandas-dataframe/
    """
    # Create shoping list as a list
    shopping_items = []
    shopping_list = shopping.split('\n')
    shopping_items.append(shopping_list)

    # Flatten List into a dictionary and count the number of occurances
    flat_list = [item for new_list in shopping_items for item in new_list]
    item_count = Counter(flat_list)

    # Create DataFrame 
    shopping_df = pd.DataFrame(list(item_count.items()))
  
    # Remane and index the shopping list 
    shopping_df = shopping_df.rename(columns={0: 'Item_Name', 1: 'Quantity'})
    shopping_df = shopping_df.set_index('Item_Name', verify_integrity=True)
    
    print("Here is the summary of your order:\n\n" , shopping_df)

    # index inventory 
    inventory = inventory_df.set_index('Item_Name', verify_integrity=True)

    #print(inventory)
   
    # Merge shopping cart with inventory list
    shopping_cart = inventory.merge(shopping_df, on='Item_Name', how='right')

    # Subtract the inventory and fill empty values with 0 
    inventory['Stock'] = inventory['Stock'].subtract(shopping_df['Quantity'], fill_value=0)
    
    # Replace NaN with the orginal values
    inventory['Stock'] = inventory['Stock'].fillna(value=shopping_cart['Stock'])

    # Change inventory stock column to integers
    inventory['Stock'] = inventory['Stock'].astype(int)

    reset = inventory.reset_index()

    print(reset)
      
def order():
    """
    Updates the order spreadsheet
    """
    
    user_selects = inventory_df[['Item_Name', 'Stock']]
    print(user_selects)

def main():
    # customer = Customer()
    # membership = membership_m()
    search_results = search()
    shopping = bag(search_results)
    #start_again()
    order_amount(shopping) 

    
    #stock = in_stock()
    
    # shopping = bag(search_results) 
    
    # shopping_stock_calc(shopping)      
    # expired_items = expired()

main()


# deduct selection from the inventory 
# call number and minus one 
# update speadsheet

# Call user selection 
# user_selects 

# 

# ---------------------------Manipulation of data of the gspread--------------------


def expired():

    """
    Based on the expiry date

    """
    #Takes todays date and changes it into Pandas format
    today = datetime.date.today()
    today_pd = pd.to_datetime(today)

    #Changes the data type of the expiry_date column from string to Pandas format eg datetime64[ns] 
    inventory_df['Expiry_Date'] = pd.to_datetime(inventory_df['Expiry_Date'], format='%d/%m/%y')

    # ------------------------------------------------------- added Code institute tutor support
    #creates a list of expired food
    expired_items = inventory_df["Expiry_Date"] < today_pd

    return expired_items


def update_spreadsheet():

    """
    Update spreadsheet with dataframe
    - reused for expired, sold_out and in_stock

    """
     #change Status column to expired
    inventory_df.loc[expired_items, 'Status'] = 'Expired'

    #Update the pandas dataframe
    update_spreadsheet = inventory_df.update(inventory_df)

    print(inventory_df[inventory_df['Status'] == 'Expired'])
    print("Successfully updated")

    # -----------------------------------------------------------

    #Clear and update spreadsheet with dataframe
    inventory.clear()
    set_with_dataframe(worksheet=inventory, dataframe=inventory_df, include_index=False, include_column_header=True, resize=True)


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


# Left align columns (https://www.geeksforgeeks.org/align-columns-to-left-in-pandas-python/)

# Data validation - invalid data
# search for an excluding e.g. not fish
        # extension 
        # change colour on spreadsheet
        # Password Protect the Membership numbers file
# Select food and put in basket
# Check out update orders













# expired_items = inventory_df[inventory_df["Expiry_Date"] < today_pd]

    # expired_items['Status'] = 'Expired'

    # #.loc[expired_items['Status'],]

    # update_spreadsheet = inventory_df.update(expired_items)
    
    
    # print("Sucessfully updated")
    # print(expired_items)

    

    # Make those that fall in the subset expired_filt to change the status coloumn every subse't of inventory_df into   
    

        #filtered_df = inventory_df[inventory_df['Expiry_Date'].dt.strftime('%d/%m/%y') < today_obj]
    #
    
# expired_filt = inventory_df[inventory_df['Expiry_Date'] < datetime.today()]
   #current issue - datetime...(now) is <class 'datetime.date'>
    # - Expiry Date is datetime64[ns]

    #expired_filt = inventory_df['Expiry_Date'] 


    #expired_now = (inventory_df["Expiry_Date"])

    #print(inventory_df)

    #
    #print(expired_filt)









# Login 












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