# models/pendapatan.py
from models.db import db
from datetime import datetime
from sqlalchemy import Numeric

class Pendapatan(db.Model):
    __tablename__ = 'pendapatan'

    id           = db.Column(db.Integer, primary_key=True)
    nama_barang  = db.Column(db.String(100), nullable=False)
    total_harga  = db.Column(db.Numeric(15, 2), nullable=False)
    jumlah_bayar = db.Column(db.Numeric(15, 2), nullable=False)
    kembalian    = db.Column(db.Numeric(15, 2), nullable=False)
    tanggal      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, nama_barang, total_harga, jumlah_bayar, kembalian):
        self.nama_barang  = nama_barang
        self.total_harga  = total_harga
        self.jumlah_bayar = jumlah_bayar
        self.kembalian    = kembalian

    def __repr__(self):
        return f"Pendapatan(id={self.id}, nama={self.nama_barang}, total={self.total_harga})"