document.addEventListener('DOMContentLoaded', () => {
    const chatLog = document.getElementById('chatLog');
    const chatInput = document.getElementById('chatInput');

    const symbolInput = document.getElementById('symbol');
    const thresholdInput = document.getElementById('threshold');
    const startAlert = document.getElementById('startAlert');
    const alertsArea = document.getElementById('alertsArea');
    const alertsList = document.getElementById('alertsList');

    const predSymbol = document.getElementById('predSymbol');
    const minutesInput = document.getElementById('minutes');
    const predictBtn = document.getElementById('predictBtn');
    const predictionResult = document.getElementById('predictionResult');

    (document.getElementById('sendChat')).addEventListener('click', () => {
        const msg = chatInput.value.trim();
        if (!msg) return;
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        })
        .then(res => res.json())
        .then(data => {
            chatLog.innerHTML += `<div><strong>You:</strong> ${msg}</div>`;
            chatLog.innerHTML += `<div><strong>Bot:</strong> ${data.response}</div>`;
            chatInput.value = '';
            chatLog.scrollTop = chatLog.scrollHeight;
        });
    });

    startAlert.addEventListener('click', () => {
        const symbol = symbolInput.value.trim();
        const threshold = parseFloat(thresholdInput.value);
        if (!symbol || isNaN(threshold)) return;
        fetch('/alert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, threshold })
        }).then(() => {
            alertsArea.style.border = '1px solid #ddd';
            alertsArea.style.padding = '0.5rem';
            alertsArea.style.maxHeight = '300px';
            alertsArea.style.overflow = 'auto';
            alertsArea.querySelector('#alertsList').insertAdjacentHTML('afterbegin', `<li class="alert-card">Alert started for <strong>${symbol.toUpperCase()}</strong></li>`);
        });
    });

    // Helper to render an alert into the history list
    function addAlertToUI(alert) {
        if (!alertsList) return;
        const html = `
            <li class="alert-card">
                <div class="alert-header">${alert.symbol} <span class="price">$${Number(alert.price).toFixed(2)}</span></div>
                <div class="alert-body">Threshold: <strong>$${Number(alert.threshold).toFixed(2)}</strong></div>
                <div class="alert-time">${alert.time}</div>
            </li>`;
        alertsList.insertAdjacentHTML('afterbegin', html);
    }

    // Load historical alerts on page load
    fetch('/alerts').then(r => r.json()).then(data => {
        if (Array.isArray(data)) {
            data.slice().reverse().forEach(addAlertToUI);
        }
    }).catch(() => {});

    // Real-time alerts via Socket.IO
    try {
        const socket = io();
        socket.on('connect', () => {
            console.log('socket connected');
        });
        socket.on('alert', (alert) => {
            addAlertToUI(alert);
        });
        socket.on('disconnect', () => {
            console.log('socket disconnected');
        });
    } catch (e) {
        console.warn('Socket.IO client not available', e);
    }

    predictBtn.addEventListener('click', () => {
        const symbol = predSymbol.value.trim();
        const minutes = parseInt(minutesInput.value, 10);
        if (!symbol || isNaN(minutes)) return;
        fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, minutes })
        })
        .then(res => res.json())
        .then(data => {
            if (data.predicted_price !== undefined) {
                predictionResult.textContent = 'Predicted price: ' + data.predicted_price;
            } else {
                predictionResult.textContent = 'Error: ' + data.error;
            }
        });
    });
});