# sparkifydb ETL

Sparkify is a music streaming app, who wants to analyze the data they've been collecting on songs and user activity.

Data is originally stored in json files, but in order to analyse it a postgres database was built with the following schema:
## Schema
- Fact Table: `songplays`
    - records in log data associated with song plays i.e. records with page NextSong
        - songplay_id
        - start_time
        - user_id
        - level
        - song_id
        - artist_id
        - session_id
        - location
        - user_agent

- Dimension Tables:
    - `users` - users in the app
        - user_id
        - first_name
        - last_name
        - gender
        - level
    - `songs` - songs in music database
        - song_id
        - title
        - artist_id
        - year
        - duration
    - `artists` - artists in music database
        - artist_id
        - name
        - location
        - latitude
        - longitude
    - `time` - timestamps of records in songplays broken down into specific units
        - start_time
        - hour
        - day
        - week
        - month
        - year
        - weekday
### Running
The process that creates the schema can be run as follows:
```
python create_tables.py
```

## ETL
The logical process by which the data is uploaded to the database is composed by two steps:
- `create_tables.py`
    - `CREATE` schema
    - `DROP` drop schema
- `etl.py`
    - populates the entire database by using the data available in `/data/`
    
### Running
After the schema is built, the ETL process can be run as follows:
```
python etl.py
```

## Project requirements
Requirements can be found in `requirements.txt`

# Docker
A container for the whole application can be found in `docker/`

## Running
```
cd docker/
sudo docker-compose up
```