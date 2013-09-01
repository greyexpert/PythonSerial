__author__ = 'greyexpert'

class ProtocolError(Exception):
    pass

class Protocol:
    stream = None

    MAX_CHANNELS = 15
    MAX_DATA_SIZE = 7

    # Decoder state
    __dataSize = 0
    __step = 0
    __buffer = None
    __channel = 0

    __listeners = [None for x in range(MAX_CHANNELS)]

    def __init__(self, stream):
        self.stream = stream

    def start(self):
        if not self.stream.isOpen():
            self.stream.open()
        self.stream.flushInput()
        self.stream.flushOutput()

    def stop(self):
        self.stream.close()

    # Receiving methods

    def waitForPackage(self):
        while True:
            byte = self.stream.read()
            if self.processByte(byte):
                return self.__channel, bytes(self.__buffer)

    def listen(self):
        while True:
            channel, data = self.waitForPackage()
            self.received(channel, data)

    def attach(self, channel, callback):
        self.__listeners[channel] = callback

    def received(self, channel, data):
        if self.__listeners[channel] is not None:
            self.__listeners[channel](channel, data)

    # Sending methods

    def send(self, channel, data=""):
        self.stream.write(self.encode(channel, data))

    # Data converting methods

    def encode(self, channel, data=""):
        if channel > self.MAX_CHANNELS or channel < 0:
            raise ProtocolError("Channel should be less than %d and more than 0" % self.MAX_CHANNELS)

        if len(data) > self.MAX_DATA_SIZE:
            raise ProtocolError("data size should not exceed %d bytes" % self.MAX_DATA_SIZE)

        marker = (0x80 | (channel & 0x0F) << 3) + len(data); # Package Marker
        if not data:
            return bytes(bytearray([marker]))

        headerLength = (len(data) / 7 + 2)
        buff = bytearray(headerLength + len(data))
        buff[0] = marker

        for index in range(len(data)):
            buff[headerLength + index] = ord(data[index]) & 0x7f
            buff[index / 8 + 1] |= ((ord(data[index]) >> 7) << index % 8) & 0x7f

        return bytes(buff)

    def processByte(self, inp):
        byte = ord(inp)

        if byte >= 0x80:

            self.__dataSize = byte & 0x07;
            self.__channel = (byte & 0x7F) >> 3;
            self.__step = 0

            if not self.__dataSize:
                self.__buffer = bytearray()
                return True

            self.__buffer = bytearray(self.__dataSize + (self.__dataSize / 7 + 1))

        elif self.__dataSize:
            headerLength = self.__dataSize / 7 + 1
            if self.__step < headerLength:
                self.__buffer[self.__step] = byte
            else:
                dataOffset = self.__step - headerLength
                if self.__buffer[dataOffset / 7] & (1 << dataOffset % 7):
                    byte |= 0x80

                self.__buffer[self.__step] = byte
            self.__step += 1

            if self.__dataSize == self.__step - headerLength:
                self.__buffer = self.__buffer[headerLength:]
                return True

        return False


if __name__ == "__main__":
    pass
