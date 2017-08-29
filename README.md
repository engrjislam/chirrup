Python 2.7 required.


Install all the required modules using pip (currently no requirements for default python 2.7 installation):
"pip install -r requirements.txt"

Run all the tests:
"python run_tests.py"

Create database using sql_dump files. Removes database if it already exists.
"python init_database.py"


Run api: 
"python resources.py"

Run client: 
"python chirrup.py"

Api runs on port 5000 and client on port 5001. Run both to use Chirrup