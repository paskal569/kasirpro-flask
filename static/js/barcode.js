function startBarcodeScanner() {
            // Simulasi pemindaian barcode
            const barcode = "1234567890"; // Ganti dengan hasil pemindaian sebenarnya
            document.getElementById("barcodeDisplay").innerText = "Barcode: " + barcode;
            document.getElementById("kodeBarang").value = barcode;
        }
document.getElementById('scan-btn').addEventListener('click', scan);

document.createElement('barcode');

const scanner = new Instascan.Scanner({ video: document.getElementById('preview') });
scanner.addListener('scan', function (content) {
    document.getElementById('barcode').value = content;
});
Instascan.Camera.getCameras().then(function (cameras) {
    if (cameras.length > 0) {
        scanner.start(cameras[0]);
    } else {
        console.error('No cameras found.');
    }
}).catch(function (e) {
    console.error(e);
});     

function stop() {
    scanner.stop();
}
function scan() {
        Instascan.Camera.getCameras().then(function (cameras) {
            if (cameras.length > 0) {
                scanner.start(cameras[0]);
            } else {
                console.error('No cameras found.');
            }
        }).catch(function (e) {
            console.error(e);
        });
    }
    document.getElementById('stop-btn').addEventListener('click', function () {
        scanner.stop();
    });

    // Simulasi pemindaian barcode
    const barcode = "1234567890"; // Ganti dengan hasil pemindaian sebenarnya
    document.getElementById("barcodeDisplay").innerText = "Barcode: " + barcode;
    document.getElementById("kodeBarang").value = barcode;