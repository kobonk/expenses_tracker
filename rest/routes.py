from flask import Flask, jsonify, render_template, request, make_response
from flask_cors import CORS
from flask_restful import Resource, Api

from expense.Category import Category
from expense.Tag import Tag
from expense.Expense import Expense, convert_date_string_to_timestamp
from storage.ExpensesPersisterFactory import ExpensesPersisterFactory
from storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory
from const import DATABASE_TYPE

app = Flask(__name__)
CORS(app)
api = Api(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.errorhandler(404)
def page_not_found(e):
    """Renders default 404 Page Not Found template"""
    return render_template("404.html"), 404

def get_expenses_retriever():
    return ExpensesRetrieverFactory.create(DATABASE_TYPE)

def get_expenses_persister():
    return ExpensesPersisterFactory.create(DATABASE_TYPE)

def convert_models_to_json(models):
    return list(map(lambda model: model.to_json(), models))

def group_expenses_by_months(expenses):
    grouped_expenses = {}

    if not expenses:
        return grouped_expenses

    for expense in expenses:
        month = expense.get_purchase_date_string()[0:7]

        if month in grouped_expenses:
            grouped_expenses[month].append(expense.to_json())
        else:
            grouped_expenses[month] = [expense.to_json()]

    return grouped_expenses

@app.route("/cost/<expense_name>", methods=["GET"])
def get_common_cost(expense_name):
    if request.method == "GET":
        expenses_retriever = get_expenses_retriever()

        return jsonify(expenses_retriever.retrieve_common_expense_cost(expense_name))

@app.route("/filter/<expense_name>", methods=["GET"])
def filter_expenses(expense_name):
    if request.method == "GET":
        expenses_retriever = get_expenses_retriever()
        expenses = expenses_retriever.filter_expenses(expense_name)

        if expenses:
            return jsonify(group_expenses_by_months(expenses))

@app.route("/expense", methods = ["POST"])
def add_expense():
    if request.method == "POST":
        json_data = request.get_json(force=True)
        expense = Expense.from_json(json_data)
        persister = get_expenses_persister()

        persister.add_expense(expense)

        return jsonify(expense.to_json())

@app.route("/expense/<expense_id>", methods = ["GET", "PATCH", "DELETE"])
def update_expense(expense_id):
    if request.method == "PATCH":
        persister = get_expenses_persister()
        expenses_retriever = get_expenses_retriever()
        expense = expenses_retriever.retrieve_expense(expense_id)

        if expense:
            json_data = request.get_json(force=True)

            if "date" in json_data:
                json_data["date"] = convert_date_string_to_timestamp(json_data["date"])

            expense = persister.update_expense(expense_id, json_data)

            return jsonify(expense.to_json())

    if request.method == "GET":
        expenses_retriever = get_expenses_retriever()
        expense = expenses_retriever.retrieve_expense(expense_id)

        if expense:
            return jsonify(expense.to_json())

@app.route("/expenses/<starting_month>/<number_of_months>", methods = ["GET"])
def retrieve_expenses(starting_month, number_of_months):
    """Returns a JSON with all Expenses for the selected period"""
    if request.method != "GET":
        return None

    retriever = get_expenses_retriever()
    expenses = retriever.retrieve_expenses(starting_month, int(number_of_months))
    expenses_as_json = convert_models_to_json(expenses)

    return jsonify(expenses_as_json)

@app.route("/months", methods = ["GET"])
def retrieve_months():
    """Returns a JSON array with all available months"""
    if request.method != "GET":
        return None

    retriever = get_expenses_retriever()
    months = retriever.retrieve_months()

    return jsonify(months)

@app.route("/tags", methods = ["GET"])
def retrieve_tags():
    """Returns a JSON array with all the tags from database"""
    if request.method != "GET":
        return None

    retriever = get_expenses_retriever()
    tags = retriever.retrieve_tags()

    return jsonify(convert_models_to_json(tags))

@app.route("/tags", methods = ["POST"])
def add_tags():
    if request.method == "POST":
        tags_payload = request.get_json(force=True)

        if not tags_payload:
            return jsonify([])

        tags = [Tag(None, tag) for tag in tags_payload]
        expenses_persister = get_expenses_persister()

        added_tags = expenses_persister.persist_tags(tags)

        return jsonify(convert_models_to_json(added_tags))

    return None

class ExpenseNames(Resource):
    def get(self, name):
        if not name:
            return jsonify([])

        expenses_retriever = get_expenses_retriever()
        expense_names = expenses_retriever.retrieve_similar_expense_names(name)

        return jsonify(expense_names)

class Categories(Resource):
    def get(self):
        expenses_retriever = get_expenses_retriever()
        categories = expenses_retriever.retrieve_categories()
        categories_as_json = convert_models_to_json(categories)

        return jsonify(categories_as_json)

    def post(self):
        json_data = request.get_json(force=True)
        category = Category.from_json(json_data)
        persister = get_expenses_persister()

        persister.add_category(category)

        expenses_retriever = get_expenses_retriever()
        categories = expenses_retriever.retrieve_categories()
        categories_as_json = convert_models_to_json(categories)

        return jsonify(categories_as_json)

class ExpenseSugestions(Resource):
    def get(self, month):
        if not month:
            return jsonify([])

        expenses_retriever = get_expenses_retriever()
        suggestions = expenses_retriever.retrieve_expense_suggestions(month)

        return jsonify(convert_models_to_json(suggestions))

api.add_resource(ExpenseNames, "/expense-names/<name>")
api.add_resource(Categories, "/categories")
api.add_resource(ExpenseSugestions, "/suggestions/<month>")
