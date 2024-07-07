document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    let btn_start = document.getElementById('start');
    let video;
    let webSocket;
    let intervalId;

    btn_start.addEventListener('click', function () {
        startWebSocket();
        startCamera();
    });

    function startCamera() {
        navigator.mediaDevices.getUserMedia({video: true})
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
                        requestAnimationFrame(drawFrame);
                    }

                    drawFrame();

                    intervalId = setInterval(function () {
                        let dataURL = canvas.toDataURL('image/jpeg', 0.8);
                        let blob = dataURLtoBlob(dataURL);
                        sendImage(blob);
                    }, 3000);
                });
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

        return new Blob([u8arr], {type: mime});
    }

    function startWebSocket() {
        const productTable = document.getElementById('product-table');

        webSocket = new WebSocket(`ws://${window.location.host}/ws/product/detect/cart-${user_id}/`);
        webSocket.onopen = function () {
            console.log('WebSocket is open now.');
        };
        webSocket.onclose = function () {
            console.log('WebSocket is closed now.');
        };
        webSocket.onmessage = function (event) {
            const data = JSON.parse(event.data);
            console.log(data)
        };
    }

    function sendImage(blob) {
        if (webSocket && webSocket.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.readAsArrayBuffer(blob);
            reader.onloadend = function () {
                const imageBytes = new Uint8Array(reader.result);
                webSocket.send(imageBytes);
            };
        }
    }

    function stopWebSocket() {
        if (webSocket) {
            webSocket.close();
        }
        if (intervalId) {
            clearInterval(intervalId);
        }
    }
});
