from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from models.transaksi import transaksi as Transaksi
from models.produk import Produk
from models.pelanggan import Pelanggan
from models.item_transaksi import ItemTransaksi
from models.base import db
from routes.auth import login_required
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import json
import io

transaksi_bp = Blueprint('transaksi', __name__, url_prefix='/transaksi')


# ─── HELPER: GENERATE PDF ────────────────────────────────────────────────────

def generate_pdf(t):
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"INVOICE: {t.invoice}", styles['Title']))
    elements.append(Spacer(1, 12))

    info_data = [
        ['Tanggal',   t.created_at.strftime('%d %B %Y, %H:%M')],
        ['Pelanggan', t.pelanggan.nama if t.pelanggan else 'Umum'],
        ['Kasir',     t.user.username if t.user else '—'],
        ['Metode',    t.metode_bayar or '—'],
        ['Status',    t.status.capitalize()],
    ]
    info_table = Table(info_data, colWidths=[120, 300])
    info_table.setStyle(TableStyle([
        ('FONTNAME',      (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 0), (-1, -1), 10),
        ('TEXTCOLOR',     (0, 0), (0, -1),  colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 16))

    item_data = [['#', 'Nama Barang', 'Qty', 'Harga Satuan', 'Subtotal']]
    for i, item in enumerate(t.items, 1):
        item_data.append([
            str(i),
            item.produk.nama if item.produk else '—',
            str(item.qty),
            f"Rp {item.harga_satuan:,.0f}",
            f"Rp {item.subtotal:,.0f}",
        ])
    item_data.append(['', '', '', 'Total', f"Rp {t.total:,.0f}"])

    item_table = Table(item_data, colWidths=[25, 200, 40, 100, 100])
    item_table.setStyle(TableStyle([
        ('BACKGROUND',     (0, 0),  (-1, 0),  colors.HexColor('#1e40af')),
        ('TEXTCOLOR',      (0, 0),  (-1, 0),  colors.white),
        ('FONTNAME',       (0, 0),  (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',       (0, 0),  (-1, -1), 9),
        ('ALIGN',          (2, 0),  (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1),  (-1, -2), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTNAME',       (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE',      (0, -1), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING',  (0, 0),  (-1, -1), 7),
        ('TOPPADDING',     (0, 0),  (-1, -1), 7),
        ('GRID',           (0, 0),  (-1, -2), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(item_table)

    elements.append(Spacer(1, 16))
    summary_data = [
        ['Subtotal',  f"Rp {t.subtotal:,.0f}"],
        ['Diskon',    f"Rp {t.diskon:,.0f}"    if t.diskon    else 'Rp 0'],
        ['Pajak',     f"Rp {t.pajak:,.0f}"     if t.pajak     else 'Rp 0'],
        ['Total',     f"Rp {t.total:,.0f}"],
        ['Bayar',     f"Rp {t.bayar:,.0f}"     if t.bayar     else '—'],
        ['Kembalian', f"Rp {t.kembalian:,.0f}" if t.kembalian else 'Rp 0'],
    ]
    summary_table = Table(summary_data, colWidths=[120, 150])
    summary_table.setStyle(TableStyle([
        ('FONTNAME',      (0, 0),  (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 0),  (-1, -1), 10),
        ('ALIGN',         (1, 0),  (1, -1),  'RIGHT'),
        ('TEXTCOLOR',     (0, 0),  (0, -1),  colors.grey),
        ('FONTNAME',      (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE',     (0, -3), (-1, -3), 1, colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING', (0, 0),  (-1, -1), 5),
    ]))
    elements.append(summary_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@transaksi_bp.route('/')
@login_required
def daftar_transaksi():
    page     = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q        = request.args.get('q', '').strip()

    if per_page not in [10, 25, 50, 100]:
        per_page = 10

    query = Transaksi.query.order_by(Transaksi.created_at.desc())

    if q:
        query = query.filter(Transaksi.invoice.ilike(f'%{q}%'))

    transaksi_list = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('transaksi.html',
                           transaksi_list=transaksi_list,
                           per_page=per_page)


@transaksi_bp.route('/baru', methods=['POST'])
@login_required
def baru():
    try:
        data = request.get_json()

        if not data or 'items' not in data:
            return jsonify({'success': False, 'error': 'Data tidak valid'})

        items        = data['items']
        pelanggan_id = data.get('pelanggan_id')
        diskon       = float(data.get('diskon', 0))
        pajak        = float(data.get('pajak', 0))
        bayar        = float(data.get('bayar', 0))
        metode_bayar = data.get('metode_bayar', 'tunai')  # ✅ satu default saja
        no_rekening  = data.get('no_rekening', '').strip()

        # ✅ Validasi nomor rekening hanya jika metode non-tunai
        if metode_bayar in ['kartu', 'debit', 'kredit', 'ewallet', 'transfer']:
            if not no_rekening:
                return jsonify({
                    'success': False,
                    'error': 'Nomor rekening wajib diisi untuk pembayaran non-tunai'
                })

        subtotal  = sum(float(i['harga']) * int(i['qty']) for i in items)
        total     = subtotal - diskon + pajak

        if bayar < total:
            return jsonify({'success': False, 'error': 'Pembayaran kurang'})

        kembalian = bayar - total
        invoice   = Transaksi.generate_invoice()

        t = Transaksi(
            invoice=invoice,
            pelanggan_id=pelanggan_id,
            user_id=session['user_id'],
            subtotal=subtotal,
            diskon=diskon,
            pajak=pajak,
            total=total,
            bayar=bayar,
            kembalian=kembalian,
            metode_bayar=metode_bayar,
            no_rekening=no_rekening if no_rekening else None,
            status='selesai'
        )
        db.session.add(t)
        db.session.flush()

        for item in items:
            produk = Produk.query.get(item['produk_id'])
            if not produk:
                db.session.rollback()
                return jsonify({'success': False, 'error': f"Produk {item['produk_id']} tidak ditemukan"})

            if not produk.kurangi_stok(item['qty']):
                db.session.rollback()
                return jsonify({'success': False, 'error': f"Stok {produk.nama} tidak mencukupi"})

            db.session.add(ItemTransaksi(
                transaksi_id=t.id,
                produk_id=item['produk_id'],
                qty=item['qty'],
                harga_satuan=item['harga'],
                subtotal=float(item['harga']) * int(item['qty'])
            ))

        db.session.commit()
        return jsonify({
            'success':      True,
            'invoice':      invoice,
            'transaksi_id': t.id,
            'total':        total,
            'kembalian':    kembalian,
            'waktu':        datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@transaksi_bp.route('/riwayat')
@login_required
def riwayat():
    page       = request.args.get('page', 1, type=int)
    per_page   = 50
    start_date = request.args.get('start_date')
    end_date   = request.args.get('end_date')
    invoice    = request.args.get('invoice', '')

    query = Transaksi.query

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end   = datetime.strptime(end_date,   '%Y-%m-%d')
            query = query.filter(Transaksi.created_at.between(start, end))
        except ValueError:
            pass

    if invoice:
        query = query.filter(Transaksi.invoice.ilike(f'%{invoice}%'))

    query          = query.order_by(Transaksi.created_at.desc())
    transaksi_list = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('transaksi/riwayat.html',
                           transaksi=transaksi_list,
                           start_date=start_date,
                           end_date=end_date,
                           invoice=invoice)


@transaksi_bp.route('/<int:id>')
@login_required
def detail(id):
    t = Transaksi.query.get_or_404(id)

    selisih_waktu = datetime.now() - t.created_at
    bisa_batalkan = selisih_waktu < timedelta(hours=24)
    sisa_waktu    = max(timedelta(hours=24) - selisih_waktu, timedelta(0))

    if not bisa_batalkan:
        flash('Transaksi tidak bisa dibatalkan karena sudah lewat 24 jam.', 'warning')
    else:
        jam   = int(sisa_waktu.total_seconds() // 3600)
        menit = int((sisa_waktu.total_seconds() % 3600) // 60)
        flash(f'Transaksi masih bisa dibatalkan. Sisa waktu: {jam}j {menit}m.', 'success')

    return render_template('detail_transaksi.html',
                           t=t,
                           bisa_batalkan=bisa_batalkan,
                           sisa_waktu=sisa_waktu)


@transaksi_bp.route('/<int:id>/unduh_pdf')
@login_required
def unduh_pdf(id):
    t = Transaksi.query.get_or_404(id)
    try:
        pdf_bytes = generate_pdf(t)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Invoice_{t.invoice}.pdf"
        )
    except Exception as e:
        flash(f'Gagal membuat PDF: {str(e)}', 'danger')
        return redirect(url_for('transaksi.detail', id=id))


@transaksi_bp.route('/<int:id>/struk')
@login_required
def struk(id):
    t = Transaksi.query.get_or_404(id)
    return render_template('transaksi/struk.html', t=t)


@transaksi_bp.route('/<int:id>/batalkan', methods=['POST'])
@login_required
def batalkan(id):
    t = Transaksi.query.get_or_404(id)

    selisih_waktu = datetime.now() - t.created_at
    if selisih_waktu >= timedelta(hours=24):
        flash('Transaksi tidak bisa dibatalkan karena sudah lewat 24 jam.', 'warning')
        return redirect(url_for('transaksi.detail', id=id))

    if t.status == 'batal':
        flash('Transaksi sudah dibatalkan sebelumnya.', 'warning')
        return redirect(url_for('transaksi.detail', id=id))

    try:
        for item in t.items:
            produk = Produk.query.get(item.produk_id)
            if produk:
                produk.stok += item.qty

        t.status = 'batal'
        db.session.commit()
        flash(f'Transaksi {t.invoice} berhasil dibatalkan.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Gagal membatalkan transaksi: {str(e)}', 'danger')

    return redirect(url_for('transaksi.detail', id=id))


@transaksi_bp.route('/<int:id>/cetak')
@login_required
def cetak(id):
    t = Transaksi.query.get_or_404(id)
    return render_template('cetak.html', t=t)


@transaksi_bp.route('/api/harian')
@login_required
def api_harian():
    days   = int(request.args.get('days', 7))
    result = []

    for i in range(days):
        tgl      = datetime.now() - timedelta(days=i)
        date_str = tgl.strftime('%Y-%m-%d')

        total = Transaksi.query.filter(
            db.func.date(Transaksi.created_at) == tgl.date(),
            Transaksi.status == 'selesai'
        ).with_entities(db.func.sum(Transaksi.total)).scalar() or 0

        count = Transaksi.query.filter(
            db.func.date(Transaksi.created_at) == tgl.date(),
            Transaksi.status == 'selesai'
        ).count()

        result.append({'tanggal': date_str, 'total': float(total), 'jumlah': count})

    result.reverse()
    return jsonify(result)