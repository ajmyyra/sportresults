# Example Flask-Sqlalchemy application

This is an example application for storing results from a running competition, with support for split times.

## "Improvements"

See something in the code that could be made to perform better? Please don't. The whole idea of this application is to be non-performant, so it's easier to demonstrate the impact of DB caching, running workers in paraller with uWSGI/Gunicorn etc.

Changes that make the code run longer and slower, or taking up more memory are always needed. Improvements on code readability, structure etc are most welcome!
