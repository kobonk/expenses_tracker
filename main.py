from rest.routes import app
from const import DATABASE_PATH, DATABASE_TYPE, DATABASE_TABLES
from storage.ExpensesRetrieverFactory import ExpensesRetrieverFactory

if __name__ == "__main__":
    retriever = ExpensesRetrieverFactory.create(DATABASE_TYPE, DATABASE_PATH,
                                                DATABASE_TABLES)

    retriever.ensure_necessary_tables_exist()

    app.run(debug=True)
