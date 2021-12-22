# Requirements  
  
* Python (3.9.6) or Higher  
* Install all requirements using "pip install -r requirements.txt"

# Database Setup  
After installing the requirements ensure that you create a postgresql database, WITHOUT TABLES.

In order to properly communicate with the database you must create a .env file in the application's root directory and add the following information:  

HOST="The ip of your database server host."  
DATABASE="The name of your database."  
USER="Username for connecting to your database."  
PASSWORD="Password for connecting to the database."  
PORT="The port used by postgres."
  
# Usage  
Once the database is setup and your .env file has all the information in the above format you may run *app.py*.  

Find documentation at http://localhost:5000/swagger-ui




