
async function startVideo() {
    const video = document.getElementById('video');
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
}

async function captureFace() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
    const formData = new FormData();
    formData.append('image', blob);

    const response = await fetch('/capture-face', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();

    if (data.success) {
        alert('Registration successful!');
        window.location.href = '/login';
    } else {
        alert(data.error);
    }
}

async function authenticate() {
    const email = document.getElementById('login-email').value;
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
    const formData = new FormData();
    formData.append('email', email);
    formData.append('image', blob);

    const response = await fetch('/login', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();

    if (data.success) {
        window.location.href = '/dashboard';
    } else {
        alert(data.error);
    }
}

// Start video on login page load
if (window.location.pathname === '/login') {
    startVideo();
}
