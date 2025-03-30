from src import create_app
from flask_cors import CORS

app = create_app()
CORS(app)

if __name__ == "__main__":
    # For running 
    # app.run(host="0.0.0.0", port=3000)

    # For develop
    app.run(debug=True)