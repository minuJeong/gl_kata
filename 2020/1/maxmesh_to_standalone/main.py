import sys
import time
import logging
from multiprocessing import Process

from glm import *
import glfw
from PyQt5 import QtWidgets
from flask import Flask
from flask import request

from client_glfw import ClientGLFW
from client_pyqt5 import ClientPYQT5


UP = vec3(0.0, 1.0, 0.0)


logger = logging.getLogger("root logger")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

# select framework
framework = "GLFW"
# framework = "PYQT5"


def server_func():
    server = Flask("max connection")

    @server.route("/stop")
    def stop():
        logger.info("server stop request received, stopping server..")
        request.environ.get("werkzeug.server.shutdown")()
        logger.info("stopped server")
        return "stopped server"

    @server.route("/signal/<signal>")
    def signal(signal=None):
        signal = signal or "No Signal"
        logger.info(signal)
        return signal

    server.run()


def client_func():
    width, height = 1024, 1024
    client = None

    if framework == "GLFW":
        print("client initializing with GLFW..")
        client = ClientGLFW(width, height, logger)

    elif framework == "PYQT5":
        print("client initializing with PYQT5..")

        client = Client()
        app = QtWidgets.QApplication([])
        renderwidget = QtWidgets.QOpenGLWidget()
        renderwidget.setMinimumSize(width, height)
        renderwidget.setMaximumSize(width, height)

        def paintGL():
            client.paint()
            renderwidget.update()

        renderwidget.initializeGL = client.init
        renderwidget.paintGL = paintGL
        renderwidget.show()
        app.exec_()

    else:
        raise Exception(f"selected framework not supported: {framework}")


def run_server():
    proc = Process(target=server_func)
    proc.start()
    return proc


def run_client():
    proc = Process(target=client_func)
    proc.start()
    return proc


def run_app(server_process, client_process):
    while server_process.is_alive() and client_process.is_alive():
        time.sleep(0.5)

    server_process.kill()
    client_process.kill()
    logger.info("App is dead")


def main():
    server_process = run_server()
    client_process = run_client()
    run_app(server_process, client_process)


if __name__ == "__main__":
    main()
