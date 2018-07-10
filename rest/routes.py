from flask import Flask, render_template
from expenses_tracker.const import DATABASE_PATH, EXPENSES_TABLE_NAME
from expenses_tracker.storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory
 
app = Flask(__name__)      
 
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/expenses")
def expenses():
    retriever_factory = ExpensesRetrieverFactory()
    expenses_retriever = retriever_factory.create("sqlite", DATABASE_PATH,
                                                  EXPENSES_TABLE_NAME)
    expenses = expenses_retriever.retrieve_expenses()

    return render_template("expenses.html", expenses=expenses)
 
if __name__ == "__main__":
    app.run(debug=True)
