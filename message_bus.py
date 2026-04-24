from collections import deque


class MessageBus:
    def __init__(self):
        self.queue = deque()
        self.history = []

    def send(self, message):
        self.queue.append(message)
        self.history.append(message)
        print(f"[BUS] {message['fromagent']} -> {message['toagent']} | {message['messagetype']}")

    def receive(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def is_empty(self):
        return len(self.queue) == 0