window.addEventListener('DOMContentLoaded', (event) => {
    const webSocket = new WebSocket(`ws://${window.location.host}/ws/qr/${token}/`);

    webSocket.onopen = () => {
        console.log('WebSocket is open now.');
    }

    webSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'successful') {
            const sessionKey = data.session_key;
            fetch(loginQR, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': `${token}`
                },
                body: JSON.stringify({session_key: sessionKey})
            }).then(response => {
                if (response.ok) {
                    webSocket.send(JSON.stringify({type: 'authenticated'}));
                    window.location.href = redirectURL;
                } else {
                    console.error(response.statusText);
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        }
    };
});