
from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import date

app = Flask(__name__)
DB = "finance.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            transaction_date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Personal Finance Manager</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f3f5fa;
    color: #222;
}
header {
    background: #172554;
    color: white;
    padding: 22px 6%;
}
header h1 { margin: 0; }
header p { margin-bottom: 0; color: #cbd5e1; }
.container {
    max-width: 1100px;
    margin: 30px auto;
    padding: 0 18px;
}
.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 18px;
}
.card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 3px 12px #0000000d;
}
.card p { color: #64748b; margin: 0; }
.card h2 { margin-bottom: 0; font-size: 27px; }
.green { color: #16a34a; }
.red { color: #dc2626; }
.blue { color: #2563eb; }
.section {
    background: white;
    padding: 24px;
    border-radius: 12px;
    margin-top: 24px;
    box-shadow: 0 3px 12px #0000000d;
}
form .fields {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
}
input, select {
    width: 100%;
    padding: 12px;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    margin-top: 7px;
}
label { font-size: 13px; color: #475569; }
button {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 7px;
    padding: 12px 20px;
    cursor: pointer;
    margin-top: 15px;
}
button:hover { background: #1d4ed8; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td {
    text-align: left;
    padding: 13px 8px;
    border-bottom: 1px solid #e2e8f0;
}
th { color: #64748b; font-size: 13px; }
.delete {
    background: #dc2626;
    padding: 7px 10px;
    margin: 0;
}
.bar {
    height: 12px;
    background: #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
    margin: 8px 0 16px;
}
.fill {
    height: 100%;
    background: #2563eb;
}
@media(max-width:600px) {
    table { font-size: 12px; }
    th, td { padding: 9px 4px; }
}
</style>
</head>
<body>

<header>
    <h1>Personal Finance Manager</h1>
    <p>Track your money. Manage your future.</p>
</header>

<div class="container">

    <div class="cards">
        <div class="card">
            <p>Total Income</p>
            <h2 class="green">₹{{ "%.2f"|format(income) }}</h2>
        </div>
        <div class="card">
            <p>Total Expenses</p>
            <h2 class="red">₹{{ "%.2f"|format(expenses) }}</h2>
        </div>
        <div class="card">
            <p>Available Balance</p>
            <h2 class="blue">₹{{ "%.2f"|format(balance) }}</h2>
        </div>
        <div class="card">
            <p>Total Transactions</p>
            <h2>{{ transactions|length }}</h2>
        </div>
    </div>

    <div class="section">
        <h2>Add Transaction</h2>
        <form action="/add" method="POST">
            <div class="fields">
                <div>
                    <label>Transaction Type</label>
                    <select name="transaction_type" required>
                        <option value="Expense">Expense</option>
                        <option value="Income">Income</option>
                    </select>
                </div>
                <div>
                    <label>Amount (₹)</label>
                    <input type="number" name="amount" min="0.01"
                    step="0.01" placeholder="Enter amount" required>
                </div>
                <div>
                    <label>Category</label>
                    <select name="category" required>
                        <option>Food</option>
                        <option>Travel</option>
                        <option>Shopping</option>
                        <option>Bills</option>
                        <option>Education</option>
                        <option>Health</option>
                        <option>Salary</option>
                        <option>Business</option>
                        <option>Other</option>
                    </select>
                </div>
                <div>
                    <label>Date</label>
                    <input type="date" name="transaction_date"
                    value="{{ today }}" required>
                </div>
                <div>
                    <label>Description</label>
                    <input type="text" name="description"
                    placeholder="What was this for?">
                </div>
            </div>
            <button type="submit">+ Add Transaction</button>
        </form>
    </div>

    <div class="section">
        <h2>Expense Breakdown</h2>
        {% if categories %}
            {% for category, amount in categories %}
                <p><strong>{{ category }}</strong> — ₹{{ "%.2f"|format(amount) }}</p>
                <div class="bar">
                    <div class="fill"
                    style="width: {{ (amount / max_category * 100) if max_category else 0 }}%">
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <p>No expenses recorded yet.</p>
        {% endif %}
    </div>

    <div class="section">
        <h2>Transaction History</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
            {% for t in transactions %}
                <tr>
                    <td>{{ t.transaction_date }}</td>
                    <td>{{ t.transaction_type }}</td>
                    <td>{{ t.category }}</td>
                    <td>{{ t.description }}</td>
                    <td class="{{ 'green' if t.transaction_type == 'Income' else 'red' }}">
                        ₹{{ "%.2f"|format(t.amount) }}
                    </td>
                    <td>
                        <form action="/delete/{{ t.id }}" method="POST"
                        onsubmit="return confirm('Delete this transaction?')">
                            <button class="delete">Delete</button>
                        </form>
                    </td>
                </tr>
            {% else %}
                <tr><td colspan="6">No transactions yet. Add your first transaction above.</td></tr>
            {% endfor %}
            </tbody>
        </table>
    </div>

</div>
</body>
</html>
"""


@app.route("/")
def home():
    conn = get_db()

    transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC"
    ).fetchall()

    income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE transaction_type='Income'"
    ).fetchone()[0]

    expenses = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE transaction_type='Expense'"
    ).fetchone()[0]

    category_data = conn.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE transaction_type='Expense'
        GROUP BY category
        ORDER BY total DESC
    """).fetchall()

    conn.close()

    categories = [(row["category"], row["total"]) for row in category_data]
    max_category = max((amount for _, amount in categories), default=0)

    return render_template_string(
        HTML,
        transactions=transactions,
        income=income,
        expenses=expenses,
        balance=income-expenses,
        categories=categories,
        max_category=max_category,
        today=date.today().isoformat()
    )


@app.route("/add", methods=["POST"])
def add_transaction():
    transaction_type = request.form["transaction_type"]
    amount = request.form["amount"]
    category = request.form["category"]
    description = request.form.get("description", "")
    transaction_date = request.form["transaction_date"]

    if transaction_type not in ("Income", "Expense"):
        return "Invalid transaction type", 400

    try:
        amount = float(amount)
        if amount <= 0:
            return "Amount must be greater than zero", 400
    except ValueError:
        return "Invalid amount", 400

    conn = get_db()
    conn.execute("""
        INSERT INTO transactions
        (transaction_type, amount, category, description, transaction_date)
        VALUES (?, ?, ?, ?, ?)
    """, (transaction_type, amount, category, description, transaction_date))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    conn = get_db()
    conn.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    initialize_db()
    app.run(debug=True)
