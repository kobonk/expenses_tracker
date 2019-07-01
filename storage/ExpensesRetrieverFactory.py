from storage.SqliteDatabaseConnectionProvider import SqliteDatabaseConnectionProvider
from storage.SqliteExpensesRetriever import SqliteExpensesRetriever

class ExpensesRetrieverFactory:
    def create(self, type, database_path, expenses_table_name,
               categories_table_name):
        if type is "sqlite":
            return self.__create_sqlite_retriever(database_path,
                                                  expenses_table_name,
                                                  categories_table_name)

    def __create_sqlite_retriever(self, database_path, expenses_table_name,
                                  categories_table_name):
        connection_provider = SqliteDatabaseConnectionProvider(database_path)
        
        return SqliteExpensesRetriever(expenses_table_name,
                                       categories_table_name,
                                       connection_provider)
