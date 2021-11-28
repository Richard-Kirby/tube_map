import time
import threading
import ntplib
import sys
import socket

# WS2812 library
import rpi_ws281x

import line_status
import tfl_status


# Main threaded Class for the displaying tube line status via a EL Wires.
class TubelineStatusDisplay(threading.Thread):

    def __init__(self):

        # Init the threading
        threading.Thread.__init__(self)

        # LED strip configuration:
        LED_COUNT = 100  # Number of LED pixels.
        LED_PIN = 18  # GPIO pin connected to the pixels (must support PWM!).

        self.led_station_control = line_status.LedStationControl(LED_COUNT, LED_PIN, type=rpi_ws281x.SK6812_STRIP)

        self.led_station_control.start()
        self.last_time_displayed = None
        self.display_interval_min = 1

        # check on the time sync.  If not synched yet, then wait and break out of the loop when detected or max loop
        # reached
        ntp_client = ntplib.NTPClient()

        # Give some maximum time to sync, otherwise crack on.
        for i in range (90):
            try:
                ntp_response = ntp_client.request('europe.pool.ntp.org', version=4)
                # print (ntp_response.offset)

                if ntp_response.offset < 2:
                    print("Synced @ {}" .format(i))
                    break

            except ntplib.NTPException:
                print("NTP Exception ", sys.exc_info())

            except socket.gaierror:
                print("socket.gaierror exception - can be a problem on first boot:", sys.exc_info())

            time.sleep(1)

        # TFL status - gets the data for the Tube Lines.
        self.tfl_status_thread = tfl_status.Tfl_Status()
        self.tfl_status_thread.daemon = True
        self.tfl_status_thread.start()

    # Main method that runs regularly in the thread.
    def run(self):

        while True:
            current_time = time.localtime()

            if self.tfl_status_thread.status_dictionary is not None:
                self.led_station_control.tfl_status_queue.put_nowait(self.tfl_status_thread.status_dictionary)

            time.sleep(5)


if __name__ == "__main__":

    print("main program")

    tubeline_status_display = TubelineStatusDisplay()
    tubeline_status_display.daemon = True
    tubeline_status_display.start()

    while True:
        time.sleep(10)
