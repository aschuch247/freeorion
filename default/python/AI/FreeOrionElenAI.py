import freeOrionAIInterface as fo

def startNewGame(aggression_input = fo.aggression.aggressive):
    print 'startNewGame()'
    return

def resumeLoadedGame(saved_state_string):
    print 'resumeLoadedGame()'
    return

def prepareForSave():
    print 'prepareForSave()'
    return

def handleChatMessage(sender_id, message_text):
    print 'handleChatMessage()'
    return

def handleDiplomaticMessage(message):
    print 'handleDiplomaticMessage()'
    print 'Received diplomatic %s message from %s to %s.' % (
        message.type,
        fo.getEmpire(message.sender).name,
        'me' if message.recipient == fo.empireID() else fo.getEmpire(message.recipient)
    )

    # Right now, always accept a peace proposal and an alliance proposal.

    if message.type == fo.diplomaticMessageType.peaceProposal:
        diplomatic_reply = fo.diplomaticMessage(message.recipient, message.sender, fo.diplomaticMessageType.acceptPeaceProposal)
        print 'Sending diplomatic message to empire %s of type %s.' % (fo.getEmpire(message.sender).name, diplomatic_reply.type)
        fo.sendDiplomaticMessage(diplomatic_reply)
    elif message.type == fo.diplomaticMessageType.alliesProposal:
        diplomatic_reply = fo.diplomaticMessage(message.recipient, message.sender, fo.diplomaticMessageType.acceptAlliesProposal)
        print 'Sending diplomatic message to empire %s of type %s.' % (fo.getEmpire(message.sender).name, diplomatic_reply.type)
        fo.sendDiplomaticMessage(diplomatic_reply)

    return

# @todo @listener
def generateOrders():
    print 'generateOrders()'
    return
