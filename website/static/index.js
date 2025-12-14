function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function deleteDevice(deviceId) {
  fetch("/delete-device", {
    method: "POST",
    body: JSON.stringify({ deviceId: deviceId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function refreshCaptcha() {
  const img = document.getElementById('captcha-image');
  if (!img) return;

  const baseUrl = img.dataset.baseUrl || img.src.split('?')[0];
  img.dataset.baseUrl = baseUrl;
  img.src = baseUrl + '?t=' + Date.now(); // cache-buster
}
