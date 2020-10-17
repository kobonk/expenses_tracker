from waitress import serve

from rest.routes import app
from const import DATABASE_TYPE, DEBUG_MODE
from storage.DatabaseConnectionProviderFactory import DatabaseConnectionProviderFactory

def run_server(debug = False):
    if debug:
        app.run(debug=True)

        return None

    print("Starting server at 0.0.0.0:5000...")
    serve(app, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    connection_provider = DatabaseConnectionProviderFactory.create(DATABASE_TYPE)

    connection_provider.ensure_necessary_tables_exist()
    run_server(DEBUG_MODE)
