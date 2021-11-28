import sqlite3

db_con = sqlite3.connect('lu_station.db')

with db_con:
    db_con.execute("""
        CREATE TABLE STATION(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Line TEXT,
        PixelNum INTEGER
        );
    """)

sql = 'INSERT INTO STATION (PixelNum, Name, Line) values(?, ?, ?)'
data = [
    (0, 'Amersham', 'Met'),
    (1, 'Chalfort and Latimer', 'Met'),
    (2,'Rickmansworth' , 'Met'),
    (3, 'Northwood', 'Met'),
    (4, 'Pinner', 'Met'),
    (5, 'Harrow-on-the-hill', 'Met'),
    (6, 'Northwick Park', 'Met'),
    (7, 'Preston Road', 'Met'),
    (8, 'Wembley Park', 'Met'),
    (9, 'Stanmore', 'Jub'),
    (10, 'Kingsbury', 'Jub'),
    (11, 'Wembley Park', 'Jub'),
    (12, 'Kilburn', 'Jub'),
    (13, 'Finchley Road', 'Met'),
    (14, 'Finchley Road', 'Jub'),
    (15, 'Swiss Cottage', 'Jub'),
    (16, 'Baker Street', 'Met'),
    (16, 'Baker Street', 'Circle'),
    (16, 'Baker Street', 'H&C'),
    (17, 'Euston Square', 'H&C'),
    (17, 'Euston Square', 'Met'),
    (17, 'Euston Square', 'Circle'),
    (18, 'Kings Cross', 'H&C'),
    (18, 'Kings Cross', 'Met'),
    (18, 'Kings Cross', 'Circle'),
    (19, 'Barbican', 'H&C'),
    (19, 'Barbican', 'Met'),
    (19, 'Barbican', 'Circle'),
    (20, 'Moorgate', 'H&C'),
    (20, 'Moorgate', 'Met'),
    (20, 'Moorgate', 'Circle'),
    (21, 'Liverpool Street', 'H&C'),
    (21, 'Liverpool Street', 'Met'),
    (21, 'Liverpool Street', 'Circle'),
    (22, 'Tower Hill', 'District'),
    (22, 'Tower Hill', 'Circle'),
    (23, 'Aldgate East', 'H&C'),
    (23, 'Aldgate East', 'District'),
    (33, 'Stepney Green', 'H&C'),
    (33, 'Stepney Green', 'District'),
    (24, 'Mile End', 'H&C'),
    (24, 'Mile End', 'District'),
    (25, 'West Ham', 'H&C'),
    (25, 'West Ham', 'District'),
    (26, 'East Ham', 'H&C'),
    (26, 'East Ham', 'District'),
    (28, 'Upminster', 'District'),
    (29, 'Elm Park', 'District'),
    (30, 'Upney', 'District'),
    (31, 'Plaistow', 'District'),
    (31, 'Plaistow', 'H&C'),
    (32, 'Bromley-by-Bow', 'District'),
    (32, 'Bromley-by-Bow', 'H&C'),
    (34, 'Aldgate', 'Met'),
    (34, 'Aldgate', 'Circle'),
    (35, 'Monument', 'Circle'),
    (35, 'Monument', 'District'),
    (38, 'Blackfriars', 'Circle'),
    (38, 'Blackfriars', 'District'),
    (36, 'Temple', 'Circle'),
    (36, 'Temple', 'District'),
    (37, 'Cannon Street', 'Circle'),
    (37, 'Cannon Street', 'District'),
    (39, 'Embankment', 'Circle'),
    (39, 'Embankment', 'District'),
    (41, 'Westminster', 'Circle'),
    (41, 'Westminster', 'District'),
    (42, 'South Kensington', 'Circle'),
    (42, 'South Kensington', 'District'),
    (43, 'Putney Bridge', 'District'),
    (44, 'Wimbledon', 'District'),
    (45, 'Wimbledon Park', 'District'),
    (46, 'West Brompton', 'District'),
    (47, 'Richmond', 'District'),
    (48, 'Ealing Broadway', 'District'),
    (49, 'Acton Town', 'District'),
    (50, 'Turnham Green', 'District'),
    (51, 'Kew Garden', 'District'),
    (52, 'Ealing Common', 'District'),
    (53, 'Gunnersby', 'District'),
    (54, 'Hammersmith', 'H&C'),
    (54, 'Hammersmith', 'Circle'),
    (55, 'Ladbroke Grove', 'H&C'),
    (55, 'Ladbroke Grove', 'Circle'),
    (56, 'High Street Kensington', 'Circle'),
    (56, 'High Street Kensington', 'District'),
    (57, 'Earls Court', 'District'),
    (58, 'Notting Hill Gate', 'Circle'),
    (58, 'Notting Hill Gate', 'District'),
    (59, 'Wood Lane', 'H&C'),
    (59, 'Wood Lane', 'Circle'),
    (60, 'Paddington', 'H&C'),
    (60, 'Paddington', 'Circle'),
    (61, 'Paddington', 'Circle'),
    (61, 'Paddington', 'District'),
    (62, 'Edgware Road', 'Circle'),
    (62, 'Edgware Road', 'H&C'),
    (62, 'Edgware Road', 'District'),
    (63, 'Royal Oak', 'H&C'),
    (63, 'Royal Oak', 'Circle'),
]

with db_con:
    db_con.executemany(sql, data)


# Create a table for each pixel.
with db_con:
    db_con.execute("""
        CREATE TABLE Pixels(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        PixelNum INTEGER,
        Station TEXT,
        Line TEXT,
        Status TEXT
        );
    """)

with db_con:
    for i in range(100):
        db_con.execute("INSERT INTO Pixels (PixelNum, Station, Line, Status) VALUES ({}, 'No Station', 'No Line', 'No Status')"
                       .format(i))
        db_con.commit()

    pixels = db_con.execute("SELECT * FROM Pixels")

    for pixel in pixels:
        print(pixel)
