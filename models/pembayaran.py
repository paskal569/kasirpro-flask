from .base import db, BaseModel
from models.base import db
class Pembayaran(BaseModel):
    __tablename__ = 'pembayaran'

    id = db.Column(db.Integer, primary_key=True)

    transaksi_id = db.Column(
        db.Integer,
        db.ForeignKey('transaksi.id'),
        nullable=False
    )

    produk_id = db.Column(
        db.Integer,
        db.ForeignKey('produk.id'),
        nullable=False
    )

    # Detail item
    qty = db.Column(db.Integer, nullable=False)
    harga_satuan = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    pilihan_pembayaran = db.Column(
        db.String(50),
        nullable=False
    )

    # Diskon per item (jika ada)
    diskon_item = db.Column(db.Float, default=0)
