import datetime
from collections import Counter
import threading
import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials

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
    """
    Returns the logo for the GoodFood Pantry
    """
    logo = (r"""
          _____                 _ ______              _
         / ____|               | |  ____|            | |
        | |  __  ___   ___   __| | |__ ___   ___   __| |
        | | |_ |/ _ \ / _ \ / _` |  __/ _ \ / _ \ / _` |
        | |__| | (_) | (_) | (_| | | | (_) | (_) | (_| |
        \______|\___/ \___/ \__,_|_|  \___/ \___/ \__,_|
            """)
    return logo


def welcome():
    """
    Welcome to users, explains, purpose, and how to use the app
    ---------------------------------------------

    functions: logo_function

    print: logo_function, welcome message

    returns: None
    """
    print(logo_function())
    print(("""
\t\t\x1b[32;4mWelcome to GoodFood Pantry online\u001b[0m\n
Discover a world of affordable, fresh food, right at your fingertips.
As a member, you can:\n\n\t\u001b[32mSearch:\x1b[0m: For the items you need
\t\u001b[32mSelect:\x1b[0m Choose up to \u001b[32m5 items\x1b[0m per order
\t\u001b[32mSave:\x1b[0m Enjoy affordable prices of just \u001b[32m£3\x1b[0m
\t\nTo reserve your food, you have \u001b[32m5 minutes\x1b[0m to complete your
order, otherwise, the items will go back on the shelf.
If you make a mistake, you can refresh your browser to start again.
\n\u001b[32mHappy shopping!\x1b[0m
"""))
    print("Start exploring our selection today!")
    return None


def check_last_order(order_df, membership_no, username_valid):
    """
    Check the last order from the orders spreadsheet
    ---------------------------------------------
    connections: order spreadsheet,
    membership_details = membership_no, username_valid

    print: "Welcome back so soon, You can only order once per week..."

    returns: True if the user can order, False if the user cannot order
    """
    # If the order spreadsheet is empty, the user can still order
    if order_df.empty:
        return True
    # Compares membership number to order spreadsheet
    membership_info = order_df['Membership Number'] == int(membership_no)

    if membership_info.any():
        # Returns the last order from the order spreadsheet
        last_order = order_df[membership_info].iloc[-1]

        # Extracts the date of the last order
        last_order_date = last_order['Date']
    else:
        last_order_date = None

    # Converts the date to a Pandas format
    last_order_date = pd.to_datetime(last_order_date)

    # Checks if the last order was within the last week
    if last_order_date is None or (
        last_order_date + pd.Timedelta(days=7) <= pd.Timestamp.now()
    ):
        return True
    else:
        # Calculates the number of days until the user can order again
        days_to_wait = 7 - (pd.Timestamp.now() - last_order_date).days
        print(f"""
\nWelcome back so soon \u001b[32m{username_valid}\x1b[0m,
\nYou can only order once per week, please check again in
\u001b[32m{days_to_wait}\x1b[0m day(s).
        """)
        return False


def membership_details():
    """
    Matches the users input in a specific column and returns.
    ---------------------------------------------

    Connections: customer spreadsheet

    functions: check_last_order

    print: "Please enter your name:"
    "Looks like you're not quite a member yet!..."
    "You have reached the maximum number of.."
    "Welcome {username},Your membership number {membership number}
    Finding your perfect food match!"

    returns: username, membership number and phone
    """
    shop_or_exit = 0

    # While loop to allow the user to only try again up to 5 tries
    while shop_or_exit < 10:
        username = input(
            "\n\x1b[32;3mPlease enter your name:\x1b[0m \n"
        ).strip()
        # Turns user name into title format
        username_valid = username.title()
        try:
            # Compares username to customer spreadsheet by name
            customer_info = customer_df.loc[customer_df[0] == username_valid]

            # User is not a member
            if customer_info.empty:
                print(f"""
\n\u001b[32m{username_valid}\x1b[0m,Looks like you're not quite a member yet!
Pop into our shop to sign up and start exploring our delicious offerings.
                        """)
                shop_or_exit += 1

# User has tried to enter the name too many times
            if shop_or_exit == 10:
                print("""
\x1b[32;3mYou have reached the maximum number of attempts.\x1b[0m""")
                return None

            # Uses column location to retrive data from spreadsheet
            membership_no = customer_info[1].values[0]
            phone = customer_info[4].values[0]

            # Call the check_last_order function
            valid_customer = check_last_order(
                order_df, membership_no, username_valid)

            if valid_customer:

                # prints welcome message to user
                print(f"""
    \nWelcome \u001b[32m{username_valid}\x1b[0m,
Your membership number \u001b[32m{membership_no}\x1b[0m
\n\x1b[32;4mFinding your perfect food match!\u001b[0m
    """)
                # To be used in the order function
                return username, membership_no, phone, username_valid
            else:
                return None
        except IndexError:
            shop_or_exit += 1
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


def stock_levels(inventory, inventory_df):
    """
    Based on the expiry date and in the inventory
    ---------------------------------------------

    connections: inventory sreadsheet

    functions: update_spreadsheet, check_for_timeout

    returns: inventory_df, today_pd

    """
    if check_for_timeout():
        return None

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

        # Calls update the inventory function to update spreadsheet
        update_spreadsheet(inventory, inventory_df)

        return inventory_df, today_pd

    except Exception as e:
        print(f"stock_levels: {str(e)}")

    finally:
        update_spreadsheet(inventory, inventory_df)


def in_stock(inventory_df):
    """
    Displays the items that are in stock
    ---------------------------------------------

    connections: inventory spreadsheet

    functions: check_for_timeout, stock_levels

    returns: stock_results
    """
    if check_for_timeout():
        return None

    stock_mask = inventory_df[inventory_df['Status'] == 'In stock']
    stock_results = stock_mask[['Item_Name', 'Allegen']]
    print(stock_results)
    return stock_results


def check_for_timeout():
    """
    Checks the global variable if a timeout has occurred
    ---------------------------------------------

    connections: bag function

    functions: time_out

    print: "Your session has expired..."

    returns: True if a timeout has occurred
    """
    global time_out_occurred
    if time_out_occurred:
        print("""
\n\x1b[32;3mYour session has expired.
Please refresh the page to start a new order.\x1b[0m\n""")
        return True


def bag(stock, stock_results):
    """
    User selects an item using the index and it is added to the shopping bag
    ---------------------------------------------

    global variables: order_timer, order_complete, time_out_occurred

    connections: checks the stock level and updates inventory spreadsheet

    functions: check_for_timeout, user_selection, add_item_to_bag,
    calculate_shopping_bag,calculate_last_item, display_basket,
    manage_timer, stock_levels, in_stock, update_inventory, order, time_out

    print: "Checking what we have in store for you today..."
    "To add multiple items, simply select the item again"
    "Your order is now being prepared by our amazing volunteers..."

    returns: shopping_bag_df

"""
    # refactored code with Copilot to break into smaller functions
    # copilot added the following functions:
    # add_item_to_bag, calculate_shopping_bag, calculate_last_item,
    # display_basket, manage_timer, update_inventory, order, time_out
    global order_timer
    global order_complete
    global time_out_occurred

    shopping_bag = []
    items = 0

    if check_for_timeout():
        return None

    while items < 5:

        # checks for global variable time_out_occurred
        if check_for_timeout():
            return None

        # handles user selection if nothing is inputed
        user_selects = user_selection(stock, stock_results)
        if user_selects is None:
            continue

        # Add the item to the shopping bag
        add_item_to_bag(user_selects, stock, shopping_bag)
        items += 1

        # Calculate the shopping bag
        shopping_bag_df = calculate_shopping_bag(shopping_bag)
        last_item_df = calculate_last_item(shopping_bag)

        # Update the inventory with stock levels
        update_inventory(inventory_df, last_item_df)

        # Check stock levels
        stock_levels(inventory, inventory_df)

        # Display the shopping bag
        if items < 5:
            print("""Checking what we have in store for you today...\n
\n\t\x1b[32;3mTo add multiple items, simply select the item again\x1b[0m
              """)
            stock_results = in_stock(inventory_df)
            display_basket(shopping_bag_df, stock_results)
        else:
            print("""
\u001b[32mYour order is now being prepared by our
amazing volunteers. Please pick it up between 10 AM and 3 PM.
""")
            display_basket(shopping_bag_df, None)

        manage_timer(shopping_bag_df, inventory_df)

    return shopping_bag_df


def user_selection(stock, stock_results):
    """
    User selects an item using the index and it is added to the shopping bag
    ---------------------------------------------

    functions: bag, check_for_timeout

    print:
    Use the numbers on the left hand side to pick an item.
    Please enter a number to select an item
    Sorry, that item has sold out
    I can't seem to find that item, please try again

    returns: user_selects
    """
    try:
        user_selects = int(input("""
\t\x1b[32;3mUse the numbers on the left hand side to pick an item.\x1b[0m\n
\t\x1b[32;3mIf you make a mistake, just restart your browser\x1b[0m
\t\x1b[32;3mand try again\x1b[0m\n
                                """))
    except ValueError:
        print("""
\n\x1b[32;3mPlease enter a number to select an item\x1b[0m
            """)
        return None

    if check_for_timeout():
        return None

    if user_selects not in stock.index:
        print("""\n\t\x1b[32;3mI can't seem to find that item,
                please try again\x1b[0m""")
        return None

    if user_selects not in stock_results.index:
        print("""\n\x1b[32;3mSorry, that item has sold out\x1b[0m""")
        return None

    return user_selects


def add_item_to_bag(user_selects, stock, shopping_bag):
    """
    Adds the item to the shopping bag
    ---------------------------------------------

    functions: bag

    """
    in_the_bag = stock.loc[user_selects, 'Item_Name']
    shopping_bag.append(in_the_bag)


def calculate_shopping_bag(shopping_bag):
    """
    Looks for duplicate entries in the shopping bag and counts them
    ---------------------------------------------

    functions: bag

    returns: shopping_bag_df
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
    ---------------------------------------------

    functions: bag

    returns: last_item_df
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
    ---------------------------------------------

    functions: bag, check_for_timeout

    print: shopping_bag_df & message "Currently in your basket"

    returns: None

    """
    if check_for_timeout():
        return None

    # print(stock_results)
    print("\n\u001b[32mCurrently in your basket:\x1b[0m", shopping_bag_df)


def manage_timer(shopping_bag_df, inventory_df):
    """
    Manages the timer for the order
    ---------------------------------------------

    global variables: order_timer

    functions: bag, check_for_timeout, time_out

    returns: None

    """
    global order_timer
    if order_timer:
        order_timer.cancel()
    order_timer = threading.Timer(
        60, time_out, [shopping_bag_df, inventory_df])
    order_timer.start()


def update_inventory(inventory_df, shopping_bag_df):
    """
    Deducts the items from the inventory and changes it into a
    dataframe to update the inventory spreadsheet
    ---------------------------------------------
    connections: inventory spreadsheet

    functions: update_spreadsheet, bag, stock_levels
    """

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
    Summarises the order and adds it to the order spreadsheet
    ---------------------------------------------
    connections: order spreadsheet

    functions: update_spreadsheet

    print: "Don't forget to bring a reusable bag."
    "Thank you for shopping with us today!"

    Returns: None
    """
    global order_complete
    order_complete = True

    today = datetime.date.today()

    name, membership_no, phone, username_valid = membership_details

    name = name.title()

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

    print("""
\t\t\x1b[32;3mDon't forget to bring a reusable bag.\x1b[0m\n
\t\tThank you for shopping with us today!\x1b[0m""")


def time_out(shopping_bag_df, inventory_df):
    """
    Adds the last items back into the inventory if the user does not
    complete the order.
    ---------------------------------------------
    connections: inventory spreadsheet

    functions: update_spreadsheet

    print: "Timeout, your order has been cancelled..."

    returns: None
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
    if time_out_occurred:
        return None


def update_spreadsheet(worksheet, dataframe):
    """
    Updates the spreadsheet with the dataframe
    ---------------------------------------------
    connections: inventory & orders spreadsheet

    functions: order, time_out, update_inventory, stock_levels

    returns: None
    """
    set_with_dataframe(worksheet=worksheet, dataframe=dataframe,
                       include_index=False, include_column_header=True,
                       resize=False)


def combine_api_calls(update_spreadsheet, stock_levels, inventory_df,
                      inventory, orders=None, order_df=None):
    """
    Combines the API calls
    ---------------------------------------------
    connections: stock_levels, update_spreadsheet

    functions: order, time_out, update_inventory, stock_levels

    returns: None

    """
    try:
        stock_levels_thread = threading.Thread(target=stock_levels, args=(
            inventory, inventory_df))
        stock_levels_thread.start()

        update_spreadsheet_thread = threading.Thread(
                target=update_spreadsheet,
                args=(inventory, inventory_df))

        if orders is not None and order_df is not None:
            update_spreadsheet_thread = threading.Thread(
                target=update_spreadsheet,
                args=(orders, order_df)
            )
            update_spreadsheet_thread.start()
            update_spreadsheet_thread.join()

        stock_levels_thread.join()

    except TypeError:
        print("Finding your perfect food match!")


def main():
    # Checking membership and exiting if not a member

    welcome()

    membership_details_returned = membership_details()

    logo = logo_function()

    if membership_details_returned is None:
        print(logo)
        return

    # Call the check_last_order function
    valid_customer = check_last_order(
        order_df,
        membership_details_returned[1],
        membership_details_returned[1]
    )
    if not valid_customer:
        print(logo)
        return

    # Combine API calls
    combine_api_calls(
        update_spreadsheet, stock_levels, inventory_df,
        inventory)
    # Check stock levels

    # stock_levels(inventory, inventory_df)

    stock_results = in_stock(inventory_df)

    shopping_bag_df = bag(stock_results, stock_results)

    if shopping_bag_df is None:
        return

    # shopping_amount = order_amount(shopping_bag_df)

    order(membership_details_returned, shopping_bag_df, order_df)

    # Combine API calls
    combine_api_calls(
        update_spreadsheet, stock_levels, inventory_df,
        inventory, orders, order_df)

    # # Update inventory spreadsheet
    # update_spreadsheet(inventory, inventory_df)

    # # Update orders spreadsheet (example)
    # update_spreadsheet(orders, order_df)


main()
