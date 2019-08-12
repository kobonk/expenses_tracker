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

        if type is DATABASE_TYPES["sqlite"]:
            return ExpensesRetrieverFactory.__create_sqlite_retriever(
                                            database_path, database_tables)

        return None

    @staticmethod
    def __create_sqlite_retriever(database_path, database_tables):
        connection_provider = SqliteDatabaseConnectionProvider(database_path)

        return SqliteExpensesRetriever(database_tables, connection_provider)
