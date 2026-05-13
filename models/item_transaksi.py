from .base import db, BaseModel
from models.base import db
class ItemTransaksi(BaseModel):
    __tablename__ = 'item_transaksi'
    
    transaksi_id = db.Column(db.Integer, db.ForeignKey('transaksi.id'), nullable=False)
    produk_id = db.Column(db.Integer, db.ForeignKey('produk.id'), nullable=False)
    
    # Detail item
    qty = db.Column(db.Integer, nullable=False)
    harga_satuan = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    # Diskon per item (jika ada)
    diskon_item = db.Column(db.Float, default=0)

    produk = db.relationship('Produk', lazy=True)
    
    def __repr__(self):
        return f'<ItemTransaksi {self.id}: {self.qty} item>'
    
    def hitung_subtotal(self):
        """Hitung subtotal item"""
        self.subtotal = (self.harga_satuan * self.qty) - self.diskon_item
        return self.subtotal
    
