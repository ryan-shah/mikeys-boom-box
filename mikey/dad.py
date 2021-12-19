def getNewName(search, msg):
    start = msg.lower().index(search) + len(search)
    end = len(msg)
    if '.' in msg:
        idx = msg.index('.')
        if idx > start:
            end = idx
    if ',' in msg:
        idx = msg.index('.')
        if idx > start and idx < end:
            end = idx
    return msg[start:end]
            
def dadJoke(message):
    triggers = ["i'm ", "i am ", " im "]
    for word in triggers:
        if word in message.content.lower():
            name = getNewName(word, message.content)
            response = "Hi " + name + ", I thought you were <@" + str(message.author.id) + ">."
            return response