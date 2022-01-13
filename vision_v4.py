from s_m import *
from math import pi
from find_shapes import find_shape
from rotate_with_qr2 import *
from OAKWrapper import *
import cv2
import numpy
import time

class Inint(State):
    #Initialiseringen af porgrammet
    def Execute(self):
        #Variabler til socket
        self.s_m.host = "192.168.1.17"
        self.s_m.port = 9090

        #Start af kamera
        self.s_m.cap = OAKCamColorDepth()
        
        #Kordinater til camposition
        self.s_m.cam_pos = b"(-0.029,-0.270,0.660,2.200,3.223,1.960)"
        

        #Variabler til udregning af verden
        self.s_m.verden_udregnet = False
        self.s_m.q1 = "Bottom left"
        self.s_m.q2 = "Top right"

        self.s_m.ChangeState(Start_kom())

class Start_kom(State):
#Starter servren og venter på ur robotten forbinder

    def Execute(self):
        #stater serveren
        self.s_m.server.bind((self.s_m.host, self.s_m.port))
        self.s_m.server.listen(1)
        self.s_m.com, self.s_m.add = self.s_m.server.accept()
        self.s_m.ChangeState(UR_nul_pos())

    def Exit(self):
        #Printer adressen på clienten
        print("Connectet to: ", self.s_m.add)
        cv2.waitKey(500)

class UR_nul_pos(State):
#Modtager nul positionen fra robotten og lægger denne over i x, y, z og angle variabler

    def Execute(self):

        while True:
            #Sender "1" til robotten og venter på svar
            self.s_m.com.sendall(b"(1)")
            from_ur = self.s_m.com.recv(4096).decode("ascii")

            if from_ur != None:
                #Svaret er nul positionen, der bliver fjernet tegn der ikke skal bruges.
                print(from_ur)
                self.s_m.find_pos = from_ur.replace("p","").replace("[","").replace("]","")
                self.s_m.find_pos = self.s_m.find_pos.split(",")

                # UR start position ved qr kode lægges over i hver deres variable
                self.s_m.ur_x = float(self.s_m.find_pos[0])
                self.s_m.ur_y = float(self.s_m.find_pos[1])
                self.s_m.ur_z = float(self.s_m.find_pos[2])
                self.s_m.ur_angle = 2 * pi + float(self.s_m.find_pos[5])
                break
        self.s_m.ChangeState(UR_cam_pos())

class UR_cam_pos(State):
#Sender cam position koordinater til UR

    def Execute(self):
        #Sender koordinater og venter på svar
        self.s_m.com.sendall(self.s_m.cam_pos)
        while True:
            from_ur = self.s_m.com.recv(4096)
            print("fra UR loop", from_ur)
            if from_ur == b"1":
                print("1 fra UR")
                break

        self.s_m.ChangeState(Find_shapes())

class Find_shapes(State):
#Tager et billede og køre vores vision flow, finder qr koder og klodser, hvis position bliver lagt ned i variabler til afsendelse
    def Enter(self):
        #Nulstilling af positioner, så dataen fra sidste gennemløb ikke bliver brugt
        self.s_m.new_pos = None
        self.s_m.dropzone = None


    def Execute(self): 

        #Oprettelse af variabler kun brugt i denne funktion
        red_checked = None
        green_checked = None
        blue_checked = None
        new_picture = False
        
        #Kamera fokusere
        time.sleep(1)
        #Tager billede
        image = self.s_m.cap.getFrame()
        cv2.imshow("before", image)
        cv2.waitKey(10)
        
        while True:
            #Hvis der ikke bliver taget et billede prøver den igen
            if image.shape[0] == 0 or image.shape[1] == 0:
                while True:
                    image = self.s_m.cap.getFrame()
                    cv2.imshow("Klods", image)
                    cv2.waitKey(10)
                    if image.shape[0] != 0 or image.shape[1] != 0:
                        break
                    print("fejl billede")

            #sæt antal pixel der går per mm ved et kendt 2 kendte referencepunkter
            if self.s_m.verden_udregnet == False:
                self.s_m.mm_per_pixel,  self.s_m.left, self.s_m.right, self.s_m.image_angle  = udregn_verden(image, self.s_m.q1, self.s_m.q2, 254.0)
                if self.s_m.mm_per_pixel == 0:
                    print("Kan ikke læse qr kode går i new_picture")
                    new_picture = True
                    break
                print("mm per pixel: ", self.s_m.mm_per_pixel)
                self.s_m.verden_udregnet = True
            
            #Finder lokationer for rød, grøn og blå
            red_dropzone, green_dropzone, blue_dropzone = rotated_drop_zone(image,  self.s_m.left, self.s_m.image_angle, self.s_m.mm_per_pixel)

            #Hvis der ikke er nogle ledige pladser går den i new_picture
            if red_dropzone == [0,0] and green_dropzone == [0,0] and blue_dropzone == [0,0]:
                print("No space to place boxes, going to new_picture")
                new_picture = True
                break

            #Hvis der er en rød plads og rød ikke er tjekket kigger den efter rød farve
            if red_dropzone != [0,0] and red_checked != 1:
                color = "Red"
            
            #Hvis der er en grøn plads og grøn ikke er tjekket kigger den efter grøn farve
            if green_dropzone != [0,0] and green_checked != 1:
                color = "Green"
            
            #Hvis der er en blå plads og blå ikke er tjekket kigger den efter blå farve
            if blue_dropzone != [0,0] and blue_checked != 1:
                color = "Blue"

            #Vælger dropzone afhængigt af farve
            if color == "Red":
                self.s_m.dropzone = red_dropzone
            elif color == "Green":
                self.s_m.dropzone = green_dropzone
            elif color == "Blue":
                self.s_m.dropzone = blue_dropzone
            else: self.s_m.dropzone = None

            #Her bliver billedet beskåret, således at det kun er i et kontrolleret område at vi kigger efter klodser, dette gøres ved hjælp af QR+koder
            cropped, self.s_m.left, self.s_m.right = rotate_pickup_zone(image, 0.5625,  self.s_m.left, self.s_m.right, self.s_m.image_angle)
           
            # Hvis der ikke er et billede vil den printe en fejl, !!Skal ikke med i aflevering!!
            if cropped.shape[0] == 0 or cropped.shape[1] == 0:
                print("Fejl i croppede billede")
            
            #På det beskårede billede bliver der kigget efter klodser i den farve som er valgt ovenfor
            if color != None:
                cropped, shape = find_shape(cropped, self.s_m.mm_per_pixel, color)
            cv2.waitKey(10)

            #Checker for rød
            if shape == [0,0,0] and color == "Red":
                red_checked = 1
                color = None
                continue
            
            #Checker for grøn
            if shape == [0,0,0] and color == "Green":
                green_checked = 1
                color = None
                continue
            
            #Checker for blue
            if shape == [0,0,0] and color == "Blue":
                blue_checked = 1
                color = None
                continue

            #Hvis den har fundet en klods og er kommet hertil, vil den nulstille checked variablerne, da der kan være dukket en ny klods op
            if shape != [0,0,0]:
                red_checked = 0
                green_checked = 0
                blue_checked = 0

                #Hvis der ikke er nogle klodser går den i new_picture
            if red_checked == 1 and green_checked == 1 and blue_checked == 1:
                print("No boxes, going to new_picture (all checkede)")
                red_checked = 0
                green_checked = 0
                blue_checked = 0
                new_picture = True
                break
            
            #Hvis der ikke er nogle klodser der matcher ledige pladser går den i new_picture
            if color == None:
                print("No match, going to new_picture")
                red_checked = 0
                green_checked = 0
                blue_checked = 0
                new_picture = True
                break

            
            #Vis klodser funder i det beskårne billede
            cv2.imshow("cropped", cropped)
            cv2.waitKey(10)

            #Printer i terminalen hvilken klods der skal hentes
            print("Box: ", shape)

            #Printer i terminalen hvor klodsen skal placeres
            print("Placement: ", self.s_m.dropzone)
  

            
            #Nye positioner for placering af klods som skal hentes bliver skrevet i en variabel
            ur_new_x = self.s_m.ur_x + shape[1]/1000
            ur_new_y = self.s_m.ur_y - shape[0]/1000
            ur_new_angle = self.s_m.ur_angle - (pi * 2 / 360 * shape[2])
            self.s_m.new_pos = "("+str(ur_new_x)+","+str(ur_new_y)+","+str(self.s_m.ur_z)+",0,0,"+str(ur_new_angle)+")"
            self.s_m.new_pos = self.s_m.new_pos.encode("ascii")

            #Position til placering af klods bliver sendt til UR
            self.s_m.dropzone = "("+str(self.s_m.ur_x-(self.s_m.dropzone[1]/1000))+","+str(self.s_m.ur_y-(self.s_m.dropzone[0]/1000))+","+str(self.s_m.ur_z)+",0,0,"+str(self.s_m.find_pos[5])+")"
            self.s_m.dropzone = self.s_m.dropzone.encode("ascii")
            
            if self.s_m.new_pos != None and self.s_m.dropzone != None:
                new_picture = False
                break
            
        #Hvis der skal tages et nyt billede vil den gå i Tag_nyt_billede, hvis den har fundet dropzone og klods, vi den sende data til UR i Send_kords
        if new_picture == False:    
            self.s_m.ChangeState(Send_kords())
        elif new_picture == True:
            self.s_m.ChangeState(Tag_nyt_billede())

class Send_kords(State):
#Sender kordinaterne til UR
    def Execute(self):
        #Sender "2" til robotten for at aktivere modtagelsen af positioner
        self.s_m.com.sendall(b"(2)")
        #Sender klods position til robot
        while True:
            from_ur = self.s_m.com.recv(4096)
            #Hvis robotten sender "1", vil den svare med klods positionen
            if from_ur == b"1":
                self.s_m.com.sendall(self.s_m.new_pos)
                from_ur = None
                break
        
        #Sender dropzone position til robotten
        while True:
            from_ur = self.s_m.com.recv(4096)
            #Hvis robotten sender "1", vil den svare med dropzone position
            if from_ur == b"1":
                cv2.waitKey(10)
                self.s_m.com.sendall(self.s_m.dropzone)
                from_ur = None
                break
        self.s_m.ChangeState(Standby())

class Standby(State):
#Venter på robotten har afleveret klodsen og er tilbage i cam position
    def Execute(self):
        while True:
            from_ur = self.s_m.com.recv(4096)
            if from_ur == b"1":
                break
        self.s_m.ChangeState(Find_shapes())

class Tag_nyt_billede(State):
#Der er ikke fundet nok i billede kunne køre programmet, så den venter i 3 sekunder og kører igen.
    def Execute(self):
        time.sleep(3)
        self.s_m.ChangeState(Find_shapes())
