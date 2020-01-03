import freeOrionAIInterface as fo

from ElenAi.CElenAi import CElenAi


def startNewGame(aggression_input = fo.aggression.aggressive):
    print 'startNewGame()'

    global oElenAi
    oElenAi = CElenAi()

    return


def resumeLoadedGame(saved_state_string):
    print 'resumeLoadedGame()'

    global oElenAi
    oElenAi = CElenAi()

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


def handleDiplomaticStatusUpdate(status_update):
    print 'handleDiplomaticStatusUpdate()'
    print 'Received diplomatic status update to %s about empire %s and empire %s.' % (
        status_update.status,
        'me' if status_update.empire1 == fo.empireID() else fo.getEmpire(status_update.empire1).name,
        'me' if status_update.empire2 == fo.empireID() else fo.getEmpire(status_update.empire2).name
    )

    return


def generateOrders():
    print 'generateOrders()'

    global oElenAi
    oElenAi.vAssessUniverse(fo)

    return


oElenAi = None
