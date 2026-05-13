// loading_konfirmasi.js
window.addEventListener('DOMContentLoaded', function () {
    // Auto submit form setelah 1.5 detik
    setTimeout(function () {
        document.getElementById('loadingForm').submit();
    }, 1500);
});