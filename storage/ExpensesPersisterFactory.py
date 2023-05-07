from storage.MariaDbDatabaseConnectionProvider import MariaDbDatabaseConnectionProvider
from storage.MariaDbExpensesPersister import MariaDbExpensesPersister
from storage.MariaDbQueryProvider import MariaDbQueryProvider
from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from storage.SqliteExpensesPersister import SqliteExpensesPersister
from storage.SqliteDbQueryProvider import SqliteDbQueryProvider
from validation_utils import validate_non_empty_string
from const import DATABASE_TABLES, DATABASE_TYPES, FULL_DATABASE_PATH

class ExpensesPersisterFactory:
    @staticmethod
    def create(type):
        validate_non_empty_string(type, "type")

        if type is DATABASE_TYPES["sqlite"]:
            return ExpensesPersisterFactory.__create_sqlite_persister()

        if type is DATABASE_TYPES["mariadb"]:
          return ExpensesPersisterFactory.__create_mariadb_persister()

    @classmethod
    def __create_sqlite_persister(cls):
        return SqliteExpensesPersister(
            DATABASE_TABLES,
            SqliteDatabaseConnectionProvider(
                FULL_DATABASE_PATH,
                DATABASE_TABLES
            ),
            SqliteDbQueryProvider()
        )

    @classmethod
    def __create_mariadb_persister(cls):
        return MariaDbExpensesPersister(
            DATABASE_TABLES,
            MariaDbDatabaseConnectionProvider(DATABASE_TABLES),
            MariaDbQueryProvider()
        )
