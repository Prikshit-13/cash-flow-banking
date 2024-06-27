import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel, Label, Entry, Button
import json
import os
from datetime import datetime
ACCOUNTS_FILE = "user_accounts.json"
TRANSACTIONS_FILE = "bank_transactions.json"
REQUESTS_FILE = "requests.json"
LOAN_REQUESTS_FILE = "loan_requests.json"
def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as file:
        json.dump(accounts, file, indent=4)

def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, "r") as file:
            return json.load(file)
    return []

def save_transactions(transactions):
    with open(TRANSACTIONS_FILE, "w") as file:
        json.dump(transactions, file, default=str, indent=4)

def load_requests():
    if os.path.exists(REQUESTS_FILE):
        with open(REQUESTS_FILE, "r") as file:
            return json.load(file)
    return []

def save_requests(requests):
    with open(REQUESTS_FILE, "w") as file:
        json.dump(requests, file, indent=4)

def load_loan_requests():
    if os.path.exists(LOAN_REQUESTS_FILE):
        with open(LOAN_REQUESTS_FILE, "r") as file:
            return json.load(file)
    return []

def save_loan_requests(loan_requests):
    with open(LOAN_REQUESTS_FILE, "w") as file:
        json.dump(loan_requests, file, indent=4)

def show_frame(frame):
    frame.tkraise()
    if frame != login_frame:
        frame_history.append(frame)

def go_back():
    if len(frame_history) > 1:
        frame_history.pop()  
        show_frame(frame_history[-1]) 

def create_user_account():
    username = username_entry.get()
    password = password_entry.get()
    
    if username and password:
        accounts = load_accounts()
        if username in accounts:
            messagebox.showerror("Error", "Username already exists!")
        else:
            accounts[username] = {"password": password, "balance": 0}
            save_accounts(accounts)
            messagebox.showinfo("Success", "Account created successfully!")
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Username and Password cannot be empty!")

# Function to handle admin login
def admin_login():
    show_frame(admin_password_frame)

def check_admin_password():
    password = admin_password_entry.get()
    
    if password == "andotra@13":
        messagebox.showinfo("Admin Login", "Login successful!")
        admin_password_entry.delete(0, tk.END)
        show_frame(admin_operations_frame)
    else:
        messagebox.showerror("Admin Login", "Incorrect password!")
        admin_password_entry.delete(0, tk.END)

def user_login():
    # Fetch current accounts
    accounts = load_accounts()
    user_list = "\n".join(f"ID: {idx} - {username}" for idx, username in enumerate(accounts.keys(), start=1))
    selected_user_id = simpledialog.askinteger("Select User", f"Select User by ID:\n{user_list}")
    
    if selected_user_id is not None and 1 <= selected_user_id <= len(accounts):
        selected_username = list(accounts.keys())[selected_user_id - 1]
        
        # Prompt for password
        password = simpledialog.askstring("Enter Password", f"Enter password for {selected_username}:")
        
        if password == accounts[selected_username]["password"]:
            messagebox.showinfo("Success", "Login successful!")
            show_frame(user_operations_frame)
            username_label.config(text=f"Welcome, {selected_username}!")
            global current_username
            current_username = selected_username
        else:
            messagebox.showerror("Error", "Invalid password!")
    else:
        messagebox.showerror("Error", "Invalid user selection!")

# Function to handle credit amount
def credit_amount():
    username = credit_username_entry.get()
    amount = credit_amount_entry.get()
    
    try:
        amount = float(amount)
        accounts = load_accounts()
        if username in accounts:
            accounts[username]["balance"] += amount
            save_accounts(accounts)
            # Log transaction
            log_transaction("credit", username, amount)
            messagebox.showinfo("Success", "Amount credited successfully!")
            credit_username_entry.delete(0, tk.END)
            credit_amount_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Username does not exist!")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount!")

# Function to handle debit amount
def debit_amount():
    username = debit_username_entry.get()
    amount = debit_amount_entry.get()
    
    try:
        amount = float(amount)
        accounts = load_accounts()
        if username in accounts:
            if accounts[username]["balance"] >= amount:
                accounts[username]["balance"] -= amount
                save_accounts(accounts)
                # Log transaction
                log_transaction("debit", username, amount)
                messagebox.showinfo("Success", "Amount debited successfully!")
                debit_username_entry.delete(0, tk.END)
                debit_amount_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Insufficient balance!")
        else:
            messagebox.showerror("Error", "Username does not exist!")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount!")

# Function to log transactions
def log_transaction(transaction_type, username, amount):
    transactions = load_transactions()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction = {
        "timestamp": timestamp,
        "type": transaction_type,
        "username": username,
        "amount": amount
    }
    transaction['index'] = len(transactions)  # Add index to transaction
    transactions.append(transaction)
    save_transactions(transactions)

# Function to view all transactions
def view_all_transactions():
    transactions = load_transactions()
    if transactions:
        transaction_list = "\n".join(
            f"{transaction['timestamp']} - {transaction['type'].capitalize()} by {transaction['username']} amount: {transaction['amount']}"
            for transaction in transactions
        )
        messagebox.showinfo("Bank Transactions", transaction_list)
    else:
        messagebox.showinfo("Bank Transactions", "No transactions yet.")

# Function to undo the last transaction
def undo_transaction():
    transactions = load_transactions()
    if transactions:
        last_transaction = transactions.pop()
        username = last_transaction['username']
        amount = last_transaction['amount']
        accounts = load_accounts()
        
        if last_transaction['type'] == 'credit':
            accounts[username]['balance'] -= amount
        elif last_transaction['type'] == 'debit':
            accounts[username]['balance'] += amount
        
        save_accounts(accounts)
        save_transactions(transactions)
        messagebox.showinfo("Undo", "Last transaction undone successfully!")
    else:
        messagebox.showerror("Error", "No transactions to undo!")

# Function to handle transaction request
def handle_requests():
    requests = load_requests()
    loan_requests = load_loan_requests()
    request_list = "\n".join(
        f"ID: {idx} - Transfer Request: {request['sender']} -> {request['recipient']} amount: {request['amount']}"
        for idx, request in enumerate(requests, start=1)
    ) + "\n\n" + "\n".join(
        f"ID: {idx} - Loan Request: {loan_request['username']} amount: {loan_request['amount']}"
        for idx, loan_request in enumerate(loan_requests, start=len(requests) + 1)
    )

    def approve_request(request_id):
        if request_id <= len(requests):
            request = requests[request_id - 1]
            # Approve transfer request
            transfer_money(request['sender'], request['recipient'], request['amount'])
            del requests[request_id - 1]
            save_requests(requests)
        else:
            loan_request_id = request_id - len(requests) - 1
            loan_request = loan_requests[loan_request_id]
            # Approve loan request
            add_balance(loan_request['username'], loan_request['amount'])
            del loan_requests[loan_request_id]
            save_loan_requests(loan_requests)
        messagebox.showinfo("Request Approved", "Request approved successfully")

    def disapprove_request(request_id):
        if request_id <= len(requests):
            del requests[request_id - 1]
            save_requests(requests)
        else:
            loan_request_id = request_id - len(requests) - 1
            del loan_requests[loan_request_id]
            save_loan_requests(loan_requests)
        messagebox.showinfo("Request Disapproved", "Request disapproved successfully")

    request_window = Toplevel(root)
    request_window.title("Requests")

    request_label = Label(request_window, text=request_list)
    request_label.pack(pady=20)

    request_id_label = Label(request_window, text="Enter request ID to approve or disapprove:")
    request_id_label.pack(pady=10)

    request_id_entry = Entry(request_window)
    request_id_entry.pack(pady=10)

    approve_button = Button(request_window, text="Approve", command=lambda: approve_request(int(request_id_entry.get())))
    approve_button.pack(pady=10)

    disapprove_button = Button(request_window, text="Disapprove", command=lambda: disapprove_request(int(request_id_entry.get())))
    disapprove_button.pack(pady=10)

# Function to manage user accounts (credit/debit)
def manage_user_accounts():
    # Fetch current accounts
    accounts = load_accounts()
    user_list = "\n".join(f"ID: {idx} - {username}" for idx, username in enumerate(accounts.keys(), start=1))
    selected_user_id = simpledialog.askinteger("Select User", f"Select User by ID:\n{user_list}")
    
    if selected_user_id is not None and 1 <= selected_user_id <= len(accounts):
        selected_username = list(accounts.keys())[selected_user_id - 1]
        
        # Prompt for action (credit or debit)
        action = messagebox.askquestion("Credit or Debit", f"Selected User: {selected_username}\nDo you want to credit or debit?")
        
        if action == "yes":  # Credit
            credit_amount = simpledialog.askfloat("Credit Amount", f"Enter credit amount for {selected_username}:")
            if credit_amount is not None and credit_amount > 0:
                accounts[selected_username]["balance"] += credit_amount
                save_accounts(accounts)
                log_transaction("credit", selected_username, credit_amount)
                messagebox.showinfo("Success", f"{credit_amount} credited to {selected_username}")
            else:
                messagebox.showerror("Error", "Invalid amount!")
        
        elif action == "no":  # Debit
            debit_amount = simpledialog.askfloat("Debit Amount", f"Enter debit amount for {selected_username}:")
            if debit_amount is not None and debit_amount > 0:
                if accounts[selected_username]["balance"] >= debit_amount:
                    accounts[selected_username]["balance"] -= debit_amount
                    save_accounts(accounts)
                    log_transaction("debit", selected_username, debit_amount)
                    messagebox.showinfo("Success", f"{debit_amount} debited from {selected_username}")
                else:
                    messagebox.showerror("Error", "Insufficientbalance!")
            else:
                messagebox.showerror("Error", "Invalid amount!")
    else:
        messagebox.showerror("Error", "Invalid user selection!")

# Function to check balance
def check_balance(username):
    accounts = load_accounts()
    balance = accounts[username]["balance"]
    messagebox.showinfo("Balance", f"Your balance is: {balance}")

# Function to transfer money
def transfer_money(sender, recipient, amount):
    accounts = load_accounts()
    if recipient in accounts:
        if accounts[sender]["balance"] >= amount:
            accounts[sender]["balance"] -= amount
            accounts[recipient]["balance"] += amount
            save_accounts(accounts)
            log_transaction("transfer", sender, amount, recipient)
            messagebox.showinfo("Success", "Money transferred successfully!")
        else:
            messagebox.showerror("Error", "Insufficient balance!")
    else:
        messagebox.showerror("Error", "Recipient username does not exist!")

# Function to view transactions
def view_transactions(username):
    transactions = load_transactions()
    user_transactions = [transaction for transaction in transactions if transaction["username"] == username]
    if user_transactions:
        transaction_list = "\n".join(
            f"{transaction['timestamp']} - {transaction['type'].capitalize()} {transaction['amount']}"
            for transaction in user_transactions
        )
        messagebox.showinfo("Transactions", transaction_list)
    else:
        messagebox.showinfo("Transactions", "No transactions yet.")

# Function to request money
def request_money():
    # Get sender username and amount
    sender_username = simpledialog.askstring("Enter Sender Username", "Enter sender username:")
    amount = simpledialog.askfloat("Enter Amount", "Enter amount to request:")
    
    if sender_username and amount:
        accounts = load_accounts()
        if sender_username in accounts:
            # Log request
            requests = load_requests()
            requests.append({"sender": sender_username, "recipient": current_username, "amount": amount})
            save_requests(requests)
            messagebox.showinfo("Success", "Request sent successfully!")
        else:
            messagebox.showerror("Error", "Sender username does not exist!")
    else:
        messagebox.showerror("Error", "Invalid input!")

# Function to request loan
def loan_request():
    # Get amount
    amount = simpledialog.askfloat("Enter Amount", "Enter amount to request:")
    
    if amount:
        # Log request
        loan_requests = load_loan_requests()
        loan_requests.append({"username": current_username, "amount": amount})
        save_loan_requests(loan_requests)
        messagebox.showinfo("Success", "Loan request sent successfully!")
    else:
        messagebox.showerror("Error", "Invalid input!")

# Create the main window
root = tk.Tk()
root.title("Cash Flow Minimizer [Banking]")
root.geometry("694x478")  # Set the window size to match the image size

# Load the background image
try:
    bg_image = tk.PhotoImage(file="C:/Users/ASUS/Downloads/ppp/Screenshot 2024-06-26 122735.png")
except Exception as e:
    print(f"Image loading error: {e}")

# Create a canvas and set the background image
canvas = tk.Canvas(root, width=694, height=478)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_image, anchor="nw")

# Create a container frame for stacking different frames
container = tk.Frame(root)
container.place(relx=0.5, rely=0.5, anchor="center")

# Create frames for different views
login_frame = tk.Frame(container)
admin_password_frame = tk.Frame(container)
admin_operations_frame = tk.Frame(container)
create_user_frame = tk.Frame(container)
user_management_frame = tk.Frame(container)
user_operations_frame = tk.Frame(container)

for frame in (login_frame, admin_password_frame, admin_operations_frame, create_user_frame, user_management_frame, user_operations_frame):
    frame.grid(row=0, column=0, sticky='nsew')

# History of frames to implement back navigation
frame_history = [login_frame]

# Populate login frame
login_heading = ttk.Label(login_frame, text="Cash Flow Minimizer [Banking]", font=("Helvetica", 18))
login_heading.pack(pady=20)

admin_button = ttk.Button(login_frame, text="Admin Login", command=admin_login, width=20)
admin_button.pack(pady=10)

user_button = ttk.Button(login_frame, text="User Login", command=user_login, width=20)
user_button.pack(pady=10)

# Populate admin password frame
admin_password_label = ttk.Label(admin_password_frame, text="Admin Password:")
admin_password_label.pack(pady=5)
admin_password_entry = ttk.Entry(admin_password_frame, show='*')
admin_password_entry.pack(pady=5)

admin_password_button = ttk.Button(admin_password_frame, text="Submit", command=check_admin_password, width=20)
admin_password_button.pack(pady=10)

back_button0 = ttk.Button(admin_password_frame, text="Back", command=go_back)
back_button0.pack(pady=10)

# Populate admin operations frame
admin_heading = ttk.Label(admin_operations_frame, text="Admin Operations", font=("Helvetica", 18))
admin_heading.pack(pady=20)

create_user_button = ttk.Button(admin_operations_frame, text="Create User Account", command=lambda: show_frame(create_user_frame))
create_user_button.pack(pady=10)

manage_accounts_button = ttk.Button(admin_operations_frame, text="Manage User Accounts", command=manage_user_accounts)
manage_accounts_button.pack(pady=10)

view_transactions_button = ttk.Button(admin_operations_frame, text="View Transactions", command=view_all_transactions)
view_transactions_button.pack(pady=10)

undo_button = ttk.Button(admin_operations_frame, text="Undo Transaction", command=undo_transaction)
undo_button.pack(pady=10)

requests_button = ttk.Button(admin_operations_frame, text="Requests", command=handle_requests)
requests_button.pack(pady=10)

previous_button = ttk.Button(admin_operations_frame, text="Previous", command=go_back)
previous_button.pack(pady=10)

# Populate create user frame
username_label = ttk.Label(create_user_frame, text="Username:")
username_label.pack(pady=5)
username_entry = ttk.Entry(create_user_frame)
username_entry.pack(pady=5)

password_label = ttk.Label(create_user_frame, text="Password:")
password_label.pack(pady=5)
password_entry = ttk.Entry(create_user_frame, show='*')
password_entry.pack(pady=5)

create_button = ttk.Button(create_user_frame, text="Create Account", command=create_user_account)
create_button.pack(pady=10)

back_button1 = ttk.Button(create_user_frame, text="Back", command=go_back)
back_button1.pack(pady=10)

# Populate user management frame
user_list_label = ttk.Label(user_management_frame, text="List of Users", font=("Helvetica", 18))
user_list_label.pack(pady=20)

manage_accounts_button2 = ttk.Button(user_management_frame, text="Manage User Accounts", command=manage_user_accounts)
manage_accounts_button2.pack(pady=10)

back_button2 = ttk.Button(user_management_frame, text="Back", command=go_back)
back_button2.pack(pady=10)
# Populate user operations frame
user_list_label = ttk.Label(user_operations_frame, text="List of Users", font=("Helvetica", 18))
user_list_label.pack(pady=20)

user_list = "\n".join(f"ID: {idx} - {username}" for idx, username in enumerate(load_accounts().keys(), start=1))
user_list_text = ttk.Label(user_operations_frame, text=user_list)
user_list_text.pack(pady=10)

check_balance_button = ttk.Button(user_operations_frame, text="Check Balance", command=lambda: check_balance(current_username))
check_balance_button.pack(pady=10)

transfer_money_button = ttk.Button(user_operations_frame, text="Transfer Money", command=transfer_money)
transfer_money_button.pack(pady=10)

view_transactions_button = ttk.Button(user_operations_frame, text="View Transactions", command=lambda: view_transactions(current_username))
view_transactions_button.pack(pady=10)

request_money_button = ttk.Button(user_operations_frame, text="Request Money", command=request_money)
request_money_button.pack(pady=10)

loan_request_button = ttk.Button(user_operations_frame, text="Loan Request", command=loan_request)
loan_request_button.pack(pady=10)

back_button = ttk.Button(user_operations_frame, text="Back", command=go_back)
back_button.pack(pady=10)
show_frame(login_frame)
root.mainloop()