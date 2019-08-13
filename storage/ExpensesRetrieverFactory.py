from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from storage.SqliteExpensesRetriever import SqliteExpensesRetriever
from validation_utils import validate_non_empty_string
from const import DATABASE_TABLES, DATABASE_TYPES, SQLITE_DATABASE_PATH

class ExpensesRetrieverFactory:
    @staticmethod
    def create(type):
        validate_non_empty_string(type, "type")

        if type is DATABASE_TYPES["sqlite"]:
            return ExpensesRetrieverFactory.__create_sqlite_retriever()

        return None

    @staticmethod
    def __create_sqlite_retriever():
        conn_provider = SqliteDatabaseConnectionProvider(SQLITE_DATABASE_PATH)

        return SqliteExpensesRetriever(DATABASE_TABLES, conn_provider)
