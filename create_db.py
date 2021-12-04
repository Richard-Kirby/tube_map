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
    (0, 'Amersham', 'Metropolitan'),
    (1, 'Chalfort and Latimer', 'Metropolitan'),
    (2,'Rickmansworth' , 'Metropolitan'),
    (3, 'Northwood', 'Metropolitan'),
    (4, 'Pinner', 'Metropolitan'),
    (5, 'Harrow-on-the-hill', 'Metropolitan'),
    (6, 'Northwick Park', 'Metropolitan'),
    (7, 'Preston Road', 'Metropolitan'),
    (8, 'Wembley Park', 'Metropolitan'),
    (9, 'Stanmore', 'Jubilee'),
    (10, 'Kingsbury', 'Jubilee'),
    (11, 'Wembley Park', 'Jubilee'),
    (12, 'Kilburn', 'Jubilee'),
    (13, 'Finchley Road', 'Metropolitan'),
    (14, 'Finchley Road', 'Jubilee'),
    (15, 'Swiss Cottage', 'Jubilee'),
    (16, 'Baker Street', 'Metropolitan'),
    (16, 'Baker Street', 'Circle'),
    (16, 'Baker Street', 'Hammersmith & City'),
    (17, 'Euston Square', 'Hammersmith & City'),
    (17, 'Euston Square', 'Metropolitan'),
    (17, 'Euston Square', 'Circle'),
    (18, 'Kings Cross', 'Hammersmith & City'),
    (18, 'Kings Cross', 'Metropolitan'),
    (18, 'Kings Cross', 'Circle'),
    (19, 'Barbican', 'Hammersmith & City'),
    (19, 'Barbican', 'Metropolitan'),
    (19, 'Barbican', 'Circle'),
    (20, 'Moorgate', 'Hammersmith & City'),
    (20, 'Moorgate', 'Metropolitan'),
    (20, 'Moorgate', 'Circle'),
    (21, 'Liverpool Street', 'Hammersmith & City'),
    (21, 'Liverpool Street', 'Metropolitan'),
    (21, 'Liverpool Street', 'Circle'),
    (22, 'Tower Hill', 'District'),
    (22, 'Tower Hill', 'Circle'),
    (23, 'Aldgate East', 'Hammersmith & City'),
    (23, 'Aldgate East', 'District'),
    (33, 'Stepney Green', 'Hammersmith & City'),
    (33, 'Stepney Green', 'District'),
    (24, 'Mile End', 'Hammersmith & City'),
    (24, 'Mile End', 'District'),
    (25, 'West Ham', 'Hammersmith & City'),
    (25, 'West Ham', 'District'),
    (26, 'East Ham', 'Hammersmith & City'),
    (26, 'East Ham', 'District'),
    (27, 'Dagenham Heathway', 'District'),
    (28, 'Upminster', 'District'),
    (29, 'Elm Park', 'District'),
    (30, 'Upney', 'District'),
    (31, 'Plaistow', 'District'),
    (31, 'Plaistow', 'Hammersmith & City'),
    (32, 'Bromley-by-Bow', 'District'),
    (32, 'Bromley-by-Bow', 'Hammersmith & City'),
    (34, 'Aldgate', 'Metropolitan'),
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
    (40, 'Victoria','District'),
    (40, 'Victoria', 'Circle'),
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
    (54, 'Hammersmith', 'Hammersmith & City'),
    (54, 'Hammersmith', 'Circle'),
    (55, 'Ladbroke Grove', 'Hammersmith & City'),
    (55, 'Ladbroke Grove', 'Circle'),
    (56, 'High Street Kensington', 'Circle'),
    (56, 'High Street Kensington', 'District'),
    (57, 'Earls Court', 'District'),
    (58, 'Notting Hill Gate', 'Circle'),
    (58, 'Notting Hill Gate', 'District'),
    (59, 'Wood Lane', 'Hammersmith & City'),
    (59, 'Wood Lane', 'Circle'),
    (60, 'Paddington', 'Hammersmith & City'),
    (60, 'Paddington', 'Circle'),
    (61, 'Paddington', 'Circle'),
    (61, 'Paddington', 'District'),
    (62, 'Edgware Road', 'Circle'),
    (62, 'Edgware Road', 'Hammersmith & City'),
    (62, 'Edgware Road', 'District'),
    (63, 'Royal Oak', 'Hammersmith & City'),
    (63, 'Royal Oak', 'Circle'),
    (77, 'Baker Street', 'Jubilee'),
    (78, 'Euston Square', 'Circle'),
    (78, 'Euston Square','Hammersmith & City'),
    (78, 'Euston Square', 'Metropolitan'),

    (79, 'Baker Street', 'Circle'),
    (79, 'Baker Street', 'Hammersmith & City'),
    (79, 'Baker Street', 'Metropolitan'),

    (80, 'Bond Street', 'Jubilee'),

    (81, 'Embankmant', 'Circle'),
    (81, 'Embankmant', 'District'),

    (82, 'Monument', 'Circle'),
    (82, 'Monument', 'District'),

    (83, 'Blackfriars', 'Circle'),
    (83, 'Blackfriars', 'District'),

    (84, 'Moorgate', 'Circle'),
    (84, 'Moorgate', 'Hammersmith & City'),
    (84, 'Moorgate', 'Metropolitan'),

    (85, 'Farringdon', 'Circle'),
    (85, 'Farringdon', 'Hammersmith & City'),
    (85, 'Farringdon', 'Metropolitan'),

    (86, 'Canon Street', 'Circle'),
    (86, 'Canon Street', 'District'),

    (87, 'Liverpool Street', 'Circle'),
    (87, 'Liverpool Street', 'Hammersmith & City'),
    (87, 'Liverpool Street', 'Metropolitan'),

    (88, 'Tower Hill', 'Circle'),
    (88, 'Tower Hill', 'District'),

    (89, 'Aldgate East', 'Hammersmith & City'),
    (89, 'Aldgate East', 'District'),

    (90, 'Bakerloo Status', 'Bakerloo'),
    (91, 'Circle Status', 'Circle'),
    (92, 'Hammersmith & City Status', 'Hammersmith & City'),
    (93, 'Piccadilly Status', 'Piccadilly'),
    (94, 'Metropolitan Status', 'Metropolitan'),
    (95, 'Central Status', 'Central'),
    (96, 'District Status', 'District'),
    (97, 'Jubilee Status', 'Jubilee'),
    (98, 'Northern Status', 'Northern'),
    (99, 'Victoria Status', 'Victoria')
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
