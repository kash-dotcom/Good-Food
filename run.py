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
orders = SHEET.worksheet('orders')

# imports the data and changes to a data frame for easier viewing
inventory_li = inventory.get_all_records()
inventory_df = pd.DataFrame(inventory_li)

# import the data and changes to
customer_li = customers.get_all_values()
customer_df = pd.DataFrame(customer_li)

# import the data for orders

order_li = orders.get_all_records()
order_df = pd.DataFrame(order_li)

# Dataframe Style - https://medium.com/@syncwithdanish/bring-colors-to-your-data-frames-cfb7707259a6
#def index_colour():
    #colour == ("colour: green;", "")
    #inventory_df.style.apply_index(colour)

def membership_details():
    """
    Matches the users input in a specific column and returns.

    Reference:
    linking gspread to pandas
    https://medium.com/@vince.shields913/reading-google-sheets-into-a-pandas-dataframe-with-gspread-and-oauth2-375b932be7bf
    """
    try:
        username = input("\n\nWhat is your name? ")

        username_valid = username.title()

        customer_info = customer_df.loc[customer_df[0] == username_valid]

        name = customer_info[0].values[0]
        membership_no = customer_info[1].values[0]
        phone = customer_info[4].values[0]

        #membership_no = customer_df.loc[customer_df[2] == user_input].values[0]
        print(f"\nWelcome {username}, to Good Food Pantry Online. Your membership number {membership_no}\n")
        return username, membership_no, phone

    except KeyError:
        print ("We couldn't find your name in our records. Please try again.")

    except Exception as e:
        print(f"Nah then, summat's gone wrong! An error has occured: {str(e)}")

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
    
    print(('Welcome to GoodFood Pantry online\n\n. Here you will be able to search for available food '
    'and reserve items as part of your membership. For just £3 per order, you can choose 5 items.'
    'Our food comes from FareShare and HIS Food, who save good food from going to landfill.'
    'It has a shorter shelf life (6 months) but is still good quality. To become one of our volunteers '
    'or to sign up to be a member, simply visit one of our pantries. Let’s get started. You can choose '
    '5 items for £3 per order, sourced from quality surplus food that might otherwise end up in landfill.'
    'To get started, please provide us with your name and begin enjoying the benefits of GoodFood Pantry'))

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
                    return results
                    print(results)
         
def bag(search_results):
     
    """
    User selects an item using the index and it is added to the shopping bag
    """
    shopping_bag = []
    items = 0

    while items < 2:
        
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

def order(membership_details, shopping_bag, order_df, orders):
    """
    customer_order, inventory_df, 
    Summarise Order spreadsheet
    """
    today = datetime.date.today()

    name, membership_no, phone = membership_details

    customer_order = shopping_bag
    
    #print(today)
    #print(name)
    #print(membership_no)
    #print(phone)
    print(customer_order)

    # Create a DataFrame
    new_order = pd.DataFrame({
        "Date": [today],
        "Name": [name],
        "Membership Number": [membership_no],
        "phone": [phone],
        "Order":[customer_order]
    })

    order_df = pd.concat([order_df, new_order])

    orders.clear()
    set_with_dataframe(worksheet=orders, dataframe=order_df, include_index=False, include_column_header=True, resize=True) 

def order_amount(shopping, inventory_df):
    
    """
    Calcuation the number of items the customer has in the shopping basket
    Turns user's shopping list into a DataFrame

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
    
    print("\n\u001b[32mHere is the summary of your order:\x1b[0m\n\n" , shopping_df)
    print("\n\u001b[32mThank you for your order, please visit the shop between 10 am and 3 pm to collect your order\x1b[0m\n")
    

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

    inventory_df = reset

   
    return reset

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
        order(today_pd)
        return inventory_df, today_pd

    except Exception as e:
        print("Opps!", e)
     
# Make those that fall in the subset expired_filt to change the status coloumn every subse't of inventory_df into 

def update_spreadsheet(reset):
    """
    Deletes the old content from the spreadsheet and updates with new function

    Uses
    ~ Update Status column with the stock_levels function
    """

    inventory.clear()
    set_with_dataframe(worksheet=inventory, dataframe=inventory_df, include_index=False, include_column_header=True, resize=True) 

def main():
    membership_details_returned = membership_details()

    inventory = Inventory(inventory_df)
    search_results = inventory.search()

    shopping_bag = bag(search_results)
    order_amount(shopping_bag, inventory_df)

    order(membership_details_returned, shopping_bag, order_df, orders)
    

    #update_spreadsheet(reset)
    #expired(inventory_df) 
    
main()
