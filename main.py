from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import aiohttp
import cv2, time,requests,math
import os
from threading import Event

app = Flask(__name__)
CORS(app)





cap = cv2.VideoCapture(0)
stop_event = Event()

#make a canny video
def canny_video(low, high):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(grey, low, high)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        ret, buffer = cv2.imencode('.jpg', edges_bgr)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


#flask route for canny video        
@app.route('/canny_video_feed')
def canny_video_feed():
    low = int(request.args.get('Low', 100))
    high = int(request.args.get('High', 200))
    return Response(canny_video(low, high), mimetype='multipart/x-mixed-replace; boundary=frame')

#text connection of flask route
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


#flask route for video feed
@app.route('/video_feed')
def video_feed():
    def generate():
        prev_time = time.time()
        while True:
            
            ret, frame = cap.read()
            if not ret:
                break
            curr_time = time.time()
            fps = (1/(curr_time - prev_time)) if curr_time != prev_time else 0
            prev_time = curr_time
            cv2.putText(frame, f'FPS: {fps}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


#flask route for generating a greyscale image
@app.route('/capture_greyscale')
def capture_greyscale():
    ret, frame = cap.read()
    if not ret:
        return jsonify({"message": "Failed to grab frame"}), 500
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#convert to greyscale
    capture_dir = os.path.join(os.path.dirname(__file__), 'capture')#create capture directory
    if not os.path.exists(capture_dir):
        os.makedirs(capture_dir)
    image_path = os.path.join(capture_dir, 'captured_greyscale.jpg')#save greyscale image
    cv2.imwrite(image_path, grey_frame)
    return jsonify({"message": "Greyscale image saved successfully in capture folder!"})


#blurring faces in the image
@app.route('/Blur')
def blur_face():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    def generate():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                face_roi = frame[y:y+h, x:x+w]
                face_roi = cv2.GaussianBlur(face_roi, (99, 99), 30)
                frame[y:y+h, x:x+w] = face_roi
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/face_detection')
def face_detection():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    def generate():
        prev_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            curr_time = time.time()
            fps = (1/(curr_time - prev_time)) if curr_time != prev_time else 0
            prev_time = curr_time
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 5)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        



    


if __name__ == "__main__":
    app.run(debug=True)