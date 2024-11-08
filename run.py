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

# Dataframe Style - https://medium.com/@syncwithdanish/bring-colors-to-your-data-frames-cfb7707259a6
#def index_colour():
    #colour == ("colour: green;", "")
    #inventory_df.style.apply_index(colour)

#index_colour()
      
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
    user_input = input("\n\nWhat is your name? ")
    for row in name:
        if row[0] == user_input:
            membership_no = row[1]
            print((f"\nWelcome {user_input}, to Good Food Pantry Online. Your membership number {membership_no}\n"))
            return membership_no
            break
    else:
        print("We can't find your name in the list")

class Inventory:
    """
    Customers can search for food based on In Stock & Allegens
    """    
    def __init__(self, inventory_df):
        self.inventory_df = inventory_df

    def search_in_stock(self, user_search_valid):
        in_stock = self.inventory_df['Status'].str.contains(user_search_valid, na=False)
        in_stock_mask = self.inventory_df.loc[in_stock]
        in_stock_results = in_stock_mask[['Item_Name', 'Allegen', 'Status']]
        print(in_stock_results)
        return in_stock_results
        
    def search_allegens_item(self, user_search_valid):
        allegen_search = (self.inventory_df['Allegen'].str.contains(user_search_valid, na=False)) & (self.inventory_df['Status'] == 'In stock') | (self.inventory_df['Item_Name'].str.contains(user_search_valid, na=False)) & (self.inventory_df['Status'] == 'In stock')
        allegen_search_mask =self.inventory_df.loc[allegen_search]
        allegen_results = allegen_search_mask[['Item_Name', 'Allegen', 'Status']]
        print(allegen_results)   
        return allegen_results

    def search(self):
        while True:
            print("\n\x1b[32;4mSearch our inventory\u001b[0m")
            user_search = input('You can write \u001b[32min stock\u001b[0m to find all the items available. \n Search by dietary requirements like \u001b[32mvegetarian\x1b[0m or \u001b[32mvegan\x1b[0m\n\t\x1b[32;3mRemember you can only select 5 items\x1b[0m\n \n')

            user_search_valid = user_search[0].upper()+ user_search[1:]

            try:
                if user_search_valid == 'In stock':
                    results = self.search_in_stock(user_search_valid)
                       
                else:
                    results = self.search_allegens_item(user_search_valid)
                
                if self.search_in_stock is None and self.search_allegens_item is None:
                    print(f"That item is currently out of stock")    

            except Exception as e:
                    print(f"107 Nah then, summat's gone wrong! An error has occured: {str(e)}")
                    return None 
            
            finally:
                    #breakpoint()
                    return results
                    print(results)
         
def bag(search_results):
     
    """
    User selects an item using the index and it is added to the shopping bag
    """
    shopping_bag = []
    items = 0

    while items < 3:
        
        user_selects = int(input('\nChose an item: '))
        print(search_results, "129")
        
        # breakpoint()
        try:
            in_the_bag = search_results.loc[user_selects, 'Item_Name']
            shopping_bag.append(in_the_bag)
            shopping_bag_str = '\n'.join(shopping_bag) 
            print("\n\u001b[32mCurrently in your basket:\x1b[0m\n",shopping_bag_str)
            items += 1  
            
            
        except Exception as e:
            print(f"137 Ey up, summat's gone wrong! An error has occured: {str(e)}")
            return None   

        #else:
            #print("143 Nah then, t'uther error! We have not been able to find your result. Please try again!")
            #print("There are not results")
            r#eturn

        except (KeyError):
            print("Sorry, we can't find that item. Please choose another item from the list:KE")
            continue

        except (ValueError):
            print("Sorry, we can't find that item. Plebrease choose another item from the list:VE")
            continue

        #BUG - ValueError when user doesn't input anything - programme restarts
    
    
    return shopping_bag_str

def start_again():
    restart = input("\n\nThank you, would you like to reserve your items or start again?\nWrite\u001b[32m SA\x1b[0m to start again, or\n\u001b[32mR\x1b[0m to start again")
    print("\n\nThank you, would you like to reserve your items or start again?\n\n")

    restart_valid = restart.upper()

    if restart_valid == "SA":
        Inventory()
    elif restart_valid =="R":
        order_amount()
    else:
        start_again()

def order_amount(shopping):
    
    """
    Calcuation the number of items the customer has in the shopping basket

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
    Summarise Order spreadsheet
    """
    user_selects = inventory_df[['Item_Name', 'Stock']]
    print(user_selects)

    
def stock_levels(inventory_df):
    """
    Based on the expiry date

    """   
    try:
        # Takes todays date and changes it into Pandas format
        today = datetime.date.today()
        today_pd = pd.to_datetime(today)

        # Change the Status column depending on the amount of stock
        inventory_df.loc[inventory_df['Stock'] == 0, 'Status'] ="Sold out"
        inventory_df.loc[inventory_df['Stock'] >= 1, 'Status'] ="In stock"


        #Changes the data type of the expiry_date column from string to Pandas format eg datetime64[ns]                 
        inventory_df['Expiry_Date'] = pd.to_datetime(inventory_df['Expiry_Date'], format='%d/%m/%y')

        # Changes the Status depending on the date and the Expiry Date
        inventory_df.loc[inventory_df['Expiry_Date'] < today_pd, 'Status'] = 'Expired'

    except Exception as e:
        print("Opps!", e)
     

# Make those that fall in the subset expired_filt to change the status coloumn every subse't of inventory_df into 

def update_spreadsheet():
    """
    Deletes the old content from the spreadsheet and updates with new function

    Uses
    ~ Update Status column with the stock_levels function
    """

    inventory.clear()
    set_with_dataframe(worksheet=inventory, dataframe=inventory_df, include_index=False, include_column_header=True, resize=True) 

def main():
    # customer = Customer()
    #membership = membership_m()

    inventory = Inventory(inventory_df)
    search_results = inventory.search()
    shopping_bag = bag(search_results)
    order_amount(shopping_bag)
    stock_levels(inventory_df)
    update_spreadsheet()
    #expired(inventory_df) 
    #start_again()

main()
    
    #stock = in_stock()
    
    # shopping = bag(search_results) 
    
    # shopping_stock_calc(shopping)      
    # expired_items = expired()

# deduct selection from the inventory 
# call number and minus one 
# update speadsheet

# Call user selection 
# user_selects 











"""
    # print(out_of_stock)
    
        #out_of_stock = (inventory_df[inventory_df['Stock']] == 0)
    #no_stock = inventory_df.loc[out_of_stock]
   

    #if inventory_df['Stock'] > 0:
        #inventory_df['Status'] = "In Stock"
        #print(inventory_df)



# class Customer:
    # def __init__(self, membership, search, bag, order, inventory_update):
    #self.membership = membership
    #self.search = stock
    # self.bag = options
    #self.order = selects

def search(inventory_df, food_exclusion):
    

    
    Matches the users input in a specific column and returns 
    * uses for dietary requirements
    

    References
    https://builtin.com/data-science/pandas-filter
    https://shecancode.io/filter-a-pandas-dataframe-by-a-partial-string-or-pattern-in-8-ways/
    https://sentry.io/answers/write-a-list-to-a-file-in-python-with-each-item-on-a-new-line/

    https://sparkbyexamples.com/pandas/not-in-filter-in-pandas/#:~:text=Apply%20the%20NOT%20IN%20filter,unwanted%20rows%20from%20the%20DataFrame.
 

    def filter_by_allegens(row, food_exclusion):
        return any(allergen in str(row))
    # Food exlusion list
    print((""
Are there any foods you dislike, or do you have any allergies?
You can either write NO if you don't have any allegeries.
Don't worry vegans and vegetarians dietary requirements in the next question:
    \nGluten\nDiary\nFish\nSulphites\nSoya\nSesame\nMustard\nShellfish\nEgg\nCelery\nPeanuts\nWheat\n ""))

    # Turn allegen's column into a list of lists
    # https://www.geeksforgeeks.org/how-to-break-up-a-comma-separated-string-in-pandas-column/
    inventory_df['Allegen'] = inventory_df['Allegen'].str.split(',')
    allergens = food_exclusion.split(",")
    
    list_values = ["Gluten", "Diary", "Fish", "Sulphites", "Soya", "Sesame", "Mustard", "Shellfish", "Egg", "Celery", "Peanuts", "Wheat"]
    food_exclusion = input("Write you answer separted by a comma, e.g. Fish, Diary, Egg or If you don't have any allegeries hit ENTER :\n")

    mask = inventory_df.apply(lambda x: x.map(lambda s: search(text, food_exclusion)))

    filtered_df = inventory_df.loc[mask.any(axis=1)]
    print(filtered_df)
    return search in text().lower()

#search(text, food_exclusion)
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

  #creates a list of expired food
        expired_items = inventory_df[inventory_df["Expiry_Date"] < today_pd]
        #expired_filt = expired_status[['Item_Name', 'Expiry_Date']]   

        #change the status column when food has expired 

        expired_items['Status'] = 'Expired'
        inventory_df.update(expired_items)
  
        #print(expired_filt)
        print("Sucessfully updated")
        
        breakpoint()
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

 Order amount

        for items in shopping_items:''
        inventory_df.loc[inventory_df['Item_Name'] == items]
        new = pd.join(inventory_df, shopping_items, on='Item_Name', how="inner")
        print(new)
    ref 
    #mask = inventory_df.apply(lambda x: x.map(lambda s: search(s, )))

    #filtered_search = inventory_df.loc[mask.any(axis=1)]

    #print(filtered_search)

    # Working Search

    user_search = input('Would you like to see only vegan or vegetarian foods? \n \n If yes, please write "Vegan" or "Vegetarian" below. \n \n ')

    filt = (inventory_df['Allegen'].str.contains(user_search, na=False)) & (inventory_df['Status'] == 'In stock') 
    filt_df =inventory_df.loc[filt]

    if not filt_df.empty:
        in_stock = filt_df[['Item_Name', 'Allegen', 'Status']]
        print(in_stock)
        return in_stock
    else:
        print("Sorry, there are any items that match your request. Please try again:C")

        for food in food_exclusion:
        if food_exclusion:
            exclusion_df = inventory_df[inventory_df['Allegen'].isin(list_values)]
            print(exclusion_df) 
    else:
        print("Opps!!, something went wrong!")

    # exclusion = inventory_df[~inventory_df['Allegen'].isin(list_values)]
    # exclusion = inventory_df[~inventory_df['Allegen'].str.contains(food_exclusion, na=False).isin(list_values) & (inventory_df['Status'] == 'In stock')]
    Reference

    """