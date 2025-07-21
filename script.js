//Testing fetch api to get data from flask server
fetch('http://127.0.0.1:5000/api/test')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById("test").innerHTML = data.text;
    })
    .catch(error => {
        console.log("Error:", error);
    })

    //fetch image caputre from flask server
// Function to call /save_image when button is pressed
function captureImage() {
    fetch('http://127.0.0.1:5000/save_image')
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            alert("Capture successful!");
            document.getElementById("normalImage").style.display = "block";
            document.getElementById("photoLabel").style.display = "block";
        })
        .catch(error => {
            alert("Error: " + error);
        });
}

function stopCapturing() {
    fetch('http://127.0.0.1:5000/stop_capture')
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            alert("Error: " + error);
        });
}

//function to capture greyscale image
function captureGreyScale(){
    fetch('http://127.0.0.1:5000/capture_greyscale')
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            alert("Greyscale capture successful!")
        })
        .catch(error => {
            alert("Oops! Error: " + error);
        })
}

let currentFeed = "video";

function showStream(streamId) {
    // Hide all streams
    document.getElementById("videoStream").style.display = "none";
    document.getElementById("cannyStream").style.display = "none";
    document.getElementById("blurfaceStream").style.display = "none";
    document.getElementById("coloredEdgesStream").style.display = "none";
    document.getElementById("FaceDetection").style.display = "none";
    // Show the selected stream
    document.getElementById(streamId).style.display = "block";
    // Track current feed
    switch(streamId) {
        case "videoStream": currentFeed = "video"; break;
        case "cannyStream": currentFeed = "canny"; break;
        case "blurfaceStream": currentFeed = "blur"; break;
        case "coloredEdgesStream": currentFeed = "colored"; break;
        case "FaceDetection": currentFeed = "faceDetection"; break;
        default: currentFeed = "video";
    }
}

function showNormalStream() {
    showStream("videoStream");
}
function cannyEdgeDetection(){
    document.getElementById("cannyStream").src = "http://127.0.0.1:5000/canny_video_feed";
    showStream("cannyStream");
}
function blurFace(){
    document.getElementById("blurfaceStream").src = "http://127.0.0.1:5000/Blur";
    showStream("blurfaceStream");
}
function Face_detection(){
    document.getElementById("FaceDetection").src = "http://127.0.0.1:5000/face_detection";
    showStream("FaceDetection");
}
function coloredEdges(){
    document.getElementById("coloredEdgesStream").src = "http://127.0.0.1:5000/colored_border";
    showStream("coloredEdgesStream");
}
function downsampleImage(){
    fetch('http://127.0.0.1:5000/downsample', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if(data.path){
                document.getElementById("downsampleImage").style.display = "block";
            } else {
                document.getElementById("downsampleResult").innerText = data.message;
            }
        })
        .catch(error => {
            document.getElementById("downsampleResult").innerText = "Error: " + error;
        });
}

document.getElementById("videoStream").onclick = showNormalStream;
document.getElementById("Face_detection").onclick = Face_detection;
document.getElementById("captureBtn").onclick = function() {
    let route = "save_image";
    if(currentFeed === "canny") route = "save_canny_image";
    else if(currentFeed === "blur") route = "save_blur_image";
    else if(currentFeed === "faceDetection") route = "save_face_detection_image";
    else if(currentFeed === "colored") route = "save_colored_edges_image";
    fetch(`http://127.0.0.1:5000/${route}`)
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            alert("Capture successful!");
            document.getElementById("normalImage").src = "capture/captured_image.jpg?" + new Date().getTime();
            document.getElementById("normalImage").style.display = "block";
            document.getElementById("photoLabel").style.display = "block";
        })
        .catch(error => {
            alert("Error: " + error);
        });
}
document.getElementById("stopBtn").onclick = stopCapturing;
document.getElementById("capture_greyscale").onclick = captureGreyScale;
document.getElementById("cannybtn").onclick = cannyEdgeDetection;
document.getElementById("Face_Blur").onclick = blurFace
document.getElementById("coloredEdgesBtn").onclick = coloredEdges;
document.getElementById("downsampleBtn").onclick = downsampleImage;

document.getElementById("startVideoBtn").onclick = function() {
    document.getElementById("startVideoBtn").style.display = "none";
    document.getElementById("mainControls").style.display = "block";
    document.getElementById("videoStream").style.display = "block";
}

document.getElementById("stopBtn").onclick = function() {
    fetch('http://127.0.0.1:5000/stop_capture')
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            document.getElementById("mainControls").style.display = "none";
            document.getElementById("startVideoBtn").style.display = "inline-block";
            document.getElementById("videoStream").style.display = "none";
        })
        .catch(error => {
            alert("Error: " + error);
        });
}

document.getElementById("downsampleImage").style.display = "none";