import numpy as np
import cv2
#from numpy.lib.function_base import angle, copy
#from numpy.lib.type_check import imag
from pyzbar.pyzbar import decode#, ZBarSymbol
#from PIL import Image
from calculate_triangle import calculateTriangle, rotated_coordinate
from OAKWrapper import *
from math import sqrt #,pi


def rotate_image(image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result



def rotate_pickup_zone(image, height_width_ratio, left, right,ImageAngle):
    
    #Variabler som skal bruges i denne funktion
    
    #Midtpunkt af billede defineres
    midpoint = image.shape
    midpoint = [midpoint[1]/2,midpoint[0]/2]

    #Roterer billedet i forhold til vinkel, så billedet ligger lige
    rotated_image = rotate_image(image,ImageAngle)

    cropped_image = rotated_image.copy()

    #Her findes øverst højre hjørne af billedet, ved hjælp af bredde højde forskellen
    distance_between_left_right = right[0]-left[0]
    height = distance_between_left_right * height_width_ratio
    top = right[1]-height
    if right[1]-height < 0:
        top = 0
    top_right = [right[0],top]

    #Her defineres start og slut på X og Y asken til beskæring af billedet
    y_start = int(round(top_right[1],0))
    y_end = int(round(left[1],0))
    x_start = int(round(left[0],0))
    x_end = int(round(top_right[0],0))
    cropped_image = cropped_image[y_start:y_end,x_start:x_end]
    
    #Retunerer beskåret billede + de nye positioner for QR-koderne
    return cropped_image,left,right




def udregn_verden(image, left_name_str, right_name_str,distance_left_right_mm):

    image_qr = image.copy()

    right = 0.0
    left = 0.0


    #Midtpunkt af billede defineres
    midpoint = image.shape
    midpoint = [midpoint[1]/2,midpoint[0]/2]

            # lave en variable af de 3 hjørner og de 3 farver.
    for barcode in decode(image_qr):
            #print(barcode.data.decode('utf-8'))
            barcodestring = (barcode.data.decode('utf-8'))
            myData = barcode.data.decode('utf-8')
            #print(type(myData))
            pts = np.array([barcode.polygon],np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(image_qr,[pts],True,(255,0,255),5)
            pts2 = barcode.rect
            cv2.putText(image_qr,myData,(pts2[0],pts2[1]),cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,255),2 )
            midX = (barcode.polygon[0][0] + barcode.polygon[2][0]) * 0.5
            midY = (barcode.polygon[0][1] + barcode.polygon[2][1]) * 0.5

    #Der skal først udregnes vinkle før alt andet kan udregnes.

            barcodemidpoint = [midX, midY]
            if barcodestring == right_name_str:
                right = barcodemidpoint

            if barcodestring == left_name_str:
                left = barcodemidpoint

    if right == 0.0 or left == 0.0:
        return 0,0,0,0

    #Her laves 2 punkter ud fra referencekordinaterne, således at de danner en trekant
    mix1 = [right[0],left[1]]
    mix2 = [left[0],right[1]]
    
    #Her bruges den mindste af de 2 trkanter
    if right[1] > left[1]:
        mix = mix1
    if right[1] < left[1]:
        mix = mix2
 
    #Her udregnes hvordan kordinaterne kommer til at ligge så vi kan regne vinklen ud i forhold til referencepunkterne
    referenceTriangle = calculateTriangle(right,left,mix)
 
    #Her bruges den mindste af de 2 trkanter
    if mix1[1] < mix2[1]:
        ImageAngle = referenceTriangle[1][1]
    if mix1[1] > mix2[1]:
        ImageAngle = -referenceTriangle[1][0]

    #QR-kodernes placering roteres i forhold til vinklen
    left = rotated_coordinate(left,midpoint,ImageAngle)
    right = rotated_coordinate(right,midpoint,ImageAngle)

    #sideAB = math.sqrt((A[0]-B[0])**2+(A[1]-B[1])**2)
    mmPerPixel = (sqrt((right[0]-left[0])**2+(right[1]-left[1])**2))/distance_left_right_mm
    #print("left",left)
    #print("right",right)

    return mmPerPixel, left, right, ImageAngle
            



def rotated_drop_zone(image, left, ImageAngle, mmPerPixel):

    #Variabler som skal bruges i denne funktion
    image_qr = image.copy()
    red = [0,0]
    green = [0,0]
    blue = [0,0]

    #Finder midtpunktet af billedet
    midpoint = image.shape
    midpoint = [midpoint[1]/2,midpoint[0]/2]

    #Kigger billedet igennem for QR-koder, og angiver hvor de er på det i kordinater
    for barcode in decode(image_qr):
        barcodestring = (barcode.data.decode('utf-8'))
        myData = barcode.data.decode('utf-8')
        pts = np.array([barcode.polygon],np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(image_qr,[pts],True,(255,0,255),5)
        pts2 = barcode.rect
        cv2.putText(image_qr,myData,(pts2[0],pts2[1]),cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,255),2 )
        
        #definerer midtpunkt af QR-kode
        midX = (barcode.polygon[0][0] + barcode.polygon[2][0]) * 0.5
        midY = (barcode.polygon[0][1] + barcode.polygon[2][1]) * 0.5
        barcodemidpoint = [midX, midY]
        
        #Navnet på QR-koden buges til at give den korrekte variabel sit kordinat
        if barcodestring == "Red":
            red = barcodemidpoint
    
        if barcodestring == "Green":
            green = barcodemidpoint
     
        if barcodestring == "Blue":
            blue = barcodemidpoint
     
    #Roterer billedet i forhold til vinkler, så billedet ligger lige
    rotated_image = rotate_image(image_qr,ImageAngle)

    #Visning af billedet roteret
    cv2.imshow("qr",rotated_image)
    #cv2.imwrite("qr.png",rotated_image)

    #Hvis der er fundet en rød, får denne en position her
    if red != [0,0]:
        red = rotated_coordinate(red,midpoint,ImageAngle)
        red = [red[0]-left[0],red[1]-left[1]]
        red = [red[0]/mmPerPixel,red[1]/mmPerPixel]

    #Hvis der er fundet en grøn, får denne en position her
    if green != [0,0]:
        green = rotated_coordinate(green,midpoint,ImageAngle)
        green = [green[0]-left[0],green[1]-left[1]]
        green = [green[0]/mmPerPixel,green[1]/mmPerPixel]

    #Hvis der er fundet en blå, får denne en position her
    if blue != [0,0]:
        blue = rotated_coordinate(blue,midpoint,ImageAngle)
        blue = [blue[0]-left[0],blue[1]-left[1]]
        blue = [blue[0]/mmPerPixel,blue[1]/mmPerPixel] 

    #Retunerer kordinater for placering af rød, grøn og blå
    return red,green,blue