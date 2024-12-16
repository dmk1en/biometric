document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('startFaceLogin');
    const imageDataInput = document.getElementById('imageData');


    // Capture the current frame from the video
    captureBtn.addEventListener('click', () => {
        window.location.href = "/face_login";
    });
});
