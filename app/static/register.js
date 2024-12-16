document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const showCameraBtn = document.getElementById('showCameraBtn');
    const result = document.getElementById('result');


    // Open the camera when the button is clicked
    showCameraBtn.addEventListener('click', () => {
        // Access the user's camera
        navigator.mediaDevices.getUserMedia({ video: true })
            .then((stream) => {
                video.srcObject = stream;
                video.play();

                // Create the button to trigger the continuous recognition
                const captureButton = document.createElement('button');
                captureButton.textContent = 'Capture';
                document.body.appendChild(captureButton);

                // Create a canvas to capture the video frames
                const canvas = document.createElement('canvas');

                captureButton.addEventListener('click', () => {
                    // Send the image 10 times
                    let count = 0;
                    const captureInterval = setInterval(async () => { // Use async here
                        if (count < 10) {
                            const re = await captureAndSendImage(count); // Await the result of captureAndSendImage
                            console.log('re:', re);
                            if (re === 'good') {
                                count++;
                            }
                            console.log('count:', count);
                        } else {
                            clearInterval(captureInterval); // Stop after 10 fetches
                            console.log('Completed 10 fetches');
                        }
                    }, 200); // Adjust interval if needed (200ms between fetches)
                });

                // Function to capture and send the image to the server
                async function captureAndSendImage(count) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);

                    return new Promise((resolve, reject) => {
                        // Convert the canvas to a Blob
                        canvas.toBlob((blob) => {
                            const formData = new FormData();
                            formData.append('image', blob, 'capture.jpg');
                            formData.append('count', count.toString());
                            // Send the captured image to the server
                            fetch('/recognize', {
                                method: 'POST',
                                body: formData,
                            })
                                .then(response => response.json())
                                .then(data => {
                                    console.log('Success:', data);
                                    resolve(data.result); // Resolve the promise with the result
                                })
                                .catch(error => {
                                    console.error('Error:', error);
                                    alert('Error recognizing the image.');
                                    reject(error); // Reject the promise if there's an error
                                });
                        }, 'image/jpeg');
                    });
                }
            })
            .catch((err) => {
                console.error('Error accessing camera:', err.name, err.message);
            });
    });
});
