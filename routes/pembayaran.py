from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from datetime import datetime
from models import db, transaksi as Transaksi  # alias agar tidak bentrok dengan variabel
import uuid

pembayaran_bp = Blueprint('pembayaran', __name__, url_prefix='/pembayaran')


# ── HELPER ─────────────────────────────────────────────────
def generate_invoice():
    return f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}"


# ── ROUTE 1: Halaman pembayaran ─────────────────────────────
@pembayaran_bp.route('/', methods=['GET', 'POST'])
def pembayaran():
    total_harga = request.args.get('total_harga') or request.form.get('total_harga')
    invoice     = request.args.get('invoice', '')  # TAMBAH INI

    try:
        total_harga = int(str(total_harga).replace('.', '').replace(',', ''))
    except (ValueError, TypeError):
        total_harga = 0

    #if total_harga == 0:
        #flash('Total harga tidak valid', 'danger')
        #return render_template('pembayaran.html', total_harga=0)

    session['total_pembayaran'] = total_harga
    session['pending_invoice']   = invoice 
    return render_template('pembayaran.html', total_harga=total_harga, invoice=invoice)


# ── ROUTE 2: Proses pembayaran ──────────────────────────────
@pembayaran_bp.route('/proses', methods=['POST'])
def proses_pembayaran():

    user_id = current_user.id if current_user.is_authenticated else None

    payment_method  = request.form.get('payment_method', '')
    pelanggan_id    = request.form.get('pelanggan_id')
    subtotal_raw    = request.form.get('subtotal',    '0').replace('.', '').replace(',', '')
    diskon_raw      = request.form.get('diskon',      '0').replace('.', '').replace(',', '')
    pajak_raw       = request.form.get('pajak',       '0').replace('.', '').replace(',', '')
    cash_amount_raw = request.form.get('cash_amount', '0').replace('.', '').replace(',', '')

    total_pembayaran = session.get('total_pembayaran')

    if total_pembayaran is None:
        flash('Sesi pembayaran tidak valid, silakan ulangi', 'danger')
        return redirect(url_for('pembayaran.pembayaran'))

    if not payment_method:
        flash('Metode pembayaran harus dipilih', 'danger')
        return redirect(url_for('pembayaran.pembayaran'))

    try:
        subtotal = int(subtotal_raw)
        diskon   = int(diskon_raw)
        pajak    = int(pajak_raw)
    except ValueError:
        flash('Data subtotal/diskon/pajak tidak valid', 'danger')
        return redirect(url_for('pembayaran.pembayaran'))

    if payment_method == 'tunai':
        try:
            cash_amount = int(cash_amount_raw)
        except ValueError:
            flash('Jumlah uang tunai harus berupa angka', 'danger')
            return redirect(url_for('pembayaran.pembayaran'))

        if cash_amount < total_pembayaran:
            flash('Jumlah uang tunai tidak mencukupi', 'danger')
            return redirect(url_for('pembayaran.pembayaran'))

        kembalian = cash_amount - total_pembayaran

    elif payment_method.startswith('kartu_') or payment_method.startswith('ewallet_'):
        cash_amount = total_pembayaran
        kembalian   = 0

    else:
        flash('Metode pembayaran tidak dikenali', 'danger')
        return redirect(url_for('pembayaran.pembayaran'))

    # Simpan ke database
    try:
        invoice_pending = session.get('pending_invoice', '')
        transaksi_baru  = None

        if invoice_pending:
            transaksi_baru = Transaksi.query.filter_by(invoice=invoice_pending).first()

        if transaksi_baru:
            # Update transaksi pending
            transaksi_baru.status       = 'selesai'
            transaksi_baru.metode_bayar = payment_method
            transaksi_baru.bayar        = cash_amount
            transaksi_baru.kembalian    = kembalian
            transaksi_baru.pelanggan_id = pelanggan_id
        else:
            # Buat transaksi baru
            transaksi_baru = Transaksi(
                invoice      = generate_invoice(),
                pelanggan_id = pelanggan_id,
                user_id      = user_id,
                subtotal     = subtotal,
                diskon       = diskon,
                pajak        = pajak,
                total        = total_pembayaran,
                bayar        = cash_amount,
                kembalian    = kembalian,
                metode_bayar = payment_method,
                status       = 'selesai'
            )
            db.session.add(transaksi_baru)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menyimpan transaksi: {str(e)}', 'danger')
        return redirect(url_for('pembayaran.pembayaran'))

    session.pop('total_pembayaran', None)
    session.pop('pending_invoice',  None)
    flash('Pembayaran berhasil!', 'success')
    return redirect(url_for('transaksi.detail', id=transaksi_baru.id))


# ── ROUTE 3: Halaman sukses ─────────────────────────────────
@pembayaran_bp.route('/sukses')
def sukses():
    transaksi_data = session.get('transaksi_terakhir')
    if not transaksi_data:
        return redirect(url_for('pembayaran.pembayaran'))
    return render_template('pembayaran_sukses.html', transaksi=transaksi_data)

@pembayaran_bp.route('/loading', methods=['GET'])
#@login_required
def loading():
    return render_template('proses_pembayaran.html')