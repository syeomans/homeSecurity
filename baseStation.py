from math import ceil
import time

bufferSize = 32
portSize = 8
dataSize = 8
checksumSize = int(ceil((portSize*2+dataSize) / 4.0))
leadingBits = 0b1

thisAddress = 1

baudRate = 1200
baudDelay = 1.0/baudRate

idempotenceRuns = 5
idempotenceDelay = 10*baudDelay

def calculateChecksum(message):
    """
    Calculate a checksum

    The message is divided into 4 sections, each of k bits.
    All the sections are added together to get the sum.
    The sum is complemented and becomes the Checksum.

    message (int): An integer representing the bits of the message.
        Remember to not include the checksum in the message on the
        receiving end.

    returns (int): An integer representation of the checksum
    """
    # Calculate k and make a bitmask
    messageLength = len(list(bin(message)))-2
    k = int(ceil(messageLength / 4.0))
    kBitMask = 2**k-1 # bitwise, this is k 1's

    # Divide message into 4 sections of k bits
    c1 = message & kBitMask
    message = message >> k
    c2 = message & kBitMask
    message = message >> k
    c3 = message & kBitMask
    message = message >> k
    c4 = message

    # Add sections together
    sum = c1 + c2 + c3 + c4

    # Complement checksum and return
    checksum = sum^kBitMask # bitwise XOR with all 1's is the same as taking a complement
    return(checksum)

def generateMessage(destinationPort, data):
    '''
    Generate a message to be sent later

    Message format:
        [leadingBits, sourcePort, destinationPort, data, checksum]

    destinationAddress (int): The destination address

    data (int): The data to write

    returns (int): The requested message with checksum included
    '''
    message = leadingBits
    message = message << portSize
    message = message | thisAddress
    message = message << portSize
    message = message | destinationPort
    message = message << dataSize
    message = message | data
    checksum = calculateChecksum(message)
    message = message << checksumSize
    message = message | checksum
    return(message)

def sendMessage(message):
    '''
    Send a message in bits

    Send a message in bits using the globally defined baud rate. Uses
        idempotence to ensure message delivery.

    message (int): A message of 32 bits
        preferebly generated with generateMessage

    no returns
    '''
    for i in range(idempotenceRuns):
        for bit in bin(message)[2:]:
            print(bit)
            time.sleep(baudDelay)
        time.sleep(idempotenceDelay)

# Test code
myMessage = generateMessage(5, 3)
sendMessage(myMessage)
