document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("loginForm");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const usernameError = document.getElementById("usernameError");
    const passwordError = document.getElementById("passwordError");
    const togglePassword = document.getElementById("togglePassword");
    const loginButton = document.getElementById("loginButton");
    const buttonText = document.getElementById("buttonText");

    // ================= HELPER =================
    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    function showError(el, msg) {
        if (!el) return;
        el.textContent = msg;
        el.classList.add("show-error");
    }

    function clearError(el) {
        if (!el) return;
        el.textContent = "";
        el.classList.remove("show-error");
    }

    // ================= TOGGLE PASSWORD =================
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener("click", () => {
            const icon = togglePassword.querySelector("i");

            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                icon?.classList.replace("fa-eye", "fa-eye-slash");
            } else {
                passwordInput.type = "password";
                icon?.classList.replace("fa-eye-slash", "fa-eye");
            }
        });
    }

    // ================= REAL-TIME VALIDATION =================
    usernameInput?.addEventListener("input", function () {
        const val = this.value.trim();
        if (val) {
            clearError(usernameError);
        }
    });

    passwordInput?.addEventListener("input", function () {
        const val = this.value.trim();
        if (val && val.length >= 6) {
            clearError(passwordError);
        }
    });

    // ================= SUBMIT VALIDATION =================
    if (form) {
        form.addEventListener("submit", (e) => {
            let isValid = true;

            clearError(usernameError);
            clearError(passwordError);

            const username = usernameInput?.value.trim() || "";
            const password = passwordInput?.value.trim() || "";

            // Validasi username / email
            if (!username) {
                showError(usernameError, "Username atau email harus diisi");
                usernameInput?.focus();
                isValid = false;
            } else if (!isValidEmail(username) && username.length < 3) {
                showError(usernameError, "Format email tidak valid atau username terlalu pendek");
                usernameInput?.focus();
                isValid = false;
            }

            // Validasi password
            if (!password) {
                showError(passwordError, "Password harus diisi");
                if (isValid) passwordInput?.focus();
                isValid = false;
            } else if (password.length < 6) {
                showError(passwordError, "Password minimal 6 karakter");
                if (isValid) passwordInput?.focus();
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
                return;
            }

            // Loading state
            if (loginButton) {
                loginButton.classList.add("loading");
                loginButton.disabled = true;
            }
            if (buttonText) buttonText.textContent = "Memproses...";
        });
    }

});