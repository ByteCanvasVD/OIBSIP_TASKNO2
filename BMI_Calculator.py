import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BMI_Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")

        # Variables for weight and height
        self.weight_var = tk.DoubleVar()
        self.height_var = tk.DoubleVar()

        # Connect to SQLite database
        self.conn = sqlite3.connect("bmi_data.db")
        self.create_table_if_not_exists()

        # Create labels, entry widgets, and buttons
        tk.Label(root, text="Weight (kg):").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.weight_var).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(root, text="Height (m):").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.height_var).grid(row=1, column=1, padx=10, pady=10)

        tk.Button(root, text="Calculate BMI", command=self.calculate_bmi).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(root, text="View History", command=self.view_history).grid(row=3, column=0, columnspan=2, pady=10)

    def create_table_if_not_exists(self):
        # Create a table for BMI data if it does not exist
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS bmi_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weight REAL,
                    height REAL,
                    bmi REAL,
                    category TEXT,
                    timestamp DATETIME
                )
            ''')

    def calculate_bmi(self):
        try:
            # Get weight and height values
            weight = self.weight_var.get()
            height = self.height_var.get()

            # Check for valid input
            if not (0 < weight < 500) or not (0.5 < height < 2.5):
                raise ValueError("Weight and height must be within reasonable ranges.")

            # Calculate BMI
            bmi = weight / (height ** 2)

            # Classify BMI
            category = self.classify_bmi(bmi)

            # Save data to the database
            self.save_data(weight, height, bmi, category)

            # Display BMI result
            self.show_bmi_result(bmi, category)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_bmi_result(self, bmi, category):
        # Display the result
        result_text = f"Your BMI is: {bmi:.2f}\nYou are classified as: {category}"
        messagebox.showinfo("BMI Result", result_text)

    def classify_bmi(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

    def save_data(self, weight, height, bmi, category):
        # Save data to the database
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self.conn:
            self.conn.execute('''
                INSERT INTO bmi_data (weight, height, bmi, category, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (weight, height, bmi, category, timestamp))

    def view_history(self):
        # Retrieve data from the database
        with self.conn:
            cursor = self.conn.execute('''
                SELECT timestamp, weight, height, bmi, category
                FROM bmi_data
                ORDER BY timestamp DESC
            ''')
            data = cursor.fetchall()

        # Create a new window for history viewing
        history_window = tk.Toplevel(self.root)
        history_window.title("BMI History")

        # Create a treeview widget for displaying data
        tree = ttk.Treeview(history_window)
        tree["columns"] = ("Timestamp", "Weight", "Height", "BMI", "Category")
        tree.heading("#0", text="ID")
        tree.column("#0", width=0, stretch=tk.NO)  # Hide ID column

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)

        for row in data:
            tree.insert("", "end", values=row)

        tree.pack(expand=True, fill=tk.BOTH)

        # Add a button to show BMI trend analysis
        trend_button = tk.Button(history_window, text="Show BMI Trend", command=lambda: self.show_bmi_trend(data, history_window))
        trend_button.pack(pady=10)

    def show_bmi_trend(self, data, history_window):
        # Extract timestamps and BMIs from the data
        timestamps = [row[0] for row in data]
        bmis = [row[3] for row in data]

        # Plot BMI trend
        fig, ax = plt.subplots()
        ax.bar(timestamps, bmis, color='blue', alpha=0.7)
        ax.set(xlabel='Timestamp', ylabel='BMI', title='BMI Trend Analysis')
        ax.grid()

        # Create a new frame for the Matplotlib plot within history_window
        trend_frame = ttk.Frame(history_window)
        trend_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a Tkinter canvas for embedding the Matplotlib plot
        canvas = FigureCanvasTkAgg(fig, master=trend_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create a toolbar for the Matplotlib plot
        toolbar = tk.Frame(master=trend_frame)
        toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        toolbar_btn = tk.Button(master=toolbar, text="Quit", command=lambda: plt.close(fig))
        toolbar_btn.pack(side=tk.RIGHT)


if __name__ == "__main__":
    root = tk.Tk()
    app = BMI_Calculator(root)
    root.mainloop()

