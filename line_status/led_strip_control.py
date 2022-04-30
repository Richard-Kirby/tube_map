import time
import random
import threading
import queue
import sqlite3
import os
import subprocess
import logging
# create logger
logger = logging.getLogger(__name__)

# PIGPIO is used to control digital IO
import pigpio

# WS2812 library
import rpi_ws281x

"""
This bit just gets the pigpiod daemon up and running if it isn't already.
The pigpio daemon accesses the Raspberry Pi GPIO.  
"""
p = subprocess.Popen(['pgrep', '-f', 'pigpiod'], stdout=subprocess.PIPE)
out, err = p.communicate()

if len(out.strip()) == 0:
    os.system("sudo pigpiod")
    time.sleep(3)



# Gamma correction makes the colours perceived correctly.
gamma8 = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]


# Class to  control the LED Strip based on the tweets.
class LedStationControl(threading.Thread):

    # Set up the strip with the passed parameters.  The Gamma correction is done by the library, so it gete passed in.
    def __init__(self, led_count, led_pin, type = None):

        # Init the threading
        threading.Thread.__init__(self)

        print("***** Starting LedStationControl in led_strip_control.py")

        self.strip = rpi_ws281x.PixelStrip(led_count, led_pin, gamma=gamma8, strip_type= type)

        # print("led count {}".format(led_count))
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

        self.tfl_status_dict = None
        self.tfl_status_queue = queue.Queue()

        # Set up the pi object to control the digital inputs/outputs.
        self.pi = pigpio.pi()

        # Patterns for each of the Services Status types - defines how the pixels change depending on line status.
        self.patterns = {
            'Good Service': [1, 1, 1, 1, 1, 1, 1, 1],
            'Severe Delays': [1, 0, 1, 0, 1, 0, 1, 0],
            'Minor Delays': [1, 0.8, 1, 0.8, 1, 0.8, 1, 0.8],
            'Closure': [1, 0, 0, 0, 1, 0, 0, 0],
            'default': [1, 0, 0, 0, 1, 0, 0, 0]
        }

        # Base colours for each line.
        self.line_colours = {
            'District': (51, 0, 0),
            'Circle': (75, 75, 35),
            'Hammersmith & City': (50, 85, 85),
            'Jubilee': (75, 75, 75),
            'Metropolitan': (0, 102, 51),
            'Bakerloo': (76, 153, 0),
            'Central': (0, 75, 0),
            'Piccadilly': (0, 0, 75),
            'Victoria': (75, 0, 153),
            'Northern': (60, 60, 60),
            'Waterloo & City': (60, 60, 60),
            "DLR": (60, 60, 60)
        }

        # Connnection to the DB.
        self.db_con = sqlite3.connect('lu_station.db', check_same_thread=False)

    # Populate pixels with the line's status.  This is called for each line.
    def populate_pixels(self, line, status):
        with self.db_con:
            print(line)
            #line_data = self.db_con.execute("SELECT * FROM Pixels WHERE Line == '{}'".format(line))
            line_data = self.db_con.execute("UPDATE Pixels SET status = '{}' WHERE Line == '{}'"
                                            .format(status, line))

            #print(line_data)

            updated= self.db_con.execute("SELECT * FROM Pixels")

            # self.db_con.cursor.close()

            for station in updated:
                print(station)
                #self.db_con.execute(
                #    "UPDATE Pixels SET status ='{}', Name = '{}', Line = '{}' where PixelNum =='{}' and StrandNum=='{}'"
                #    .format(status, station[1], line, , station[3]))

    # Not a main function - leaving it in case needed for debugging.
    def set_same_colour(self, colour, count= None):

        if (count == None):
            count = self.strip.numPixels()

        print(count)
        for i in range(count):
            self.strip.setPixelColor(i, rpi_ws281x.Color(*colour))
        self.strip.show()

    # Clears al the pixels.
    def pixel_clear(self):
        # Clear all the pixels
        for i in range(0, self.strip.numPixels()):  # Green Red Blue
            self.strip.setPixelColor(i, rpi_ws281x.Color(0, 0, 0))

        self.strip.show()

    # Set the strand number by setting the demux
    def set_pixel_strand(self, strand_num):

        # Set all to zero (strip 0)
        self.pi.write(13, 0)
        self.pi.write(6, 0)
        self.pi.write(5, 0)

        # Set the necessary bits high according to the strand number.
        if strand_num == 1:
            self.pi.write(13, 1)
        elif strand_num == 2:
            self.pi.write(13, 0)
            self.pi.write(6, 1)
        elif strand_num == 3:
            self.pi.write(13, 1)
            self.pi.write(6, 1)

    # Draw the status according to the line status.
    def draw_pixel_states(self):

        # Cycle through each strand (4 of)
        for i in range(4):
            self.set_pixel_strand(i)

            # There is only 1 logical strip - set them to black
            for j in range(100):
                self.strip.setPixelColor(j, rpi_ws281x.Color(0, 0, 0))

            # Some pixels are not used - only get those pixels that are populated.
            with self.db_con:
                query = "Select * from Pixels WHERE Status != 'No Status' AND StrandNum == '{}'".format(i)
                # print(query)
                pixel_data = self.db_con.execute(query)

            # Process each pixel, some pixels are over-written as they represent multiple lines.
            for pixel in pixel_data:
                service_type = pixel[5]
                # print(service_type)
                # print(pixel)

                # Set service type to default if not recognised.  Raise an error so it can be sorted out later.
                if service_type not in self.patterns.keys():
                    print("Error - don't recognise {}".format(service_type))
                    service_type = 'default'

                # Patterns use different pixel blinking frequencies to show state.
                colour = (int(self.patterns[service_type][0] * self.line_colours[pixel[2]][0]),
                          int(self.patterns[service_type][0] * self.line_colours[pixel[2]][1]),
                          int(self.patterns[service_type][0] * self.line_colours[pixel[2]][2]))

                # The actual setting of colour - as noted may be over-written by other lines.
                # print(pixel[4])
                self.strip.setPixelColor(pixel[4], rpi_ws281x.Color(*colour))


            # Shows the pixels once they are all ready.
            self.strip.show()
            time.sleep(0.01)

        # rotate to the next part of the pattern.
        for key in self.patterns.keys():
            last_item = self.patterns[key].pop()
            self.patterns[key].insert(0, last_item)


    def run(self):
        try:
            self.tfl_status_dict = None

            line_order = ['Circle', 'District', 'Hammersmith & City', 'Jubilee', 'Metropolitan', 'Central', 'Bakerloo',
                          'Northern', 'Piccadilly', 'Victoria', 'Waterloo & City']

            while True:
                # Get the latest commanded pixels from the queue
                while not self.tfl_status_queue.empty():
                    self.tfl_status_dict = self.tfl_status_queue.get_nowait()

                if self.tfl_status_dict is not None:
                    print(self.tfl_status_dict)

                    #self.pixel_clear()

                    for line in line_order:
                        if line in self.tfl_status_dict:
                            self.populate_pixels(line, self.tfl_status_dict[line])
                            print(line, self.tfl_status_dict[line])

                    for i in range(48):
                        self.draw_pixel_states()
                        time.sleep(0.5)

                    # Change the lines around so the one on top is modified.
                    # Important for shared stations as only on LED.
                    end = line_order.pop()
                    line_order.insert(0, end)

                    #time.sleep(2)

        except KeyboardInterrupt:
            logger.exception("Keyboard interrupt")

        except:
            raise

        finally:
            # Todo: Can't get back to 0 RPM when shutdown by Ctrl-C
            logger.error("finally")



if __name__ == "__main__":

    # LED strip configuration:
    LED_COUNT = 100      # Number of LED pixels.
    LED_PIN = 18      # GPIO pin connected to the pixels (must support PWM!).

    led_station_control = LedStationControl(LED_COUNT, LED_PIN, type = rpi_ws281x.SK6812_STRIP)
    led_station_control.start()


    sample_data=[
    {'Bakerloo': 'Good Service', 'Central': 'Good Service', 'Circle': 'Good Service', 'District': 'Good Service',
         'Hammersmith & City': 'Good Service', 'Jubilee': 'Good Service', 'Metropolitan': 'Good Service',
         'Northern': 'Good Service', 'Piccadilly': 'Good Service', 'Victoria': 'Good Service',
         'Waterloo & City': 'Good Service'},

    {'Bakerloo': 'Severe Delays', 'Central': 'Good Service', 'Circle': 'Severe Delays', 'District': 'Good Service',
     'Hammersmith & City': 'Minor Delays', 'Jubilee': 'Good Service', 'Metropolitan': 'Good Service',
     'Northern': 'Good Service', 'Piccadilly': 'Good Service', 'Victoria': 'Good Service',
     'Waterloo & City': 'Good Service'},

    {'Bakerloo': 'Severe Delays', 'Central': 'Good Service', 'Circle': 'Good Service', 'District': 'Severe Delays',
     'Hammersmith & City': 'Good Service', 'Jubilee': 'Good Service', 'Metropolitan': 'Good Service',
     'Northern': 'Good Service', 'Piccadilly': 'Good Service', 'Victoria': 'Good Service',
     'Waterloo & City': 'Good Service'},

    {'Bakerloo': 'Severe Delays', 'Central': 'Good Service', 'Circle': 'Good Service', 'District': 'Good Service',
     'Hammersmith & City': 'Minor Delays', 'Jubilee': 'Good Service', 'Metropolitan': 'Severe Delays',
     'Northern': 'Good Service', 'Piccadilly': 'Good Service', 'Victoria': 'Good Service',
     'Waterloo & City': 'Good Service'},

    {'Bakerloo': 'Severe Delays', 'Central': 'Good Service', 'Circle': 'Good Service', 'District': 'Good Service',
     'Hammersmith & City': 'Minor Delays', 'Jubilee': 'Severe Delays', 'Metropolitan': 'Good Service',
     'Northern': 'Good Service', 'Piccadilly': 'Good Service', 'Victoria': 'Good Service',
     'Waterloo & City': 'Good Service'},

    {'Bakerloo': 'Severe Delays', 'Central': 'Good Service', 'Circle': 'Good Service', 'District': 'Good Service',
     'Hammersmith & City': 'Severe Delays', 'Jubilee': 'Good Service', 'Metropolitan': 'Good Service',
     'Northern': 'Good Service', 'Piccadilly': 'Good Service', 'Victoria': 'Good Service',
     'Waterloo & City': 'Good Service'},

    {'Bakerloo': 'Severe Delays', 'Central': 'Good Service', 'Circle': 'Minor Delays', 'District': 'Minor Delays',
     'Hammersmith & City': 'Minor Delays', 'Jubilee': 'Minor Delays', 'Metropolitan': 'Minor Delays',
     'Northern': 'Good Service', 'Piccadilly': 'Good Service', 'Victoria': 'Good Service',
     'Waterloo & City': 'Good Service'}

    ]


    while True:
        for i in range(len(sample_data)):
            led_station_control.tfl_status_queue.put_nowait(sample_data[i])
            print(sample_data[i])
            time.sleep(20)
