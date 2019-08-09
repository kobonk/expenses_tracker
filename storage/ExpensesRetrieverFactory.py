from const import DATABASE_TYPES
from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from storage.SqliteExpensesRetriever import SqliteExpensesRetriever
from validation_utils import validate_non_empty_string, validate_dict_keys

class ExpensesRetrieverFactory:
    @staticmethod
    def create(type, database_path, database_tables):
        validate_non_empty_string(type, "type")
        validate_non_empty_string(database_path, "database_path")
        validate_dict_keys(database_tables, "database_tables", [
            "expenses", "categories", "tags"
        ])

        expenses_table_name = database_tables["expenses"]
        categories_table_name = database_tables["categories"]

        if type is DATABASE_TYPES["sqlite"]:
            return ExpensesRetrieverFactory.__create_sqlite_retriever(
                                                    database_path,
                                                    expenses_table_name,
                                                    categories_table_name)

        return None

    @staticmethod
    def __create_sqlite_retriever(database_path, expenses_table_name,
                                  categories_table_name):
        connection_provider = SqliteDatabaseConnectionProvider(database_path)

        return SqliteExpensesRetriever(expenses_table_name,
                                       categories_table_name,
                                       connection_provider)
