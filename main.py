#!/usr/bin/env python3
from skpy import SkypeEventLoop, SkypeNewMessageEvent, SkypeChatUpdateEvent, Skype
from datetime import datetime
import argparse
import os
import sys
import threading
import time
import signal


class PendingChats:
  def __init__(self):
    self.chats = {}

  def onMessageReceived(self, chat):
    """ Returns the time in seconds since the last message was
    received in this chat. """
    now = datetime.now()
    if chat.id not in self.chats:
      self.chats[chat.id] = now
      return sys.maxsize
    secondsPassed = (now - self.chats[chat.id]).total_seconds()
    self.chats[chat.id] = now
    return secondsPassed


class SkypeAutoResponse(SkypeEventLoop):
    def __init__(self, username, password, response, timeoutInSeconds=60):
        super(SkypeAutoResponse, self).__init__(username, password)
        self.response = response
        self.timeoutInSeconds = timeoutInSeconds
        # Cache pending contact requests
        self.pending_contact_requests = [x.user.id for x in self.contacts.requests()]
        # Cache pending chats
        self.pending_chats = PendingChats()

    def onNewMessageEvent(self, event):
        self.respondIfTimedOut(event.msg.chat)

    def onEvent(self, event):
        if isinstance(event, SkypeNewMessageEvent) and event.msg.userId != self.userId:
          return self.onNewMessageEvent(event)

    def respondIfTimedOut(self, chat):
        secondsSinceLastMsg = self.pending_chats.onMessageReceived(chat)
        if secondsSinceLastMsg > self.timeoutInSeconds:
          chat.sendMsg(self.response)

    def updateContactRequests(self):
        contact_requests = self.contacts.requests()
        for request in contact_requests:
          if request.user.id not in self.pending_contact_requests:
            self.acceptContactRequest(request)
            self.respondIfTimedOut(request.user.chat)

    def acceptContactRequest(self, request):
        print(f'\nAccepting incoming contact request from {request.user.id}.')
        self.pending_contact_requests.append(request.user.id)
        request.accept()
        self.respondIfTimedOut(request.user.chat)

    def loop(self):
      self.running = True
      while self.running:
        self.cycle()
        self.updateContactRequests()

    def stop(self):
      self.running = False

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Skype auto-responder.")
  parser.add_argument("--response", required=True, help="Path to text file containing the auto-reply content.")
  parser.add_argument("--username", required=True, help="Your skype username.")
  parser.add_argument("--password", required=True, help="Your skype password.")
  parser.add_argument("--timeout", type=int, default=60, help="Timeout after which new messages will trigger the auto-reply again.")
  args = parser.parse_args()

  with open(args.response, 'r') as f:
    response = f.read()
    print(f'\nNew Skype messages will be answered with:\n{response}')

  ping = SkypeAutoResponse(args.username, args.password, response, args.timeout)
  thread = threading.Thread(target=ping.loop, args=())
  thread.start()
  input("Press any key to exit..")
  ping.stop()
  thread.join()