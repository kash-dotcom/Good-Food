import gspread
from google.oauth2.service_account import Credentials

import pandas as pd
import re



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


#for cell in inventory.range('B2:B31'):
   #print(cell.value)



def match_and_return():
    """
    Matches the users input in a specific column and returns 
    * uses for dietary requirements
    * login
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
    https://builtin.com/data-science/pandas-filter
    https://shecancode.io/filter-a-pandas-dataframe-by-a-partial-string-or-pattern-in-8-ways/
    https://sentry.io/answers/write-a-list-to-a-file-in-python-with-each-item-on-a-new-line/
    """
    super_list = inventory.get_all_records()
    df = pd.DataFrame(super_list)

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
        except (KeyError, ValueError):
            print("Sorry, we can't find that item. Please choose another item from the list")
        #BUG - ValueError when user doesn't input anything - programme restarts

    
    print("Thank you, would you like to reserve your items or start again? \n")
        
    

    
    
    # iteration to an another item to the array
    # if 

    

#choice = results[results["Item_Name"].isin([user_selects])]
# take user input and put it into a shopping bag'
# match user input with items
# put that into the shopping backg


def main():
    match_and_return()
    search_results = categories()
    selection(search_results)
    
main()




























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