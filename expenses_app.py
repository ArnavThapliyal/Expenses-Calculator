import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime

logging.basicConfig(level=logging.INFO, format=' - Line %(lineno)d - %(asctime)s - %(levelname)s - %(message)s')

file_path = Path("Expenses.json")

# Load existing expenses
expenses = []
chart_window = None


def gui_save_and_exit():
    save_expenses()
    plt.close('all')  # Close all chart windows
    root.destroy()


# Load existing expenses from the file, or creats an fresh empty .json file.
def load_expenses():
    global expenses
    try:
        if file_path.exists():
            with file_path.open('r', encoding='utf-8') as file:
                loaded_expenses = json.load(file)
                for exp in loaded_expenses:
                    if 'date' not in exp:
                        exp['date'] = datetime.today().strftime("%Y-%m-%d")
                expenses = loaded_expenses
                logging.info(f"Successfully loaded {len(expenses)} expenses.")
        else:
            logging.info("Expenses file not found; starting with an empty list.")
    except Exception as e:
        logging.error(f"An error occurred while loading expenses: {e}")


# SAves the current expenses to the file.
def save_expenses():
    try:
        with file_path.open('w', encoding='utf-8') as file:
            json.dump(expenses, file, indent=4)
            logging.info("Expenses saved successfully.")
    except Exception as e:
        logging.error(f"Error writing to file: {e}")


# Adds a new expense with name, amount, category, and date.
def add_expense(name, amount, category, date):
    try:
        amount = float(amount)
        expense_date = datetime.strptime(date, '%Y-%m-%d').strftime("%Y-%m-%d")
        expenses.append({"name": name, "amount": amount, "category": category, "date": expense_date})
        save_expenses()
        logging.info(f"Added expense: {name}, Amount: {amount}, Category: {category}, Date: {expense_date}.")
        update_all_charts()  # Refresh charts with the latest data
    except ValueError:
        logging.error("Invalid amount or date entered.")


# Filters the expenses list based on the optional criteria of name and category.
def view_expenses(filter_name="", filter_category="All"):
    filtered = expenses
    if filter_category != "All":
        filtered = [exp for exp in filtered if exp['category'].lower() == filter_category.lower()]
    if filter_name:
        filtered = [exp for exp in filtered if filter_name.lower() in exp['name'].lower()]
    return filtered


# Display filtered entries with Proper serial number
def filter_expenses():
    chosen_category = category_combobox.get()
    filter_by_name = name_filter_entry.get()
    filtered_expenses = view_expenses(filter_name=filter_by_name, filter_category=chosen_category)
    
    for item in expense_tree.get_children():
        expense_tree.delete(item)

# enumerate will unpack each item into idx(adds serial no.) & exp
    for idx, exp in enumerate(filtered_expenses, start=1):
        expense_tree.insert('', tk.END, values=(idx, exp['name'], exp['amount'], exp['category'], exp['date']))

    update_total_expenses()  # Update total after filtering the expenses



# GUI for adding a new entry
def gui_add_expense():
    name = name_entry.get()
    amount = amount_entry.get()
    category = category_entry.get()
    date = date_entry.get()

    # Updates the categories and shows the total amount 
    if name and amount and category and date:
        add_expense(name, amount, category, date)
        category_combobox['values'] = ["All"] + list(set(exp["category"] for exp in expenses))
        filter_expenses() 
        update_total_expenses()  # Update total after adding an expense
        
        # resets the input fields (Dosen't wrok)
        name_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))  # Reset the date to today's date
    else:
        messagebox.showwarning("Input Error", "Please fill all fields.")


# Shows the (bar, pie, line) charts
def show_charts():
    global chart_window
    if len(expenses) == 0:
        return

    # Create a new window for the charts
    chart_window = tk.Toplevel(root)
    chart_window.title("Expense Charts")

    # Create a matplotlib figure
    fig = Figure(figsize=(9, 6))
    
    axes1 = fig.add_subplot(131)
    axes2 = fig.add_subplot(132)
    axes3 = fig.add_subplot(133)

    # Chart 1: Expenses by Category - Bar chart
    category_totals = defaultdict(float)
    for exp in expenses:
        category_totals[exp['category']] += exp['amount']
    
    categories, totals = zip(*sorted(category_totals.items()))
    axes1.bar(categories, totals, color='skyblue')
    axes1.set_title("By Category")
    axes1.set_xlabel('Category')
    axes1.set_ylabel('Total Amount')
    axes1.tick_params(axis='x', rotation=45)

    # Chart 2: Distribution by Category - Pai Chart
    axes2.pie(totals, labels=categories, autopct='%1.1f%%', startangle=140)
    axes2.set_title("Distribution by Category")
    axes2.axis('equal')

    # Chart 3: Trend Over Time - Line chart
    expenses_sorted = sorted(expenses, key=lambda x: x['date'])
    dates = [exp['date'] for exp in expenses_sorted]
    amounts = [exp['amount'] for exp in expenses_sorted]
    axes3.plot(dates, amounts, marker='o')
    axes3.set_title("Trend Over Time")
    axes3.tick_params(axis='x', rotation=45)
    axes3.set_xlabel('Date')
    axes3.set_ylabel('Amount')

    # Add the matplotlib figure to the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    chart_window.mainloop()


# Update all charts by re-showing them
def update_all_charts():
    # Close the previous chart window if it exists
    global chart_window
    if chart_window is not None:
        chart_window.destroy()

    # Show new charts
    show_charts()

# Calculates and updates the toal amount
def update_total_expenses():
    total = sum(exp['amount'] for exp in expenses)  # Sum all expense 
    total_label.config(text=f"Total Expenses: ${total:.2f}")  # Update the label text





# main function
# Load expenses when the module is loaded
load_expenses()

# Initialize GUI (Tkinter window)
root = tk.Tk()
root.title("Expense Tracker")

# The Styling of the UI components.
style = ttk.Style()
style.configure('TButton', padding=6)
style.configure('TEntry', padding=4)
style.configure('TLabel', padding=4)

# The fraim layout
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Following is the UI code for Expense Entry
name_label = ttk.Label(frame, text="Expense Name:")
name_label.grid(row=1, column=1, sticky=tk.W)
name_entry = ttk.Entry(frame)
name_entry.grid(row=1, column=2, sticky=(tk.W, tk.E))

amount_label = ttk.Label(frame, text="Amount:")
amount_label.grid(row=2, column=1, sticky=tk.W)
amount_entry = ttk.Entry(frame)
amount_entry.grid(row=2, column=2, sticky=(tk.W, tk.E))

category_label = ttk.Label(frame, text="Category:")
category_label.grid(row=3, column=1, sticky=tk.W)
category_entry = ttk.Entry(frame)
category_entry.grid(row=3, column=2, sticky=(tk.W, tk.E))

date_label = ttk.Label(frame, text="Date:")
date_label.grid(row=4, column=1, sticky=tk.W)
date_entry = ttk.Entry(frame)
date_entry.grid(row=4, column=2, sticky=(tk.W, tk.E))
date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))  # Default to today's date

# The Button for expense
add_button = ttk.Button(frame, text="Add Expense", command=gui_add_expense)
add_button.grid(row=5, column=1, columnspan=2)

# Filters by name and category
name_filter_label = ttk.Label(frame, text="Filter by Name:")
name_filter_label.grid(row=6, column=1, sticky=tk.W)

name_filter_entry = ttk.Entry(frame)
name_filter_entry.grid(row=6, column=2, sticky=(tk.W, tk.E))

category_combobox_label = ttk.Label(frame, text="Filter by Category:")
category_combobox_label.grid(row=7, column=1, sticky=tk.W)

category_combobox = ttk.Combobox(frame, values=["All"] + list(set(exp["category"] for exp in expenses)))
category_combobox.set("All")
category_combobox.grid(row=7, column=2)

# The button for filtering the entries
filter_button = ttk.Button(frame, text="Filter", command=filter_expenses)
filter_button.grid(row=8, column=1, columnspan=2)

# Expense List view
columns = ('Serial No.', 'Name', 'Amount', 'Category', 'Date')
expense_tree = ttk.Treeview(frame, columns=columns, show='headings')
for col in columns:
    expense_tree.heading(col, text=col)
expense_tree.grid(row=9, column=1, columnspan=2)


# Total expenses label
total_label = ttk.Label(frame, text="Total Expenses: $0.00")
total_label.grid(row=10, column=1, columnspan=2)


filter_expenses()




# Automatically open charts at startup
update_all_charts()

# For when the app is closed 
root.protocol("WM_DELETE_WINDOW", gui_save_and_exit)
root.mainloop()
