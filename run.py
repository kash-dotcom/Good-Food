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
            print(f"Hello {user_input}, your membership number {membership_no}\n")
            break
    else:
        print("We can't find your name in the list")

match_and_return()

def categories():

    """
    Matches the users input in a specific column and returns 
    * uses for dietary requirements
    * login
    https://builtin.com/data-science/pandas-filter
    """
    super_list = inventory.get_all_records()
    df = pd.DataFrame(super_list)

    user_search = input("What kind of food do you want? ")

 
    filt = (df['Allegen'].str.contains(user_search, na=False)) & (df['Status'] == 'In stock')
    filt_df =df.loc[filt]


    print(filt_df[['Item ID', 'Item_Name', 'Allegen', 'Status']])

categories()



def read_logins():
    """
    Common delimiter and remove the new line marker

    """

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
    
    """
    login page
    https://www.youtube.com/watch?v=L2i6lELbNI0
    https://github.com/rodbove/console-login-system/blob/master/main.py
    https://docs.gspread.org/en/latest/
     """

   
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

    """

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

    """

       #filt = (df['Allegen'] == user_search)