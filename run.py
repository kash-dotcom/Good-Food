import datetime
import logging
from collections import Counter
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

    print("\n\n\u001b[32mStart exploring our selection today!\x1b[0m")
    return None


def membership_details():
    """
    Matches the users input in a specific column and returns.
    Returns
    Username, membership number and phone
    """
    shop_or_exit = 0
    while shop_or_exit < 5:
        username = input("\n\n Please enter your name: \n")
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

                raise ValueError("User login error - empty")

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
        inventory_df.loc[inventory_df['Stock'] <= 10, 'Status'] = "Sold out"
        inventory_df.loc[inventory_df['Stock'] > 10, 'Status'] = "In stock"

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

        print("""
\n\x1b[32mChecking what we have in store for you today...\x1b[0m\n""")
        return inventory_df, today_pd

    except Exception as e:
        logging.debug(f"stock_levels: {str(e)}")

    finally:
        update_spreadsheet(inventory, inventory_df)


def in_stock(inventory_df):
    stock_mask = inventory_df[inventory_df['Status'] == 'In stock']
    stock_results = stock_mask[['Item_Name', 'Allegen', 'Status']]
    print(stock_results)
    return stock_results


def bag(stock):

    """
    User selects an item using the index and it is added to the
    shopping bag
    """
    shopping_bag = []
    items = 0

    while items < 5:
        try:
            user_selects = int(input(
                "\nUse the numbers on the left hand side to pick an item.\n"
            ))
            print("To add multiple items, simply select the item again.")
            # print("""\n\t\x1b[32;3mFriendly reminder: \x1b[0m\n0 Please
            # select your items before pressing Enter to avoid restarting .
            # your order""")
        except ValueError:
            print(
                """\n\x1b[32;3mPlease enter a number to select an item
                \x1b[0m"""
            )
            continue

        if user_selects not in stock.index:
            print("""\n\x1b[32;3mI can't seem to find that item, please"
            "try again\x1b[0m""")
            continue

        in_the_bag = stock.loc[user_selects, 'Item_Name']
        shopping_bag.append(in_the_bag)
        shopping_bag_str = '\n'.join(shopping_bag)
        print("\n\u001b[32mCurrently in your basket:\x1b[0m\n",
              shopping_bag_str)
        items += 1

        # updates inventory
        continue
    return shopping_bag_str


def order_amount(shopping_bag):
    """
    Calcuation the number of items the customer has in the shopping basket
    Turns user's shopping list into a DataFrame

    """
    if shopping_bag is None:
        print("No item")

    # # Create shopping list as a list
    shopping_items = []
    shopping_list = shopping_bag.split('\n')
    shopping_items.append(shopping_list)

    # Flatten List into a dictionary and count the number of occurances
    flat_list = [item for new_list in shopping_items for item in new_list]
    item_count = Counter(flat_list)

    # Create DataFrame and counts the number of times they have occured
    shopping_amount = pd.DataFrame(list(item_count.items()))

    shopping_amount = shopping_amount.rename(
        columns={
            0: 'Item_Name',
            1: 'Quantity'
        }
    )
    shopping_amount = shopping_amount.set_index(
        'Item_Name', verify_integrity=True
    )

    print("\n\u001b[32mHere is the summary of your order:\x1b[0m\n\n",
          shopping_amount)
    print("\nPlease wait we are processing your order...")

    return shopping_amount


def update_inventory(inventory_df, shopping_amount):

    # index inventory
    inventory_oa = inventory_df.set_index('Item_Name', verify_integrity=True)

    # Merge shopping cart with inventory list
    shopping_cart = inventory_oa.merge(
        shopping_amount, on='Item_Name', how='right'
    )

    # Subtract the inventory and fill empty values with 0
    inventory_oa['Stock'] = inventory_oa['Stock'].subtract(
        shopping_amount['Quantity'], fill_value=0
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

# Make those that fall in the subset expired_filt to change the status coloumn
# every subset of inventory_df into


def order(membership_details, shopping_bag, order_df):
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

    # Update the order spreadsheet
    update_spreadsheet(orders, order_df)

    print("""\n\u001b[32mYour order is now being prepared by our
amazing volunteers. Please pick it up between 10 AM and 3 PM.
\n\nDon't forget to bring a reusable bag to help us reduce waste.
\x1b[0m\n
          """)


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

    stock = in_stock(inventory_df)

    shopping_bag = bag(stock)

    shopping_amount = order_amount(shopping_bag)

    order(membership_details_returned, shopping_bag, order_df)

    update_inventory(inventory_df, shopping_amount)

    # Clears the old content from the spreadsheet
    clear_spreadsheet(inventory, inventory_df)

    # Update inventory spreadsheet
    update_spreadsheet(inventory, inventory_df)

    # Update orders spreadsheet (example)
    update_spreadsheet(orders, order_df)


main()
