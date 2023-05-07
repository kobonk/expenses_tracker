from storage.MariaDbDatabaseConnectionProvider import MariaDbDatabaseConnectionProvider
from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from validation_utils import validate_non_empty_string
from const import DATABASE_TABLES, DATABASE_TYPES, FULL_DATABASE_PATH

class DatabaseConnectionProviderFactory:
    @staticmethod
    def create(type):
        validate_non_empty_string(type, "type")

        if type is DATABASE_TYPES["sqlite"]:
            return SqliteDatabaseConnectionProvider(
                FULL_DATABASE_PATH, DATABASE_TABLES)

        if type is DATABASE_TYPES["mariadb"]:
          return MariaDbDatabaseConnectionProvider(DATABASE_TABLES)

        return None
