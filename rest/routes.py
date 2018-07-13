from flask import Flask, jsonify, render_template
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
    expenses_as_json = convert_expenses_to_json(expenses)

    return jsonify({ "results": list(expenses_as_json) })

def convert_expenses_to_json(expenses):
    return map(lambda expense: expense.to_json(), expenses)
 
if __name__ == "__main__":
    app.run(debug=True)
