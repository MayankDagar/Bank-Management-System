import sys
import time
import random
import datetime
import prettytable
import mysql.connector

mydb = mysql.connector.connect(host="localhost",user="root",password="")
mycursor = mydb.cursor()

mycursor.execute("SHOW databases")
databases = mycursor.fetchall()
if ("bank",) not in databases:
    mycursor.execute("Create Database bank")
    mydb.commit()

mycursor.execute("USE bank")
mycursor.execute("SHOW TABLES")
tables = mycursor.fetchall()
if ("customers",) not in tables:
    mycursor.execute("CREATE TABLE customers(Account_no integer NOT NULL PRIMARY KEY,Name varchar(40) NOT NULL,DOB date,Email_id varchar(50),Gender char(1),Balance varchar(20),Account_type char(1))")
    mydb.commit()
if ("transactions",) not in tables:
    mycursor.execute("CREATE TABLE transactions(Account_no integer NOT NULL,Operation varchar(100),Amount DECIMAL(20,5),Date date,Time TIME)")
    mydb.commit()
if ("admin",) not in tables:
    mycursor.execute("CREATE TABLE admin(admin_name varchar(40),admin_id integer NOT NULL PRIMARY KEY,password varchar(30))")
    mydb.commit()
if ("userlogin",) not in tables:
    mycursor.execute("CREATE TABLE userlogin(Account_no integer PRIMARY KEY,Name varchar(40),passwords varchar(40))")
    mydb.commit()

default_admin = ('Sneh Rai',1,'sr2006')
mycursor.execute("SELECT * FROM admin")
admins_list = mycursor.fetchall()
if default_admin not in admins_list:
    mycursor.execute(f"INSERT INTO admin VALUES{default_admin}")
    mydb.commit()

def get_date():
    date = datetime.date.today()
    return str(date)

def wait():
    print("Wait...")
    time.sleep(2)

def get_time():
    hour = int(datetime.datetime.now().hour)
    minute = int(datetime.datetime.now().minute)
    second = int(datetime.datetime.now().second)
    time = f"{hour}:{minute}:{second}"
    return time

def generate_ac_no():
    mycursor.execute("SELECT Account_no FROM customers")
    ac_nos = []
    for i in mycursor:
        ac_nos.append(i)
    while True:
        k = random.randint(1,10000)
        if k not in ac_nos:
            return k

def check_login(name,password):
    mycursor.execute(f"SELECT Name,passwords FROM userlogin")
    logins = mycursor.fetchall()
    if (name,password) in logins:
        return True

def Create_Account():
    name = input("Enter the Account Holder Name: ")
    dob = input("Enter Date of Birth(yyyy-mm-dd): ")
    email = input("Enter Your Email ID: ")
    gender = input("Enter your Gender(M/F/O): ")
    account_type = input("Enter the Type of Account(C/S): ")
    password = input("Create your password(Must be strong): ")
    initial_amount = float(input("Enter the initial amount\n(Minimum 1000)\n: "))
    ac_no = generate_ac_no()
    details = (ac_no,name,dob,email,gender,initial_amount,account_type)
    date = get_date()
    time = get_time()
    transaction_details = (ac_no,"Account Created",initial_amount,date,time)
    login_details = (ac_no,name,password)
    mycursor.execute(f"INSERT INTO customers VALUES{details}")
    mycursor.execute(f"INSERT INTO transactions VALUES{transaction_details}")
    mycursor.execute(f"INSERT INTO userlogin VALUES{login_details}")
    mydb.commit()
    wait()
    print("\n\nAccount Created")
    print(f"Your Account number: {ac_no}")

def Close_Account():
    name = input("Enter the Account Holder Name: ")
    password = input("Enter your password: ")
    if check_login(name,password)==True:
        account_number = int(input("Enter Account Number: "))
        closing_account = input("Do you want to close your account(Y/N): ")
        if closing_account.upper()=="Y":
            date = get_date()
            time = get_time()
            mycursor.execute(f"SELECT Balance FROM customers where Account_no={account_number}")
            balance = mycursor.fetchone()
            transaction = (account_number,"Account Closed",balance[0],date,time)
            mycursor.execute(f"DELETE FROM customers WHERE Account_no={account_number}")
            mycursor.execute(f"DELETE FROM userlogin WHERE Account_no={account_number}")
            mycursor.execute(f"INSERT INTO transactions VALUES{transaction}")
            mydb.commit()
            wait()
            print("\n\nAccount Closed")

def Deposit_Amount():
    name = input("Enter user name: ")
    password = input("Enter your password: ")
    if check_login(name,password)==True:
        account_number = int(input("Enter Account Number: "))
        deposit_money = float(input("Enter the amount you want to Deposit: "))
        date = get_date()
        time = get_time()
        transaction_details = (account_number,"Amount Deposited",deposit_money,date,time)
        mycursor.execute(f"UPDATE customers SET Balance=Balance+{deposit_money} WHERE Account_no={account_number}")
        mycursor.execute(f"INSERT INTO transactions VALUES{transaction_details}")
        mydb.commit()
        wait()
        print("Transaction Successfull")
    else:
        print("Invalid Credentials")

def Withdraw_Amount():
    name = input("Enter user name: ")
    password = input("Enter your password: ")
    if check_login(name,password)==True:
        account_number = int(input("Enter Account Number: "))
        withdraw_money = float(input("Enter the amount you want to Withdraw: "))
        date = get_date()
        time = get_time()
        transaction_details = (account_number,"Amount Withdrawn",withdraw_money,date,time)
        mycursor.execute(f"UPDATE customers SET Balance=Balance-{withdraw_money} WHERE Account_no={account_number}")
        mycursor.execute(f"INSERT INTO transactions VALUES{transaction_details}")
        mydb.commit()
        wait()
        print("Transaction Successfull")
    else:
        print("Invalid Credentials")

def Balance_enquiry():
    name = input("Enter user name: ")
    password = input("Enter your password: ")
    if check_login(name,password)==True:
        account_number = int(input("Enter Account Number: "))
        mycursor.execute(f"SELECT Balance FROM customers WHERE Account_no={account_number}")
        balance = mycursor.fetchone()
        show_balance = prettytable.PrettyTable(["Balance"])
        show_balance.add_row(balance)
        wait()
        print(f"Your Balance is:\n{show_balance}")

def view_transaction_history():
    name = input("Enter user name: ")
    password = input("Enter your password: ")
    if check_login(name,password)==True:
        account_number = int(input("Enter Account Number: "))
        mycursor.execute(f"SELECT Operation,Amount,Date,Time FROM transactions WHERE Account_no={account_number}")
        transaction_history = mycursor.fetchall()
        transaction_table = prettytable.PrettyTable(["Operation","Amount","Date","Time"])
        for i in transaction_history:
            transaction_table.add_row(i)
        wait()
        print(f"Your Transaction History:\n{transaction_table}")

def transfer_money():
    name = input("Enter Your user name: ")
    password = input("Enter your password: ")
    if check_login(name,password)==True:
        account_number_sender = int(input("Enter Your Account Number: "))
        account_number_receiver = int(input("Enter Receiver's Account Number: "))
        amount = float(input("Enter amount you want to transfer: "))
        date = get_date()
        time = get_time()
        transaction_sender = (account_number_sender,f"Amount tranfered to Account NO {account_number_receiver}",amount,date,time)
        transaction_receiver = (account_number_receiver,f"Amount received from Account NO {account_number_sender}",amount,date,time)
        mycursor.execute(f"UPDATE customers SET Balance=Balance-{amount} WHERE Account_no={account_number_sender}")
        mycursor.execute(f"INSERT INTO transactions VALUES{transaction_sender}")
        mycursor.execute(f"UPDATE customers SET Balance=Balance+{amount} WHERE Account_no={account_number_receiver}")
        mycursor.execute(f"INSERT INTO transactions VALUES{transaction_receiver}")
        mydb.commit()
        wait()
        print("Amount Transfered")

def show_customer_details():
    mycursor.execute("SELECT * FROM customers")
    customers_details = mycursor.fetchall()
    customer_table = prettytable.PrettyTable(["Account_no","Name","DOB","Email_id","Gender","Balance","Account_type"])
    for i in customers_details:
        customer_table.add_row(i)
    print(customer_table)

def generate_admin_id():
    mycursor.execute("SELECT admin_id FROM admin")
    admin_ids = []
    for i in mycursor:
        admin_ids.append(i)
    while True:
        k = random.randint(1,10000)
        if k not in admin_ids:
            return k

def create_new_admin():
    name = input("Enter New Admin Name: ")
    admin_id = generate_admin_id()
    adm_password = input("Create New Admin password: ")
    new_admin_details =  (name,admin_id,adm_password)
    mycursor.execute(f"INSERT INTO admin VALUES{new_admin_details}")
    mydb.commit()
    wait()
    print(f"\nNew admin Created with admin id: {admin_id}")

def admin_login():
    name = input("Enter Your Admin Name: ")
    adm_id = int(input("Enter your Admin ID: "))
    adm_password = input("Enter your admin password: ")
    enter_tuple = (name,adm_id,adm_password)
    mycursor.execute("SELECT * FROM admin")
    for i in mycursor:
        if enter_tuple==i:
            return True
        else:
            return False

def money_bank():
    mycursor.execute("SELECT SUM(Balance) FROM customers;")
    money = mycursor.fetchone()
    money_table = prettytable.PrettyTable(["Total Money Deposited"])
    money_table.add_row(money)
    print(money_table)

print("="*100)
print("\t\t\t\tBANK MANAGEMENT SYSTEM\n\t\tMADE BY SNEH RAI(GROUP LEADER), AMAN, MAYANK DAGAR, AYUSHI VATS")
print("="*100)

while True:
    print("MAIN MENU")
    Identity = input("\nChoose your Identity\n1.CUSTOMER\n2.ADMIN\n(1/2): ")
    if int(Identity)==1:
        while True:
            print("\n\n1.CREATE NEW ACCOUNT")
            print("2.CLOSE AN ACCOUNT")
            print("3.DEPOSIT AMOUNT")
            print("4.WITHDRAW AMOUNT")
            print("5.BALANCE ENQUIRY")
            print("6.VIEW YOUR TRANSACTION DETAILS")
            print("7.SEND MONEY")
            print("8.EXIT")
            c = int(input("\nSelect your choice(1-9): "))
            if c==1:
                Create_Account()
            elif c==2:
                Close_Account()
            elif c==3:
                Deposit_Amount()
            elif c==4:
                Withdraw_Amount()
            elif c==5:
                Balance_enquiry()
            elif c==6:
                view_transaction_history()
            elif c==7:
                transfer_money()
            elif c==8:
                print("Thanks for using our BANK MANAGEMENT SYSTEM.\n")
                sys.exit()
            else:
                print("Invalid Input")
    elif int(Identity)==2:
        if admin_login()==True:
            while True:
                print("\n\n1.ALL ACCOUNT HOLDER LIST")
                print("2.TOTAL MONEY DEPOSITED IN BANK")
                print("3.CREATE NEW ADMIN")
                print("4.EXIT")
                c = int(input("Select your choice(1-2): "))
                if c==1:
                    show_customer_details()
                elif c==2:
                    money_bank()
                elif c==3:
                    create_new_admin()
                elif c==4:
                    print("Thanks for using our BANK MANAGEMENT SYSTEM.\n")
                    sys.exit()
                else:
                    print("Invalid Input")
        else:
            print("Invalid Admin details")
    else:
        print("Invalid Choice")