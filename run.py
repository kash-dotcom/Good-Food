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
    """
    super_list = inventory.get_all_values()
    user_search = input("What kind of food do you want? ")
    options = []

    for sublist in super_list:
        for item in sublist:
            if item == user_search:
                 options.append(sublist)
    print(options)
    
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
