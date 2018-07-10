import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DATABASE_PATH = r"{DIR_PATH}\dbs\expenses-tracker.db".format(**locals()).replace("\\", "\\\\")
EXPENSES_TABLE_NAME = "expenses"
