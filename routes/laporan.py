from flask import Blueprint, render_template, request, jsonify, send_file
from sqlalchemy import func
from models.transaksi import transaksi as Transaksi
from models.item_transaksi import ItemTransaksi
from models.produk import Produk
from models.user import User
from models.kategori import Kategori as KategoriModel
from models.base import db
from routes.auth import login_required, admin_required
from datetime import datetime, date, timedelta
import io
import csv

laporan_bp = Blueprint('laporan', __name__, url_prefix='/laporan')


# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────
def parse_tanggal(start_date_str, end_date_str, default_days=30):
    today = date.today()
    try:
        start = datetime.strptime(start_date_str, '%Y-%m-%d')
        end   = datetime.strptime(end_date_str,   '%Y-%m-%d') + timedelta(days=1)
        return start, end, start_date_str, end_date_str
    except (ValueError, TypeError):
        start     = datetime.combine(today - timedelta(days=default_days), datetime.min.time())
        end       = datetime.combine(today + timedelta(days=1),            datetime.min.time())
        start_str = (today - timedelta(days=default_days)).isoformat()
        end_str   = today.isoformat()
        return start, end, start_str, end_str


# ─────────────────────────────────────────
# HALAMAN UTAMA LAPORAN
# ─────────────────────────────────────────
# ✅ Redirect ke output_barang agar variabel page tersedia
@laporan_bp.route('/')
@login_required
@admin_required
def laporan():
    from flask import redirect, url_for
    return redirect(url_for('laporan.output_barang'))


# ─────────────────────────────────────────
# PENJUALAN
# ─────────────────────────────────────────
@laporan_bp.route('/penjualan')
@login_required
@admin_required
def penjualan():
    today     = date.today()
    start_str = request.args.get('start_date', today.replace(day=1).isoformat())
    end_str   = request.args.get('end_date',   today.isoformat())

    start, end, start_date, end_date = parse_tanggal(start_str, end_str, default_days=30)

    transaksi_list  = Transaksi.query.filter(
        Transaksi.created_at >= start,
        Transaksi.created_at <  end,
        Transaksi.status     == 'selesai'
    ).order_by(Transaksi.created_at.desc()).all()

    total_transaksi = len(transaksi_list)
    total_penjualan = sum(t.total for t in transaksi_list)
    rata_rata       = total_penjualan / total_transaksi if total_transaksi > 0 else 0

    return render_template('laporan.html',
        total_transaksi = total_transaksi,
        total_penjualan = total_penjualan,
        rata_rata       = rata_rata,
        start_date      = start_date,
        end_date        = end_date,
        # ✅ Variabel wajib agar tidak undefined di template
        page            = 1,
        per_page        = 10,
        total_barang    = 0,
        total_pages     = 1,
        data_barang     = [],
        total_nilai     = 0,
        date_from       = start_date,
        date_to         = end_date,
        keyword         = ''
    )


# ─────────────────────────────────────────
# PRODUK TERLARIS
# ─────────────────────────────────────────
@laporan_bp.route('/produk-terlaris')
@login_required
@admin_required
def produk_terlaris():
    today     = date.today()
    start_str = request.args.get('start_date', (today - timedelta(days=30)).isoformat())
    end_str   = request.args.get('end_date',   today.isoformat())

    start, end, start_date, end_date = parse_tanggal(start_str, end_str, default_days=30)

    # Query produk terlaris
    rows = db.session.query(
        Produk.nama,
        KategoriModel.nama.label('kategori'),
        func.sum(ItemTransaksi.qty).label('total_terjual'),
        func.sum(ItemTransaksi.subtotal).label('total_nilai')
    ).join(
        ItemTransaksi, Produk.id == ItemTransaksi.produk_id
    ).join(
        Transaksi, ItemTransaksi.transaksi_id == Transaksi.id
    ).outerjoin(
        KategoriModel, Produk.kategori_id == KategoriModel.id
    ).filter(
        Transaksi.created_at >= start,
        Transaksi.created_at <  end,
        Transaksi.status     == 'selesai'
    ).group_by(
        Produk.id, Produk.nama, KategoriModel.nama
    ).order_by(
        func.sum(ItemTransaksi.qty).desc()
    ).limit(20).all()

    return render_template('laporan.html',
        start_date      = start_date,
        end_date        = end_date,
        produk_terlaris = rows,
        # ✅ Variabel wajib
        page            = 1,
        per_page        = 10,
        total_barang    = len(rows),
        total_pages     = 1,
        data_barang     = [],
        total_nilai     = sum(r.total_nilai or 0 for r in rows),
        date_from       = start_date,
        date_to         = end_date,
        keyword         = ''
    )


# ─────────────────────────────────────────
# OUTPUT BARANG
# ─────────────────────────────────────────
@laporan_bp.route('/output-barang')
@login_required
@admin_required
def output_barang():
    today     = date.today()
    start_str = request.args.get('date_from', today.replace(day=1).isoformat())
    end_str   = request.args.get('date_to',   today.isoformat())
    keyword   = request.args.get('q', '').strip()
    page      = request.args.get('page', 1, type=int)
    per_page  = 10

    start, end, date_from, date_to = parse_tanggal(start_str, end_str)

    query = db.session.query(
        ItemTransaksi, Transaksi, Produk, User, KategoriModel
    ).join(
        Transaksi, ItemTransaksi.transaksi_id == Transaksi.id
    ).join(
        Produk, ItemTransaksi.produk_id == Produk.id
    ).outerjoin(
        User, Transaksi.user_id == User.id
    ).outerjoin(
        KategoriModel, Produk.kategori_id == KategoriModel.id
    ).filter(
        Transaksi.created_at >= start,
        Transaksi.created_at <  end,
        Transaksi.status     == 'selesai'
    )

    if keyword:
        query = query.filter(Produk.nama.ilike(f'%{keyword}%'))

    total_barang = query.count()
    total_pages  = max(1, (total_barang + per_page - 1) // per_page)
    page         = min(max(1, page), total_pages)

    rows = query.order_by(Transaksi.created_at.desc()) \
                .offset((page - 1) * per_page) \
                .limit(per_page).all()

    data_barang = []
    for item, trx, produk, user, kat in rows:
        data_barang.append({
            'tanggal'     : trx.created_at,
            'nama_barang' : produk.nama        if produk else '-',
            'kategori'    : kat.nama            if kat    else '-',
            'jumlah'      : item.qty,
            'harga_satuan': item.harga_satuan,
            'total_harga' : item.subtotal,
            'nama_kasir'  : user.nama_lengkap   if user   else '-',
        })

    all_rows    = query.all()
    total_nilai = sum(
        item.subtotal
        for item, trx, produk, user, kat in all_rows
    ) if all_rows else 0

    return render_template('laporan.html',
        data_barang  = data_barang,
        total_barang = total_barang,
        total_nilai  = total_nilai,
        total_pages  = total_pages,
        page         = page,
        per_page     = per_page,
        date_from    = date_from,
        date_to      = date_to,
        keyword      = keyword,
        # ✅ Variabel tambahan agar template tidak undefined
        start_date   = date_from,
        end_date     = date_to,
        total_transaksi = 0,
        total_penjualan = total_nilai,
        rata_rata       = 0
    )


# ─────────────────────────────────────────
# EXPORT CSV
# ─────────────────────────────────────────
@laporan_bp.route('/export-output-barang')
@login_required
@admin_required
def export_output_barang():
    today     = date.today()
    start_str = request.args.get('date_from', today.replace(day=1).isoformat())
    end_str   = request.args.get('date_to',   today.isoformat())

    start, end, _, _ = parse_tanggal(start_str, end_str)

    rows = db.session.query(
        ItemTransaksi, Transaksi, Produk, User, KategoriModel
    ).join(
        Transaksi, ItemTransaksi.transaksi_id == Transaksi.id
    ).join(
        Produk, ItemTransaksi.produk_id == Produk.id
    ).outerjoin(
        User, Transaksi.user_id == User.id
    ).outerjoin(
        KategoriModel, Produk.kategori_id == KategoriModel.id
    ).filter(
        Transaksi.created_at >= start,
        Transaksi.created_at <  end,
        Transaksi.status     == 'selesai'
    ).order_by(Transaksi.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Tanggal', 'Nama Barang', 'Kategori',
        'Jumlah', 'Harga Satuan', 'Total Harga', 'Kasir'
    ])

    for item, trx, produk, user, kat in rows:
        writer.writerow([
            trx.created_at.strftime('%Y-%m-%d') if trx.created_at else '-',
            produk.nama        if produk else '-',
            kat.nama            if kat    else '-',
            item.qty,
            item.harga_satuan,
            item.subtotal,
            user.nama_lengkap   if user   else '-',
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'laporan_barang_keluar_{today.isoformat()}.csv'
    )


# ─────────────────────────────────────────
# KALKULATOR LAPORAN
# ─────────────────────────────────────────
# ✅ Diperbaiki: tambah @ di depan route
@laporan_bp.route('/kalkulator', methods=['GET'])
@login_required
def kalkulator():
    start_date = request.args.get('start_date', (date.today() - timedelta(days=30)).isoformat())
    end_date   = request.args.get('end_date',    date.today().isoformat())

    start = datetime.strptime(start_date, '%Y-%m-%d')
    end   = datetime.strptime(end_date,   '%Y-%m-%d').replace(hour=23, minute=59, second=59)

    query = Transaksi.query.filter(
        Transaksi.created_at >= start,
        Transaksi.created_at <= end,
        Transaksi.status     == 'selesai'
    )

    total_transaksi = query.count()
    total_penjualan = query.with_entities(
        func.sum(Transaksi.total)
    ).scalar() or 0

    rata_rata = (total_penjualan / total_transaksi) if total_transaksi > 0 else 0

    total_barang = db.session.query(
        func.sum(ItemTransaksi.qty)
    ).join(
        Transaksi, ItemTransaksi.transaksi_id == Transaksi.id
    ).filter(
        Transaksi.created_at >= start,
        Transaksi.created_at <= end,
        Transaksi.status     == 'selesai'
    ).scalar() or 0

    laporan_data = {
        'start_date'      : start_date,
        'end_date'        : end_date,
        'total_transaksi' : total_transaksi,
        'total_barang'    : total_barang,
        'total_penjualan' : total_penjualan,
        'rata_rata'       : rata_rata,
        'periode'         : f"{start_date} s/d {end_date}"
    }

    return render_template('laporan/kalkulator.html', laporan=laporan_data)