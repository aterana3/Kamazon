document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    const subtotalElement = document.getElementById('cart-subtotal');
    const totalElement = document.getElementById('cart-total');
    const checkoutButton = document.getElementById('btn-checkout');
    let video;
    let webSocket;
    let intervalId;
    let products = {};
    let last_product_id = null;
    let locked = false;
    let global_total = 0;
    let global_subtotal = 0;

    startWebSocket();
    startCamera();

    function startCamera() {
        navigator.mediaDevices.getUserMedia({
            video: {
                width: {min: 640, ideal: 1280, max: 1920},
                height: {min: 480, ideal: 720, max: 1080}
            }
        })
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

                    function captureAndSend() {
                        if (locked === false) {
                            let dataURL = canvas.toDataURL('image/jpeg', 0.8);
                            let blob = dataURLtoBlob(dataURL);
                            sendImage(blob);
                            locked = true;
                        }
                    }

                    intervalId = setInterval(captureAndSend, 1000);
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
            if (data.hasOwnProperty('error')) {
                console.error(data.error);
            } else if (Object.keys(data).length === 0) {
                console.log("El diccionario está vacío, no se realizó ninguna acción.");
            } else {
                Object.keys(data).forEach(function (product_id) {
                    products[product_id] = data[product_id];
                });
            }
            if (Object.keys(products).length > 0) {
                const keys = Object.keys(products);
                const last_key = keys[keys.length - 1];
                addDetailProduct(last_key);

                for (const key in products) {
                    const product = products[key];
                    const amount = parseInt(product.amount);
                    const price = parseFloat(product.price);

                    const subtotal = price * amount;
                    const tax = subtotal * 0.15;
                    const total = subtotal + tax;

                    global_subtotal += subtotal;
                    global_total += total;
                }
                subtotalElement.textContent = global_subtotal;
                totalElement.textContent = global_total;
            }
            locked = false;
        };
    }

    function addDetailProduct(id) {
        if (last_product_id === id)
            return;

        last_product_id = id;
        const protocol = window.location.protocol;
        const host = window.location.host;
        const fetchUrl = protocol + '//' + host + `/products/fetch/${id}/`;

        const cart_name = document.getElementById('cart-name');
        const cart_price = document.getElementById('cart-price');
        const cart_image = document.getElementById('cart-image');
        const cart_stock = document.getElementById('cart-stock');

        fetch(fetchUrl)
            .then(response => response.json())
            .then(data => {
                cart_name.textContent = data.name;
                cart_price.textContent = data.price;
                cart_image.src = data.image;
                cart_stock.textContent = data.stock;
            });
    }


    function sendImage(blob) {
        if (webSocket && webSocket.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.readAsArrayBuffer(blob);
            reader.onloadend = function () {
                const imageBytes = new Uint8Array(reader.result);
                webSocket.send(imageBytes)
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

    checkoutButton.addEventListener('click', function () {
        stopWebSocket();
        video.srcObject.getTracks().forEach(track => track.stop());

        if (products.length === 0) {
            alert('No hay productos en el carrito.');
            startWebSocket()
            startCamera();
        } else {
            const form = new FormData();
            form.append('user_id', user_id);
            form.append('products', JSON.stringify(products));
            form.append('subtotal', subtotalElement.textContent);
            form.append("tax", "0.15");
            form.append('total', totalElement.textContent);

            const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
            const protocol = window.location.protocol;
            const host = window.location.host;
            const fetchUrl = protocol + '//' + host + `/billing/create`;

            fetch(fetchUrl, {
                method: 'POST',
                body: form,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            }).then(response => response.json()
            ).then(data => {
                if (data.hasOwnProperty('error')) {
                    alert(data.error);
                } else {
                    alert('Compra realizada con éxito.');
                    window.location.href = protocol + '//' + host;
                }
            });
        }
    });
});
