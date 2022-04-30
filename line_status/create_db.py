import csv
import sqlite3

db_con = sqlite3.connect('lu_station.db')

# Database table definition
with db_con:
    db_con.execute("""
        CREATE TABLE Pixels(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Line TEXT,
        StrandNum INTEGER,
        PixelNum INTEGER,
        status TEXT
        );
    """)

# SQL command to create import the data.
sql = 'INSERT INTO Pixels (Name, Line, StrandNum, PixelNum) values(?, ?, ?, ?)'

data = []

# Open and process the CSV file that has the mapping between the strands/pixels and stations/Lines.
with open('Tube Map Data.csv', newline='') as tube_csv_file:
    tube_reader = csv.reader(tube_csv_file, delimiter=',', quotechar='|')
    for row in tube_reader:
        station_data = [row[0], row[1], row[2], row[3]]
        data.append(station_data)

# Populate data table with the imported CSV file.
with db_con:
    db_con.executemany(sql, data)

    pixels = db_con.execute("SELECT * FROM Pixels")

    for pixel in pixels:
        print(pixel)