#
import time
import threading
import queue
import pigpio

"""
This bit just gets the pigpiod daemon up and running if it isn't already.
The pigpio daemon accesses the Raspberry Pi GPIO.  
"""
import subprocess
import os

p = subprocess.Popen(['pgrep', '-f', 'pigpiod'], stdout=subprocess.PIPE)
out, err = p.communicate()

if len(out.strip()) == 0:
    os.system("sudo pigpiod")
    time.sleep(3)

pi = pigpio.pi()


# Class to manage each LU line - responsible for displaying the state of the line.
class Line(threading.Thread):

    # Initialising - set up the display, fonts, etc.
    def __init__(self, name, abbrev, gpio):
        threading.Thread.__init__(self)

        self.name = name
        self.abbrev = abbrev
        self.gpio = gpio
        self.status_queue = queue.Queue()
        self.status = None
        print(self.name, self.abbrev, self.gpio)

    # Display the status of the line - done continuously.
    def run(self):

        while True:
            while not self.status_queue.empty():
                self.status = self.status_queue.get_nowait()

            # Not all lines may be assigned a GPIO
            if self.gpio is not None:
                print("***Status for {} is {} GPIO {}".format(self.name, self.status, self.gpio))

                if self.status is None:
                    pi.write(self.gpio, 0)

                elif self.status is "OK":
                    pi.write(self.gpio, 1)

                    time.sleep(1)

                # elif self.status is "SEV.D":

                else:  # ToDo - handle other states separately

                    dot_len = 0.5  # morse code length of .

                    # S in morse
                    for i in range(3):
                        pi.write(self.gpio, 1)
                        time.sleep(dot_len)
                        pi.write(self.gpio, 0)
                        time.sleep(dot_len)

                    time.sleep(dot_len)

                    # Morse O is three dashes (3 x length of dots)
                    for i in range(3):
                        pi.write(self.gpio, 1)
                        time.sleep(dot_len * 3)
                        pi.write(self.gpio, 0)
                        time.sleep(dot_len)

                    time.sleep(dot_len)

                    # S in morse
                    for i in range(3):
                        pi.write(self.gpio, 1)
                        time.sleep(dot_len)
                        pi.write(self.gpio, 0)
                        time.sleep(dot_len)

                    time.sleep(dot_len * 5)



# This class holds all the lines and sorts out the status passed to it.
class LineStatus:

    def __init__(self):

        self.line_list = [["Bakerloo", Line("Bakerloo", "BAK", None)],
                          ["Central", Line("Central", "CEN", None)],
                          ["Circle", Line("Circle", "CIR", None)],
                          ["District", Line("District", "DIS", 27)],
                          ["Hammersmith & City", Line("Hammersmith & City", "H&C", 17)],
                          ["Jubilee", Line("Jubilee", "JUB", None)],
                          ["Metropolitan", Line("Metropolitan", "Met", 26)],
                          ["Northern", Line("Northern", "NOR", None)],
                          ["Piccadilly", Line("Piccadilly", "Picc", None)],
                          ["Waterloo & City", Line("Waterloo & City", "W&C", None)],
                          ["Victoria", Line("Victoria", "Vic", None)]
                          ]

        self.abbrev_status = {"Good Service": "OK", "Part Closure": "P.CLS", "Special Service": "SPEC",
                              "Severe Delays": "SEV.D", "Minor Delays": "MIN.D", "Planned Closure": "CLS",
                              "Service Closed": "CLS", "Part Suspended": "P.SUS", "Suspended": "SUS"}

        for line in self.line_list:
            line[1].start()

    # Fill out the line status, using abbreviations as possible.
    def fill_line_status(self, tfl_status_dict):

        # Go through all the status in the tfl status dictionary, replace lines and status with abbrev
        for line in tfl_status_dict:

            # Go through searching for the matching line
            for i in range(len(self.line_list)):
                if line == self.line_list[i][0]:
                    # Check for Abbrev - use if available, otherwise don't change it (send full string).
                    if tfl_status_dict[line] in self.abbrev_status:
                        self.line_list[i][1].status_queue.put_nowait(self.abbrev_status[tfl_status_dict[line]])
                    else:
                        self.line_list[i][1].status_queue.put_nowait(tfl_status_dict[line])
                        self.line_list[i][1] = tfl_status_dict[line]
                    break


# Clock Display Class - takes care of the display.
class LineDisplay(threading.Thread):

    # Initialising - set up the display, fonts, etc.
    def __init__(self):
        threading.Thread.__init__(self)

        self.tfl_status_dict = None
        self.tfl_status_queue = queue.Queue()
        self.line_status = LineStatus()

    # Deals with the TfL Status, including getting the data and preparing the text.
    def handle_tfl_status(self):
        while not self.tfl_status_queue.empty():
            self.tfl_status_dict = self.tfl_status_queue.get_nowait()

        if self.tfl_status_dict is not None:
            self.line_status.fill_line_status(self.tfl_status_dict)

    # Main process of the thread.  Waits for the criteria to be reached for the displaying on the screen.
    def run(self):

        while True:
            self.handle_tfl_status()

            time.sleep(15)


if __name__ == '__main__':

    clock_display = ClockDisplay(1)
    clock_display.start()
