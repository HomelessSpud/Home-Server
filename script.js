const AUTH_TOKEN = 'YOUR_SECRET_TOKEN';

function updateStatus(message) {
    const status = document.getElementById('status');
    if (status) {
        status.textContent = message;
    }
}

async function sendPowerCommand(startMinecraft) {
    const endpoint = startMinecraft ? '/api/power-and-minecraft' : '/api/power';

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'X-Auth': AUTH_TOKEN }
    });

    if (!response.ok) {
        throw new Error('Request failed with status ' + response.status);
    }

    return response.json();
}

async function power() {
    const startMinecraft = window.confirm('Start Minecraft server after the PC boots?');

    try {
        await sendPowerCommand(startMinecraft);
        if (startMinecraft) {
            updateStatus('Power command sent. Minecraft will start after boot.');
        } else {
            updateStatus('Power command sent.');
        }
    } catch (error) {
        updateStatus('Error: ' + error.message);
    }
}

const togglePowerButton = document.getElementById('toggle-power');
if (togglePowerButton) {
    togglePowerButton.addEventListener('click', power);
}
