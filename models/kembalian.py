from .base import db, BaseModel
from datetime import datetime, date
from models.base import db
class kembalian(BaseModel):
    __tablename__ = 'transaksi'
    
    invoice = db.Column(db.String(50), unique=True, nullable=False)
    pelanggan_id = db.Column(db.Integer, db.ForeignKey('pelanggan.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Harga
    subtotal = db.Column(db.Float, default=0)
    diskon = db.Column(db.Float, default=0)          # Diskon transaksi
    pajak = db.Column(db.Float, default=0)           # Pajak (PPN)
    total = db.Column(db.Float, nullable=False)
    
    # Pembayaran
    bayar = db.Column(db.Float, nullable=False)
    kembalian = db.Column(db.Float, nullable=False)
    metode_bayar = db.Column(db.String(20), default='tunai')  # tunai, debit, kredit
    status = db.Column(db.String(20), default='selesai')      # selesai, batal, pending
    
    # Relationship
    items = db.relationship('ItemTransaksi', backref='kembalian_detail', 
                           lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Transaksi {self.invoice}>'
    
    @property
    def total_item(self):
        """Total jumlah item dalam transaksi"""
        return sum(item.qty for item in self.items)
    
    def hitung_total(self):
        """Hitung ulang total transaksi"""
        subtotal = sum(item.subtotal for item in self.items)
        total = subtotal - self.diskon + self.pajak
        self.subtotal = subtotal
        self.total = total
        return total
    
    def generate_invoice():
        """Generate nomor invoice otomatis"""
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        # Cari transaksi hari ini
        today_trans = kembalian.query.filter(
            db.func.date(kembalian.created_at) == today.date()
        ).count()
        
        sequence = today_trans + 1
        return f'INV-{date_str}-{sequence:04d}'
    
    @classmethod
    def total_harian(cls):
        """Total penjualan hari ini"""
        today = date.today()
        result = cls.query.filter(
            db.func.date(cls.created_at) == today,
            cls.status == 'selesai'
        ).with_entities(db.func.sum(cls.total)).scalar()
        return result or 0
    
    @classmethod
    def ringkasan_bulanan(cls, tahun=None, bulan=None):
        """Ringkasan penjualan bulanan"""
        from datetime import datetime
        import calendar
        
        if not tahun:
            tahun = datetime.now().year
        if not bulan:
            bulan = datetime.now().month
            
        # Hitung hari dalam bulan
        _, last_day = calendar.monthrange(tahun, bulan)
        
        # Query untuk bulan tertentu
        start_date = date(tahun, bulan, 1)
        end_date = date(tahun, bulan, last_day)
        
        transaksi = cls.query.filter(
            cls.created_at.between(start_date, end_date),
            cls.status == 'selesai'
        ).all()
        
        return {
            'total_transaksi': len(transaksi),
            'total_penjualan': sum(t.total for t in transaksi),
            'rata_rata': sum(t.total for t in transaksi) / len(transaksi) if transaksi else 0
        }
        
    def hitung_total(self):
        """Hitung ulang total transaksi"""
        subtotal = sum(item.subtotal for item in self.items)
        total = subtotal - self.diskon + self.pajak
        self.subtotal = subtotal
        self.total = total
        return total
        
    def generate_invoice(self):
        """Generate nomor invoice otomatis"""
        today = datetime.now()
        date_str = today.strftime('%Y%m%d')
        
        # Cari transaksi hari ini
        today_trans = kembalian.query.filter(
            db.func.date(kembalian.created_at) == today.date()
        ).count()
        
        sequence = today_trans + 1
        return f'INV-{date_str}-{sequence:04d}'