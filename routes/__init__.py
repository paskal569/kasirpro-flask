from .barcode import barcode_bp
from .auth import auth_bp
from .produk import produk_bp
from .transaksi import transaksi_bp
from .laporan import laporan_bp
from .dashboard import dashboard_bp
from .kategori import kategori_bp
from .loading_konfirmasi import loading_konfirmasi_bp
from .input_barang import input_barang_bp, import_barang_bp
from .kalkulator import kalkulator as kalkulator_bp
from .pembayaran import pembayaran_bp
from .pelanggan import pelanggan_bp
from .stock import stock_bp
from .pengaturan import pengaturan_bp
from .input_kalkulator_barang import input_kalkulator_barang_bp

blueprints = [
    auth_bp,
    produk_bp,
    transaksi_bp,
    laporan_bp,
    dashboard_bp,
    kategori_bp,
    barcode_bp,
    loading_konfirmasi_bp,
    input_barang_bp,
    import_barang_bp,
    kalkulator_bp,
    stock_bp,
    pembayaran_bp,
    pelanggan_bp,
    input_kalkulator_barang_bp,
    pengaturan_bp,
]

def register_blueprints(app):
    for bp in blueprints:
        app.register_blueprint(bp)  # ← hanya 1 baris ini, tidak ada duplikat