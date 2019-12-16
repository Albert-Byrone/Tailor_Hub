# Insta-Copy 
## Author  
  
>[Albert-Byrone](https://github.com/Albert-Byrone/Insta-Copy.git)  
  
# Description  
This is a Django application that allow users to post pictures,like and comment on them whan having an account.
  
##  Live Link  
Click https://django-heroku-album.herokuapp.com/ to visit the webite
## Screenshots 
###### Home page

## User Story  
  
* Sign in to the application to start using.
* Upload my pictures to the application.  
* See my profile with all my pictures.
* Like a picture and leave a comment on it.
* Follow other users and see their pictures on my timeline.

## Setup and Installation  
To get the project .......  
  
##### Cloning the repository:  
 ```bash 
https://github.com/Albert-Byrone/Insta-Copy.git
```
##### Navigate into the folder and install requirements  
 ```bash 
cd INsta-Copy pip install -r requirements.txt 
```
##### Install and activate Virtual  
 ```bash 
- python3 -m venv virtual - source virtual/bin/activate  
```  
##### Install Dependencies  
 ```bash 
 pip install -r requirements.txt 
```  
 ##### Setup Database  
  SetUp your database User,Password, Host then make migrate  
 ```bash 
python manage.py makemigrations pictures 
 ``` 
 Now Migrate  
 ```bash 
 python manage.py migrate 
```
##### Run the application  
 ```bash 
 python manage.py runserver 
``` 
##### Running the application  
 ```bash 
 python manage.py server 
```
##### Testing the application  
 ```bash 
 python manage.py test 
```
Open the application on your browser `127.0.0.1:8000`.  
  
  
## Technology used  
  
* [Python3.6](https://www.python.org/)  
* [Django 1.11](https://docs.djangoproject.com/en/2.2/)  
* [Heroku](https://heroku.com)  
  
  
## Known Bugs  
* The follow and unfollow buttons are not working properly 
* The likes are not implememnted properly
  
## Contact Information   
If you have any question or contributions, please email me at [albertbyrone1677@gmail.com]  
## License 

* Copyright (c) 2019 **Albert Byrone**