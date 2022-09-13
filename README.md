# pr_AgregateIt

That is an educational project that was developed by me durind advanced python course. This django web app can aggregate currency rates from variety of resources like banks and other aggregators.
App have API for easy access to curency rates. Mostly all part of project covered by unit tests. App uses nginx/uWSGI as web server, rabbitMQ as broker and Celery as task queue

One can start the project with make command:
<p><b>make server</b>

If one one wants to use docker, this two command should be used:
<p><b>make build</b>
<p><b>make runserver</b>

The full list of commands can be obtained from make file at the root of project
