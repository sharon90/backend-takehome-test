# Genetic Data Parser
## Install and run the code:
1. Assuming you have Python installed and venv already created, activate the venv and then, run 
    > pip install -r requirements.txt

    > python src/manage.py migrate

    > python src/manage.py runserver

## How to interact
Once the server is running and assuming it's running on http://127.0.0.1:8000/:

1. Create an individual with ID individual123 using the POST /individuals endpoint
   > curl -d "id=individual123" -H "Content-Type: application/x-www-form-urlencoded" -X POST "http://127.0.0.1:8000/individuals"
2. Show that the individual is present by querying the GET /individuals endpoint
   > curl "http://127.0.0.1:8000/individuals"
3. Upload some genetic data from a file to the individual via the POST /individuals/individual123/genetic-data endpoint
   > curl -d "file=*filepath*" -X POST "http://127.0.0.1:8000/individuals/individual123/genetic-data"
4. Show that all the data is queryable via the GET /individuals/individual123/genetic-data endpoint, and then show that the filtering works successfully by calling the same endpoint again, but this time filtering for only 2 variants present in the file
   > curl "http://127.0.0.1:8000/individuals/individual123/genetic-data"

   > curl "http://127.0.0.1:8000/individuals/individual123/genetic-data?variants=rs12345,rs24680"


## Video
   > https://www.loom.com/share/669aa2ab4dc94c48a0ad3b8ed1919162?sid=f583f3cc-55b4-44c1-b55f-3f30b71e9379