import cv2
import numpy as np
import imutils
from imutils import contours
from imutils import perspective
from scipy.spatial import distance as dist

#Laver billede om til HSV og bruger inrange til begrænse området i HSV som billedet skal vise
class objectFinderByColor:
    def __init__(self,frame,lowH,highH,lowS,highS,lowV,highV):
        self.hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.lower = np.array([lowH,lowS,lowV])
        self.higher = np.array([highH,highS,highV])
        pass

    def object(self):
        mask = cv2.inRange(self.hsv, self.lower,self.higher)
        return mask

#Definerer midtpunktet mellem 2 kordinater
def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


def find_shape(image,pixelsPerMetric,color):

    X = 0
    Y = 0
    Angle = 0

    while True:

        cv2.waitKey(10)

        
        original_image = image.copy()
        #Farven på texten som bliver skrevet på de viste billeder
        textColor = (0,0,0)

        #mask for rød
        if color == "Red":
            mask = objectFinderByColor(image,0,60,230,255,100,160).object()

        #mask for grøn
        if color == "Green":
            mask = objectFinderByColor(image,50,90,110,255,30,130).object()

        #mask for blå
        if color == "Blue":
            mask = objectFinderByColor(image,80,120,70,255,70,200).object()
        #
        cv2.waitKey(10)

        #cv2.imshow("mask",mask)
        #cv2.imwrite("mask.png",mask)S

        #fjerner unødig støj fra billedet
        median = cv2.medianBlur(mask, 5)

        #cv2.imshow("medianBlur",median)
        #cv2.imwrite("medianBlur.png",median)

        #Closing
        closing = cv2.dilate(median, None, iterations=5)
        closing = cv2.erode(closing, None, iterations=5)
        
        #cv2.imshow("closing",closing)
        #cv2.imwrite("closing.png",closing)

        cv2.waitKey(10)

        # finder 'contours' i billedet
        cnts = cv2.findContours(closing.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        cv2.waitKey(10)

        #hvis der ikke findes nogle 'contour' retunerer den det originale billede og en position som hedder 0,0,0
        if cnts == []:
            print(f"no {color} box!")
            return original_image, [0,0,0]
        
        
        #sorterer 'contours' fra venstre til højre
        (cnts, _) = contours.sort_contours(cnts)

        #
        cv2.waitKey(10)

        #Kigger på hver enkelt 'contour'
        for c in cnts:
            
            #hvis 'contour' er for lille eller stor springes der videre til næste
            if cv2.contourArea(c) < 2500:
                print("small")
                continue

            if cv2.contourArea(c) > 25000:
                print("large")
                continue

            #######################################
            #epsilon = 0.1 * cv2.arcLength(c, True)
            #c = cv2.approxPolyDP(c,epsilon,True)

            # compute the rotated bounding box of the contour
            box = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            
                # order the points in the contour such that they appear
                # in top-left, top-right, bottom-right, and bottom-left
                # order, then draw the outline of the rotated bounding
                # box
            box = perspective.order_points(box)
            cv2.drawContours(original_image, [box.astype("int")], -1, (0, 255, 0), 2)
                # loop over the imageinal points and draw them
            for (x, y) in box:
                cv2.circle(original_image, (int(x), int(y)), 5, (0, 0, 255), -1)

            # unpack the ordered bounding box, then compute the midpoint
            # between the top-left and top-right coordinates, followed by
            # the midpoint between bottom-left and bottom-right coordinates
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = midpoint(tl, tr)
            (blbrX, blbrY) = midpoint(bl, br)

            # compute the midpoint between the top-left and top-right points,
            # followed by the midpoint between the top-righ and bottom-right
            (tlblX, tlblY) = midpoint(tl, bl)
            (trbrX, trbrY) = midpoint(tr, br)

            # draw the midpoints on the image
            cv2.circle(original_image, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
            cv2.circle(original_image, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
            cv2.circle(original_image, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
            cv2.circle(original_image, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
            
            
            # draw lines between the midpoints
            cv2.line(original_image, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                (255, 0, 255), 2)
            cv2.line(original_image, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                (255, 0, 255), 2)

            # compute the Euclidean distance between the midpoints
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

            # compute the size of the object
            dimA = dA / pixelsPerMetric
            dimB = dB / pixelsPerMetric

            # draw the object sizes on the image
            cv2.putText(original_image, "{:.1f}mm".format(dimA),
                (int(tltrX - 15), int(tltrY - 50)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (textColor), 2)
            cv2.putText(original_image, "{:.1f}mm".format(dimB),
                (int(trbrX + 10), int(trbrY - 50)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (textColor), 2)

            rotrect = cv2.minAreaRect(c)
            boxAngle = cv2.boxPoints(rotrect)
            boxAngle = np.int0(boxAngle)
            angle = rotrect[-1]
            #print(round(angle,2))

            # compute the center of the contour
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            #print([cX,cY])
            X = round(cX / pixelsPerMetric,2)
            Y = round(cY / pixelsPerMetric,2)
            
            Angle = round(angle,2)
            center = "X: ",round(cX / pixelsPerMetric,2),"\n","Y:",round(cY / pixelsPerMetric,2),"\nAngle:", round(angle,2)
            # draw the contour and center of the shape on the image
            cv2.drawContours(original_image, [c], -1, (0, 255, 0), 2)
            cv2.circle(original_image, (cX, cY), 7, (255, 255, 255), -1)


            cv2.putText(original_image, f"center:", (cX - 20, cY + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (textColor), 2)
            cv2.putText(original_image, f"     X: {X}", (cX - 20, cY + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (textColor), 2)
            cv2.putText(original_image, f"     Y: {Y}", (cX - 20, cY + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (textColor), 2)
            cv2.putText(original_image, f" Angle: {Angle}", (cX - 20, cY + 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (textColor), 2)
            
            # show the output image
            #cv2.imshow("test", frame)
            #cv2.imshow("Image", original_image)
            cv2.waitKey(10)
            Y = (original_image.shape[0] / pixelsPerMetric)-Y
        #
        cv2.waitKey(10)
        
        #Eventuelt fejlbillede!
        #if X == None or Y == None or Angle == None:
        #    return original_image, [0,0,0] 
        if X == 0 or Y == 0 or Angle == 0:
            return original_image, [0,0,0] 
    
        return original_image, [X,Y,Angle]