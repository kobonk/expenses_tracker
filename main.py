from rest.routes import app
from const import DATABASE_TYPE, DEBUG_MODE
from storage.DatabaseConnectionProviderFactory import DatabaseConnectionProviderFactory

if __name__ == "__main__":
    connection_provider = DatabaseConnectionProviderFactory.create(DATABASE_TYPE)

    connection_provider.ensure_necessary_tables_exist()
    app.run(debug=DEBUG_MODE)
