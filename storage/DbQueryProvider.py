from enum import Enum
from typing import Tuple

SaveExpenseParams = Tuple[str, int, int, str]

class DbQueryType(Enum):
  SAVE_EXPENSE = 'SAVE_EXPENSE'

class DbQueryProvider():
  """Creates database queries"""

  def create_query(type: DbQueryType) -> str:
    """Returns a database query of requested type"""
    raise NotImplementedError("Method not implemented!")
