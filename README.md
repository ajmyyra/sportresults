# Intentionally slow-running Flask / SQLAlchemy application

This is an example application for storing results from a running competition, with support for split times.

## "Improvements"

See something in the code that could be made to perform better? Please don't. The whole idea of this application is to be non-performant, so it's easier to demonstrate the impact of DB caching, running workers in paraller with uWSGI/Gunicorn etc.

Changes that make the code run longer and slower, or taking up more memory are always needed. Improvements on code readability, structure etc are most welcome!

## Usage

Easiest way to run the project is through docker-compose.

```
git clone git@github.com:ajmyyra/sportresults.git
cd sportresults
docker-compose up
```

After docker-compose has started the application, it will be available on http://localhost:5000/ . Its HTTP API can be used with following examples:

- Create a new contestant: `curl -X POST -d '{ "name": "Teresa Test" }' -H 'Content-Type: application/json' http://localhost:5000/contestant`
- Begin a new result timing for the contestant: `curl -X POST -d '{ "competition": "Special Runnings" }' -H 'Content-Type: application/json' http://localhost:5000/competition/<contestant_id>`
- Post a split time from the race: `curl -X PUT -d '{ "description": "Highest point of the race" }' -H 'Content-Type: application/json' http://localhost:5000/competition/<contestant_id>/<result_id>`
- End the race at the finish line: `curl -X PUT -d '{ "description": "Finish line", "finish": "true" }' -H 'Content-Type: application/json' http://localhost:5000/competition/<contestant_id>/<result_id>`
- Fetch competition info..
* For all contestants: `curl http://localhost:5000/contestant`
* For a single contestant: `curl http://localhost:5000/contestant/<contestant_id>`
* For for a single race: `curl http://localhost:5000/contestant/<contestant_id>/<result_id>`

### More performance?

Currently the application is running with a single worker within Docker containers. See what you could by raising worker count, changing the database etc. 