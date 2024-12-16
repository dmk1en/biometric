const socket = io();

// Start face authentication or motion detection
socket.emit("start_face_authen");

// Listen for real-time updates for motion detection
socket.on("motion_detected", (data) => {
    document.getElementById("motion-status").innerText = "Motion detected: " + data.motion;
});

// Setup user's camera stream
navigator.mediaDevices.getUserMedia({ video: true })
    .then(function (stream) {
        const videoElement = document.getElementById('user-video');
        videoElement.srcObject = stream;
        
        // Optional: Capture frames from the video element and send to backend for processing
        // This can be done at a regular interval or when motion is detected
        setInterval(() => {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/jpeg').replace(/^data:image\/jpeg;base64,/, ''); // Send this image to backend if needed
            
            socket.emit("send_frame", { frame: imageData });
        }, 100); // Capture a frame every 100ms
    })
    .catch(function (error) {
        console.log("Error accessing the camera: ", error);
    });

// Listen for the authentication result (optional)
socket.on("authentication_complete", (data) => {
    console.log("Authentication result:", data.status);

    if (data.status === "authenticated") {
        fetch("/set_session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username: data.username }),
        })
        .then((response) => response.json())
        .then((result) => {
            console.log(result.message);
            // Redirect to the dashboard after setting the session
            window.location.href = "/dashboard";
        })
        .catch((error) => {
            console.error("Error setting session:", error);
        });
    } else if (data.status.includes("Timeout")) {
        alert("Authentication timeout. Please try again.");
    }
});
