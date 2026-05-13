// Validate reset password form
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('#reset-password-form');
    const new_password = document.querySelector('#new_password');
    const confirm_password = document.querySelector('#confirm_password');

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        if (new_password.value.length < 6) {
            alert('Password harus minimal 6 karakter');
            return;
        }

        if (new_password.value !== confirm_password.value) {
            alert('Password baru dan konfirmasi password tidak cocok');
            return;
        }

        form.submit();
    });
});
