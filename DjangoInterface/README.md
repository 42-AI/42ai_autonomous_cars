- create / update database
``python manage.py migrate``

- create superuser
``python manage.py createsuperuser``

- run project
``python manage.py runserver``

and go to 127.0.0.1:8000 to test it localy

To use another IP address and serve IC_GUI on your network, simply add it to ALLOWED_HOSTS in settings.py and run with:
``python manage.py runserver IP``

Enjoy it !
----------