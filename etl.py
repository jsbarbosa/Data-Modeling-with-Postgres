import glob
import os
from typing import Callable

import pandas as pd
import psycopg2

from sql_queries import *


def process_song_file(cur, filepath: str):
    """
    Function that reads the json file in `filepath` and adds the following contents to the `song` table:
    - song_id
    - title
    - artist_id
    - year
    - duration

    And the following data is added to the `artist` table:
    - artist_id
    - artist_name
    - artist_location
    - artist_latitude
    - artist_longitude

    Parameters
    ----------
    cur:
        cursor of the database connection
    filepath:
        path to the json file to read
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = list(df[['song_id', 'title', 'artist_id', 'year', 'duration']].values[0])
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_data = list(
        df[['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']].values[0]
    )
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath: str):
    """
        Function that reads the json file in `filepath` and adds the following contents to the `times` table:
        - start_time
        - hour
        - day
        - week
        - month
        - year
        - weekday

        The following data is added to the `user` table:
        - userId
        - firstName
        - lastName
        - gender
        - level

        And the following data is added to the `songplays` table:
        - userId
        - level
        - songid
        - artistid
        - sessionId
        - location
        - userAgent

        Parameters
        ----------
        cur:
            cursor of the database connection
        filepath:
            path to the json file to read
        """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page'] == 'NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'])

    # insert time data records
    time_data = {
        'start_time': t,
        'hour': t.dt.hour,
        'day': t.dt.day,
        'week': t.dt.dayofweek,
        'month': t.dt.month,
        'year': t.dt.year,
        'weekday': t.dt.weekday
    }

    column_labels = ['start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday']
    time_df = pd.DataFrame(time_data, columns=column_labels)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (
            index,
            pd.to_datetime(row['ts']),
            row['userId'],
            row['level'],
            songid,
            artistid,
            row['sessionId'],
            row['location'],
            row['userAgent']
        )
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath: str, func: Callable):
    """
    Function that list all json files inside the `filepath`, and executes the function `func` to each of the json files
    found

    Parameters
    ----------
    cur:
        cursor of the database connection
    conn:
        connection of the database
    filepath:
        path to the folder containing the json files to process
    func:
        function to apply to each of the files found
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
    Function that runs all subprocess in the ETL
    """

    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
