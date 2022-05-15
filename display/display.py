#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import threading
import queue
import textwrap

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
        # print("w x h", self.disp.width, self.disp.height)

        # init and Clear
        self.disp.init()
        self.disp.Clear()

        self.image_red = Image.new('1', (self.disp.width, self.disp.height), 255)  # 255: clear the frame
        self.draw_red = ImageDraw.Draw(self.image_red)
        self.image_black = Image.new('1', (self.disp.width, self.disp.height), 255)  # 255: clear the frame
        self.draw_black = ImageDraw.Draw(self.image_black)

        main_font = './display/HammersmithOne-Regular.ttf'

        self.date_font = ImageFont.truetype(main_font, 25)
        self.message_font = ImageFont.truetype(main_font, 16)
        self.time_font = ImageFont.truetype(main_font, 70)
        #self.location_font = ImageFont.truetype(main_font, 30)
        #self.status_font = ImageFont.truetype(main_font, 20)

        # Queue to receive time updates.
        self.time_queue = queue.Queue()
        self.special_msg_queue = queue.Queue()

    # clears the working image (not the screen)
    def image_wipe(self):
        # Clear the images each time to avoid over-writing issues.
        self.image_red = Image.new('1', (self.disp.width, self.disp.height), 255)  # 255: clear the frame
        self.draw_red = ImageDraw.Draw(self.image_red)
        self.image_black = Image.new('1', (self.disp.width, self.disp.height), 255)  # 255: clear the frame
        self.draw_black = ImageDraw.Draw(self.image_black)

    # Display TFL messages that indicate an issue - messages are not created for Good Service.
    def display_tfl_message(self, message):
        self.image_wipe()

        # Use text wrapper to get the different parts.
        parts = textwrap.wrap(message, width=25)

        # Calculate the height and width and adjust to print out the message.
        y_loc =0

        w, font_vert = self.message_font.getsize('hg')

        for part in parts:
            # print(part)
            w, h = self.message_font.getsize(part)
            x_loc = self.disp.height - w
            self.draw_text((y_loc, x_loc), self.message_font, part, self.image_red, rotation = 90)
            y_loc = y_loc + font_vert + 0

        # Write to the display once image is ready.
        self.write_display()

    # Displays ddte and time on the screen
    def display_time(self, time_to_display):
        self.image_wipe()

        #
        date_str = time.strftime("%a %d %m %Y", time_to_display)
        w, h = self.date_font.getsize(date_str)
        date_offset = int((self.disp.height - w)/2)  # Calculate offset to center text.

        self.draw_text((0, date_offset), self.date_font, date_str, self.image_black, rotation=90)

        time_str = time.strftime("%H:%M", time_to_display)
        w, h = self.time_font.getsize(time_str)
        time_offset = int((self.disp.height - w)/2)  # Calculate offset to center text
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
        print("**", text)
        # draw.text((0, 0), text, 0, font)
        draw.multiline_text((0, 0), text, fill=0, font= font, align='left', spacing = 1)
        mask = mask.rotate(rotation, expand=True)
        image_red_or_black.paste(mask, position)

    # Main process of the thread.  Waits for the criteria to be reached for the displaying on the screen.
    def run(self):

        # Special Message display
        time_display_count = 0

        while True:
            if not self.time_queue.empty():
                time_to_display = self.time_queue.get_nowait()
                time_display_count += 1

                # Gets any special messages from the TLF site - these indicate special conditions such as
                # delays or closures/suspensions, etc.
                if not self.special_msg_queue.empty():
                    self.special_msgs = self.special_msg_queue.get_nowait()

                # Display time and date
                if time_display_count % 3 == 0 and len(self.special_msgs) != 0:
                    msg_to_display = self.special_msgs.pop(0)
                    self.display_tfl_message(msg_to_display)
                    self.special_msgs.append(msg_to_display)

                else:
                    self.display_time(time_to_display)

                # Write to the display - should be ready.
                self.write_display()

            time.sleep(1)


if __name__ == '__main__':
    clock_display = ClockDisplay()
    clock_display.start()

    clock_display.display_tfl_message("123456789line1123456789line2123456789line3123456789line4123456789line5")


    #while True:
    #    current_time = time.localtime()
    #
    #    clock_display.time_queue.put_nowait(current_time)
    #    time.sleep(15)
