from abc import ABC

import tornado.ioloop
import tornado.web
import tornado.websocket
import logging
import threading
import socket
import sys
import argparse

from gpiozero import LED, Device
from gpiozero.pins.mock import MockFactory

from time import sleep

TESTING = True

if TESTING is False:
    Device.pin_factory = MockFactory()

moveOnOffSwitch = LED(24)
moveCircuitPlusSwitch = LED(22)
moveCircuitMinusSwitch = LED(23)

steerOnOffSwitch = LED(27)
steerCircuitPlusSwitch = LED(4)
steerCircuitMinusSwitch = LED(17)


# Connected physical switch wrong
# so off is on and on is off
def on():
    moveOnOffSwitch.off()
    steerOnOffSwitch.off()


def off():
    moveOnOffSwitch.on()
    steerOnOffSwitch.on()


class MainHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        self.render("index.html")


class SimpleWebSocket(tornado.websocket.WebSocketHandler, ABC):
    connections = set()

    def open(self):
        self.connections.add(self)

    def on_message(self, message):
        if message == "forward":
            moveOnOffSwitch.on()
            moveCircuitPlusSwitch.on()
            moveCircuitMinusSwitch.on()
            moveOnOffSwitch.off()
        elif message == "backward":
            moveOnOffSwitch.on()
            moveCircuitPlusSwitch.off()
            moveCircuitMinusSwitch.off()
            moveOnOffSwitch.off()
        elif message == "left":
            steerOnOffSwitch.on()
            steerCircuitPlusSwitch.off()
            steerCircuitMinusSwitch.off()
            steerOnOffSwitch.off()
        elif message == "right":
            steerOnOffSwitch.on()
            steerCircuitPlusSwitch.on()
            steerCircuitMinusSwitch.on()
            steerOnOffSwitch.off()
        elif message == "stop":
            off()
        print(message)
        self.write_message(message)

    def on_close(self):
        self.connections.remove(self)

    def check_origin(self, origin: str) -> bool:
        return True


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/websocket", SimpleWebSocket)
    ])


def udp_socket():
    magic = "rccontrolserver;"
    port = 8889
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
    sock.bind(("", 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    hostname = socket.gethostbyname(socket.getfqdn())

    while 1:
        data = magic + hostname
        sock.sendto(data.encode(encoding='UTF-8', errors='strict'), ("<broadcast>", port))
        sleep(5)


if __name__ == "__main__":
    on()
    sleep(.5)
    off()

    threadedSocket = threading.Thread(target=udp_socket)
    threadedSocket.start()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
