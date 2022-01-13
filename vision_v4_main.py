from vision_v4 import *

#Lægger vores første state(Inint) over i en variable.
start_state = Inint()
#Oprettelse af statemachine med start state variable
vision_system = StateMachine(start_state)
#Printer det state, state machinen starter i
print("Vision system startet in state", start_state )
#Starter statemachinen
vision_system.Run()