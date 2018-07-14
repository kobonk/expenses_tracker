from flask import Flask, jsonify, render_template
from flask_restful import Resource, Api
from expenses_tracker.const import DATABASE_PATH, EXPENSES_TABLE_NAME
from expenses_tracker.storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory
 
app = Flask(__name__)
api = Api(app)
 
@app.route("/")
def home():
    return render_template("home.html")

class Expenses(Resource):
    def get(self):
        retriever_factory = ExpensesRetrieverFactory()
        expenses_retriever = retriever_factory.create("sqlite", DATABASE_PATH,
                                                    EXPENSES_TABLE_NAME)
        expenses = expenses_retriever.retrieve_expenses()
        expenses_as_json = self.__convert_expenses_to_json(expenses)

        return jsonify({ "results": list(expenses_as_json) })

    def __convert_expenses_to_json(self, expenses):
        return map(lambda expense: expense.to_json(), expenses)

api.add_resource(Expenses, "/expenses")
 
if __name__ == "__main__":
    app.run(debug=True)
