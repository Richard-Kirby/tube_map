import time
import random
import threading
import queue
import sqlite3


import logging
# create logger
logger = logging.getLogger(__name__)

# WS2812 library
import rpi_ws281x

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

        self.strip = rpi_ws281x.PixelStrip(led_count, led_pin, gamma=gamma8, invert = False,
                    strip_type= type)

        print("led count {}".format(led_count))
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

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



if __name__ == "__main__":

    # LED strip configuration:
    LED_COUNT = 98      # Number of LED pixels.
    LED_PIN = 18      # GPIO pin connected to the pixels (must support PWM!).

    led_station_control = LedStationControl(LED_COUNT, LED_PIN, type = rpi_ws281x.SK6812_STRIP)

    import pigpio

    pi = pigpio.pi()

    #while True:
    #      pass


    while True:

        print("strip initialised")
        # All demux outputs ABC = 0
        pi.set_mode(13, pigpio.OUTPUT)
        pi.set_mode(6, pigpio.OUTPUT)
        pi.set_mode(5, pigpio.OUTPUT)

        pi.write(13, 0)
        pi.write(6, 0)
        pi.write(5, 0)

        print("Clear demux outputs")
        time.sleep(2)

        # Clear both strips to black. Strip 0 is blanked first, followed by strip 1.
        led_station_control.set_same_colour((0,0,0), LED_COUNT)
        time.sleep(0.1)

        # Strip 1
        pi.write(13, 1) # Switch strip 1 on, strip 0 off.
        led_station_control.set_same_colour((0,0,0), LED_COUNT)
        time.sleep(0.1)

        # Strip 2
        pi.write(13, 0) # Switch strip 1 on, strip 0 off.
        pi.write(6, 1) # Switch strip 1 on, strip 0 off.
        led_station_control.set_same_colour((0,0,0), LED_COUNT)
        time.sleep(0.1)

        pi.write(13, 0) # Strip 0 on again
        time.sleep(2)

        for i in range(LED_COUNT):

            # Strip 0 command
            for j in range (0, LED_COUNT):
                led_station_control.strip.setPixelColor(j, rpi_ws281x.Color(50, 50, 125))


            pi.write(13, 0)
            pi.write(6, 0)
            led_station_control.strip.show()
            print("strip 0 pixel ", i )

            time.sleep(0.1)

            # Strip 1 command
            for j in range (0, LED_COUNT):
                led_station_control.strip.setPixelColor(j, rpi_ws281x.Color(125, 25, 50))

            pi.write(13, 1)
            led_station_control.strip.show()
            print("strip 1 pixel ", i )

            # Strip 2 command
            for j in range (0, LED_COUNT):
                led_station_control.strip.setPixelColor(j, rpi_ws281x.Color(25, 125, 25))

            time.sleep(0.1)

            pi.write(13, 0)
            pi.write(6, 1)
            led_station_control.strip.show()
            print("strip 2 pixel ", i )

            time.sleep(0.1)
    #led_station_control.start()
