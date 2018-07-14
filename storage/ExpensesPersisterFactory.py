from expenses_tracker.storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from expenses_tracker.storage.SqliteExpensesPersister import SqliteExpensesPersister

class ExpensesPersisterFactory:
    def create(self, type, database_path, expenses_table_name,
               categories_table_name):
        if type is "sqlite":
            return self.__create_sqlite_persister(database_path,
                                                  expenses_table_name,
                                                  categories_table_name)

    def __create_sqlite_persister(self, database_path, expenses_table_name,
                                  categories_table_name):
        connection_provider = SqliteDatabaseConnectionProvider(database_path)
        
        return SqliteExpensesPersister(expenses_table_name,
                                       categories_table_name,
                                       connection_provider)
