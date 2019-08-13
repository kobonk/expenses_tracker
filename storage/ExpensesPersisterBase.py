class ExpensesPersisterBase():
    def add_expense(self, expense):
        raise NotImplementedError("Method not implemented!")

    def update_expense(self, expense_id, changes):
        raise NotImplementedError("Method not implemented!")

    def add_category(self, category):
        raise NotImplementedError("Method not implemented!")

    def persist_tags(self, tags):
        raise NotImplementedError("Method not implemented!")
