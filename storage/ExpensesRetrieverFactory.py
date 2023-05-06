from storage.ExpensesRetrieverBase import ExpensesRetrieverBase
from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from storage.SqliteExpensesRetriever import SqliteExpensesRetriever
from validation_utils import validate_non_empty_string
from const import DATABASE_TABLES, DATABASE_TYPES, FULL_DATABASE_PATH

class ExpensesRetrieverFactory:
    @staticmethod
    def create(type) -> ExpensesRetrieverBase:
        validate_non_empty_string(type, "type")

        if type is DATABASE_TYPES["sqlite"]:
            return ExpensesRetrieverFactory.__create_sqlite_retriever()

        return None

    @classmethod
    def __create_sqlite_retriever(cls):
        return SqliteExpensesRetriever(
            DATABASE_TABLES,
            SqliteDatabaseConnectionProvider(
                FULL_DATABASE_PATH,
                DATABASE_TABLES
            )
        )
