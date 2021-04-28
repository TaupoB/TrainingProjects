import sqlite3
from random import randint

conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card(
            id INTEGER,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
            );""")

cur.close()


def luhn_digit(card_number): #without last digit
    digits = list(map(int, card_number))
    digits[::2] = list(map(lambda x: x * 2, digits[::2]))
    digits = map(lambda x: x if x < 10 else x - 9, digits)
    last_digit = (10 - sum(digits) % 10) % 10  # last "% 10" is for the case when sum = 10
    return str(last_digit)

def luhn_check(card_number):
    return luhn_digit(card_number[:-1]) == card_number[-1]

def balanceof(card_number):
    conn = sqlite3.connect("card.s3db")
    cur = conn.cursor()
    cur.execute("SELECT balance FROM card WHERE number = ?", (card_number,))
    t = cur.fetchone()
    cur.close()
    return(t[0])

def do_transfer(card):
    transfer_card = input("Enter card number: ")
    if luhn_check(transfer_card) == False:
        return print('Probably you made a mistake in the card number. Please try again!')
    conn = sqlite3.connect("card.s3db")
    cur = conn.cursor()
    cur.execute("SELECT number, balance FROM card WHERE number = ?", (transfer_card,))
    transfer_account = cur.fetchone()
    if transfer_account == None:
        return print('Such a card does not exist.')
    cur.close()
    summa = int(input('Enter how much money you want to transfer: '))
    if balanceof(card) < summa:
        return print('Not enough money!')
    add_income(transfer_card, summa)
    add_income(card, -summa)
    return print('Success!')


def add_income(card, income):
    prev_balance = balanceof(card)
    new_balance = prev_balance + income
    conn = sqlite3.connect("card.s3db")
    cur = conn.cursor()
    cur.execute("UPDATE card SET balance = ? WHERE number = ?", (new_balance, card))
    conn.commit()
    cur.close()


def close_account(card):
    conn = sqlite3.connect("card.s3db")
    cur = conn.cursor()
    cur.execute("DELETE FROM card WHERE number = ?;", (card,))
    conn.commit()
    conn.close()
    print('The account has been closed!')
def create_account():
    # create card number
    while True:
        id_ = randint(0, 999999999)
        card_number = f"400000{id_:09}"
        card_number += luhn_digit(card_number)
        # check if card number already exists

        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("SELECT number FROM card")
        account = cur.fetchall()
        if card_number not in account:
            break
    # create card pin
    pin = f"{randint(0, 9999):04}"

    # ------SQLite3 code -----------
    # conn.commit() ??????????
    cur.execute("INSERT INTO card(id, number, pin) VALUES (?, ?, ?);", (id_, card_number, pin))
    conn.commit()

    conn.close()
    # ----------------------------
    print("Your card has been created")
    print(f"You card number:\n{card_number}")
    print(f"Your card PIN: \n{pin}")
    print("\n")


def log_in():
    input_card = input('Enter your card number: ')
    input_pin = input('Enter your pin: ')
    print()
    # -------------------------
    conn = sqlite3.connect("card.s3db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM card WHERE number = ? AND pin = ?", (input_card, input_pin))

    account = cur.fetchone()

    conn.close()

    # -------------------------

    if account != None:
        print("You have successfully logged in!\n")
        while True:
            print("1. Balance",
                  "2. Add income",
                  "3. Do transfer",
                  "4. Close account",
                  "5. Log out",
                  "0. Exit", sep="\n")
            userinput = int(input())

            if userinput == 1: # Balance
                print(f'Balance: {balanceof(input_card)}')
            if userinput == 2: # Add income
                income = int(input('Enter income: '))
                add_income(input_card, income)
                print("Income was added!")
            if userinput == 3: # Do transfer
                do_transfer(input_card)
            if userinput == 4: #Close account
                close_account(input_card)
                break
            if userinput == 5: # Log out
                break
            if userinput == 0:
                return 0
    else:
        print("Wrong card number or PIN!\n")

# c  = sqlite3.connect("card.s3db")
# cur = c.cursor()
# cur.execute("SELECT * FROM card WHERE number = ? AND pin = ?", ("4000005509925427", "0103"))
# cur.execute("SELECT * FROM card")
# print(cur.fetchall())

# ----------start of loop--------
while True:
    print(
        "1. Create an account",
        "2. Log into account",
        "0. Exit", sep="\n")
    print()
    userinput = int(input())
    if userinput == 1:
        create_account()
    if userinput == 2:
        if log_in() == 0:  # go out of nested loop (function still executes)
            break

    if userinput == 0:
        break
# -----------end of loop--------
print("Bye!")

