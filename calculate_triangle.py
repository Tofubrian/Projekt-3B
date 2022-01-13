import math

#Udregning af trekanter med 3 kordinater
def calculateTriangle(A, B, C):
    # d= sqrt((x2-x1)^2(y2-y1)^2)
    sideAB = math.sqrt((A[0]-B[0])**2+(A[1]-B[1])**2)
    sideAC = math.sqrt((A[0]-C[0])**2+(A[1]-C[1])**2)
    sideBC = math.sqrt((B[0]-C[0])**2+(B[1]-C[1])**2)
    
    #Eventuelt fejlbillede!
    if sideAB == 0 or sideAC == 0 or sideBC == 0:
        return [[0,0,0],[0,0,0]]

    angleA = math.degrees(math.acos((sideAB**2+sideAC**2-sideBC**2)/(2*sideAB*sideAC)))
    angleB = math.degrees(math.acos((sideBC**2+sideAB**2-sideAC**2)/(2*sideAB*sideBC)))
    angleC = math.degrees(math.acos((sideBC**2+sideAC**2-sideAB**2)/(2*sideAC*sideBC)))

    #Retunerer sidernes længde og hjørnerne
    return [[sideAB,sideAC,sideBC],[angleA,angleB,angleC]]


#Udregning af et nyt kordinat ved hjælp af et rotationspunkt, og vinkel
def rotated_coordinate(point_to_rotate,rotatepoint,angle):
    
    #Vinklen bliver omregnet til radian
    angle_radians = math.radians(angle*-1)
    #flytter koordinatet så midtpunktet svarer til 0.0
    v = [point_to_rotate[0] - rotatepoint[0],point_to_rotate[1] - rotatepoint[1]]
    #Ny X position efter flytning med vinklen
    vx = (v[0]*(math.cos(angle_radians))-(v[1]*(math.sin(angle_radians))))
    #Ny Y position efter flytning med vinklen
    vy = (v[0]*(math.sin(angle_radians))+(v[1]*(math.cos(angle_radians))))
    v2=[vx,vy]
    #X og Y bliver flyttet tilbage til så midtpunktet er det originale
    v3 = [round(v2[0]+rotatepoint[0],0),round(v2[1]+rotatepoint[1],0)]
    
    #Retunerer ny position
    return v3
