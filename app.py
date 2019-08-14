from abc import ABC

import tornado.ioloop
import tornado.web
import tornado.websocket
import logging
import threading
import socket
import sys
import argparse

from gpiozero import LED
from time import sleep

onOffSwitch = LED(4)
blueSwitch = LED(17)
brownSwitch = LED(27)


class MainHandler(tornado.web.RequestHandler, ABC):
    def get(self):
        self.render("index.html")


class SimpleWebSocket(tornado.websocket.WebSocketHandler, ABC):
    connections = set()

    def open(self):
        self.connections.add(self)

    def on_message(self, message):
        if message == "forward":
            onOffSwitch.off()
            blueSwitch.off()
            brownSwitch.off()
            onOffSwitch.on()
        elif message == "backward":
            onOffSwitch.off()
            blueSwitch.on()
            brownSwitch.on()
            onOffSwitch.on()
        elif message == "stop":
            onOffSwitch.off()
            blueSwitch.off()
            brownSwitch.off()

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
    onOffSwitch.off()
    blueSwitch.off()
    brownSwitch.off()
    onOffSwitch.on()
    sleep(0.5)
    onOffSwitch.off()

    threadedSocket = threading.Thread(target=udp_socket)
    threadedSocket.start()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
