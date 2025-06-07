from datetime import datetime

# This module provides classes for reading and writing tabular data in CSV format
import csv

# To check if the file exists
import os

# A List to store all expenses.
expenses = []

# Initializing monthly_budget globally
monthly_budget = 0.0 

# Define the filename for storing expenses
EXPENSES_FILE = 'expenses.csv'

# --- Placeholder Functions ---
def addExpense():
    """This function handles adding expenses."""
    print("\n--- Enter Expense Details ---")
    expectedDateFormat="%Y-%m-%d"
    while True:
        dateOfExpense=input("Enter Date of Expense: ")
        if dateFormatValidator(dateOfExpense,expectedDateFormat):
            break
        else:
            print("Invalid Date Format. Please use {expectedDateFormat}.")
    
    allowed_categories = ["Food", "Travel", "Utilities"]
    while True:
        category=input("Enter Category of Expense(Food/Travel/Utilities): ").strip()
        if category.title() in allowed_categories:
            category = category.title()
            break
        else:
            print(f"Invalid category. Please choose from: {', '.join(allowed_categories)}.")

    
    while True:
        try:
            amtSpend=float(input("Enter Amount Spend: "))
            if amtSpend < 0:
                print("Amount cannot be negative. Please enter a valid amount")
            else:
                break
        except ValueError:
            print("Invalid amount. Please enter a number.")
            
    description = input("Enter a brief description of the Expense: ").strip() 
    
    # Creating the expense dictionary
    expense_details = {
        'date': dateOfExpense,
        'category': category,
        'amount': amtSpend,
        'description': description
    }
    
    # Adding the individual Expense Details to global list
    expenses.append(expense_details)
    print("\nExpense added successfully!")
    print(expense_details)
    
def dateFormatValidator(dateformat,expectedFormat):
    try:
        datetime.strptime(dateformat, expectedFormat)
        return True
    except ValueError:
        return False
    

    

def viewExpenses():
    """This function handles viewing expenses."""
    if not expenses:
        print("No expenses recorded yet")
        return
    
    print("*----Your Recorded Expenses----*")
    required_fields=['date','category','amount','description']
    
    for i, expense in enumerate(expenses):
        print(f"\n--- Expense {i+1} ---")
        is_complete = True
        missing_fields = []
        
        #Validate Each required field
        for field in required_fields:
            if field not in expense or expense[field] is None or \
               (isinstance(expense[field], str) and not expense[field].strip()) or \
               (isinstance(expense[field], (int, float)) and expense[field] is None):
                is_complete = False 
                missing_fields.append(field)
                
        if is_complete:
            for key, value in expense.items(): 
                print(f"{key.replace('_', ' ').title()}: {value}")
            
        else:
            print(f"INCOMPLETE ENTRY: This expense is missing data for: {', '.join(missing_fields)}") 
            print("Raw Data (for debugging):", expense)
        print("-" * 20)     
    
def trackBudget():
    """This function handles tracking the budget."""
    global monthly_budget
    print("\n*--- Tracking Budget ---*")
    
    # Step 1: Set/Update Monthly Budget
    while True:
        try:
            budget_input=input(f"Enter the total amount you want to budget for the month (Current: ${monthly_budget:.2f}): $")
            if not budget_input.strip():
                print("Budget amount cannot be empty. Please enter a number.")
                continue
            new_budget=float(budget_input)
            
            if new_budget <= 0:
                print("Budget must be a positive amount. Please enter a valid number.")
            else:
                monthly_budget = new_budget
                print(f"Monthly budget set to: ${monthly_budget:.2f}")
                break
        except ValueError:
            print("Invalid input. Please enter a number for the budget.")

        
    # Step 2: Calculate total expenses       
    totalExpense=calculateTotalExpense()
    
    # Step 3: Compare total with budget and display results
    print(f"\n--- Budget Comparison ---")
    print(f"Your Monthly Budget: ${monthly_budget:.2f}")
    print(f"Total Expenses So Far: ${totalExpense:.2f}")
    
    if totalExpense > monthly_budget:
        over_budget_by = totalExpense - monthly_budget
        print(f"\n!!! WARNING: You have EXCEEDED your budget by ${over_budget_by:.2f} !!!")
    else:
        remaining_balance = monthly_budget - totalExpense
        print(f"\nYou have ${remaining_balance:.2f} left for the month.")
    
def calculateTotalExpense():
    print("\n--- Calculating Total Expense ---")
    if not expenses: 
        print("No expenses recorded yet to calculate total.")
        return 0.0 
    total_amount = 0.0
    
    for i, expense in enumerate(expenses):
        if 'amount' in expense and isinstance(expense['amount'], (int, float)):
            total_amount += expense['amount']
        else:
            print(f"Warning: Expense {i+1} has an invalid or missing amount and will be skipped in total calculation: {expense}")
    print(f"\nYour Total Expense is: ${total_amount:.2f}")
    return total_amount
    
    
def saveExpenses():
    """This function handles saving expenses."""
    global monthly_budget
    
    # CSV file headers
    fieldnames = ['date', 'category', 'amount', 'description', 'monthly_budget_at_save']
    
    try:
        with open(EXPENSES_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() 

            for expense in expenses:
                expense_to_write = expense.copy()
                expense_to_write['monthly_budget_at_save'] = monthly_budget
                writer.writerow(expense_to_write)
        print(f"\nExpenses and current budget saved to '{EXPENSES_FILE}' successfully!")
    except IOError as e:
        print(f"\nError saving expenses to file: {e}")

def loadExpenses():
    """This function Loads expenses and the monthly budget from a CSV file into the global lists."""
    global expenses
    global monthly_budget
    expenses.clear()
    
    if not os.path.exists(EXPENSES_FILE):
        print(f"'{EXPENSES_FILE}' not found. Starting with no previous expenses.")
        return

    try:
        with open(EXPENSES_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            if not reader.fieldnames:
                print(f"'{EXPENSES_FILE}' is empty or corrupted (no headers found).")
                return

            loaded_budget = 0.0 

            for row in reader:
                try:
                    row['amount'] = float(row['amount'])

                    if 'monthly_budget_at_save' in row and row['monthly_budget_at_save']:
                        loaded_budget = float(row['monthly_budget_at_save'])

                    expense_data = {
                        'date': row.get('date'),
                        'category': row.get('category'),
                        'amount': row.get('amount'),
                        'description': row.get('description')
                    }
                    expenses.append(expense_data)
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping corrupted row in CSV: {row} - Error: {e}")

            monthly_budget = loaded_budget
        print(f"Loaded {len(expenses)} expenses and budget ${monthly_budget:.2f} from '{EXPENSES_FILE}'.")
    except IOError as e:
        print(f"Error loading expenses from file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while loading expenses: {e}")

    
# --- Function for Continuation ---
def continueOrNotFn():
    while True:
        continueOrNot = input("Confirm whether you want to continue or not(N/Y) :").upper()
        if continueOrNot == "N":
            print("Completed Budget tracking actions for now")
            return False
        elif continueOrNot == "Y":
            return True 
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")

# --- Main Menu Logic ---
def interactiveMenu():
    while True: 
        print("**Personal Expense Tracker Options**")
        print("1.Add expense")
        print("2.View expenses")
        print("3.Track budget")
        print("4.Save expenses")
        print("5.Exit")

        chooseOption = input("Enter the action(Number or Name) you want to perform :")
        should_continue_loop = True 


        if chooseOption.lower() in("1","add expense"):
#             print("Inside A loop")
            addExpense()
        elif chooseOption.lower() in("2","view expenses"):
#             print("Inside B loop")
            viewExpenses()
        elif chooseOption.lower() in("3","track budget"):
#             print("Inside C loop")
            trackBudget()
        elif chooseOption.lower() in("4","save expenses"):
#             print("Inside D loop")
            saveExpenses()
        elif chooseOption.lower() in("5","exit"):
#             print("Inside E loop")
            print("Exiting the program.")
            should_continue_loop = False
            exit() 
        else:
            print("Invalid Input")

        if should_continue_loop:
            if not continueOrNotFn():
                break 
        else:
            break
        


# --- Entry Point of the Program ---
if __name__ == "__main__":
    loadExpenses()
    interactiveMenu()