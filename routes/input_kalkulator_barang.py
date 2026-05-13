from flask import Blueprint, render_template, request, jsonify, session
from models.transaksi import transaksi as Transaksi
from models.item_transaksi import ItemTransaksi
from models.produk import Produk
from models.kategori import Kategori
from models.base import db
from routes.auth import login_required
import uuid

input_kalkulator_barang_bp = Blueprint(
    'input_kalkulator_barang', __name__, url_prefix='/input-kalkulator-barang'
)


@input_kalkulator_barang_bp.route('/', methods=['GET'])
@login_required
def halaman_kalkulator():
    return render_template('kalkulator.html')


@input_kalkulator_barang_bp.route('/simpan', methods=['POST'])
@login_required
def simpan_barang():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Data kosong'}), 400

        nama     = str(data.get('nama',     '')).strip()
        harga    = float(data.get('harga',  0))
        diskon   = float(data.get('diskon', 0))
        jumlah   = int(data.get('jumlah',   1))
        kategori = str(data.get('kategori', 'Umum')).strip()

        if not nama:
            return jsonify({'success': False, 'error': 'Nama barang harus diisi'}), 400
        if harga <= 0:
            return jsonify({'success': False, 'error': 'Harga tidak boleh 0'}), 400
        if jumlah <= 0:
            return jsonify({'success': False, 'error': 'Jumlah tidak boleh 0'}), 400

        subtotal     = harga * jumlah
        nilai_diskon = min(diskon * jumlah, subtotal)
        total        = max(0, subtotal - nilai_diskon)

        invoice = Transaksi.generate_invoice()
        user_id = session.get('user_id')

        t = Transaksi(
            invoice      = invoice,
            user_id      = user_id,
            subtotal     = subtotal,
            diskon       = nilai_diskon,
            pajak        = 0,
            total        = total,
            bayar        = total,
            kembalian    = 0,
            metode_bayar = 'tunai',
            status       = 'pending'  
        )
        db.session.add(t)
        db.session.flush()

        # Cari produk berdasarkan nama
        produk = Produk.query.filter(Produk.nama.ilike(f'%{nama}%')).first()

        # Kalau produk tidak ada, buat baru otomatis
        if not produk:
            kode_unik = 'KLK-' + uuid.uuid4().hex[:8].upper()
            kat = Kategori.query.filter_by(nama='Lainnya').first()
            produk = Produk(
                kode_barang = kode_unik,
                nama        = nama,
                harga_jual  = harga,
                harga_beli  = 0,
                stok        = 0,
                satuan      = 'pcs',
                is_active   = True,
                kategori_id = kat.id if kat else None
            )
            db.session.add(produk)
            db.session.flush()

        item = ItemTransaksi(
            transaksi_id = t.id,
            produk_id    = produk.id,
            qty          = jumlah,
            harga_satuan = harga,
            subtotal     = total,
            diskon_item  = nilai_diskon
        )
        db.session.add(item)

        # Kurangi stok
        produk.stok -= jumlah

        db.session.commit()

        return jsonify({
            'success': True,
            'invoice': invoice,
            'total'  : total,
            'pesan'  : f'Barang Tersimpan — {nama} | Rp {int(total):,}'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500