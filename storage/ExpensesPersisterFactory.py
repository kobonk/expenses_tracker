from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from storage.SqliteExpensesPersister import SqliteExpensesPersister
from validation_utils import validate_non_empty_string
from const import DATABASE_TABLES, DATABASE_TYPES, FULL_DATABASE_PATH

class ExpensesPersisterFactory:
    @staticmethod
    def create(type):
        validate_non_empty_string(type, "type")

        if type is DATABASE_TYPES["sqlite"]:
            return ExpensesPersisterFactory.__create_sqlite_persister()

    @classmethod
    def __create_sqlite_persister(cls):
        return SqliteExpensesPersister(
            DATABASE_TABLES,
            SqliteDatabaseConnectionProvider(
                FULL_DATABASE_PATH,
                DATABASE_TABLES
            )
        )
