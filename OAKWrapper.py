import cv2
import depthai as dai

class OAKCamColor:
    def __init__(self, previewWidth: int = 300, previewHeight: int = 300, interleaved: bool = False, colorOrder: dai.ColorCameraProperties.ColorOrder = dai.ColorCameraProperties.ColorOrder.RGB):
        # Create pipeline
        pipeline = dai.Pipeline()

        # Define source and output
        self.camRgb = pipeline.create(dai.node.ColorCamera)

        xoutRgb = pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")

        xoutRgbPrev = pipeline.create(dai.node.XLinkOut)
        xoutRgbPrev.setStreamName("rgbPrev")
        
        controlIn = pipeline.create(dai.node.XLinkIn)
        controlIn.setStreamName('control')

        # Properties
        self.camRgb.setPreviewSize(previewWidth, previewHeight)
        self.camRgb.setInterleaved(interleaved)
        self.camRgb.setColorOrder(colorOrder)

        # Linking
        self.camRgb.video.link(xoutRgb.input)
        self.camRgb.preview.link(xoutRgbPrev.input)
        controlIn.out.link(self.camRgb.inputControl)

        # Connect to device and start pipeline
        self.device = dai.Device(pipeline)

        # Output queues
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
        self.qRgbPrev = self.device.getOutputQueue(name="rgbPrev", maxSize=1, blocking=False)

        print("Color cam setup done")

    def getDevice(self):
        return self.device

    def getFrame(self):
        inRgb = self.qRgb.get()
        return inRgb.getCvFrame()

    def getPreviewFrame(self):
        inRgbPrev = self.qRgbPrev.get()
        return inRgbPrev.getCvFrame()

    def triggerAutoFocus(self, mode: dai.CameraControl.AutoFocusMode = dai.CameraControl.AutoFocusMode.OFF):
        #print("Autofocus trigger (and disable continuous)")
        ctrl = dai.CameraControl()
        ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.AUTO)
        ctrl.setAutoFocusTrigger()
        self.device.getInputQueue('control').send(ctrl)

    def startContinousAutoFocus(self):
        #print("Autofocus enable, continuous")
        ctrl = dai.CameraControl()
        ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
        self.device.getInputQueue('control').send(ctrl)


# https://docs.luxonis.com/projects/api/en/latest/samples/StereoDepth/depth_preview/#depth-preview
class OAKCamDepth:
    def __init__(self, LRCheck: bool = False):
        # Create pipeline
        pipeline = dai.Pipeline()

        # Define source and output
        monoLeft = pipeline.create(dai.node.MonoCamera)
        monoRight = pipeline.create(dai.node.MonoCamera)
        depth = pipeline.create(dai.node.StereoDepth)

        xout = pipeline.create(dai.node.XLinkOut)
        xout.setStreamName("disparity")

        # Properties
        monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
        monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

        # Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
        depth.initialConfig.setConfidenceThreshold(245)
        # Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
        depth.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
        depth.setLeftRightCheck(LRCheck)

        # Linking
        monoLeft.out.link(depth.left)
        monoRight.out.link(depth.right)
        depth.disparity.link(xout.input)

        # Connect to device and start pipeline
        self.device = dai.Device(pipeline)

        # Output queues
        self.qDepth = self.device.getOutputQueue(name="disparity", maxSize=1, blocking=False)

        print("depth cam setup done")

    def getDevice(self):
        return self.device

    def getDepthFrame(self):
        inDepth = self.qDepth.get()
        return inDepth.getCvFrame()

    def getDepthFrameColorMapped(self):
        qDepth = self.device.getOutputQueue(name="disparity", maxSize=1, blocking=False)
        inDepth = qDepth.get().getCvFrame()
        inDepth = cv2.applyColorMap(inDepth, cv2.COLORMAP_JET)
        return inDepth


class OAKCamColorDepth:
    def __init__(self, previewWidth: int = 300, previewHeight: int = 300, interleaved: bool = False, colorOrder: dai.ColorCameraProperties.ColorOrder = dai.ColorCameraProperties.ColorOrder.RGB, LRCheck: bool = False):
        # Create pipeline
        pipeline = dai.Pipeline()

        # Define source and output (color)
        self.camRgb = pipeline.create(dai.node.ColorCamera)

        xoutRgb = pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")

        xoutRgbPrev = pipeline.create(dai.node.XLinkOut)
        xoutRgbPrev.setStreamName("rgbPrev")
        
        controlIn = pipeline.create(dai.node.XLinkIn)
        controlIn.setStreamName('control')

        # Properties (color)
        self.camRgb.setPreviewSize(previewWidth, previewHeight)
        self.camRgb.setInterleaved(interleaved)
        self.camRgb.setColorOrder(colorOrder)

        # Linking (color)
        self.camRgb.video.link(xoutRgb.input)
        self.camRgb.preview.link(xoutRgbPrev.input)
        controlIn.out.link(self.camRgb.inputControl)

        # Define source and output (Stereo)
        monoLeft = pipeline.create(dai.node.MonoCamera)
        monoRight = pipeline.create(dai.node.MonoCamera)
        depth = pipeline.create(dai.node.StereoDepth)

        xout = pipeline.create(dai.node.XLinkOut)
        xout.setStreamName("disparity")

        # Properties (Stereo)
        monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
        monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

        # Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
        depth.initialConfig.setConfidenceThreshold(245)
        # Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
        depth.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
        depth.setLeftRightCheck(LRCheck)

        # Linking (Stereo)
        monoLeft.out.link(depth.left)
        monoRight.out.link(depth.right)
        depth.disparity.link(xout.input)

        # Connect to device and start pipeline
        self.device = dai.Device(pipeline)

        # Output queues
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
        self.qRgbPrev = self.device.getOutputQueue(name="rgbPrev", maxSize=1, blocking=False)
        self.qDepth = self.device.getOutputQueue(name="disparity", maxSize=1, blocking=False)

        print("Color+Depth cam setup done")

    def getDevice(self):
        return self.device

    def getFrame(self):
        inRgb = self.qRgb.get()
        return inRgb.getCvFrame()

    def getPreviewFrame(self):
        inRgbPrev = self.qRgbPrev.get()
        return inRgbPrev.getCvFrame()

    def triggerAutoFocus(self, mode: dai.CameraControl.AutoFocusMode = dai.CameraControl.AutoFocusMode.OFF):
        #print("Autofocus trigger (and disable continuous)")
        ctrl = dai.CameraControl()
        ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.AUTO)
        ctrl.setAutoFocusTrigger()
        self.device.getInputQueue('control').send(ctrl)

    def startContinousAutoFocus(self):
        #print("Autofocus enable, continuous")
        ctrl = dai.CameraControl()
        ctrl.setAutoFocusMode(dai.CameraControl.AutoFocusMode.CONTINUOUS_VIDEO)
        self.device.getInputQueue('control').send(ctrl)

    def getDepthFrame(self):
        inDepth = self.qDepth.get()
        return inDepth.getCvFrame()

    def getDepthFrameColorMapped(self):
        inDepth = self.qDepth.get().getCvFrame()
        inDepth = cv2.applyColorMap(inDepth, cv2.COLORMAP_JET)
        return inDepth