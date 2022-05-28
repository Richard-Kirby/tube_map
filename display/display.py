#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import threading
import queue
import textwrap
import socket
#from pydub import AudioSegment
#from pydub.playback import play

from subprocess import run
import os

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

        self.line_abbrev = {'Hammersmith & City': 'H and C',
                            'Circle':'Circ',
                            'District': 'Dist',
                            'Jubilee':'Jub',
                            'Metropolitan':'Met',
                            'Central':'Cent',
                            'Bakerloo': 'Baker',
                            'Northern': 'North',
                            'Piccadilly':'Picc',
                            'Victoria':'Vic',
                            'Waterloo & City': 'W and C',
                            'DLR': 'DLR'}

        # Queue to receive time updates.
        self.tube_status_dict = None
        self.tube_status_strs = []
        self.time_queue = queue.Queue()
        self.special_msg_queue = queue.Queue()
        self.status_msg_queue = queue.Queue()

        self.speaker_host, self.speaker_port = "localhost", 9999

        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.speaker_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


        # Mind the gap message
        self.mind_the_gap_wav = '111613__doubletrigger__mind-the-gap.wav'

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


        # Get the message read out as well.
        # self.send_message_to_speaker(message)

        # Write to the display once image is ready.
        self.write_display()

    # Send a message to the program handling the audio speaker interface.
    def send_message_to_speaker(self, message):

        # Messages are sent to the speaker program via UDP.
        self.speaker_socket.sendto(bytes(message + "\n", "utf-8"), (self.speaker_host, self.speaker_port))


    # Displays ddte and time on the screen
    def display_time(self, time_to_display):
        self.image_wipe()

        # Create the date string.
        date_str = time.strftime("%a %d %m %Y", time_to_display)
        w, h = self.date_font.getsize(date_str)
        date_offset = int((self.disp.height - w)/2)  # Calculate offset to center text.

        self.draw_text((0, date_offset), self.date_font, date_str, self.image_black, rotation=90)

        time_str = time.strftime("%H:%M", time_to_display)
        w, h = self.time_font.getsize(time_str)
        time_offset = int((self.disp.height - w)/2)  # Calculate offset to center text
        self.draw_text((15, time_offset), self.time_font, time_str, self.image_red, rotation=90)

        # Work way through the non-Good Service statuses.  Pop and then append so next time a different status
        # will be displayed.
        # Use Red Font unless all is Good Service.
        display_status = None
        pops = 0
        image_colour = self.image_black

        if len(self.tube_status_strs)>0:
            print(self.tube_status_strs)
            while display_status is None and pops < len(self.tube_status_strs):
                top_status = self.tube_status_strs.pop(0)
                # print(top_status)
                service = top_status.split(": ")
                # print(service)
                if service[1] != 'Good Service':
                    display_status = top_status
                    image_colour = self.image_red

                pops = pops + 1
                self.tube_status_strs.append(top_status)
                print(pops, top_status, display_status, len(self.tube_status_strs))

            if display_status is None:
                display_status = "Good Service on All Lines"

        w, h = self.message_font.getsize(display_status)
        x_loc = self.disp.height - w

        # self.send_message_to_speaker(display_status)
        # play(self.mind_the_gap_wav)

        # basecmd = ["mplayer", "-ao", "alsa:device=bluetooth"]
        # myfile = "/nums/32.wav"
        #cmd_str = 'bash /home/pi/tube_map/sounds/google_voice.sh "mind the gap"'
        #print(cmd_str)
        #return_code = os.system(cmd_str)
        #print(return_code, cmd_str)


        self.draw_text((85, int(x_loc/2)), self.message_font, display_status, image_colour, rotation=90)



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
        # print("**", text)
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

                if not self.status_msg_queue.empty():
                    print("New status messages")
                    self.tube_status_dict = self.status_msg_queue.get_nowait()
                    self.tube_status_strs = []
                    for line in self.tube_status_dict:
                        status_str = '{}: {}'.format(self.line_abbrev[line], self.tube_status_dict[line])
                        # print(status_str)
                        self.tube_status_strs.append(status_str)

                # Display time and date
                if time_display_count % 3 == 0 and len(self.special_msgs) != 0:
                    msg = self.special_msgs.pop(0)
                    msg_to_display = time.strftime("%H:%M ", time_to_display) + msg
                    self.display_tfl_message(msg_to_display)
                    self.special_msgs.append(msg)

                else:
                    self.display_time(time_to_display)

                if time_to_display.tm_min % 15 == 0 and len(self.special_msgs) != 0:
                    self.send_message_to_speaker(time.strftime("%H:%M ", time_to_display))
                    for msg in self.special_msgs:
                        self.send_message_to_speaker(msg)

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
