from flask import Flask, render_template, request, redirect, url_for, session
from models.extensions import login_manager
from models.db import db
from models.user import User
from routes import register_blueprints
from flask_mail import Mail
from datetime import datetime
import os
import secrets
from routes import pelanggan_bp 
mail = Mail()

# Configuration dictionary
config = {
    'default': type('Config', (), {
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:@localhost/kasir_database',
    })
}


def create_app(config_name='default'):
    """Factory function untuk membuat aplikasi Flask"""
    app = Flask(__name__)
    
    # Konfigurasi dasar
    if config_name in config:
        app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/kasir_database'
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # max 2MB
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    
    # Konfigurasi mail
    app.config['MAIL_SERVER']         = 'sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT']           = 2525
    app.config['MAIL_USE_TLS']        = True
    app.config['MAIL_USE_SSL']        = False
    app.config['MAIL_USERNAME']       = '1197d3a7d1ead7'
    app.config['MAIL_PASSWORD']       = '219d1266859bc0'
    app.config['MAIL_DEFAULT_SENDER'] = ('Kasir App', 'noreply@kasir.local')

    app.secret_key = app.config.get('SECRET_KEY', 'fallback-secret-key')

    # Inisialisasi database & mail
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
     return User.query.get(int(user_id))
   
    
    # Daftarkan blueprint
    register_blueprints(app)

    # Buat folder instance jika belum ada
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Buat folder upload jika belum ada
    upload_path = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

 # sesuaikan path-nya

    

    # ── Routes ────────────────────────────────────────────────



    @app.before_request
    def csrf_protect():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(16)

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except Exception as e:
            print(f"Error: {e}")
            return "Error occurred while rendering the page.", 500

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()
            if user and user.verify_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html',
                                       error="Username atau password salah!",
                                       date=datetime.now())

        return render_template('login.html', date=datetime.now())

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')

    # ── Error Handlers ────────────────────────────────────────

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404 eror.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # ── Context Processor ─────────────────────────────────────

    @app.context_processor
    def inject_now():
        """Inject variabel ke semua template"""
        return {'now': datetime.now()}

    return app


# ── Inisialisasi Aplikasi ─────────────────────────────────────

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@kasir.local',
                     nama_lengkap='Administrator', role='admin')
        admin.password = 'admin123'
        db.session.add(admin)
        db.session.commit()

    if not User.query.filter_by(username='user').first():
        user = User(username='user', email='user@kasir.local',
                    nama_lengkap='User', role='user')
        user.password = 'user123'
        db.session.add(user)
        db.session.commit()

    # Print semua routes
    print("\n=== DAFTAR ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:40s} {rule.rule}")
    print("====================\n")


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 APLIKASI KASIR FLASK SIAP!")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:5000/")
    print("👤 Login:     http://localhost:5000/login")
    print("🛒 Transaksi: http://localhost:5000/transaksi")
    print("📦 Produk:    http://localhost:5000/produk")
    print("📈 Laporan:   http://localhost:5000/laporan")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)