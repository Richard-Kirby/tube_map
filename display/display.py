#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import threading
import queue
import colorsys

import epaper

#from waveshare_epd import epd2in13bc  # Using the 2.13 inch Waveshare isplay

from PIL import Image, ImageDraw, ImageFont

import logging
# create logger
logger = logging.getLogger(__name__)

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 23
bus = 0 
device = 0 

# Clock Display Class - takes care of the display.
class ClockDisplay(threading.Thread):

    # Initialising - set up the display, fonts, etc.
    def __init__(self):
        threading.Thread.__init__(self)

        # Display Set up.
        self.disp = epaper.epaper('epd2in13bc').EPD()
        print("w x h", self.disp.width, self.disp.height)

        # init and Clear
        self.disp.init()
        self.disp.Clear()

        self.image_red = Image.new('1', (self.disp.width, self.disp.height), 255)  # 255: clear the frame
        self.draw_red = ImageDraw.Draw(self.image_red)
        self.image_black = Image.new('1', (self.disp.width, self.disp.height), 255)  # 255: clear the frame
        self.draw_black = ImageDraw.Draw(self.image_black)

        main_font = './display/HammersmithOne-Regular.ttf'

        self.date_font = ImageFont.truetype(main_font, 25)
        self.time_font = ImageFont.truetype(main_font, 70)
        #self.location_font = ImageFont.truetype(main_font, 30)
        #self.status_font = ImageFont.truetype(main_font, 20)

        # Queue to receive time updates.
        self.time_queue = queue.Queue()


    # Displays dte and time on the screen
    def display_time(self, time_to_display):

        # Clear the images each time to avoid over-writing issues.
        self.image_red = Image.new('1', (self.disp.width, self.disp.height), 255)  # 255: clear the frame
        self.draw_red = ImageDraw.Draw(self.image_red)
        self.image_black = Image.new('1', (self.disp.width, self.disp.height), 255)  # 255: clear the frame
        self.draw_black = ImageDraw.Draw(self.image_black)

        date_str = time.strftime("%a %d %m %Y", time_to_display)
        w, h = self.date_font.getsize(date_str)
        #print("date size", w, h)
        date_offset = int((self.disp.height - w)/2)  # Calculate offset to center text.

        #print("Disp width{} height{} date width{} date height{} offset{}".format(self.disp.width,
        #                                                                         self.disp.height,
        #                                                                         w, h, date_offset))

        self.draw_text((0, date_offset), self.date_font, date_str, self.image_black, rotation=90)

        time_str = time.strftime("%H:%M", time_to_display)
        w, h = self.time_font.getsize(time_str)
        #print("time size", w, h)
        time_offset = int((self.disp.height - w)/2)  # Calculate offset to center text
        #print("Disp width{} height{} time width{} time height{} offset{}".format(self.disp.width,
        #                                                                         self.disp.height,
        #                                                                         w, h, time_offset))

        self.draw_text((20, time_offset), self.time_font, time_str, self.image_red, rotation=90)

    # Writes the display frames to the display.
    def write_display(self):
        # display the frames
        self.disp.display(self.disp.getbuffer(self.image_black), self.disp.getbuffer(self.image_red))
        # time.sleep(3)

    # Draw text, allows for rotation.
    def draw_text(self, position, font, text, image_red_or_black, rotation=0):
        w, h = font.getsize(text)
        mask = Image.new('1', (w, h), color=1)
        draw = ImageDraw.Draw(mask)
        draw.text((0, 0), text, 0, font)
        mask = mask.rotate(rotation, expand=True)
        image_red_or_black.paste(mask, position)

    # Main process of the thread.  Waits for the criteria to be reached for the displaying on the screen.
    def run(self):

        while True:
            if not self.time_queue.empty():
                time_to_display = self.time_queue.get_nowait()

                # Create blank image for drawing.
                #self.image = Image.new("RGB", (self.disp.width, self.disp.height), "BLACK")
                #self.draw = ImageDraw.Draw(self.image)

                # Display time and date
                self.display_time(time_to_display)

                # Write to the display - should be ready.
                self.write_display()

            time.sleep(1)


if __name__ == '__main__':
    clock_display = ClockDisplay()
    clock_display.start()

    while True:
        current_time = time.localtime()

        clock_display.time_queue.put_nowait(current_time)
        time.sleep(15)
