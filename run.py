import datetime
import logging
from collections import Counter

import gspread
import pandas as pd
import numpy as np
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials

logging.basicConfig(filename="goodfood.log", level=logging.DEBUG, filemode="w")

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


def membership_details():
    """
    Matches the users input in a specific column and returns.
    Returns
    Username, membership number and phone
    Reference:
    """
    while True:
        username = input("\n\nPlease tell us your full name: \n")
        # Turns user name into title format
        username_valid = username.title()
        try:
            # Compares username to customer spreadsheet by name
            customer_info = customer_df.loc[customer_df[0] == username_valid]
            if customer_info.empty:
                print(f"""
                        \n\u001b[32m{username_valid}\x1b[0m, I can't find you on our list.
                        \nIf you are not a member pop into our shop to register.\
                        """
                        )
                raise ValueError("User login error - empty")
            # Uses column location to retrive data from spreadsheet
            name = customer_info[0].values[0]
            membership_no = customer_info[1].values[0]
            phone = customer_info[4].values[0]

            # prints welcome message to user
            print(f"""
            \nWelcome \u001b[32m{username_valid}\x1b[0m,
            Your membership number
            \u001b[32m{membership_no}\x1b[0m\n
            """)
            return username, membership_no, phone
            break
        except Exception as e:
            logging.debug(f"membership_details: {str(e)}")


class Inventory:
    """
    Customers can search for food based on In Stock & Allegens
    """
    def __init__(self, inventory_df):
        self.inventory_df = inventory_df

    def search_in_stock(self, user_search_valid):
        in_stock = self.inventory_df['Status'].str.contains(user_search_valid,
                                                            na=False)
        in_stock_mask = self.inventory_df.loc[in_stock]
        in_stock_results = in_stock_mask[['Item_Name', 'Allegen', 'Status']]
        print(in_stock_results)
        return in_stock_results

    def search_allegens_item(self, user_search_valid):
        allegen_search = (self.inventory_df['Allegen'].str.contains
        (user_search_valid, na=False)) & (self.inventory_df['Status'] 
        =='In stock') | (self.inventory_df['Item_Name'].str.contains
        (user_search_valid, na=False)) & (self.inventory_df['Status'] 
                                         == 'In stock')
        allegen_search_mask = self.inventory_df.loc[allegen_search]
        allegen_results = allegen_search_mask[['Item_Name', 'Allegen',
                                              'Status']]
        print(allegen_results)
        return allegen_results
        # Tutorial: https://www.101computing.net/python-typing-text-effect/

    print(r"""           
     _____                 _ ______              _ 
    / ____|               | |  ____|            | |
    | |  __  ___   ___   __| | |__ ___   ___   __| |
    | | |_ |/ _ \ / _ \ / _` |  __/ _ \ / _ \ / _` |
    | |__| | (_) | (_) | (_| | | | (_) | (_) | (_| |
    \_____|\___/ \___/ \__,_|_|  \___/ \___/ \__,_|
        """)

    print(("""
    \n\x1b[32;4mWelcome to GoodFood Pantry online\u001b[0m\n\n
    Here you will be able to search for available food and reserve items
    as part of your membership.For just \x1b[32;4m£3\u001b[0m per order,
    you can choose \x1b[32;4m5 items\u001b[0m."""))

    print("\n\nLets get started!!!.")


    def search(self):
        while True:
            print("\n\x1b[32;4mSearch our inventory\u001b[0m")
            user_search = input("""
            You can write \u001b[32min stock\u001b[0m to find all the items
            available. \n\tSearch by dietary requirements like
            \u001b[32mvegetarian\x1b[0m or \u001b[32mvegan\x1b[0m. 
            \n\t\x1b[32;3mRemember you can only select 5 items\x1b[0m\n \n""")
            if not user_search:
                print("""Sorry, we didn't understand your request, please try
                again""")
                logging.debug("""user searches the inventor - nothing was-
                provided in the serach""")
                continue
            # changes the case to upper to match the spreadsheet
            user_search_valid = user_search[0].upper() + user_search[1:]

            try:
                # Search all items that are in stock
                if user_search_valid == 'In stock':
                    results = self.search_in_stock(user_search_valid)
                else:
                    # Search all items that are in stock
                    results = self.search_allegens_item(user_search_valid)
                if self.search_in_stock is None and self.search_allegens_item is None:
                    print(f"""
                    Nah then, summat's gone wrong! That item is currently
                    out of stock
                    """)
            except IndexError:
                logging.debug(f""" Inventory-search. An error has"
                "occured:{str(e)}""")
                return None
            finally:
                return results


def bag(search_results):

    """
    User selects an item using the index and it is added to the shopping bag
    """
    shopping_bag = []
    items = 0

    while items < 5:
        user_selects = int(input("""\nUse the numbers on the left hand side to
        pick an item.\n"""))
        
        print(search_results)
        try:
            in_the_bag = search_results.loc[user_selects, 'Item_Name']
            shopping_bag.append(in_the_bag)
            shopping_bag_str = '\n'.join(shopping_bag)
            print("\n\u001b[32mCurrently in your basket:\x1b[0m\n",
                    shopping_bag_str)
            items += 1       
        except Exception as e:
            logging.debug('Incorrect selection')
            print("""\n\x1b[32;3mI can't seem to find that item, please
            "try again\x1b[0m""")
            print("""\n\u001b[32mCurrently in your basket:
            \x1b[0m\n""", shopping_bag_str)
            continue
        finally:
            return shopping_bag_str  

def order(membership_details, shopping_bag, order_df, order):
    """
    customer_order, inventory_df,
    Summarise order spreadsheet
    """
    today = datetime.date.today()

    name, membership_no, phone = membership_details

    customer_order = shopping_bag

    # Create a DataFrame
    new_order = pd.DataFrame({
        "Date": [today],
        "Name": [name],
        "Membership Number": [membership_no],
        "phone": [phone],
        "Order": [customer_order]
    })

    order_df = pd.concat([order_df, new_order])

    orders.clear()
    set_with_dataframe(worksheet=orders, dataframe=order_df,
                       include_index=False, include_column_header=True,
                       resize=True)

    print("""\n\u001b[32mThank you for your order, please visit the shop 
    between 10 am and 3 pm to collect your order.\n\nOur wonderful volunteers
    are now busy pulling together your order.\nDon't forget your shopping bag
    \x1b[0m\n""")


def order_amount(shopping, inventory_df):
    """
    Calcuation the number of items the customer has in the shopping basket
    Turns user's shopping list into a DataFrame

    """
    if shopping is None:
        print("No item")

    # Create shoping list as a list
    shopping_items = []
    shopping_list = shopping.split('\n')
    shopping_items.append(shopping_list)

    # Flatten List into a dictionary and count the number of occurances
    flat_list = [item for new_list in shopping_items for item in new_list]
    item_count = Counter(flat_list)

    # Create DataFrame and counts the number of times they have occured
    shopping_df = pd.DataFrame(list(item_count.items()))

    # Remane and index the shopping list
    shopping_df = shopping_df.rename(columns={0: 'Item_Name', 1: 'Quantity'})
    shopping_df = shopping_df.set_index('Item_Name', verify_integrity=True)

    print("\n\u001b[32mHere is the summary of your order:\x1b[0m\n\n",
          shopping_df)
    print("\nPlease wait we are processing your order...")

    # index inventory
    inventory = inventory_df.set_index('Item_Name', verify_integrity=True)

    # Merge shopping cart with inventory list
    shopping_cart = inventory.merge(shopping_df, on='Item_Name', how='right')

    # Subtract the inventory and fill empty values with 0
    inventory['Stock'] = inventory['Stock'].subtract(shopping_df['Quantity'],
                                                     fill_value=0)

    # Replace NaN with the orginal values
    inventory['Stock'] = inventory['Stock'].fillna(value=shopping_cart
                                                   ['Stock'])

    # Change inventory stock column to integers
    inventory['Stock'] = inventory['Stock'].astype(int)

    return inventory
    set_with_dataframe(worksheet=inventory, dataframe=inventory_df,
                       include_index=False, include_column_header=True)


def stock_levels(inventory_df):
    """
    Based on the expiry date

    """
    try:
        # Takes todays date and changes it into Pandas format
        today = datetime.date.today()
        today_pd = pd.to_datetime(today)

        # Change the Status column depending on the amount of stock
        inventory_df.loc[inventory_df['Stock'] <= 10, 'Status'] = "Sold out"
        inventory_df.loc[inventory_df['Stock'] > 10, 'Status'] = "In stock"

        # Changes the data type of the expiry_date column from string to Pandas
        # format eg datetime64[ns]
        inventory_df['Expiry_Date'] = pd.to_datetime(inventory_df
                                                     ['Expiry_Date'],
                                                     format='%d/%m/%y')

        # Changes the Status depending on the date and the Expiry Date
        inventory_df.loc[inventory_df['Expiry_Date'] < today_pd, 'Status'] = 'Expired'

        inventory.clear()
        set_with_dataframe(worksheet=inventory, dataframe=inventory_df,
                           include_index=False, include_column_header=True,
                           resize=True)

        return inventory_df, today_pd

    except Exception as e:
        logging.debug("stock_levels", e)

    finally:
        inventory.clear()
        set_with_dataframe(worksheet=inventory, dataframe=inventory_df,
                           include_index=False, include_column_header=True,
                           resize=True)

# Make those that fall in the subset expired_filt to change the status coloumn
# every subset of inventory_df into


def update_spreadsheet(reset):
    """
    Deletes the old content from the spreadsheet and updates with new function

    Uses
    ~ Update Status column with the stock_levels function
    """

    inventory.clear()
    set_with_dataframe(worksheet=inventory, dataframe=inventory_df,
                       include_index=False, include_column_header=True,
                       resize=True)


def main():
    # Fodl
    stock_levels(inventory_df)
    membership_details_returned = membership_details()
    # f
    inventory = Inventory(inventory_df)
    search_results = inventory.search()
    # d
    shopping_bag = bag(search_results)
    order_amount(shopping_bag, inventory_df)
    # f
    order(membership_details_returned, shopping_bag, order_df, order)
    # update_spreadsheet()


main()
