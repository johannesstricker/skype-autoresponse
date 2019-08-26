from skpy import SkypeEventLoop, SkypeNewMessageEvent
from datetime import datetime
import argparse
import os


class Conversation:
  def __init__(self, user):
    self.user = user
    self.messageCount = 0
    self.lastAction = datetime.now()

  def messageReceived(self):
    self.lastAction = datetime.now()
    self.messageCount += 1

  def sinceLastMessage(self):
    now = datetime.now()
    return (now - self.lastAction).total_seconds()


class SkypePing(SkypeEventLoop):
    def __init__(self, username, password, response, timeoutInSeconds=60):
        super(SkypePing, self).__init__(username, password)
        self.conversations = {}
        self.response = response
        self.timeoutInSeconds = timeoutInSeconds

    def onEvent(self, event):
        if isinstance(event, SkypeNewMessageEvent) and event.msg.userId != self.userId:
          if event.msg.userId not in self.conversations:
            self.conversations[event.msg.userId] = Conversation(event.msg.userId)

          conversation = self.conversations[event.msg.userId]
          sinceLastMsg = conversation.sinceLastMessage()
          conversation.messageReceived()
          if conversation.messageCount == 1 or sinceLastMsg > self.timeoutInSeconds:
            event.msg.chat.sendMsg(self.response)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Skype auto-responder.")
  parser.add_argument("--response", required=True, help="Path to text file containing the auto-reply content.")
  parser.add_argument("--username", required=True, help="Your skype username.")
  parser.add_argument("--password", required=True, help="Your skype password.")
  parser.add_argument("--timeout", type=int, default=60, help="Timeout after which new messages will trigger the auto-reply again.")
  args = parser.parse_args()

  with open(args.response, 'r') as f:
    response = f.read()
    print(f'\nAuto-reply:\n{response}')

  ping = SkypePing(args.username, args.password, response, args.timeout)
  ping.loop()