from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from three import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(3000)
IOLoop.instance().start()
