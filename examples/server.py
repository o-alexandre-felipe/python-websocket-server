from websocket_server import WebsocketServer, WebsocketClientBehavior

# Called for every client connecting (after handshake)
def new_client(client, server):
  print("New client connected and was given id %d" % client.id)
  server.send_message_to_all("Hey all, a new client has joined us")

# Called for every client disconnecting
def client_left(client, server):
	print("Client(%d) disconnected" % client.id)

# Called when a client sends a message but overriden)
def message_received(client, server, message):
	if len(message) > 200:
		message = message[:200]+'..'
	print("Client(%d) from %s said: %s" % (client.id, client.origin, message))



class hdrBhv(WebsocketClientBehavior):
  '''
    Set a different behavior
  '''
  def on_text(self, msg):
    '''
      if the text sent through msg is in the request headers
      respond with that header.
    '''
    if msg in self.handler.headers:
      self.send_text(self.handler.headers[msg]);
    else:
      print('Client(%d) from %s said: %s' % (self.id, self.origin, msg));
  # on_text and on_open keeps with the same behavior

class revBhv(WebsocketClientBehavior):
  '''
    Set a different behavior
  '''
  def on_text(self, msg):
    '''
      if the text sent through msg is in the request headers
      respond with that header.
    '''
    self.send_text('.'.join(msg[::-1]));
  # on_text and on_open keeps with the same behavior

PORT=9001
server = WebsocketServer(PORT)
# override the default behavior for clients connection to ws://host:PORT/hdr
server.behaviors['/headers'] = hdrBhv;
server.behaviors['/reverse'] = revBhv;

# default handlers, will be called if the connect to the server with a different address
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
