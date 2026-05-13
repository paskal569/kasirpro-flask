from .base import db, BaseModel  # ✅ cukup satu import

class Produk(BaseModel):
    __tablename__ = 'produk'

    kode_barang     = db.Column(db.String(50), unique=True, nullable=False)  # ✅ diganti jadi kode_barang agar konsisten dengan route
    barcode         = db.Column(db.String(100), unique=True, nullable=True)
    nama            = db.Column(db.String(200), nullable=False)
    kategori_id     = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=True)  # ✅ nullable=True agar tidak wajib diisi
    deskripsi       = db.Column(db.Text, nullable=True)

    # Harga
    harga_beli      = db.Column(db.Float, default=0)
    harga_jual      = db.Column(db.Float, nullable=False)
    harga_grosir    = db.Column(db.Float, nullable=True)
    minimal_grosir  = db.Column(db.Integer, default=10)

    # Stok
    stok            = db.Column(db.Integer, default=0)
    stok_minimum    = db.Column(db.Integer, default=5)
    satuan          = db.Column(db.String(20), default='pcs')

    # Gambar
    gambar          = db.Column(db.String(255), nullable=True)

    # Status
    is_active       = db.Column(db.Boolean, default=True)

    # Relationship
    transaksi_items = db.relationship('ItemTransaksi', backref='produk_detail', lazy=True)

    def __repr__(self):
        return f'<Produk {self.kode_barang}: {self.nama}>'

    @property
    def keuntungan(self):
        """Hitung keuntungan per item"""
        return self.harga_jual - self.harga_beli

    @property
    def margin(self):
        """Hitung persentase margin"""
        if self.harga_beli > 0:
            return ((self.harga_jual - self.harga_beli) / self.harga_beli) * 100
        return 0

    def kurangi_stok(self, jumlah):
        """Kurangi stok produk"""
        if self.stok >= jumlah:
            self.stok -= jumlah
            self.save()
            return True
        return False

    def tambah_stok(self, jumlah):
        """Tambah stok produk"""
        self.stok += jumlah
        self.save()
        return True

    def cek_stok(self):
        """Cek apakah stok mencukupi"""
        return self.stok > self.stok_minimum

    @classmethod
    def cari(cls, keyword):
        """Cari produk berdasarkan nama atau kode"""
        return cls.query.filter(
            (cls.nama.ilike(f'%{keyword}%')) |
            (cls.kode_barang.ilike(f'%{keyword}%'))  # ✅ disesuaikan
        ).all()

    @classmethod
    def stok_menipis(cls):
        """Ambil produk dengan stok menipis"""
        return cls.query.filter(cls.stok <= cls.stok_minimum).all()