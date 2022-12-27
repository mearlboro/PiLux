import cv2
from collections import OrderedDict
import datetime
from imutils.video import FileVideoStream, VideoStream
import logging
import numpy as np
import os
import threading
import time
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple, Generator

# initialise logging to file
import lux.tools.logger

# import relevant project libs
from lux.tools.colour  import hex_to_hsv
from lux.tools.config  import parse, unwrap_resolution


# NOTE: possibly useful for fetching a video stream in the ambilight mode
class Camera():
    def __init__(self, cam_type: Any, config: SimpleNamespace, camera_stream = None) -> None:
        """
        Wrapper around a video stream either fetching frames from a real camera,
        or mocking it using a local video file.

        Params
        ------
        cam_type
            if 'pi', uses a PiCamera on a RaspberryPi
            if a number, fetch the corresponding video stream (e.g. for webcam)
            if a path, simulate a camera using the video at the path
        config
            namespace (dot-addressible dict) including configuration for the
            camera, such as:

            resolution.width, resolution.height : int
            framerate  : int
            iso, shutter_speed, saturation: int
            awb_mode: string
        """
        self.config = config
        self.cam_type = cam_type
        self.camera_stream = camera_stream


    def start(self) -> VideoStream:
        """
        Initialise the video stream according to prameters, set image resolution
        and framerate, as well as camera parameters if PiCamera is used, then
        start the stream

        Side-effects
        ------
        create and start a video stream

        Returns
        ------
        video stream containing the frames fetched from the camera or video
        """
        if self.cam_type == 'pi':
            resolution = unwrap_resolution(self.config.resolution)
            self.video_stream_obj = VideoStream(usePiCamera = 1,
                resolution = resolution, framerate = self.config.framerate)
            self.video_stream = self.video_stream_obj.start()
            self.picamera = self.video_stream_obj.stream.camera

            ## set picam defaults
            self.update_settings(self.config)

            time.sleep(2)
        elif type(self.cam_type) is int:
            self.video_stream = self.camera_stream
            self.video_stream.start()
        else:
            if not os.path.isfile(self.cam_type):
                raise ValueError(f'No such file: {self.cam_type}')

            self.video_stream = FileVideoStream(self.cam_type).start()

        return self.video_stream


    def update_settings(self, config: SimpleNamespace):
        if self.cam_type == 'pi':
            self.picamera.iso = self.config.iso
            self.picamera.saturation = self.config.saturation
            self.picamera.shutter_speed = self.config.shutter_speed
            self.picamera.awb_mode = self.config.awb_mode


class LEDHandler():
    """
    Helper class which fetches frames from a vidstream, applies object detection
    and tracking, and computes emergence values based on the object positions &
    a macroscopic feature of the system.
    """

    def __init__(self, config: SimpleNamespace, camera_stream = None):
        """
        Initialise system behaviour and paths using the server configuration in
        config, and videostream, tracker and detector objects

        config:
            config.server changes only changed on server restart

        Params
        ------
        config
            namespace (dot-addressible dict) including config as specified in
            .//config/default.yml

            config.server
                used in the initialisation of the Flask app and the VideoProcessor,
                includes application parameters such as host, port, type of video
                feed, behaviour
            config.camera
                used in the initialisation of the Camera object, includes camera
                parameters (iso, shutter speed etc), and video parameters
                (resolution and framerate)
        """
        self.config = config
        self.running = False

        self.camera_stream  = camera_stream

        # initialize the output frame and a lock used to ensure thread-safe
        # exchanges of the output frames (useful when multiple browsers/tabs
        # are viewing the stream)
        self.output_frame = None

        self.video_stream = None

        self.tracking_thread = threading.Thread(target = self.stream)
        self.lock = threading.Lock()


    def update_solid_color(self, color: SimpleNamespace) -> None:
        """
        Following a form submission in the front-end, reinitialise config

        Params
        ------
        TODO:

        Side-effects
        ------
        TODO:
        """
        self.config.effects.solid_color = parse(hex_to_hsv(color))


    def update_picamera(self,
            iso: int, shutter_speed: int, saturation: int, awb_mode: str
        ) -> None:
        """
        Following a form submission in the front-end, update picamera settings
        with new parameters, as well as update config

        Params
        ------
            iso
                sensitivity, min 25, max 800
            shutter_speed
                in milionths of a second
            saturation
                from 1 to 100
            awb_mode
                white balance
        """
        self.config.camera.iso = int(iso)
        self.config.camera.shutter_speed = int(shutter_speed)
        self.config.camera.saturation = int(saturation)
        self.config.camera.awb_mode = awb_mode

        self.camera.update_settings(self.config)

        logging.info(f"Updated PiCamera settings from Web UI:")
        logging.info(f"  iso           : {iso          } ")
        logging.info(f"  shutter_speed : {shutter_speed} ")
        logging.info(f"  saturation    : {saturation   } ")
        logging.info(f"  awb_mode      : {awb_mode     } ")


    def stream(self) -> None:
        """
        Stream a video from the object's video_stream.

        Params
        ------
            None

        Returns
        ------
            None

        Side-effects
        ------
            - produce a stream in output_frame
            - may acquire or release lock
            - consumes the video stream
        """
        # read the first frame and detect objects
        #with self.lock:
        #    frame = self.video_stream.read()

        #if frame is None:
        #    logging.info('Error reading first frame. Exiting.')
        #    exit(0)

        ## acquire the lock, set the output frame, and release the lock
        #with self.lock:
        #    self.output_frame = frame.copy()

        ## loop over frames from the video stream and track
        #while self.running:
        #    with self.lock:
        #        frame = self.video_stream.read()

        #        if frame is not None:
        #            # TODO: fetch colours from frame
        #            pass

        #        # acquire the lock, set the output frame, and release the lock
        #        with self.lock:
        #            self.output_frame = frame.copy()
        time.sleep(0.1)


    def generate_frame(self) -> Generator[bytes, None, None]:
        """
        Encode the current output frame as a bytearray of a JPEG image

        Params
        ------
            None

        Returns
        ------
            a generator that produces a stream of bytes with the frame wrapped
            in a HTML response
        """
        framerate = 12.0
        frametime = 1.0/framerate
        while self.running:
            # wait until the lock is acquired
            begin = time.time()
            with self.lock:
                # check if the output frame is available, otherwise skip
                # the iteration of the loop
                if self.output_frame is None:
                    continue
                # encode the frame in JPEG format
                (flag, encoded_frame) = cv2.imencode(".jpg", self.output_frame)
                # ensure the frame was successfully encoded
                if not flag:
                    continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                bytearray(encoded_frame) + b'\r\n')
            end = time.time()
            diff = end - begin
            if diff > frametime:
                continue
            else:
                time.sleep(frametime - diff)


    def start(self) -> None:
        """
        Initialises camera stream, tasks and runs tracking process in a thread.
        Ensures only one tracking thread is running at a time.
        """
        # prevent starting tracking thread if one is already running
        if not self.tracking_thread.is_alive():

            # reinitialise tracking_thread in case previous run crashed
            self.tracking_thread = threading.Thread(target = self.stream)

            #self.camera = Camera(self.config.server.CAMERA, self.config.camera, self.camera_stream)
            #self.video_stream = self.camera.start()

            logging.info("Initialised Handler with params:")
            logging.info(f"camera type: {self.config.server.CAMERA}")

            self.running = True
            self.tracking_thread.start()
            self.lock = threading.Lock()


    def stop(self) -> None:
        """
        Release the video stream and writer pointers and gracefully exit the JVM

        Params
        ------
            None

        Returns
        ------
            None
        """
        logging.info('Stopping tracking thread...')
        self.running = False

        #if self.video_stream:
        #    logging.info('Closing video streamer...')
        #    self.video_stream.stop()

