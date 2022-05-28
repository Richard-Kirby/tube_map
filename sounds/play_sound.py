#from pydub import AudioSegment
#from pydub.playback import play

#import espeak

#announcement = AudioSegment.from_wav("111613__doubletrigger__mind-the-gap.wav")
#play(announcement)

#espeak.synth("mind the gap")

import os
import textwrap
import subprocess


import socketserver

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))

        msg_txt = data.decode('ascii')

        # Replace & with "and" as & is not read properly.
        msg_txt =msg_txt.replace("&", "and")

        print(msg_txt, len(msg_txt))

        parts = textwrap.wrap(msg_txt, 200)

        voice_txt = "/bin/bash /home/pi/tube_map/sounds/google_voice.sh {}".format(parts[0])

        print(voice_txt)

        os.system(voice_txt)

        # socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()


#voice_txt = "/bin/bash /home/pi/tube_map/sounds/google_voice.sh 'Northern Line: there is no service between Edgware Road and Morden due to a failed train at Woodside Park.  Tickets will be accepted on local bus services.  Apologies for the crap service.'"

#voice_txt = 'bash ls'
#print(voice_txt)

#os.system(voice_txt)