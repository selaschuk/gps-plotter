import socket
import threading
import SocketServer
import pynmea2
import json
import datetime

gpsData = {}

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        global gpsData
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        rawdata = self.data
        #uncomment following lines to debug
        #print self.data
        #print "{} wrote:".format(self.client_address[0])
        if 'GET /gps.json HTTP/1.1' in rawdata:
            response_proto = 'HTTP/1.1'
            response_status = '200'
            response_status_text = 'OK'

            response_headers = {
                'Access-Control-Allow-Origin': '*',
                'Content-Length': len(json.dumps(gpsData)),
                'Content-Type': 'text/html; encoding=utf8',
                'Connection': 'close',
            }

            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())

            self.request.send('%s %s %s' % (response_proto, response_status, response_status_text))
            self.request.send('\n')
            self.request.send(response_headers_raw)
            self.request.send('\n') # to separate headers from body
            self.request.send(json.dumps(gpsData))

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
                    gpsData.setdefault(gpsId, ggaData)
                    gpsData[gpsId].update(ggaData)
                elif isinstance(parsedNema, pynmea2.types.talker.VTG):
                    #VTG sentence detected, collect speed data
                    vtgData = {"info": gpsId, "spd": parsedNema.spd_over_grnd_kmph}
                    gpsData.setdefault(gpsId, vtgData)
                    gpsData[gpsId].update(vtgData)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Bind to port 8889
    HOST, PORT = "0.0.0.0", 8889

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    server.serve_forever()
