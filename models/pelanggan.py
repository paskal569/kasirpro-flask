from .base import db, BaseModel
from models.base import db
class Pelanggan(BaseModel):
    __tablename__ = 'pelanggan'
    
    kode = db.Column(db.String(50), unique=True, nullable=False)
    nama = db.Column(db.String(200), nullable=False)
    jenis = db.Column(db.String(20), default='umum')  # umum, member, grosir
    alamat = db.Column(db.Text)
    telepon = db.Column(db.String(20))
    
    email = db.Column(db.String(100))
    diskon = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True) # Status pelanggan aktif atau tidak (untuk soft delete)
    # Relationship
    transaksi = db.relationship('transaksi', backref='pelanggan_info', lazy=True)
    
    def __repr__(self):
        return f'<Pelanggan {self.kode}: {self.nama}>'
    
    @classmethod
    def generate_kode(cls):
        """Generate kode pelanggan otomatis"""
        last_pelanggan = cls.query.order_by(cls.id.desc()).first()
        if last_pelanggan:
            last_number = int(last_pelanggan.kode.replace('CUST', ''))
            new_number = last_number + 1
        else:
            new_number = 1001
        return f'CUST{new_number:04d}'