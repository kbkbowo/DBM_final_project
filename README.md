# DBM_final_project

Repository of DBM final project of Group 6

Online deployment server at http://165.22.52.60:8000/  
It attempts to pull and deploy this repo every 10 secs. 

## Installing the requirements

```bash
pip install -r requirements.txt
```

## Activting the website 

run the following command to activate the webpage server

```bash
python manage.py migrate
python manage.py runserver
```

You should see an url saying that the website is hosted at localhost:xxxx, click to open the website. 
