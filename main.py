from rest.routes import app
from const import DEBUG_MODE

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)
