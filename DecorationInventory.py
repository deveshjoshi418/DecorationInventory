import streamlit as st
import pandas as pd
import hmac

# Initialize session state for inventory storage
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['Item', 'Quantity', 'Size (ft)', 'Original Quantity'])
if 'inventory_list' not in st.session_state:
    st.session_state.inventory_list = []
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Item', 'Name', 'Quantity_Taken', 'Date', 'Status'])
if 'items_to_images' not in st.session_state:
    st.session_state.items_to_images = {}
# Function to add an item
def add_item(item_name, quantity, size):
    # Add new item to the inventory
    new_item = pd.DataFrame([[item_name, quantity, size, quantity]], columns=['Item', 'Quantity', 'Size (ft)', 'Original Quantity'])
    st.session_state.inventory_list.append(item_name)
    st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)

# Function to update item quantity
def update_quantity_taken(item_name, quantity_taken, user, date):
    # Find the item and update its quantity
    index = st.session_state.inventory[st.session_state.inventory['Item'] == item_name].index
    if len(index) > 0:
        st.session_state.inventory.at[index[0], 'Quantity'] -= quantity_taken
        new_entry = pd.DataFrame([[item_name, user, quantity_taken, date, 'Taken']], columns=['Item', 'Name', 'Quantity_Taken', 'Date', 'Status'])
        st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True)
    else:
        st.warning(f"Item '{item_name}' not found in inventory.")

def item_picture(item_name, image):
    st.session_state.items_to_images.update({item_name: image})

def view_item(item_name):
    if item_name in st.session_state.items_to_images.keys():
        st.image(st.session_state.items_to_images.get(item_name))
    else:
        st.warning("Item '{}' not found in inventory.".format(item_name))

def update_quantity_returned(item_name, quantity_returned, user, date):
    index = st.session_state.inventory[st.session_state.inventory['Item'] == item_name].index
    if len(index) > 0:
        st.session_state.inventory.at[index[0], 'Quantity'] += quantity_returned
        new_entry = pd.DataFrame([[item_name, user, quantity_returned, date, "Returned"]], columns=['Item', 'Name', 'Quantity_Taken', 'Date', 'Status'])
        st.session_state.history = pd.concat([st.session_state.history, new_entry], ignore_index=True)
    else:
        st.warning(f"Item '{item_name}' not found in inventory.")

# Function to remove an item
def remove_item(item_name):
    # Remove item from the inventory
    index = st.session_state.inventory[st.session_state.inventory['Item'] == item_name].index
    if len(index) > 0:
        st.session_state.inventory = st.session_state.inventory.drop(index[0])
        st.session_state.inventory_list.remove(item_name)
        st.session_state.items_to_images.pop(item_name)

    else:
        st.warning(f"Item '{item_name}' not found in inventory.")

def missing_inventory():
    for index, row in st.session_state.inventory.iterrows():
        if row['Quantity'] != row['Original Quantity']:
            st.dataframe(row.to_frame().T)

# Function to display inventory table
def display_inventory():
    st.write("## Current Inventory")
    st.dataframe(st.session_state.inventory)

# Sidebar for adding, updating, and removing items
st.sidebar.header("Inventory Management")
action = st.sidebar.radio("Choose action", ["Add Item", "Update Item (Taking)", "Add Item Picture", "View Item", "Update Item (Returning)", "Remove Item", "Display History", "Display Inventory", "Missing Inventory"])

if action == "Add Item":
    def check_password():
        """Returns `True` if the user had a correct password."""

        def login_form():
            """Form with widgets to collect user information"""
            with st.form("Credentials"):
                st.text_input("Username", key="username")
                st.text_input("Password", type="password", key="password")
                st.form_submit_button("Log in", on_click=password_entered)

        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if st.session_state["username"] in st.secrets[
                "passwords"
            ] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets.passwords[st.session_state["username"]],
            ):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the username or password.
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False

        # Return True if the username + password is validated.
        if st.session_state.get("password_correct", False):
            return True

        # Show inputs for username + password.
        login_form()
        if "password_correct" in st.session_state:
            st.error("😕 User not known or password incorrect")
        return False


    if not check_password():
        st.stop()

    st.subheader("Add Item to Inventory")
    item_name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=1)
    size = st.number_input("Size (ft)", step=1)
    original_quantity = quantity

    if st.button("Add Item") and item_name not in st.session_state.inventory_list:
        add_item(item_name, quantity, size)
        st.success(f"Item '{item_name}' added to inventory.")

if action == "Update Item (Taking)":
    st.sidebar.subheader("Update Item Quantity")
    # item_name = st.sidebar.text_input("Item Name to Update")
    item_name = st.sidebar.selectbox("Item Name to Update", options=st.session_state.inventory_list)
    user = st.sidebar.text_input("Person's Name")
    quantity_taken = st.sidebar.number_input("Quantity Taken", min_value=1, max_value=40)
    date = st.sidebar.date_input("Date")

    if st.sidebar.button("Update Quantity (Taking)") and quantity_taken <= st.session_state.inventory[st.session_state.inventory['Item'] == item_name]["Quantity"].sum():
        update_quantity_taken(item_name, quantity_taken, user, date)
        st.success(f"Quantity for '{item_name}' updated.")

elif action == "Add Item Picture":
    def check_password():
        """Returns `True` if the user had a correct password."""

        def login_form():
            """Form with widgets to collect user information"""
            with st.form("Credentials"):
                st.text_input("Username", key="username")
                st.text_input("Password", type="password", key="password")
                st.form_submit_button("Log in", on_click=password_entered)

        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if st.session_state["username"] in st.secrets[
                "passwords"
            ] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets.passwords[st.session_state["username"]],
            ):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the username or password.
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False

        # Return True if the username + password is validated.
        if st.session_state.get("password_correct", False):
            return True

        # Show inputs for username + password.
        login_form()
        if "password_correct" in st.session_state:
            st.error("😕 User not known or password incorrect")
        return False


    if not check_password():
        st.stop()

    st.sidebar.subheader("Add Item Picture")
    item_name = st.sidebar.selectbox("Picture to be added to item", options=st.session_state.inventory_list)
    # File uploader widget
    image = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    # Check if an image has been uploaded
    if image is not None:
        # Display the uploaded image
        st.image(image, caption="Uploaded Image", use_column_width=True)
    if st.sidebar.button("Item Picture"):
        item_picture(item_name, image)
        st.sidebar.success(f"Item Picture added.")

elif action == "View Item":
    item_name = st.sidebar.selectbox("Picture to be added to item", options=st.session_state.inventory_list)
    view_item(item_name)

elif action == "Update Item (Returning)":
    st.sidebar.subheader("Update Item Quantity")
    item_name = st.sidebar.selectbox("Item Name to Update", options=st.session_state.inventory_list)
    user = st.sidebar.text_input("Person's Name")
    quantity_returned = st.sidebar.number_input("Quantity Taken", min_value=1, max_value=40)
    date = st.sidebar.date_input("Date")

    if st.sidebar.button("Update Quantity (Returning)"):
        update_quantity_returned(item_name, quantity_returned, user, date)
        st.success(f"Quantity for '{item_name}' updated.")

elif action == "Remove Item":
    def check_password():
        """Returns `True` if the user had a correct password."""

        def login_form():
            """Form with widgets to collect user information"""
            with st.form("Credentials"):
                st.text_input("Username", key="username")
                st.text_input("Password", type="password", key="password")
                st.form_submit_button("Log in", on_click=password_entered)

        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if st.session_state["username"] in st.secrets[
                "passwords"
            ] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets.passwords[st.session_state["username"]],
            ):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the username or password.
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False

        # Return True if the username + password is validated.
        if st.session_state.get("password_correct", False):
            return True

        # Show inputs for username + password.
        login_form()
        if "password_correct" in st.session_state:
            st.error("😕 User not known or password incorrect")
        return False


    if not check_password():
        st.stop()

    st.subheader("Remove Item from Inventory")
    item_name = st.selectbox("Item Name to Remove", options=st.session_state.inventory_list)

    if st.button("Remove Item"):
        remove_item(item_name)
        st.success(f"Item '{item_name}' removed from inventory.")

elif action == "Display History":
    def check_password():
        """Returns `True` if the user had a correct password."""

        def login_form():
            """Form with widgets to collect user information"""
            with st.form("Credentials"):
                st.text_input("Username", key="username")
                st.text_input("Password", type="password", key="password")
                st.form_submit_button("Log in", on_click=password_entered)

        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if st.session_state["username"] in st.secrets[
                "passwords"
            ] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets.passwords[st.session_state["username"]],
            ):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the username or password.
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False

        # Return True if the username + password is validated.
        if st.session_state.get("password_correct", False):
            return True

        # Show inputs for username + password.
        login_form()
        if "password_correct" in st.session_state:
            st.error("😕 User not known or password incorrect")
        return False


    if not check_password():
        st.stop()

    st.write("## Current History")
    st.dataframe(st.session_state.history)

elif action == "Display Inventory":
    st.write("## Current Inventory")
    st.dataframe(st.session_state.inventory)

elif action == "Missing Inventory":
    st.write("## MISSING Inventory")
    missing_inventory()

# Display the current inventory
display_inventory()