import flask
import aiohttp
import cv2


#camera connection
cap = cv2.VideoCapture(0)

while True:
    #Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("failed to grab frame")
        break

    cv2.imshow("Camera Feed", frame)

    #press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()