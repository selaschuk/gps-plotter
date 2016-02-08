import SocketServer
import pynmea2
import json
import datetime

json_data = {}

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        global json_data
        self.data = self.request.recv(1024).strip()
        rawdata = self.data
        #uncomment following to debug
        #print self.data 
        if 'GET /gps.json HTTP/1.1' in rawdata:
            response_proto = 'HTTP/1.1'
            response_status = '200'
            response_status_text = 'OK'

            response_headers = {
                'Access-Control-Allow-Origin': '*',
                'Content-Length': len(json.dumps(json_data)),
                'Content-Type': 'text/html; encoding=utf8',
                'Connection': 'close',
            }

            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())

            self.request.send('%s %s %s' % (response_proto, response_status, response_status_text))
            self.request.send('\n') # to separate response from headers
            self.request.send(response_headers_raw)
            self.request.send('\n') # to separate headers from body
            self.request.send(json.dumps(json_data))

        elif 'HTTP/1.' in rawdata:
            response_proto = 'HTTP/1.1'
            response_status = '404'
            response_status_text = 'Not Found'

            self.request.send('%s %s %s' % (response_proto, response_status, response_status_text))            

        else:
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

        self.request.close()

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8889

    # Create the server, binding to localhost on port 8889
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
