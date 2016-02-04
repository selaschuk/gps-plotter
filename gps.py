import SocketServer
import pynmea2
import json
import datetime

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        rawdata = self.data
        print self.data
        #open datafile and read existing data
        with open('gps.json', 'r+') as f:
            json_data = json.load(f)
            #parse each line sent
            for line in rawdata.splitlines():
                #cradelpoint devices append the device ID to the front of the NEMA sentence
                gpsId = line.split(',')[0]
                #store the rest of the sentence as the valid NEMA sentence				
                rawNema = line.split(',', 1)[-1]
                #parse the message using pynema2
                parsedNema = pynmea2.parse(rawNema)
                if isinstance(parsedNema, pynmea2.types.talker.GGA):
                    #GGA sentence detected, collect position data
                    updateTime = datetime.datetime.combine(datetime.datetime.utcnow().date(), parsedNema.timestamp)
                    ggaData = {"info": gpsId, "lat": parsedNema.latitude, "lng": parsedNema.longitude, "updt": updateTime.isoformat()}
                    json_data.setdefault(gpsId, ggaData)
                    json_data[gpsId].update(ggaData)
                elif isinstance(parsedNema, pynmea2.types.talker.VTG):
                    #VTG sentence detected, collect speed data
                    vtgData = {"info": gpsId, "spd": parsedNema.spd_over_grnd_kmph}
                    json_data.setdefault(gpsId, vtgData)
                    json_data[gpsId].update(vtgData)
            f.seek(0)
            f.write(json.dumps(json_data))
            f.truncate()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8889

    # Create the server, binding to localhost on port 8889
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
