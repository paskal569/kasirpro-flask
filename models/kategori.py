from .base import db, BaseModel
from sqlalchemy.orm import validates
import re
from models.base import db

class Kategori(BaseModel):
    __tablename__ = 'kategori'

    # ========== KOLOM UTAMA ==========
    nama = db.Column(db.String(100), nullable=False, unique=True, index=True)
    slug = db.Column(db.String(120), unique=True, index=True)  # untuk URL
    deskripsi = db.Column(db.Text)

    # ========== TAMPILAN ==========
    icon = db.Column(db.String(50), default='📦')  # emoji atau nama icon
    nonaktif = db.Column(db.Boolean, default=False)  # untuk menandai kategori yang tidak aktif
    warna = db.Column(db.String(20), default='#4CAF50')  # warna dalam hex
    warna_text = db.Column(db.String(20), default='#FFFFFF')  # warna teks

    # ========== PENGATURAN ==========
    is_active = db.Column(db.Boolean, default=True)
    urutan = db.Column(db.Integer, default=0)  # untuk sorting
    jenis = db.Column(db.String(20), default='produk')  # produk/jasa/pulsa/dll

    # ========== STATISTIK ==========
    total_produk = db.Column(db.Integer, default=0)
    total_terjual = db.Column(db.Integer, default=0)
    total_pendapatan = db.Column(db.Float, default=0.0)

    produk = db.relationship(
        'Produk',
        backref='kategori',
        lazy=True,
        cascade='all, delete-orphan'  # otomatis hapus produk jika kategori dihapus
    )

    @validates('nama')
    def validate_nama(self, key, nama):
        if not nama or len(nama.strip()) == 0:
            raise ValueError('Nama kategori tidak boleh kosong')
        if len(nama) > 100:
            raise ValueError('Nama kategori maksimal 100 karakter')
        return nama.strip()

    @validates('slug')
    def validate_slug(self, key, slug):
        if slug:
            # Buat slug otomatis jika tidak diisi
            if not re.match(r'^[a-z0-9-]+$', slug):
                raise ValueError('Slug hanya boleh huruf kecil, angka, dan strip')
        return slug

    @validates('warna')
    def validate_warna(self, key, warna):
        # Validasi format warna hex
        if warna and not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', warna):
            raise ValueError('Format warna harus hex (#RRGGBB)')
        return warna

    # ========== METHOD KHUSUS ==========
    def __repr__(self):
        return f'<Kategori [{self.id}] {self.nama}>'

    def __str__(self):
        return f"{self.icon} {self.nama}"

    def generate_slug(self):
        """Generate slug otomatis dari nama"""
        import unicodedata

        nama = self.nama.lower()
        # Hapus karakter aneh
        nama = unicodedata.normalize('NFKD', nama).encode('ascii', 'ignore').decode('ascii')
        # Ganti spasi dengan dash
        slug = re.sub(r'[^\w\s-]', '', nama)
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')

        # Tambah angka jika slug sudah ada
        original_slug = slug
        counter = 1
        while Kategori.query.filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1

        self.slug = slug
        return slug

    def hitung_statistik(self):
        """Hitung ulang statistik kategori"""
        from .produk import Produk

        produk_list = Produk.query.filter_by(kategori_id=self.id).all()

        self.total_produk = len(produk_list)
        self.total_terjual = sum(p.total_terjual for p in produk_list if hasattr(p, 'total_terjual'))
        self.total_pendapatan = sum(p.total_pendapatan for p in produk_list if hasattr(p, 'total_pendapatan'))

        db.session.commit()
        return self

    def get_produk_terlaris(self, limit=5):
        """Ambil produk terlaris dalam kategori"""
        from .produk import Produk

        return Produk.query.filter_by(
            kategori_id=self.id
        ).order_by(
            Produk.total_terjual.desc() if hasattr(Produk, 'total_terjual') else Produk.id.desc()
        ).limit(limit).all()

    def get_produk_stok_menipis(self):
        """Ambil produk yang stoknya menipis"""
        from .produk import Produk

        return Produk.query.filter(
            Produk.kategori_id == self.id,
            Produk.stok <= Produk.stok_minimum
        ).all()

    @property
    def info_singkat(self):
        """Info kategori dalam format ringkas"""
        return {
            'id': self.id,
            'nama': self.nama,
            'icon': self.icon,
            'warna': self.warna,
            'total_produk': self.total_produk,
            'slug': self.slug
        }

    @property
    def badge_color(self):
        """Warna badge berdasarkan jenis kategori"""
        color_maps = {
            'makanan': 'warning',
            'minuman': 'info',
            'rokok': 'dark',
            'snack': 'danger',
            'pulsa': 'primary',
            'jasa': 'success',
            'elektronik': 'secondary',
            'lainnya': 'light'
        }
        return color_maps.get(self.jenis.lower(), 'secondary')

    @property
    def jumlah_produk(self):
        """Alias untuk kompatibilitas di routes"""
        if self.total_produk:
            return self.total_produk
        return len(self.produk) if self.produk is not None else 0

    @classmethod
    def get_all_active(cls):
        """Ambil semua kategori aktif"""
        return cls.query.filter_by(is_active=True).order_by(cls.urutan, cls.nama).all()

    @classmethod
    def get_by_slug(cls, slug):
        """Cari kategori berdasarkan slug"""
        return cls.query.filter_by(slug=slug, is_active=True).first()

    @classmethod
    def search(cls, keyword):
        """Cari kategori berdasarkan nama atau deskripsi"""
        return cls.query.filter(
            cls.is_active == True,
            db.or_(
                cls.nama.ilike(f'%{keyword}%'),
                cls.deskripsi.ilike(f'%{keyword}%')
            )
        ).all()

    @classmethod
    def get_for_select(cls):
        """Ambil kategori untuk dropdown/select"""
        return [(k.id, f"{k.icon} {k.nama}") for k in cls.get_all_active()]

    @classmethod
    def get_statistics(cls):
        """Statistik keseluruhan kategori"""
        total_kategori = cls.query.filter_by(is_active=True).count()
        total_produk = db.session.query(db.func.sum(cls.total_produk)).scalar() or 0

        # Kategori dengan produk terbanyak
        kategori_terbanyak = cls.query.filter(
            cls.is_active == True
        ).order_by(
            cls.total_produk.desc()
        ).first()

        return {
            'total_kategori': total_kategori,
            'total_produk': total_produk,
            'kategori_terbanyak': kategori_terbanyak.nama if kategori_terbanyak else None,
            'rata_produk': round(total_produk / total_kategori, 2) if total_kategori > 0 else 0
        }

    @classmethod
    def create_default_categories(cls):
        """Buat kategori default untuk toko baru"""
        default_categories = [
            {
                'nama': 'Makanan',
                'icon': '🍔',
                'warna': '#FF9800',
                'jenis': 'makanan',
                'deskripsi': 'Makanan ringan dan berat',
                'urutan': 1
            },
            {
                'nama': 'Minuman',
                'icon': '🧋',
                'warna': '#2196F3',
                'jenis': 'minuman',
                'deskripsi': 'Minuman kemasan dan gelas',
                'urutan': 2
            },
            {
                'nama': 'Snack & Cemilan',
                'icon': '🍫',
                'warna': '#FF5722',
                'jenis': 'snack',
                'deskripsi': 'Cemilan ringan',
                'urutan': 3
            },
            {
                'nama': 'Rokok',
                'icon': '🚬',
                'warna': '#795548',
                'jenis': 'rokok',
                'deskripsi': 'Rokok berbagai merk',
                'urutan': 4
            },
            {
                'nama': 'Pulsa & PPOB',
                'icon': '📱',
                'warna': '#00BCD4',
                'jenis': 'pulsa',
                'deskripsi': 'Pulsa, paket data, token listrik',
                'urutan': 5
            },
            {
                'nama': 'ATK',
                'icon': '📝',
                'warna': '#9C27B0',
                'jenis': 'atk',
                'deskripsi': 'Alat tulis kantor',
                'urutan': 6
            },
            {
                'nama': 'Sembako',
                'icon': '🍚',
                'warna': '#8BC34A',
                'jenis': 'sembako',
                'deskripsi': 'Kebutuhan pokok sehari-hari',
                'urutan': 7
            },
            {
                'nama': 'Perawatan Diri',
                'icon': '🧴',
                'warna': '#E91E63',
                'jenis': 'perawatan',
                'deskripsi': 'Sabun, shampoo, pasta gigi',
                'urutan': 8
            },
            {
                'nama': 'Jasa',
                'icon': '🛠️',
                'warna': '#607D8B',
                'jenis': 'jasa',
                'deskripsi': 'Layanan dan jasa',
                'urutan': 9
            },
            {
                'nama': 'Lainnya',
                'icon': '📦',
                'warna': '#9E9E9E',
                'jenis': 'lainnya',
                'deskripsi': 'Produk lainnya',
                'urutan': 999
            }
        ]

        created = []
        for cat_data in default_categories:
            # Cek apakah sudah ada
            existing = cls.query.filter_by(nama=cat_data['nama']).first()
            if not existing:
                kategori = cls(**cat_data)
                kategori.generate_slug()  # Generate slug otomatis
                db.session.add(kategori)
                created.append(cat_data['nama'])

        if created:
            db.session.commit()

        return {
            'created': created,
            'total_created': len(created),
            'message': f'Berhasil membuat {len(created)} kategori default'
        }

    # ========== HOOKS ==========
    @classmethod
    def before_insert(cls, mapper, connection, target):
        """Hook sebelum insert"""
        if not target.slug:
            target.generate_slug()

    @classmethod
    def after_insert(cls, mapper, connection, target):
        """Hook setelah insert"""
        # Log aktivitas atau trigger lainnya
        pass

    def to_dict(self):
        """Konversi ke dictionary untuk API"""
        return {
            'id': self.id,
            'nama': self.nama,
            'slug': self.slug,
            'deskripsi': self.deskripsi,
            'icon': self.icon,
            'warna': self.warna,
            'warna_text': self.warna_text,
            'jenis': self.jenis,
            'urutan': self.urutan,
            'is_active': self.is_active,
            'total_produk': self.total_produk,
            'total_terjual': self.total_terjual,
            'total_pendapatan': self.total_pendapatan,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_minimal_dict(self):
        """Data minimal untuk dropdown"""
        return {
            'id': self.id,
            'nama': self.nama,
            'icon': self.icon,
            'warna': self.warna
        }

