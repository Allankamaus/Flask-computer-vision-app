from flask import Flask, jsonify
import aiohttp
import cv2

app = Flask(__name__)

cap = cv2.VideoCapture(0)


@app.route('/api/test')
def test():
    return jsonify({"text":"hello! test successful"})

@app.route('/save_image')
#camera connection
def capture_video():
    while True:
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