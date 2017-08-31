Python 2.7 required.

1.Install all the required modules using pip: "pip install -r requirements.txt"

2.Navigate to the root of the project.

3.Create database using sql_dump files. Removes database if it already exists. "python init_database.py"

4.Run api: "python -m api.resources.py"
Runs on port 5000. Only one server can be run at a time.

5.Run client: "python chirrup.py"
Start address in "http://localhost:5001/rooms_list.html".

6.Run all tests: "python run_tests.py".