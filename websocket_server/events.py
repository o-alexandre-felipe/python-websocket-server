import threading;
import bisect;

class EventSource:
  def __init__(self):
    self.keyList = list();
    self.handlerList = list();
    self.id_counter = 0;
    self._lock = threading.Lock();
  def addListener(self, handler, priority):
    #  O(log(n)) - based on the priority list that is
    #              necessarily sorted it can be determined
    #              efficiently the insertion point
    with self._lock:
      self.id_counter += 1;
      key = (priority, self.id_counter);
      i = bisect.bisect_right(self.keyList, key);
      self.keyList.insert(i, key);
      self.handlerList.insert(i, handler);
      return key;

  def removeListener(self, key):
    # O(log(n)) - the identification list is not necessarily sorted
    #             and all the listeners may have the same priority
    with self._lock:
      if len(self.keyList) != 0:
        i = bisect.bisect_left(self.keyList, key);
        if self.keyList[i] == key:
          del self.keyList[i];
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
  def disconnect(self, idSource, key):
    if idSource in self.eventSources:
      return self.eventSources[idSource].removeListener(key);


