from flask import Flask, jsonify, Response, request, send_file
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
    return jsonify({"text":"success"})

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
            faces = face_cascade.detectMultiScale(gray, 1.3, 10)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 5)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        
@app.route('/colored_border')
def colored_border():
    low = int(request.args.get('Low', 100))
    high = int(request.args.get('High', 200))
    def generate():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(grey,high,low)
            color_frame = frame.copy()
            color_mask = edges.astype(bool)
            color_frame[color_mask] = [0, 255, 0]    
    # Overlay green edges on the color frame
            color_frame[color_mask] = [0, 255, 0]  # Green
            _, buffer = cv2.imencode('.jpg', color_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def downsample_image():
    img_path = os.path.join(os.path.dirname(__file__), 'capture', 'captured_image.jpg')
    img = cv2.imread(img_path)
    if img is None:
        print("Image not found or path is incorrect!")
        return None
    small = cv2.pyrDown(img)
    downsample_path = os.path.join(os.path.dirname(__file__), 'capture', 'downsample.jpg')
    cv2.imwrite(downsample_path, small)
    print("Downsampled image saved as", downsample_path)
    return downsample_path

@app.route('/downsample', methods=['POST'])
def downsample_route():
    path = downsample_image()
    if path:
        return jsonify({'message': 'Downsampled image saved!', 'path': '/capture/downsample.jpg'})
    else:
        return jsonify({'message': 'Source image not found!'}), 404

@app.route('/show_downsample')
def show_downsample():
    downsample_path = os.path.join(os.path.dirname(__file__), 'capture', 'downsample.jpg')
    return send_file(downsample_path, mimetype='image/jpeg')

@app.route('/save_canny_image')
def save_canny_image():
    low = 100
    high = 200
    ret, frame = cap.read()
    if not ret:
        return jsonify({"message": "Failed to grab frame"}), 500
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(grey, low, high)
    color_frame = frame.copy()
    mask = edges.astype(bool)
    color_frame[mask] = [255, 255, 255]  # White edges
    capture_dir = os.path.join(os.path.dirname(__file__), 'capture')
    if not os.path.exists(capture_dir):
        os.makedirs(capture_dir)
    image_path = os.path.join(capture_dir, 'captured_image.jpg')
    cv2.imwrite(image_path, color_frame)
    return jsonify({"message": "Canny image saved successfully!"})

@app.route('/save_blur_image')
def save_blur_image():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    ret, frame = cap.read()
    if not ret:
        return jsonify({"message": "Failed to grab frame"}), 500
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        face_roi = frame[y:y+h, x:x+w]
        face_roi = cv2.GaussianBlur(face_roi, (99, 99), 30)
        frame[y:y+h, x:x+w] = face_roi
    capture_dir = os.path.join(os.path.dirname(__file__), 'capture')
    if not os.path.exists(capture_dir):
        os.makedirs(capture_dir)
    image_path = os.path.join(capture_dir, 'captured_image.jpg')
    cv2.imwrite(image_path, frame)
    return jsonify({"message": "Blurred face image saved successfully!"})

@app.route('/save_face_detection_image')
def save_face_detection_image():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    ret, frame = cap.read()
    if not ret:
        return jsonify({"message": "Failed to grab frame"}), 500
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 5)
    capture_dir = os.path.join(os.path.dirname(__file__), 'capture')
    if not os.path.exists(capture_dir):
        os.makedirs(capture_dir)
    image_path = os.path.join(capture_dir, 'captured_image.jpg')
    cv2.imwrite(image_path, frame)
    return jsonify({"message": "Face detection image saved successfully!"})

@app.route('/save_colored_edges_image')
def save_colored_edges_image():
    low = 100
    high = 200
    ret, frame = cap.read()
    if not ret:
        return jsonify({"message": "Failed to grab frame"}), 500
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(grey, low, high)
    color_frame = frame.copy()
    mask = edges.astype(bool)
    color_frame[mask] = [0, 255, 0]  # Green edges
    capture_dir = os.path.join(os.path.dirname(__file__), 'capture')
    if not os.path.exists(capture_dir):
        os.makedirs(capture_dir)
    image_path = os.path.join(capture_dir, 'captured_image.jpg')
    cv2.imwrite(image_path, color_frame)
    return jsonify({"message": "Colored edges image saved successfully!"})


if __name__ == "__main__":
    app.run(debug=True)