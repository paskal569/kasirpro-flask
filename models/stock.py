from models.db import db

class Stock(db.Model):
   
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    kategori = db.Column(db.String(100), nullable=False)
    stok_rendah = db.Column(db.Integer, nullable=False)
    total_produk = db.Column(db.Integer, nullable=False)
    produk_tersedia = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __repr__(self):
        return f"Stock('{self.name}', '{self.quantity}', '{self.price}')"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
