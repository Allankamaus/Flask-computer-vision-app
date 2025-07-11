from flask import Flask, jsonify, Response
from flask_cors import CORS
import aiohttp
import cv2
import os
from threading import Event

app = Flask(__name__)
CORS(app)

cap = cv2.VideoCapture(0)
stop_event = Event()


@app.route('/api/test')
def test():
    return jsonify({"text":"hello! test successful"})

@app.route('/save_image')
#camera connection
def capture_video():
    stop_event.clear()
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("Camera Feed", frame)

        #save the captured image
        if ret:
            capture_dir = os.path.join(os.path.dirname(__file__), 'capture')
            if not os.path.exists(capture_dir):
                os.makedirs(capture_dir)
            image_path = os.path.join(capture_dir, 'captured_image.jpg')
            cv2.imwrite(image_path, frame)
            return jsonify({"message": "Image saved successfully in capture folder!"})


        #press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return jsonify({"message": "Capture stopped."})

@app.route('/stop_capture')
def stop_capture():
    stop_event.set()
    return jsonify({"message": "Stopped capturing."})

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)