import cv2
import numpy as np
import logging

# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Device_List(list):

    def __init__(self):
        self.update()

    def update(self):
        '''#index = 0
        arr = []
        #while True:
        for index in range(3):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                id = "video" + str(index)
                arr.append({'name': id, 'uid': str(index)})
            cap.release()
            index += 1
        
        print(arr)

        self[:] = arr

        print(self[:])'''

        self[:] = [{'name': "video{}".format(index), 'uid': str(index)} for index in range(3)]

    def cleanup(self):
        pass

class VideoCaptureWrapper:
    
    def __init__(self, id):
        self.name = "video" + str(id)
        self.index = 0      # index is basically the frame id

        self.cap = cv2.VideoCapture(int(id))

        logger.info("Create OpenCV Video Capture {}".format(self.name))

        # all available frame settings
        self.frame_sizes = [(320, 240), (160, 120), (640, 480), (1024, 768), (1920, 1080)]
        self.frame_rates = [30, 90]

        self.controls = []
        self._frame_size = (320, 240)

        # get the standard parameters
        self._frame_size = (self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._frame_rate = self.cap.get(cv2.CAP_PROP_FPS)

        #self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        #self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        # set the standard parameters
        self.frame_size = self.frame_sizes[0]
        self.frame_rate = self.frame_rates[0]

        if self.cap:

            self._frame_size = (self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._frame_rate = self.cap.get(cv2.CAP_PROP_FPS)

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    @property
    def frame_size(self):
        return self._frame_size

    @frame_size.setter
    def frame_size(self, value):
        self._frame_size = value
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._frame_size[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])

    @property
    def frame_rate(self):
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, value):
        self._frame_rate = value
        self.cap.set(cv2.CAP_PROP_FPS, self._frame_rate)
        #print("Setting frame_rate not yet supported")

    def isOpened(self):
        return self.cap and self.cap.isOpened()

    def get_frame(self):
        frame = Frame()
        result = self.cap.read()
        frame.attach_frame(result[1], self.index)

        self.index += 1
        return frame


    def release(self):
        self.cap.release()

    def __del__(self):
        self.release()

class Frame:
    '''
    The Frame Object holds image data and image metadata.
    The Frame object is returned from Capture.get_frame()
    It will hold the data in the transport format the Capture is configured to grab.
    Usually this is mjpeg or yuyv
    Other formats can be requested and will be converted/decoded on the fly.
    Frame will use caching to avoid redunant work.
    Usually RGB8,YUYV or GRAY are requested formats.
    WARNING:
    When capture.get_frame() is called again previos instances of Frame will point to invalid memory.
    Specifically all image data in the capture transport format.
    Previously converted formats are still valid.
    '''

    def __init__(self):
        self.frame = None
        self._index = -1
        self._timestamp = -1.0
        pass

    def attach_frame(self, frame, index):
        self.frame = frame
        self._index = index

    @property
    def width(self):
            return self.frame.shape[1]

    @property
    def height(self):
        return self.frame.shape[0]

    @property
    def index(self):
        return self._index

    @property
    def timestamp(self):
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value


    @property
    def jpeg_buffer(self):
        data = cv2.imencode('.jpg', self.frame)[1]
        data = data.reshape(-1)
        return data

    @property
    def yuv_buffer(self):
        print("Unsafe bgr -> yuv")
        # TODO make more efficient on multiple calls
        #print(self.frame.shape)
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2YUV)
        #if self._yuv_converted is False:
        #    self.jpeg2yuv()
        #cdef np.uint8_t[::1] view = <np.uint8_t[:self._yuv_buffer.shape[0]]>&self._yuv_buffer[0]
        #return view

    @property
    def yuv420(self):
        print("Unsafe bgr -> yuv420")
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2YUV_I420)

    @property
    def yuv422(self):
        print("YUV422 conversion: might lead to problems")
        yuv_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2YUV)
        y,u,v = cv2.split(yuv_image)
        u = u[:,::2]
        v = v[:,::2]
        print(y.shape)
        print(u.shape)
        print(v.shape)
        return np.ascontiguousarray(y), np.ascontiguousarray(u), np.ascontiguousarray(v)

    @property
    def gray(self):
        #print("Unsafe gray")
        # return gray aka luminace plane of YUV image.
        gray_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        #print(gray_image.shape)
        return gray_image

    @property 
    def bgr(self):
        #print("Unsafe brg -> bgr")
        return self.frame

    #for legacy reasons.
    @property
    def img(self):
        print("Unsafe img")
        return self.bgr

