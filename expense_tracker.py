"""
Expense Tracker (console) - Save as expense_tracker.py

Features:
- Add expense (date, amount, category, description)
- View all expenses (nice table)
- Search / Filter (by category or date range)
- Monthly report (table + bar chart)
- Category report (table + pie chart)
- Export full CSV report
- Robust handling of missing/corrupted CSV headers
"""

import csv
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

FILE_NAME = "expenses.csv"

# Ensure CSV exists and has correct headers
def init_file():
    if not os.path.exists(FILE_NAME) or os.path.getsize(FILE_NAME) == 0:
        with open(FILE_NAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Amount", "Category", "Description"])

# Load data safely and fix header problems
def load_data():
    init_file()
    try:
        df = pd.read_csv(FILE_NAME, header=0)
        # If expected columns aren't present, reset file with headers
        expected = {"Date", "Amount", "Category", "Description"}
        if not expected.issubset(set(df.columns)):
            raise ValueError("Missing headers - resetting file")
        return df
    except Exception:
        # Try to reinitialize and return an empty DataFrame
        init_file()
        return pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])

# Save a DataFrame to CSV
def save_data(df):
    df.to_csv(FILE_NAME, index=False)

# Add new expense
def add_expense():
    date_input = input("Enter date (YYYY-MM-DD, leave empty for today): ").strip()
    if date_input == "":
        date_input = datetime.today().strftime("%Y-%m-%d")
    else:
        # basic validation
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD.")
            return

    try:
        amount = float(input("Enter amount (numbers only): ").strip())
    except ValueError:
        print("❌ Invalid amount.")
        return

    category = input("Enter category (e.g., Food, Travel, Shopping): ").strip().title() or "Other"
    description = input("Enter description: ").strip()

    # Append to CSV
    with open(FILE_NAME, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date_input, amount, category, description])

    print("✅ Expense added.\n")

# View all expenses (formatted)
def view_expenses():
    df = load_data()
    if df.empty:
        print("📭 No expenses found.\n")
        return
    # Attempt to parse dates for display
    df_display = df.copy()
    try:
        df_display["Date"] = pd.to_datetime(df_display["Date"], errors="coerce").dt.date
    except Exception:
        pass
    print("\n📒 All Expenses:")
    print("-" * 80)
    print("{:<12} {:>10} {:<15} {:<35}".format("Date", "Amount", "Category", "Description"))
    print("-" * 80)
    for _, r in df_display.iterrows():
        print("{:<12} {:>10} {:<15} {:<35}".format(
            str(r["Date"]), str(r["Amount"]), str(r["Category"]), str(r["Description"])[:35]
        ))
    print("-" * 80 + "\n")

# Search / filter expenses
def search_expenses():
    df = load_data()
    if df.empty:
        print("📭 No expenses found.\n")
        return

    print("Search options:")
    print("1) By category")
    print("2) By date range")
    choice = input("Choose (1/2): ").strip()
    if choice == "1":
        cat = input("Enter category (case-insensitive): ").strip().title()
        result = df[df["Category"].astype(str).str.title() == cat]
    elif choice == "2":
        start = input("Start date (YYYY-MM-DD): ").strip()
        end = input("End date (YYYY-MM-DD): ").strip()
        try:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
            result = df[(df["Date"] >= start_dt) & (df["Date"] <= end_dt)]
        except Exception:
            print("❌ Date parsing failed. Use YYYY-MM-DD.")
            return
    else:
        print("❌ Invalid choice.")
        return

    if result.empty:
        print("⚠ No matching records.\n")
    else:
        print("\n🔎 Filtered results:")
        print(result.to_string(index=False))
        print()

# Monthly report (table + optional chart)
def monthly_report(show_chart=True):
    df = load_data()
    if df.empty:
        print("📭 No expenses found.\n")
        return

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    if df.empty:
        print("⚠ No valid date records for report.\n")
        return

    monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
    print("\n📊 Monthly Report:")
    print("-" * 30)
    print("{:<10} {:>12}".format("Month", "Amount"))
    print("-" * 30)
    for m, amt in monthly.items():
        print("{:<10} {:>12}".format(str(m), amt))
    print()

    if show_chart and not monthly.empty:
        monthly.index = monthly.index.astype(str)
        monthly.plot(kind="bar", title="Monthly Expenses", xlabel="Month", ylabel="Amount")
        plt.tight_layout()
        plt.show()

# Category report (table + optional chart)
def category_report(show_chart=True):
    df = load_data()
    if df.empty:
        print("📭 No expenses found.\n")
        return

    cat = df.groupby(df["Category"])["Amount"].sum().sort_values(ascending=False)
    if cat.empty:
        print("⚠ No category data.\n")
        return

    print("\n📌 Category Report:")
    print(cat.to_string())
    print()

    if show_chart and not cat.empty:
        cat.plot(kind="pie", autopct='%1.1f%%', title="Expenses by Category")
        plt.ylabel("")
        plt.tight_layout()
        plt.show()

# Export full CSV copy
def export_report():
    df = load_data()
    if df.empty:
        print("📭 No expenses to export.\n")
        return
    out = "expense_report_export.csv"
    df.to_csv(out, index=False)
    print(f"📂 Exported to {out}\n")

# Main menu
def main():
    init_file()
    while True:
        print("=== Expense Tracker ===")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Search / Filter Expenses")
        print("4. Monthly Report")
        print("5. Category Report")
        print("6. Export Report (CSV)")
        print("7. Exit")
        choice = input("Choose (1-7): ").strip()
        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            search_expenses()
        elif choice == "4":
            monthly_report(show_chart=True)
        elif choice == "5":
            category_report(show_chart=True)
        elif choice == "6":
            export_report()
        elif choice == "7":
            print("Goodbye 👋")
            break
        else:
            print("Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()
