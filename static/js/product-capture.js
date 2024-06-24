document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form-container');
    const btn_open = document.getElementById('open-dialog');
    const btn_close = document.getElementById('close-dialog');
    const capture_dialog = document.getElementById('capture');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    const roiWidth = 200;
    const roiHeight = 200;
    let imageCount = 0;
    let video;
    let webSocket;

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
                        if (capture_dialog.open) {
                            context.drawImage(video, 0, 0, width, height);
                            let x1 = width / 2 - roiWidth / 2;
                            let y1 = height / 2 - roiHeight / 2;

                            context.strokeStyle = 'green';
                            context.lineWidth = 2;
                            context.strokeRect(x1, y1, roiWidth, roiHeight);

                            requestAnimationFrame(drawFrame);
                        }
                    }

                    drawFrame();

                    document.addEventListener('keydown', function (event) {
                        if (!capture_dialog.open) return;
                        if (event.key === "c") {
                            let roiCanvas = document.createElement('canvas');
                            roiCanvas.width = roiWidth;
                            roiCanvas.height = roiHeight;
                            let roiContext = roiCanvas.getContext('2d');

                            let x1 = width / 2 - roiWidth / 2;
                            let y1 = height / 2 - roiHeight / 2;
                            roiContext.drawImage(video, x1, y1, roiWidth, roiHeight, 0, 0, roiWidth, roiHeight);

                            let imgURL = roiCanvas.toDataURL('image/jpeg');
                            let filename = `image_${imageCount}.jpg`;
                            let blob = dataURLtoBlob(imgURL);

                            sendImage(filename, blob);
                            imageCount++;
                        }
                    });
                });
            }).catch(function (error) {
                console.log("Error: No se puede acceder a la cámara");
                console.error(error);
            });
    }

    function stopCamera() {
        if (video && video.srcObject) {
            let stream = video.srcObject;
            let tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
        }
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
        webSocket = new WebSocket(`ws://${window.location.host}/ws/product/${token}/`);
        webSocket.onopen = function (event) {
            console.log('WebSocket is open now.');
        };
    }

    function closeWebSocket() {
        if (webSocket) {
            webSocket.close();
        }
    }


    function sendImage(filename, blob) {
        if (webSocket && webSocket.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.readAsArrayBuffer(blob);
            reader.onloadend = function () {
                const imageBytes = new Uint8Array(reader.result);
                const data = JSON.stringify({
                    action: 'temp',
                    id_product: product_id,
                    filename: filename,
                    image: Array.from(imageBytes)
                });
                webSocket.send(data);
            };
        }
    }

    form.addEventListener('submit', function (event) {
        if (webSocket && webSocket.readyState === WebSocket.CLOSED) {
            startWebSocket();
        }
        webSocket.send(JSON.stringify({ action: 'save', id_product: product_id }));
    });
});