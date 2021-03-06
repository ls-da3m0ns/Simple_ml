import cv2
import numpy as np
from PIL import Image, ImageFilter
from cv2 import dnn_superres
from PIL.ImageFilter import (
BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE,
EMBOSS, FIND_EDGES, SMOOTH, SMOOTH_MORE, SHARPEN
)
import base64
pathImage = ""
flag = 0

def reorder(myPoints):

    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)

    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] =myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] =myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]

    return myPointsNew

def biggestContour(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 5000:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest,max_area

def drawRectangle(img,biggest,thickness):
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)

    return img

def image(input):
    img = cv2.imread(pathImage+input)
    widthImg = 1600
    heightImg = 768
    img = cv2.resize(img, (widthImg, heightImg)) # RESIZE IMAGE
    imgBlank = np.zeros((heightImg,widthImg, 3), np.uint8) # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # CONVERT IMAGE TO GRAY SCALE
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1) # ADD GAUSSIAN BLUR
    thres=[200,255]
    imgThreshold = cv2.Canny(imgBlur,thres[0],thres[1]) # APPLY CANNY BLUR
    kernel = np.ones((5, 5))
    imgDial = cv2.dilate(imgThreshold, kernel, iterations=2) # APPLY DILATION
    imgThreshold = cv2.erode(imgDial, kernel, iterations=1)  # APPLY EROSION

    ## FIND ALL COUNTOURS
    imgContours = img.copy() # COPY IMAGE FOR DISPLAY PURPOSES
    imgBigContour = img.copy() # COPY IMAGE FOR DISPLAY PURPOSES
    contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # FIND ALL CONTOURS
    cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10) # DRAW ALL DETECTED CONTOURS


    # FIND THE BIGGEST COUNTOUR
    biggest, maxArea = biggestContour(contours) # FIND THE BIGGEST CONTOUR
    if biggest.size != 0:
        biggest=reorder(biggest)
        cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20) # DRAW THE BIGGEST CONTOUR
        imgBigContour = drawRectangle(imgBigContour,biggest,2)
        pts1 = np.float32(biggest) # PREPARE POINTS FOR WARP
        pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

        #REMOVE 20 PIXELS FORM EACH SIDE
        imgWarpColored=imgWarpColored[20:imgWarpColored.shape[0], 20:imgWarpColored.shape[1]]
        imgWarpColored = cv2.resize(imgWarpColored,(widthImg,heightImg))

        # APPLY ADAPTIVE THRESHOLD
        imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY)
        imgAdaptiveThre= cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
        imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
        imgAdaptiveThre=cv2.medianBlur(imgAdaptiveThre,3)

        # cv2.imwrite(pathImage +"Images/output.jpg",imgWarpColored)
        flag = 0
        return imgWarpColored,flag
    else:
        flag = 1 
        # cv2.imwrite(pathImage+"Images/original.jpg",img)
        return img,flag
    

def sharpen(Image):
    image = Image
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpen = cv2.filter2D(image, -1, sharpen_kernel)
    # cv2.imwrite(pathImage+"Images/sharpen.jpg", sharpen)
    return sharpen 

def super_resolution(sharpen):
    sr = dnn_superres.DnnSuperResImpl_create()    # Read image
    image = sharpen
    path = pathImage+"models/FSRCNN_x4.pb"
    sr.readModel(path)
    sr.setModel("fsrcnn", 4)
    result = sr.upsample(image)
    #cv2.imwrite(pathImage+"Images/upscaled.jpg", result)
    return result

def smooth(path):
    img = Image.open(path)
    img1 = img.filter(SMOOTH_MORE)
    img1.save(path)

def convertToString(data):
    with open(data, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode('utf-8')


"""curl -k -X POST "https://api.symbl.ai/oauth2/token:generate" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d $'{
      "type" : "application",
      "appId": "'4a31355a776f68563553574a6e3352546731795a7256676e3639613562453237'",
      "appSecret": "'5f664c686970383671785a6a396a464d5f6f314c523961554e4e3643577269433168645a7971417a45316b517867377530772d6148442d7a754e395a514e3055'"
    }'
    eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFVUTRNemhDUVVWQk1rTkJNemszUTBNMlFVVTRRekkyUmpWQ056VTJRelUxUTBVeE5EZzFNUSJ9.eyJodHRwczovL3BsYXRmb3JtLnN5bWJsLmFpL3VzZXJJZCI6IjQ3ODM1MDE2NjU2MzIyNTYiLCJpc3MiOiJodHRwczovL2RpcmVjdC1wbGF0Zm9ybS5hdXRoMC5jb20vIiwic3ViIjoiSjE1WndvaFY1U1dKbjNSVGcxeVpyVmduNjlhNWJFMjdAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vcGxhdGZvcm0ucmFtbWVyLmFpIiwiaWF0IjoxNjMyMDI2MzQyLCJleHAiOjE2MzIxMTI3NDIsImF6cCI6IkoxNVp3b2hWNVNXSm4zUlRnMXlaclZnbjY5YTViRTI3IiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIn0.hGaI9PfuuKGoBFS_W0pka_QCeaZevu8JSP5acgINulV4mVdhxdGHpqjBFTH3AN6B98KBEbZaxZyeB2yuGbkraNfU343iCZUfmOFDTD3igXPinLUfSybnnpI_6LvjwvATknaMRyWyVEQqqeb5gTJ3DrONEl3nwGPdFQjbwmTUuiLbcb49kJGZN1VYFmQFIfmy9n4C3UOtz904TqIq6yCwBtMdaoWoQZjmK1C83SSHbzMRSCwYCD1v1004YK_ZclBUwl9G3Jl5M2L9d_nOaMXy-4QNaFJV9eaTrWK7XXTaySptRztcXrZO-yxgqb-uBBro9dzrBTwsY-2zffcMgqj5JQ
    """