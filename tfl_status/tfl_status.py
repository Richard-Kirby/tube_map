import requests
import json
import threading
import time


# Class that manages the TFL status - sorts out the credentials and makes the queries when asked.
class Tfl_Status(threading.Thread):

    # Get setup, including reading in credentials from the JSON file.  Credentials need to be obtained from TFL.
    def __init__(self):
        # Init the threading
        threading.Thread.__init__(self)

        # Grab the credentials.  TODO: everyone has to get their own credentials.  Not in the repo.
        with open('tfl_status/tfl_credentials.secret') as json_data_file:
            config = json.load(json_data_file)

        # assign to appropriate variables - get used for each call to get status.
        self.application_id = config['credentials']['application_id']
        self.application_keys = config['credentials']['application_keys']

        self.status_request_url = "https://api.tfl.gov.uk/Line/Mode/tube/Status?detail=false&app_key={}&app_id={}"\
                .format(config['credentials']['application_keys'], config['credentials']['application_id'])

        self.status_dictionary = None
        self.special_messages = None

        self.lines = ['Circle', 'District', 'Hammersmith-City', 'Jubilee', 'Metropolitan', 'Central', 'Bakerloo',
                          'Northern', 'Piccadilly', 'Victoria', 'Waterloo-City']

    # Get the status from the TFL site and process it to get just the summary status.
    def get_summary_status(self):

        self.status_dictionary ={}
        self.special_messages = []
        self.station_prediction = {}

        try:
            for line in self.lines:
                self.trackernet_request_url = "https://api.tfl.gov.uk/line/{}/arrivals?app_key={}&app_id={}" \
                    .format(line, self.application_keys, self.application_id)

                trackernet_feed = requests.get(self.trackernet_request_url).json()

                for row in trackernet_feed:
                    # print(row)
                    station_name = row["stationName"].split(" Underground Station")
                    platform = row["platformName"].split(" - ")

                    if len(platform) == 2:
                        nsew_direction = platform[0]
                        platform_num = platform[1]
                    else:
                        nsew_direction = "None"
                        platform_num = platform[0]

                    if "direction" in row:
                        direction = row["direction"]
                    else:
                        direction = "None"

                    dict_key = row["lineName"] +',' + station_name[0] + ',' + direction

                    #print(key)

                    # If already populated, check if lower.
                    if dict_key in self.station_prediction:
                        # Copy time over if lower than current value
                        if row["timeToStation"] < self.station_prediction[dict_key]:
                            self.station_prediction[dict_key] = row["timeToStation"]
                    else:
                        self.station_prediction[dict_key] = row["timeToStation"]

            #for key in self.station_prediction:
            #    print(key, self.station_prediction[key])

        except:
            print("TFL Arrivals get failed - random number generator or Internet not avail?")
            print("Keep Trying")

        try:
            result = requests.get(self.status_request_url).json()
            for line in result:
                #print(line)
                #print (line['name'],":", line['lineStatuses'][0]['statusSeverityDescription'])
                if "reason" in line['lineStatuses'][0]:
                    #print(line['name'], ":", line['lineStatuses'][0]['reason'])
                    self.special_messages.append(line['lineStatuses'][0]['reason'])
                self.status_dictionary[line['name']] = line['lineStatuses'][0]['statusSeverityDescription']
        except: # removed raise exception - would mean it just gives up.
            print("tfl status get failed - random number generator or Internet not avail?")
            print("Keep Trying")

    def run(self):
        # Get the status every once in a while
        while True:
            self.get_summary_status()
            # if self.special_messages !=[]:
                #print(self.special_messages)
            time.sleep(120)


if __name__ == "__main__":
    tfl_status = Tfl_Status()
    tfl_status.get_summary_status()
    tfl_status.start()

