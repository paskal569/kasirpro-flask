from werkzeug.security import check_password_hash, generate_password_hash
from models.db import db
from models.base import BaseModel
import sys

class User(BaseModel):
    __tablename__ = 'users'

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    nama_lengkap = db.Column(db.String(120))
    role = db.Column(db.String(20), default='kasir')
    password_hash = db.Column(db.String(255), nullable=False)
    reset_token  = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def verify_password(self, value):
        return check_password_hash(self.password_hash, value)

    def is_admin(self):
        return self.role == 'admin'

    def is_kasir(self):
        return self.role == 'kasir'

    def is_owner(self):
        return self.role == 'owner'

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nama_lengkap': self.nama_lengkap,
            'role': self.role,
            'last_login': self.last_login
        }
    
    def set_password(self, password):
        """Perbaikan: Gunakan generate_password_hash untuk menyimpan password dengan aman"""
        self.password_hash = generate_password_hash(password)
    

    def check_password(self, password):
        """Perbaikan: Gunakan check_password_hash untuk memverifikasi password"""
        return check_password_hash(self.password_hash, password)
    