
from .base import db
from datetime import datetime

class Kunjungan(db.Model):
    __tablename__ = 'kunjungan'
    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.Date,    nullable=False, default=datetime.utcnow().date)
    pelanggan_id = db.Column(db.Integer, db.ForeignKey('pelanggan.id'), nullable=False)
    transaksi_id  = db.Column(db.Integer, db.ForeignKey('transaksi.id'), nullable=True)
    jumlah = db.Column(db.Integer, nullable=False)
    keterangan = db.Column(db.String(255), nullable=True)
    jam_masuk = db.Column(db.DateTime, nullable=False)
    jam_keluar = db.Column(db.DateTime, nullable=True)
    pembeli       = db.Column(db.Boolean, default=False)
    total_belanja = db.Column(db.Float, nullable=False)
    durasi_jam = db.Column(db.Integer, nullable=False)
    durasi_menit = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __repr__(self):
         return f'<Kunjungan {self.tanggal} {self.jam_masuk}>'
    
    
@property
def jam_bucket(self):
        """Mengembalikan label jam (mis. '08:00–09:00') untuk grafik pola jam."""
        h = self.jam_masuk.hour
        return f'{h:02d}:00–{h+1:02d}:00'
    
    
