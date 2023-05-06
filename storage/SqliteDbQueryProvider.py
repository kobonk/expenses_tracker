from storage.DbQueryProvider import DbQueryProvider, DbQueryType

class SqliteDbQueryProvider(DbQueryProvider):
  """Creates Sqlite database queries"""

  def create_query(self, type: DbQueryType) -> str:
    if type == DbQueryType.SAVE_EXPENSE:
      return self.__create_save_expense_query()

    return super().create_query()

  def __create_save_expense_query(self):
    """Creates a query that saves an Expense in the database"""
    return "INSERT INTO expenses (name, cost, purchase_date, category_id) VALUES (?, ?, ?, ?)"
