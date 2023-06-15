from tor import *

torSession1 = Tor("127.0.0.1", 9050)
torSession1.initialize()
torSession1.connect("ident.me", 80)
request = torSession1.get_request()
print(request)

torController = TorControl("127.0.0.1", 9051)
torController.authenticate("proxy")
torController.new_identity()                             # You must create a new Tor session after requesting new identity
 
torSession2 = Tor("127.0.0.1", 9050)
torSession2.initialize()
torSession2.connect("ident.me", 80)
request2 = torSession2.get_request()
print(request2)


#command = torController.command("SIGNAL NEWNYM")        # Manual / Custom command
#status_code = command.status #.status is integer        # Get the output of the command in 2 parts
#status_info = command.info                              # Info (string)
#print( str(status_code) + " " + status_info )           # Status code (integer)