# Skype Auto-Response
A python script to automatically reply to new skype messages.

## Sample Invocation
```
main.py --username <your_skype_username> --password <your_skype_password> --response response.txt --timeout 60
```
This will reply to new messages with the contents of the file `response.txt` if the sender's last message was at least 60 seconds ago.

## Requirements and Limitations
The script uses the [SkPy package](https://github.com/Terrance/SkPy) to interact with the Skype API. Because the API is undocumented and might change at any time the code could break unpredictably as well.
