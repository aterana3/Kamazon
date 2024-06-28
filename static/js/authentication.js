window.addEventListener('DOMContentLoaded', (event) => {
    const webSocket = new WebSocket(`ws://${window.location.host}/ws/qr/${token}/`);
    webSocket.onopen = () => {
        console.log('WebSocket is open now.');
    }

    webSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const action = data.action;
        if (action === 'successful') {
            const sessionKey = data.session_key;
            fetch("{% url 'authentication:qr_login' %}", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': `${token}`
                    },
                    body: JSON.stringify({session_key: sessionKey})
            }).then(response => {
                if (response.ok) {
                    webSocket.send(JSON.stringify({action: 'authenticated'}));
                    return
                }
                console.error(response.message);
            }).catch(error => {
                console.error('Error:', error);
            });
        }
    }
});
