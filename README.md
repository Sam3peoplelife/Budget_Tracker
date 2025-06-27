# Budget Tracker

A simple Flask web application for personal finance management. Easily upload your transactions via CSV, manage your records, and visualize your spending and income with interactive charts.

## Features

- **CSV Import:** Upload transactions in bulk using a CSV file (`date`, `title`, `amount`, `category` columns required).
- **Transaction Management:** Add, update, and delete transactions directly from the web interface.
- **Filtering:** Filter transactions by category or date range.
- **Balance Tracking:** Instantly view your current balance, total income, and expenses.
- **Interactive Charts:** Visualize your spending and income trends with Chart.js.
- **Responsive Design:** Clean, mobile-friendly interface with custom icons.
- **SQLite Storage:** All data is stored locally in an SQLite database.

## Screenshots

### Manage Transactions
![Manage Transactions](https://github.com/user-attachments/assets/d13449ae-9342-44ed-934f-8eca7848f851)

### Current Balance
![Current Balance](https://github.com/user-attachments/assets/130fcd61-a880-4b6c-8ba7-a30751a9f662)

## Getting Started

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/Budget_Tracker.git
   cd Budget_Tracker
   ```

2. **Install dependencies:**
   ```
   pip install flask
   ```

3. **Run the app:**
   ```
   python app.py
   ```

4. **Open your browser:**  
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

## CSV Format

Your CSV file should have the following columns:

| date       | title         | amount | category  |
|------------|---------------|--------|-----------|
| 2024-06-01 | Grocery Store | -50.00 | groceries |
| 2024-06-02 | Salary        | 1000.0 | income    |

- **date:** Format `YYYY-MM-DD`
- **amount:** Use negative values for expenses, positive for income

## License

MIT