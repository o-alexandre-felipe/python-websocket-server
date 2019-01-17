from websocket_server import WebsocketServer, WebsocketClientBehavior
from websocket_server import EventSource, EventSourceManager

class senderBhv(WebsocketClientBehavior):
  '''
    Set a different behavior
  '''
  eventManager = EventSourceManager()
  def on_text(self, msg):
    '''
      if the text sent through msg is in the request headers
      respond with that header.
    '''
    self.eventSource.notify('Source %d: %s' % (self.id, msg));
  def on_open(self):
    '''
      Create an event source for this connection
    '''
    self.eventSource = EventSource();
    self.eventManager.addEventSource(self.eventSource, self.id);
    self.send_text('this is the event source %d' % self.id);

  def on_close(self):
    self.eventManager.removeEventSource(self.id)
  # on_text and on_open keeps with the same behavior

class listenerBhv(WebsocketClientBehavior):
  '''
    Set a different behavior
  '''
  def on_open(self):
    self.eventManager = senderBhv.eventManager;
    self.events = [];
  def on_text(self, msg):
    '''
      if the text sent through msg is in the request headers
      respond with that header.
    '''
    try:
      idSource, priority = map(int, msg.split());
    except Exception as e:
      self.send_text(str(e));
      return
    if(idSource in self.eventManager.eventSources):
      key = self.eventManager.connect(idSource, self.notify_event, priority);
      self.events.append(
         (idSource, key)
      );
      self.send_text('listening to events from ' + str(idSource));
    else:
      self.send_text(str(idSource) + ' not available');
  def notify_event(self, data):
    self.send_text(str(data));
  def on_close(self):
    for idSource, key in self.events:
      self.eventManager.disconnect(idSource, key);
  # on_text and on_open keeps with the same behavior

PORT=9001
server = WebsocketServer(PORT)
# override the default behavior for clients connection to ws://host:PORT/hdr
server.behaviors['/notify'] = senderBhv;
server.behaviors['/listen'] = listenerBhv;

# default handlers, will be called if the connect to the server with a different address
server.run_forever()
