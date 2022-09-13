# pr_AgregateIt

That is an educational project that was developed by me python course. This django web app can aggregate currency rates from variety of resources like banks or other aggregators.
App have API for easy access to curency rates. Mostly all part of project covered by unit tests. App uses nginx/uWSGI as web server, rabbitMQ as broker and Celery as task queue.
You can start the project with make command:
<p><b>make server</b></p>
If you want to use docker, use this commands in such sequence:
<br>
<br>
<p><b>make build</b></p>
<p><b>make runserver</b></p>
<br>
The full list of commands can be obtained from MAKEFILE at the root of project
