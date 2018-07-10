from expenses_tracker.storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from expenses_tracker.storage.SqliteExpensesRetriever import SqliteExpensesRetriever

class ExpensesRetrieverFactory:
    def create(self, type, database_path, table_name):
        if type is "sqlite":
            return self.__create_sqlite_expenses_retriever(database_path,
                                                           table_name)

    def __create_sqlite_expenses_retriever(self, database_path, table_name):
        connection_provider = SqliteDatabaseConnectionProvider(database_path)
        
        return SqliteExpensesRetriever(table_name, connection_provider)
