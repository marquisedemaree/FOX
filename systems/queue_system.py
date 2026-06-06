# systems/queue_system.py

from collections import deque
import threading


class MessageQueue:
    '''
    Thread-safe FIFO message queue used to buffer sensor events.
    METHODS:
        - push(event): Add a single event to the back of the queue.
        - push_batch(events): Add multiple events to the back of the queue.
        - pop(): Remove and return the front event from the queue.
        - drain(): Remove and return events from the front of the queue.
        - size(): Return the current number of queued events.
        - clear(): Remove all events from the queue.
    '''

    def __init__(self):
        '''
        Initialize queue storage and synchronization.
        '''
        self.queue = deque()
        self.lock = threading.Lock()

    def push(self, event):
        '''
        Add a single event to the back of the queue.
        INPUT: 
            - event: dict
        '''
        with self.lock:
            self.queue.append(event)

    def push_batch(self, events):
        '''
        Add multiple events to the back of the queue.
        INPUT: 
            - events: [dict]
        '''
        with self.lock:
            self.queue.extend(events)

    def pop(self):
        '''
        Remove and return the front event from the queue.
        OUTPUT: 
            - event: dict or None
        '''
        with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None

    def drain(self, max_items=None):
        '''
        Remove and return up to max_items events from the front of the queue.
        OUTPUT: 
            - items: [dict]
        '''
        
        items = []

        # 1: ACQUIRE LOCK AND EXTRACT EVENTS
        with self.lock:
            
            # 1.1: DRAIN ENTIRE QUEUE
            if max_items is None:
                
                # 1.1.1: REMOVE EVENTS UNTIL QUEUE IS EMPTY
                while self.queue:
                    items.append(self.queue.popleft())
            
            # 1.2: DRAIN UP TO SPECIFIED LIMIT
            else:
                
                # 1.2.1: DETERMINE NUMBER OF EVENTS TO REMOVE
                count = min(max_items, len(self.queue))
                
                # 1.2.2: REMOVE SPECIFIED NUMBER OF EVENTS
                for _ in range(count):
                    items.append(self.queue.popleft())

        return items

    def size(self):
        '''
        Return the current number of queued events.
        OUTPUT: 
            - int
        '''
        with self.lock:
            return len(self.queue)

    def clear(self):
        '''
        Remove all events from the queue.
        '''
        with self.lock:
            self.queue.clear()
