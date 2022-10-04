import cv2 #importing OpenCV library
import numpy as np #importing numpy library in order for the OpenCV modules to operate
import RPi.GPIO as rg #importing a special library that is designed to create an environment communication with Raspberry-Pi pins


cap = cv2.VideoCapture("/dev/video0") #calling a function that is used for the recognition of a camera device which is connected to the Raspberry-Pi

rg.setmode(rg.BCM) #Setting the communication mode as "BCM" since there is no physical breadboard connection

rg.setup(18, rg.OUT) #Setting the GPIO18 pin as output 
rg.setup(22,rg.OUT)  #Setting the GPIO22 pin as output

ENA=rg.PWM(18,100)   #Setting the GPIO18 pin as ENA pin in order to control the motorA's speed values
ENB=rg.PWM(22,100)   #Setting the GPIO22 pin as ENB pin in order to control the motorB's speed values

rg.setup(23,rg.OUT)  #Setting the GPIO23 pin as output
rg.setup(24,rg.OUT)  #Setting the GPIO24 pin as output
rg.setup(17,rg.OUT)  #Setting the GPIO17 pin as output
rg.setup(27,rg.OUT)  #Setting the GPIO27 pin as output

ENB.start(0)        #setting the initial speed value as 0 for motorB
ENA.start(0)        #setting the initial speed value as 0 for motorA

rg.setwarnings(False)  #sometimes the system may needs to be shutdown instantly and when it does, the RPi.GPIO module may give some warning errors. This line turns off
                     #those warnings 

I= int() #declaring an empty intiger variable for INTEGRAL segment
K= int() #declaring an empty intiger variable for PROPORTIONAL segment
D= int() #declaring an empty intiger variable for DERIVATIVE segment


Kp= 0.055 #0.058                  #declaring a constant value for PROPORTIONAL segment for "tunning" operation
Ki= 0.00000000001                #declaring a constant value for INTEGRAL segment for "tunning" operation
Kd= 0.0055  #0.005-0.008          #declaring a constant value for DERIVATIVE segment for "tunning" operation

baseA=20  #declaring the base speed value of motorA                         
baseB=20  #declaring the base speed value of motorA 

maxA=90   #declaring the max speed value of motorA 
maxB=90   #declaring the max speed value of motorA 

lastError=0 #declaring an intiger for DERIVATIVE segment to use in order to calculate the error value the system will encounter

def forward(pwmA,pwmB): #creating a function for setting the appropirate speed value for motorA and motorB so that the robot goes forward by various rotation angles
 rg.output(23 ,rg.LOW)
 rg.output(24, rg.HIGH)
 rg.output(27, rg.HIGH)
 rg.output(17, rg.LOW)
 ENA.ChangeDutyCycle(pwmA)
 ENB.ChangeDutyCycle(pwmB)



def PID_control(offset): 

 global P  #setting the empty intiger P variable as global, in order for the PID_control function to recognize that variable
 global I  #setting the empty intiger I variable as global, in order for the PID_control function to recognize that variable
 global D  #setting the empty intiger D variable as global, in order for the PID_control function to recognize that variable
 global lastError #setting the empty intiger lastError variable as global in order for the PID_control function to recognize that variable

 error = 330- offset
 P= error
 I= I + error
 D= error - lastError
 lastError=error


 movement= (Kp*P) + (Ki*I) + (Kd*D)
 speedA= baseA + movement
 speedB= baseB - movement

 if speedA > maxA:
     speedA = maxA
 if speedB > maxB:
     speedB = maxB
 if speedA < 0:
     speedA = 0
 if speedB < 0:
     speedB = 0
 forward(speedA,speedB)

while True: #since a video is a colletcion of photos an infinite loop is necessary in order for the camera to repeatidely take some photos and view them as a video
    
    ret, frame = cap.read() #"read" function takes two variables in order to be called properly. "frame" is the main variable for the video window to be activated
   
    blur = cv2.GaussianBlur(frame,(3,3),0) #blurring the "frame" by 3x3 matrixes in order to neglacte some noise
    
    low_b = np.uint8([21,21,21]) #increasing the 8-bit value of a dark surface in order to create a binary threshold by declaring "low_b" variable
    high_b = np.uint8([0,0,0])   #keeping the 8-bit value of a light surface relative to "low_b" lower in order to create more gap between black and white colors...
    #...by declaring a "high_b" variable
     
    mask = cv2.inRange(blur, high_b, low_b) #masking the blurred frame by "low_b" and "high_b" in order to create a black and white view
    
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #calling a function from OpenCV in order to detect the contours in the...
    #... masked frame. RETR_EXTERNAL parameter is utilized in order to detect the outer lines of an object that is detected and CHAIN_APPROX_SIMPLE parameter is...
    #... utilized in order to to draw the contour according to edge points of a detected object
    
    if len(contours) > 200: #increasing the accuracy of detection by limiting the detected contour lenght by 200 units
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0: #since the center point values that are stored in M variable are listed in an array, unless those values are not 0 the "PID_control" funtion...
        #... will be called 
         cx = int(M['m10'] / M['m00'])
         print("CX : " + str(cx)) #printing cx value

         PID_control(cx) #calling the "PID_control" function with cx parameter



    cv2.imshow("Mask",mask) #displaying the masked frame


    if cv2.waitKey(1) == ord('q'): #if keboard button "q" is pressed: 
        rg.cleanup() #all RPi.GPIO settings will be terminated
        break #the loop will be destroyed
cap.release() #stored images will be deleted from RAMs
cv2.destroyAllWindows() #all windows will be closed
