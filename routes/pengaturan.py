from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file,
    flash,
    redirect,
    url_for,
    session
)

from datetime import datetime
import json
import os
import io
import zipfile

from models.base import db
from models.user import User
from models.produk import Produk
from models.pelanggan import Pelanggan
from models.kategori import Kategori as KategoriModel
from models.transaksi import transaksi as Transaksi
from models.item_transaksi import ItemTransaksi

from routes.auth import login_required, admin_required


# =====================================================
# BLUEPRINT
# =====================================================
pengaturan_bp = Blueprint(
    'pengaturan',
    __name__,
    url_prefix='/pengaturan'
)


# =====================================================
# PATH FILE JSON
# =====================================================
BASE_DIR = os.path.dirname(__file__)

DATA_PERUSAHAAN_PATH = os.path.join(BASE_DIR, '..', 'data_perusahaan.json')
BACKUP_SETTING_PATH  = os.path.join(BASE_DIR, '..', 'backup_setting.json')
PRINTER_SETTING_PATH = os.path.join(BASE_DIR, '..', 'printer_setting.json')


# =====================================================
# HELPER — USER
# =====================================================
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


# =====================================================
# HELPER — DATA PERUSAHAAN
# =====================================================
def baca_data_perusahaan():
    default = {'nama': '', 'alamat': '', 'telepon': '', 'website': ''}
    try:
        if os.path.exists(DATA_PERUSAHAAN_PATH):
            with open(DATA_PERUSAHAAN_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return default


def simpan_data_perusahaan(data):
    with open(DATA_PERUSAHAAN_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =====================================================
# HELPER — BACKUP SETTING
# =====================================================
DEFAULT_BACKUP_SETTING = {
    'backup_otomatis' : False,
    'enkripsi'        : False,
    'frekuensi'       : 'harian',
    'waktu'           : '02:00',
    'retensi'         : 30,
    'lokasi'          : 'lokal',
    'backup_transaksi': True,
    'backup_produk'   : True,
    'backup_pelanggan': True,
    'backup_kategori' : True
}


def baca_backup_setting():
    try:
        if os.path.exists(BACKUP_SETTING_PATH):
            with open(BACKUP_SETTING_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {**DEFAULT_BACKUP_SETTING, **data}
    except Exception:
        pass
    return DEFAULT_BACKUP_SETTING.copy()


def simpan_backup_setting(data):
    with open(BACKUP_SETTING_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =====================================================
# HELPER — PRINTER SETTING
# =====================================================
DEFAULT_PRINTER_SETTING = {
    'port_koneksi'      : 'USB001',
    'baud_rate'         : '9600',
    'lebar_kertas'      : '80mm',
    'karakter_per_baris': '42',
    'auto_cut'          : True,
    'buka_laci'         : True,
    'bunyi_cetak'       : False
}


def baca_printer_setting():
    try:
        if os.path.exists(PRINTER_SETTING_PATH):
            with open(PRINTER_SETTING_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {**DEFAULT_PRINTER_SETTING, **data}
    except Exception:
        pass
    return DEFAULT_PRINTER_SETTING.copy()


def simpan_printer_setting(data):
    with open(PRINTER_SETTING_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =====================================================
# HELPER — DETEKSI PRINTER
# =====================================================
def get_printers():
    """
    Deteksi printer yang terpasang.
    Pakai win32print jika tersedia (Windows).
    Fallback ke data dummy jika tidak ada / Linux / server.
    """
    printers = []

    try:
        # ✅ Import hanya jika tersedia — tidak crash di Linux/server
        import win32print
        raw = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL |
            win32print.PRINTER_ENUM_CONNECTIONS
        )
        for p in raw:
            printers.append({
                'nama'   : p[2],
                'model'  : p[2],
                'port'   : p[1] or 'USB',
                'kertas' : '80mm',
                'status' : 'online',
                'default': win32print.GetDefaultPrinter() == p[2]
            })

    except ImportError:
        # ✅ Fallback: win32print tidak tersedia (Linux/Mac/server)
        printers = [
            {
                'nama'   : 'Epson TM-T82X',
                'model'  : 'TM-T82X',
                'port'   : 'USB001',
                'kertas' : '80mm',
                'status' : 'online',
                'default': True
            },
            {
                'nama'   : 'Star TSP143',
                'model'  : 'TSP143IIIU',
                'port'   : 'COM1',
                'kertas' : '80mm',
                'status' : 'offline',
                'default': False
            }
        ]

    except Exception:
        # ✅ Error lain — kembalikan list kosong
        printers = []

    return printers


def get_scanners():
    """
    Deteksi scanner. Saat ini pakai data dummy.
    Bisa dikembangkan dengan library WIA/SANE.
    """
    return [
        {
            'nama'  : 'Honeywell 1900',
            'model' : '1900GSR-2',
            'status': 'offline'
        }
    ]


# =====================================================
# HALAMAN UTAMA PENGATURAN
# =====================================================
@pengaturan_bp.route('/')
@login_required
@admin_required
def pengaturan():
    user = get_current_user()
    if not user:
        flash('Sesi tidak valid, silakan login ulang', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('pengaturan.html', user=user)


# =====================================================
# PROFIL PENGGUNA
# =====================================================
@pengaturan_bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil_pengguna():
    user = get_current_user()
    if not user:
        flash('Sesi tidak valid, silakan login ulang', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nama    = request.form.get('nama_lengkap', '').strip()
        email   = request.form.get('email', '').strip()
        telepon = request.form.get('telepon', '').strip()

        if not nama or not email:
            flash('Nama dan email wajib diisi', 'danger')
            return redirect(url_for('pengaturan.profil_pengguna'))

        user.nama_lengkap = nama
        user.email        = email
        user.telepon      = telepon
        db.session.commit()

        session['nama'] = nama
        flash('Profil berhasil disimpan', 'success')
        return redirect(url_for('pengaturan.profil_pengguna'))

    return render_template('pengaturan.html', user=user)


# =====================================================
# DATA PERUSAHAAN
# =====================================================
@pengaturan_bp.route('/data-perusahaan', methods=['GET', 'POST'])
@login_required
@admin_required
def data_perusahaan():
    if request.method == 'POST':
        nama    = request.form.get('nama_perusahaan', '').strip()
        alamat  = request.form.get('alamat', '').strip()
        telepon = request.form.get('telepon', '').strip()
        website = request.form.get('website', '').strip()

        if not nama:
            flash('Nama perusahaan wajib diisi', 'danger')
            return redirect(url_for('pengaturan.data_perusahaan'))

        simpan_data_perusahaan({
            'nama'   : nama,
            'alamat' : alamat,
            'telepon': telepon,
            'website': website
        })

        flash('Data perusahaan berhasil disimpan', 'success')
        return redirect(url_for('pengaturan.data_perusahaan'))

    info = baca_data_perusahaan()
    return render_template('data_perusahaan.html', info=info)


# =====================================================
# HALAMAN BACKUP & RESTORE
# =====================================================
@pengaturan_bp.route('/backup-restore')
@login_required
@admin_required
def halaman_backup_restore():
    setting = baca_backup_setting()
    return render_template('backup_restore.html', setting=setting)


# =====================================================
# BACKUP — Download ZIP
# =====================================================
@pengaturan_bp.route('/backup', methods=['POST'])
@login_required
@admin_required
def backup():
    # ✅ Nama fungsi konsisten huruf kecil semua
    setting = {
        'backup_otomatis' : request.form.get('backup_otomatis') == 'on',
        'enkripsi'        : request.form.get('enkripsi')        == 'on',
        'frekuensi'       : request.form.get('frekuensi',  'harian'),
        'waktu'           : request.form.get('waktu',      '02:00'),
        'retensi'         : int(request.form.get('retensi', 30)),
        'lokasi'          : request.form.get('lokasi',     'lokal'),
        'backup_transaksi': request.form.get('backup_transaksi') == 'on',
        'backup_produk'   : request.form.get('backup_produk')    == 'on',
        'backup_pelanggan': request.form.get('backup_pelanggan') == 'on',
        'backup_kategori' : request.form.get('backup_kategori')  == 'on'
    }

    simpan_backup_setting(setting)

    try:
        data_backup = {}

        if setting['backup_kategori']:
            data_backup['kategori'] = [
                {'id': k.id, 'nama': k.nama}
                for k in KategoriModel.query.all()
            ]

        if setting['backup_produk']:
            data_backup['produk'] = [
                {
                    'id'        : p.id,
                    'nama'      : p.nama,
                    'harga_jual': p.harga_jual,
                    'harga_beli': p.harga_beli,
                    'stok'      : p.stok
                }
                for p in Produk.query.all()
            ]

        if setting['backup_pelanggan']:
            data_backup['pelanggan'] = [
                {'id': p.id, 'nama': p.nama}
                for p in Pelanggan.query.all()
            ]

        if setting['backup_transaksi']:
            data_backup['transaksi'] = [
                {
                    'id'          : t.id,
                    'invoice'     : t.invoice,
                    'total'       : t.total,
                    'status'      : t.status,
                    'metode_bayar': t.metode_bayar,
                    'created_at'  : t.created_at.isoformat() if t.created_at else None,
                    'items'       : [
                        {
                            'produk_id'   : i.produk_id,
                            'qty'         : i.qty,
                            'harga_satuan': i.harga_satuan,
                            'subtotal'    : i.subtotal
                        }
                        for i in t.items
                    ]
                }
                for t in Transaksi.query.all()
            ]

        data_backup['info'] = {
            'tanggal_backup': datetime.now().isoformat(),
            'versi'         : '1.0'
        }

        json_bytes = json.dumps(
            data_backup,
            ensure_ascii=False,
            indent=2
        ).encode('utf-8')

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('backup.json', json_bytes)
        zip_buffer.seek(0)

        filename = f"backup_kasir_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        flash(f'Backup gagal: {str(e)}', 'danger')
        return redirect(url_for('pengaturan.halaman_backup_restore'))


# =====================================================
# RESTORE — Upload ZIP
# =====================================================
@pengaturan_bp.route('/backup-restore/restore', methods=['POST'])
@login_required
@admin_required
def restore():
    try:
        file = request.files.get('file_backup')
        if not file or not file.filename:
            return jsonify({'success': False, 'message': 'File tidak ditemukan'}), 400

        zip_buffer = io.BytesIO(file.read())
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            if 'backup.json' not in zf.namelist():
                return jsonify({'success': False, 'message': 'File backup tidak valid'}), 400
            data_backup = json.loads(zf.read('backup.json').decode('utf-8'))

        if 'kategori' in data_backup:
            for k in data_backup['kategori']:
                if not KategoriModel.query.get(k['id']):
                    db.session.add(KategoriModel(id=k['id'], nama=k['nama']))
            db.session.flush()

        if 'produk' in data_backup:
            for p in data_backup['produk']:
                if not Produk.query.get(p['id']):
                    db.session.add(Produk(
                        id         = p['id'],
                        nama       = p['nama'],
                        harga_jual = p['harga_jual'],
                        harga_beli = p['harga_beli'],
                        stok       = p['stok']
                    ))
            db.session.flush()

        if 'pelanggan' in data_backup:
            for p in data_backup['pelanggan']:
                if not Pelanggan.query.get(p['id']):
                    db.session.add(Pelanggan(id=p['id'], nama=p['nama']))
            db.session.flush()

        if 'transaksi' in data_backup:
            for t in data_backup['transaksi']:
                if not Transaksi.query.get(t['id']):
                    t_baru = Transaksi(
                        id           = t['id'],
                        invoice      = t['invoice'],
                        total        = t['total'],
                        status       = t['status'],
                        metode_bayar = t['metode_bayar'],
                        created_at   = datetime.fromisoformat(t['created_at']) if t['created_at'] else None
                    )
                    db.session.add(t_baru)
                    db.session.flush()

                    for item in t.get('items', []):
                        db.session.add(ItemTransaksi(
                            transaksi_id = t_baru.id,
                            produk_id    = item['produk_id'],
                            qty          = item['qty'],
                            harga_satuan = item['harga_satuan'],
                            subtotal     = item['subtotal']
                        ))

        db.session.commit()
        return jsonify({'success': True, 'message': 'Restore berhasil!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# INTEGRASI PRINTER
# =====================================================
@pengaturan_bp.route('/integrasi', methods=['GET', 'POST'])
@login_required
def integrasi():

    if request.method == 'POST':
        data = {
            'port_koneksi'      : request.form.get('port_koneksi', 'USB001'),
            'baud_rate'         : request.form.get('baud_rate', '9600'),
            'lebar_kertas'      : request.form.get('lebar_kertas', '80mm'),
            'karakter_per_baris': request.form.get('karakter_per_baris', '42'),
            'auto_cut'          : 'auto_cut'    in request.form,
            'buka_laci'         : 'buka_laci'   in request.form,
            'bunyi_cetak'       : 'bunyi_cetak' in request.form
        }

        simpan_printer_setting(data)

        flash('Pengaturan printer berhasil disimpan', 'success')
        return redirect(url_for('pengaturan.integrasi'))

    # ✅ Ambil data printer & scanner dari helper
    printers           = get_printers()
    scanners           = get_scanners()
    pengaturan_printer = baca_printer_setting()

    return render_template(
        'integrasi.html',
        printers           = printers,
        scanners           = scanners,
        pengaturan_printer = pengaturan_printer
    )