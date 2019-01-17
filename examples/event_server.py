import threading;
import bisect;
from websocket_server import WebsocketServer, WebsocketClientBehavior

class EventSource:
  def __init__(self):
    self.priorityList = list();
    self.idList = list();
    self.handlerList = list();
    self.id_counter = 0;
    self._lock = threading.Lock();
  def addListener(self, handler, priority):
    #  O(log(n)) - based on the priority list that is
    #              necessarily sorted it can be determined
    #              efficiently the insertion point
    with self._lock:
      self.id_counter += 1;
      i = bisect.bisect_right(self.priorityList, priority);
      self.priorityList.insert(i, priority);
      self.idList.insert(i, self.id_counter);
      self.handlerList.insert(i, handler);
      return self.id_counter;

  def removeListener(self, id):
    # O(n) - the identification list is not necessarily sorted
    #        and all the listeners may have the same priority
    with self._lock:
      i = self.idList.find(id);
      if len(self.idList) != 0:
        if self.idList[i] == i:
          del self.priorityList[i];
          del self.idList[i];
          del self.handlerList[i];
  def notify(self, data):
    # O(1) - the listener with highest priority is at the beginning of the 
    # list, so it can be called readily
    with self._lock:
      if len(self.handlerList) == 0:
        return;
      fn = self.handlerList[-1]
    return fn(data);



class EventSourceManager:
  def __init__(self):
    self.eventSources = dict();
  def addEventSource(self, ev, idSource):
    self.eventSources[idSource] = ev;
  def removeEventSource(self, idSource):
    if idSource in self.eventSources:
      del self.eventSources[idSource]
  def connect(self, idSource, handler, priority):
    if idSource in self.eventSources:
      return self.eventSources[idSource].addListener(handler, priority);
  def disconnect(self, idSource, idListener):
    if idSource in self.eventSources:
      return eventSources[idSource].removeListener(self, idListener);



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
      self.events.append(
         (idSource, self.eventManager.connect(idSource, self.notify_event, priority))
      );
      self.send_text('listening to events from ' + str(idSource));
    else:
      self.send_text(str(idSource) + ' not available');
  def notify_event(self, data):
    self.send_text(str(data));
  def on_close(self):
    for idSource, idListener in self.events:
      self.eventManager.disconnect(idSource, idListener);
  # on_text and on_open keeps with the same behavior

PORT=9001
server = WebsocketServer(PORT)
# override the default behavior for clients connection to ws://host:PORT/hdr
server.behaviors['/notify'] = senderBhv;
server.behaviors['/listen'] = listenerBhv;

# default handlers, will be called if the connect to the server with a different address
server.run_forever()
