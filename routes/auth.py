from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from models.user import User
import secrets
from models.base import db
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import or_
from flask import current_app

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def init_app(app):
    app.register_blueprint(auth_bp)

    def index():
        return render_template('login.html')
    auth_bp.add_url_rule('/', view_func=index)


# ─────────────────────────────────────────
#  DECORATORS
# ─────────────────────────────────────────

def login_required(f):
    """Decorator untuk halaman yang membutuhkan login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator untuk halaman admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Akses ditolak. Hanya untuk admin.', 'danger')
            return redirect(url_for('dashboard.index'))

        return f(*args, **kwargs)
    return decorated_function


# ─────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        token    = request.form.get('csrf_token')

        # ✅ FIX 1: Validasi field kosong SEBELUM query/verify
        if not username or not password:
            flash('Username dan password harus diisi', 'danger')
            return redirect(url_for('auth.login'))

        # ✅ FIX 2: Validasi CSRF token
        if token != session.get('csrf_token'):
            flash('Token tidak valid', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter(
            or_(User.username == username, User.email == username)
        ).first()

        if not user:
            flash('User tidak ditemukan', 'danger')
            return redirect(url_for('auth.login'))

        # ✅ FIX 3: password sudah pasti string, tidak akan None di sini
        if not user.verify_password(password):
            flash('Password salah', 'danger')
            return redirect(url_for('auth.login'))

        # Login berhasil
        session['user_id']  = user.id
        session['username'] = user.username
        session['role']     = user.role
        session['nama']     = user.nama_lengkap or user.username

        user.last_login = datetime.now()
        db.session.commit()

        flash(f'Selamat datang, {session["nama"]}!', 'success')
        return redirect(url_for('dashboard.index'))

    # GET request — buat CSRF token baru
    session['csrf_token'] = secrets.token_hex(16)
    return render_template('login.html', csrf_token=session['csrf_token'])


# ─────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('auth.login'))


# ─────────────────────────────────────────
#  REGISTER
# ─────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username         = request.form.get('username', '').strip()
        email            = request.form.get('email', '').strip()
        password         = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        nama_lengkap     = request.form.get('nama_lengkap', '').strip()
        role             = request.form.get('role', 'user').strip()

        allowed_roles = ['user', 'admin', 'kasir', 'supervisor', 'manager', 'administrator']
        if role not in allowed_roles:
            flash('Role tidak valid', 'danger')
            return render_template('register.html')

        # ✅ Validasi semua field wajib
        if not all([username, email, password, nama_lengkap]):
            flash('Semua field harus diisi', 'danger')
            return render_template('register.html')

        # ✅ Validasi panjang password
        if len(password) < 6:
            flash('Password minimal 6 karakter', 'danger')
            return render_template('register.html')

        # ✅ Validasi konfirmasi password
        if confirm_password and password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok', 'danger')
            return render_template('register.html')

        # Cek username & email duplikat
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email sudah digunakan', 'danger')
            return render_template('register.html')

        try:
            new_user = User(
                username=username,
                email=email,
                nama_lengkap=nama_lengkap,
                role=role,
                is_active=True
            )

            if hasattr(new_user, 'set_password'):
                new_user.set_password(password)
            else:
                from werkzeug.security import generate_password_hash
                new_user.password_hash = generate_password_hash(password)

            db.session.add(new_user)
            db.session.commit()

            flash(f'User {nama_lengkap} berhasil dibuat!', 'success')

            # Jika admin yang membuat → ke halaman users
            if 'user_id' in session:
                current_user = User.query.get(session['user_id'])
                if current_user and current_user.role == 'admin':
                    return redirect(url_for('auth.users'))

            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return render_template('register.html')

    return render_template('register.html')


# ─────────────────────────────────────────
#  USERS (admin only)
# ─────────────────────────────────────────

@auth_bp.route('/users')
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/users.html', users=users_list)


# ─────────────────────────────────────────
#  PROFILE
# ─────────────────────────────────────────

@auth_bp.route('/profile')
@login_required
def profile():
    user = User.query.get_or_404(session.get('user_id'))
    return render_template('auth/profile.html', user=user)


# ─────────────────────────────────────────
#  CHANGE PASSWORD
# ─────────────────────────────────────────

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    user = User.query.get_or_404(session.get('user_id'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password     = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # ✅ FIX: Validasi field kosong SEBELUM check_password
        if not current_password or not new_password or not confirm_password:
            flash('Semua field harus diisi', 'danger')
            return redirect(url_for('auth.change_password'))

        if len(new_password) < 6:
            flash('Password baru minimal 6 karakter', 'danger')
            return redirect(url_for('auth.change_password'))

        # ✅ Sekarang aman, current_password pasti string
        if not user.check_password(current_password):
            flash('Password saat ini salah', 'danger')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash('Password baru dan konfirmasi tidak cocok', 'danger')
            return redirect(url_for('auth.change_password'))

        if hasattr(user, 'set_password'):
            user.set_password(new_password)
        else:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash('Password berhasil diubah', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('change_password.html', user=user)


# ─────────────────────────────────────────
#  FORGOT PASSWORD
# ─────────────────────────────────────────

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash('Email harus diisi', 'danger')
            return redirect(url_for('auth.forgot_password'))

        user = User.query.filter_by(email=email).first()

        # Selalu tampilkan pesan yang sama agar email tidak bisa di-enumerate
        if not user:
            flash('Jika email terdaftar, link reset akan dikirim ke email kamu.', 'info')
            return redirect(url_for('auth.forgot_password'))

        token = secrets.token_urlsafe(32)
        user.reset_token        = token
        user.reset_token_expiry = datetime.now() + timedelta(hours=1)
        db.session.commit()

        try:
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg       = Message('Reset Password - KasirPro', recipients=[email])
            msg.body  = f"Klik link ini untuk reset password: {reset_url}"
            msg.html  = f'''
                <h3>Reset Password</h3>
                <p>Halo <strong>{user.nama_lengkap or user.username}</strong>,</p>
                <p>Klik link berikut untuk reset password kamu:</p>
                <a href="{reset_url}"
                   style="background:#4CAF50;color:white;padding:10px 20px;
                          text-decoration:none;border-radius:5px;">
                    Reset Password
                </a>
                <p>Link berlaku selama <strong>1 jam</strong>.</p>
                <p>Jika kamu tidak meminta reset password, abaikan email ini.</p>
            '''
            mail = Mail(current_app._get_current_object())
            mail.send(msg)
            flash('Email reset password telah dikirim.', 'info')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f'Gagal mengirim email: {str(e)}', 'danger')
            return redirect(url_for('auth.forgot_password'))

    
    return render_template('change_password.html')


# ─────────────────────────────────────────
#  RESET PASSWORD
# ─────────────────────────────────────────

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_token_expiry < datetime.now():
        flash('Token tidak valid atau sudah expired', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password     = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            flash('Semua field harus diisi', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        if len(new_password) < 6:
            flash('Password harus minimal 6 karakter', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        if new_password != confirm_password:
            flash('Password baru dan konfirmasi tidak cocok', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        user.set_password(new_password)
        user.reset_token        = None
        user.reset_token_expiry = None
        db.session.commit()

        flash('Password berhasil direset! Silakan login dengan password baru.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)