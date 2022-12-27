import sys, os
from flask import Flask, jsonify, render_template, redirect, request, url_for
from flask.wrappers import Response
from imutils.video import VideoStream
import signal
import logging
import yaml
from types import SimpleNamespace
from copy import deepcopy

from lux.leds.effects import effect_names
from lux.web.handler  import LEDHandler
from lux.tools.config import parse, unparse, unwrap_hsv
from lux.tools.colour import hsv_to_hex


def create_app(server_type, conf, conf_path, camera_stream=None):
    app = Flask(__name__)
    app.debug = True
    conf.conf_path = conf_path

    logging.info(f"Creating {server_type} server with config:\n{conf}")
    proc = LEDHandler(conf, camera_stream)

    def handler(signum, frame):
        res = input("Do you want to exit? Press y.")
        if res == 'y':
            proc.stop()
            exit(1)

    signal.signal(signal.SIGINT, handler)

    def is_running():
        if proc.running:
            return "Main thread is running, lights should be dancing."
        else:
            return "Main thread not running."


    @app.route("/")
    def index():
        opts = unparse(proc.config)
        opts['segment']['effect']['solid'] = hsv_to_hex(vars(proc.config.segment.effect.solid))
        return render_template("index.html", opts = opts, running_text=is_running())

    @app.route("/start")
    def start():
        if not proc.running:
            proc.start()
        return redirect(url_for("index"))

    @app.route("/stop")
    def stop():
        if proc.running:
            proc.stop()
        return redirect(url_for("index"))

    @app.route("/settings", methods = [ 'GET', 'POST' ])
    def settings():
        #use_picamera = proc.config.server.CAMERA == 'pi'

        if request.method == 'GET':
            opts = unparse(proc.config)
            # color picker expects hex colours
            opts['segment']['effect']['solid'] = hsv_to_hex(vars(proc.config.segment.effect.solid))

            return render_template("settings.html", #use_picamera = use_picamera,
                conf_path = proc.config.conf_path, save_file = False,
                opts = opts, effects = effect_names)
        else:
            #if use_picamera:
            #    proc.update_picamera(request.form['iso'], request.form['shutter_speed'],
            #        request.form['saturation'], request.form['awb_mode'])
            # TODO: implement effect switch
            if request.form['effect'] == 'solid':
                proc.update_solid(request.form['solid'])

            if 'save_file' in request.form:
                conf_path = request.form['conf_path']
                file = open(conf_path, 'w')
                conf_to_save = deepcopy(proc.config)
                conf_to_save.segment.effect.solid = parse(unwrap_hsv(conf_to_save.segment.effect.solid))
                delattr(conf_to_save, 'conf_path')
                yaml.dump(unparse(conf_to_save), file)

            return redirect(url_for("settings"))


    @app.route("/video_feed")
    def video_feed():
        """
        Direct generated frame to webserver

        Returns
        ------
            HTTP response of corresponding type containing the generated stream
        """
        return Response(proc.generate_frame(),
            mimetype = "multipart/x-mixed-replace; boundary=frame")

    return app


if __name__ == '__main__':
    server_type='observer'
    if len(sys.argv) > 1:
        server_type = sys.argv[1]

    host = os.environ.get('HOST', default = '0.0.0.0')
    port = int(os.environ.get('PORT', default = '8888'))
    conf_path = os.environ.get('CONFIG_PATH', default = './config/default.yml')
    print(os.path.abspath("."))

    logging.info(f"Starting server, listening on {host} at port {port}, using config at {conf_path}")

    with open(conf_path, 'r') as fh:
        yaml_dict = yaml.safe_load(fh)
        config = parse(yaml_dict)

        # NOTE: to use /dev/video* devices, you must launch in the main process
        #       so we create the camera stream here
        # NOTE: camera stream may be useful in the ambilight mode
        #camera_number = config.server.CAMERA
        #camera_stream = None
        #if camera_number != None and type(camera_number) == int:
        #    logging.info(f"Opening Camera {camera_number}")
        #    camera_stream = VideoStream(int(camera_number), framerate = config.camera.framerate)
        #create_app(server_type, config, conf_path, camera_stream=camera_stream).run(
        #        host = host, port = port, debug = True,
        #        threaded = True, use_reloader = False)

        create_app(server_type, config, conf_path).run(
                host = host, port = port, debug = True,
                threaded = True, use_reloader = False)
