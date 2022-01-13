import socket
import OAKWrapper

# Super class for a state object
class State:
    s_m = None

    def Execute(self):
        pass

    def Enter(self):
        pass

    def Exit(self):
        pass


# Implementation of a state machine for running states
class StateMachine:
    def __init__(self, state):
        #Statemachine dependencies
        self.state = state
        self.state.s_m = self

        #test
        self.step = None

        #Socket variabler
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = str
        self.port = int
        self.com = None
        self.add = None

        #Komunikation variabler
        #self.start_pos = None

        #UR robot positions variabler
        self.find_pos = None
        self.ur_x = None
        self.ur_y = None
        self.ur_z = None
        self.ur_angle = None
        self.cam_pos = None

        self.new_pos = None

        self.dropzone = None

        #Kamera
        self.cap = None


        #Flow variabler
        self.verden_udregnet = False
        self.mm_per_pixel = None

        self.q1 = None
        self.q2 = None

        #Verden udregnet variabler
        self.left = None
        self.right = None
        self.verden_udregnet = False
        self.image_angle = None


    def Run(self):
        self.state.Enter()
        self.running = True
        while self.running:
            self.state.Execute()

    def ChangeState(self, newState):
        print("New state is :", type(newState))
        self.state.Exit()
        self.state = newState
        self.state.s_m = self
        self.state.Enter()