document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form-container');
    const btn_open = document.getElementById('open-dialog');
    const btn_close = document.getElementById('close-dialog');
    const capture_dialog = document.getElementById('capture');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    let imageCount = 0;
    let video;
    let webSocket;
    let isSettingROI = false;
    let roiCoordinates = { x: 0, y: 0, width: 0, height: 0 };

    btn_open.addEventListener('click', function () {
        capture_dialog.showModal();
        startCamera();
        startWebSocket();
    });

    btn_close.addEventListener('click', function () {
        capture_dialog.close();
        stopCamera();
    });

    capture_dialog.addEventListener('close', function () {
        stopCamera();
    });

    function startCamera() {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                video.addEventListener('loadeddata', function () {
                    let width = video.videoWidth;
                    let height = video.videoHeight;
                    canvas.width = width;
                    canvas.height = height;

                    function drawFrame() {
                        context.drawImage(video, 0, 0, width, height);
                        if (isSettingROI) {
                            context.strokeStyle = 'green';
                            context.lineWidth = 2;
                            context.strokeRect(roiCoordinates.x, roiCoordinates.y, roiCoordinates.width, roiCoordinates.height);
                        }
                        requestAnimationFrame(drawFrame);
                    }

                    drawFrame();

                    document.addEventListener('keydown', function (event) {
                        if (!capture_dialog.open) return;
                        if (event.key === "c") {
                            if (!isSettingROI) {
                                isSettingROI = true;
                                pauseVideo();
                            } else {
                                isSettingROI = false;
                                captureAndSendImage();
                                resumeVideo();
                            }
                        }
                    });

                    canvas.addEventListener('mousedown', function (event) {
                        if (isSettingROI) {
                            roiCoordinates.x = event.offsetX;
                            roiCoordinates.y = event.offsetY;
                            roiCoordinates.width = 0;
                            roiCoordinates.height = 0;
                            canvas.addEventListener('mousemove', setROI);
                            canvas.addEventListener('mouseup', endSetROI);
                        }
                    });

                    function setROI(event) {
                        roiCoordinates.width = event.offsetX - roiCoordinates.x;
                        roiCoordinates.height = event.offsetY - roiCoordinates.y;
                    }

                    function endSetROI() {
                        canvas.removeEventListener('mousemove', setROI);
                        canvas.removeEventListener('mouseup', endSetROI);
                    }

                    function pauseVideo() {
                        video.pause();
                    }

                    function resumeVideo() {
                        video.play();
                    }

                    function captureAndSendImage() {
                        // Capturing the original image from the video
                        context.drawImage(video, 0, 0, width, height);

                        let imgURL = canvas.toDataURL('image/jpeg');
                        let filename = `image_${imageCount}.jpg`;
                        let blob = dataURLtoBlob(imgURL);

                        // Sending image and ROI data
                        sendImage(filename, blob, roiCoordinates);
                        imageCount++;
                    }
                });
            }).catch(function (error) {
                console.log("Error: No se puede acceder a la cámara");
                console.error(error);
            });
    }

    function dataURLtoBlob(dataURL) {
        let arr = dataURL.split(',');
        let mime = arr[0].match(/:(.*?);/)[1];
        let bstr = atob(arr[1]);
        let n = bstr.length;
        let u8arr = new Uint8Array(n);

        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }

        return new Blob([u8arr], { type: mime });
    }

    const token = document.getElementsByName('csrfmiddlewaretoken')[0].value;

    function startWebSocket() {
        webSocket = new WebSocket(`ws://${window.location.host}/ws/product/training/${token}/`);
        webSocket.onopen = function (event) {
            console.log('WebSocket is open now.');
        };
    }

    function sendImage(filename, blob, roiData) {
        if (webSocket && webSocket.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.readAsArrayBuffer(blob);
            reader.onloadend = function () {
                const imageBytes = new Uint8Array(reader.result);
                const data = JSON.stringify({
                    action: 'temp',
                    id_product: product_id,
                    filename: filename,
                    image: Array.from(imageBytes),
                    roi: roiData  // Sending ROI data along with the image
                });
                webSocket.send(data);
            };
        }
    }

    function stopCamera() {
        if (video && video.srcObject) {
            let stream = video.srcObject;
            let tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
        }
    }

    function closeWebSocket() {
        if (webSocket) {
            webSocket.close();
        }
    }

    form.addEventListener('submit', function (event) {
        if (webSocket && webSocket.readyState === WebSocket.CLOSED) {
            startWebSocket();
        }
        webSocket.send(JSON.stringify({ action: 'save', id_product: product_id }));
    });

    // Ensure cleanup on page unload
    window.addEventListener('unload', function () {
        stopCamera();
        closeWebSocket();
    });
});
