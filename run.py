import datetime
import logging
from collections import Counter
import threading
import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe
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


# Code institute tutor support to create inventory_li and inventory_df
# imports the data and changes to a data frame for easier viewing
inventory_li = inventory.get_all_records()
inventory_df = pd.DataFrame(inventory_li)

# import the data and changes to
customer_li = customers.get_all_values()
customer_df = pd.DataFrame(customer_li)

# import the data for orders

order_li = orders.get_all_records()
order_df = pd.DataFrame(order_li)

# Global flag to show when an order has been completed
order_complete = False

# Global variable to hold the timer
order_timer = None

# Global variable to show if the time out has occurred
time_out_occurred = False

# logo function


def logo_function():
    logo = (r"""
         _____                 _ ______              _
        / ____|               | |  ____|            | |
        | |  __  ___   ___   __| | |__ ___   ___   __| |
        | | |_ |/ _ \ / _ \ / _` |  __/ _ \ / _ \ / _` |
        | |__| | (_) | (_) | (_| | | | (_) | (_) | (_| |
        \_____|\___/ \___/ \__,_|_|  \___/ \___/ \__,_|
            """)
    return logo


def welcome():
    print(logo_function())
    print(("""
    \n\x1b[32;4mWelcome to GoodFood Pantry online\u001b[0m\n\n
Discover a world of affordable, fresh food, right at your fingertips.
As a member, you can:\n\n\u001b[32mSearch:\x1b[0m: For the items you need
\u001b[32mSelect:\x1b[0m Choose up to \u001b[32m5 items\x1b[0m per order
\u001b[32mSave:\x1b[0m Enjoy affordable prices of just \u001b[32m£3\x1b[0m
"""))
    print("\nStart exploring our selection today!")
    return None


def membership_details():
    """
    Matches the users input in a specific column and returns.
    Returns
    Username, membership number and phone
    """
    shop_or_exit = 0
    while shop_or_exit < 5:
        username = input("\n\x1b[32;3mPlease enter your name:\x1b[0m \n")
        # Turns user name into title format
        username_valid = username.title()
        try:
            # Compares username to customer spreadsheet by name
            customer_info = customer_df.loc[customer_df[0] == username_valid]
            if customer_info.empty:
                print(f"""
\n\u001b[32m{username_valid}\x1b[0m,Looks like you're not quite a member yet!
Pop into our shop to sign up and start exploring our delicious offerings.
                        """)
                shop_or_exit += 1
            if shop_or_exit == 5:
                print("""
\x1b[32;3mYou have reached the maximum number of attempts.\x1b[0m""")
                return None

            # Uses column location to retrive data from spreadsheet
            # name = customer_info[0].values[0]
            membership_no = customer_info[1].values[0]
            phone = customer_info[4].values[0]

            # prints welcome message to user
            print(f"""
\nWelcome \u001b[32m{username_valid}\x1b[0m,
Your membership number \u001b[32m{membership_no}\x1b[0m\n
\n\x1b[32;4mFind your perfect food match!\u001b[0m
""")
            return username, membership_no, phone
            break
        except Exception as e:
            logging.debug(f"membership_details: {str(e)}")


def stock_levels(inventory, inventory_df):
    """
    Based on the expiry date

    """
    try:
        # Takes todays date and changes it into Pandas format
        today = datetime.date.today()
        today_pd = pd.to_datetime(today)

        # Change the Status column depending on the amount of stock
        inventory_df.loc[inventory_df['Stock'] <= 0, 'Status'] = "Sold out"
        inventory_df.loc[inventory_df['Stock'] > 0, 'Status'] = "In stock"

        # Changes the data type of the expiry_date column from string to Pandas
        # format eg datetime64[ns]
        inventory_df['Expiry_Date'] = pd.to_datetime(inventory_df
                                                     ['Expiry_Date'],
                                                     format='%d/%m/%y')

        # Changes the Status depending on the date and the Expiry Date
        inventory_df.loc[inventory_df['Expiry_Date'] <
                         today_pd, 'Status'] = 'Expired'

        clear_spreadsheet(inventory, inventory_df)
        update_spreadsheet(inventory, inventory_df)

        print("""Checking what we have in store for you today...\n
\n\t\x1b[32;3mTo add multiple items, simply select the item again\x1b[0m
              """)
        return inventory_df, today_pd

    except Exception as e:
        logging.debug(f"stock_levels: {str(e)}")

    finally:
        update_spreadsheet(inventory, inventory_df)


def in_stock(inventory_df):
    """
    Displays the items that are in stock
    """
    stock_mask = inventory_df[inventory_df['Status'] == 'In stock']
    stock_results = stock_mask[['Item_Name', 'Allegen', 'Status']]
    print(stock_results)
    return stock_results


def check_for_timeout():
    if time_out_occurred:
        print("""
\n\x1b[32;3mYou cannot continue ordering as the timeout has occurred.
        Please restart your browser \x1b[0m\n""")
        return True
    return False


def bag(stock, stock_results):

    # refactored code with Copilot to break into smaller functions
    # copilot added the following functions:
    # add_item_to_bag, calculate_shopping_bag, calculate_last_item,
    # display_basket, manage_timer, update_inventory, order, time_out
    """
    User selects an item using the index and it is added to the
    shopping bag
    """
    global order_timer, order_complete, time_out_occurred
    shopping_bag = []
    items = 0

    if check_for_timeout():
        return None

    # While in development, the user can select up to 2 items
    while items < 3:
        if check_for_timeout():
            return None

        user_selects = user_selection(stock, stock_results)
        if user_selects is None:
            continue

        if check_for_timeout():
            return None

        # Add the item to the shopping bag
        add_item_to_bag(user_selects, stock, shopping_bag)
        items += 1

        # Calculate the shopping bag
        shopping_bag_df = calculate_shopping_bag(shopping_bag)
        last_item_df = calculate_last_item(shopping_bag)

        if check_for_timeout():
            return None

        # Update the inventory with stock levels
        update_inventory(inventory_df, last_item_df)
        stock_levels(inventory, inventory_df)
        stock_results = in_stock(inventory_df)
        manage_timer(shopping_bag_df, inventory_df)

        # Prints shopping bag in terminal
        display_basket(shopping_bag_df, stock_results)

        # Update the inventory with stock levels
    return shopping_bag_df


def user_selection(stock, stock_results):
    """
    User selects an item using the index and it is added to the shopping bag
    """
    if time_out_occurred:
        print(
            """\n\x1b[32;3mYou cannot continue ordering as the timeout has occurred.
            Please restart your browser \x1b[0m\n"""
        )
        return None

    try:
        user_selects = int(input("""
\t\x1b[32;3mUse the numbers on the left hand side to pick an item.\x1b[0m\n
                                 """))
        # Friendly reminder: If you don't select something for five minutes
        # your items will be returned to the shelf.\n\n
    except ValueError:
        print("""\n\x1b[32;3mPlease enter a number to select an item\x1b[0m""")
        return None

    if user_selects not in stock.index:
        print("""\n\t\x1b[32;3mI can't seem to find that item, please try again
              \x1b[0m""")
        return None

    if user_selects not in stock_results.index:
        print("""\n\x1b[32;3mSorry, that item has sold out\x1b[0m""")
        return None

    return user_selects


def add_item_to_bag(user_selects, stock, shopping_bag):
    in_the_bag = stock.loc[user_selects, 'Item_Name']
    shopping_bag.append(in_the_bag)


def calculate_shopping_bag(shopping_bag):
    """
    Looks for duplicate entries in the shopping bag and counts them
    """
    item_count = Counter(shopping_bag)
    shopping_bag_df = pd.DataFrame(
        list(item_count.items()),
        columns=['Item_Name', 'Quantity']
    )
    shopping_bag_df = shopping_bag_df.set_index(
        'Item_Name', verify_integrity=True
    )
    return shopping_bag_df


def calculate_last_item(shopping_bag):
    """
    Calculate the last item that has been added to the shopping bag
    """
    last_item = [shopping_bag[-1]]
    last_item_count = Counter(last_item)
    last_item_df = pd.DataFrame(
        list(last_item_count.items()),
        columns=['Item_Name', 'Quantity']
    )
    last_item_df = last_item_df.set_index('Item_Name', verify_integrity=True)
    return last_item_df


def display_basket(shopping_bag_df, stock_results):
    """
    prints the shopping bag and the results
    """
    # print(stock_results)
    print("\n\u001b[32mCurrently in your basket:\x1b[0m", shopping_bag_df)


def manage_timer(shopping_bag_df, inventory_df):
    global order_timer
    if order_timer:
        order_timer.cancel()
    order_timer = threading.Timer(15, time_out, [shopping_bag_df, inventory_df])
    order_timer.start()


def update_inventory(inventory_df, shopping_bag_df):

    # index inventory
    inventory_oa = inventory_df.set_index('Item_Name', verify_integrity=True)

    # Merge shopping cart with inventory list
    shopping_cart = inventory_oa.merge(
        shopping_bag_df, on='Item_Name', how='right'
    )

    # Subtract the inventory and fill empty values with 0
    inventory_oa['Stock'] = inventory_oa['Stock'].subtract(
        shopping_bag_df['Quantity'], fill_value=0
    )

    # Replace NaN with the orginal values
    inventory_oa['Stock'] = inventory_oa['Stock'].fillna(value=shopping_cart
                                                         ['Stock'])

    # Change inventory stock column to integers
    inventory_oa['Stock'] = inventory_oa['Stock'].astype(int)

    # Reset the index to include 'Item_Name' as a column
    inventory_oa = inventory_oa.reset_index()

    # Reorder columns in inventory_oa to match inventory_df
    inventory_oa = inventory_oa[inventory_df.columns]

    # Update the original inventory_df with the changes made in inventory_oa
    inventory_df.update(inventory_oa)

    update_spreadsheet(inventory, inventory_df)


def order(membership_details, shopping_bag, order_df):
    """
    customer_order, inventory_df,
    Summarise order spreadsheet
    """
    global order_complete
    order_complete = True

    today = datetime.date.today()

    name, membership_no, phone = membership_details

    customer_order = shopping_bag

    # Create a DataFrame
    new_order = pd.DataFrame({
        "Date": [today],
        "Name": [name],
        "Membership Number": [membership_no],
        "Phone": [phone],
        "Order": [customer_order]
    })

    order_df = pd.concat([order_df, new_order])

    # Update the order spreadsheet
    update_spreadsheet(orders, order_df)

    print("""\n\u001b[32mYour order is now being prepared by our
amazing volunteers. Please pick it up between 10 AM and 3 PM.
\n\nDon't forget to bring a reusable bag to help us reduce waste.
\x1b[0m\n
          """)


def time_out(shopping_bag_df, inventory_df):
    """
    Adds the last items back into the inventory if the user does not
    complete the order.
    """
    global order_complete, time_out_occurred
    global order_timer
    if not order_complete:
        # index inventory
        inventory_oa = inventory_df.set_index(
            'Item_Name', verify_integrity=True)

        # Add the last item back to the inventory
        inventory_oa['Stock'] = inventory_oa['Stock'].add(
            shopping_bag_df['Quantity'], fill_value=0)

        # Reset the index to include 'Item_Name' as a column
        inventory_oa = inventory_oa.reset_index()

        # Update the original inventory_df
        # with the changes made in inventory_oa
        inventory_df.update(inventory_oa)
        update_spreadsheet(inventory, inventory_df)

        print("""
\t\tTimeout, your order has been cancelled
\n\t\t\x1b[32;3mPlease refresh the page and start again\x1b[0m\n
              """)
        time_out_occurred = True


def clear_spreadsheet(worksheet, dataframe):
    """
    Clears the old content from the spreadsheet

    Uses
    ~ Update Status column with the stock_levels function
    """
    worksheet.clear()


def update_spreadsheet(worksheet, dataframe):
    """
    Deletes the old content from the spreadsheet and updates with new function

    Uses
    ~ Update Status column with the stock_levels function
    """
    set_with_dataframe(worksheet=worksheet, dataframe=dataframe,
                       include_index=False, include_column_header=True,
                       resize=False)


def main():
    # Checking membership and exiting if not a member

    welcome()

    membership_details_returned = membership_details()

    logo = logo_function()

    if membership_details_returned is None:
        print(logo)
        return

    # Check stock levels
    stock_levels(inventory, inventory_df)

    stock_results = in_stock(inventory_df)

    shopping_bag_df = bag(stock_results, stock_results)

    if shopping_bag_df is None:
        return

    # shopping_amount = order_amount(shopping_bag_df)

    order(membership_details_returned, shopping_bag_df, order_df)

    # Clears the old content from the spreadsheet
    clear_spreadsheet(inventory, inventory_df)

    # Update inventory spreadsheet
    update_spreadsheet(inventory, inventory_df)

    # Update orders spreadsheet (example)
    update_spreadsheet(orders, order_df)


main()
