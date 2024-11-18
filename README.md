# Simple_Hotel_Booking_System

Note: > It's one of my college requirements. I may or may not update it as I focus on learning other things.

## How to install and run
1. Install Python 3.6+ from the official website.
2. Git clone the repository or download the zip and unzip it. 
3. Make a make a virtual enviroment and Install dependencies 
4. Make migrations and runserver, you can access it using browser http://127.0.0.1:8000/

Guide for local deployment 
```
python3 -m venv env
source env/bin/activate            
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
## Features
* Booking Module 
* Payment Module 
* Contact Email Module. (Check django docs for setting up email api)
* Google maps api and Google account when creating an account. Insert API in (settings.py)
* Guest Ratings Sentiment-Classification (It classify ratings of guest whether it is postive or negative feedback with 89% accuracy level.)

## Todo :
- [ ] Create a function when guest check out  
- [ ] Make a ERD diagram, Flowchart, etc. 




