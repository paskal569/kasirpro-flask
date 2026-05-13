from flask import Blueprint, render_template, request, session, redirect, url_for
from .barcode import generateBarcode

loading_konfirmasi_bp = Blueprint('loading_konfirmasi', __name__, url_prefix='/loading-konfirmasi')

@loading_konfirmasi_bp.route('/', methods=['GET', 'POST'])
def loading_konfirmasi():
    
    if request.method == 'POST':
        # Simpan data ke session
        session['barang_draft'] = request.form.to_dict(flat=False)
        
        # Generate barcode
        generateBarcode()
        
        # Redirect (sesuaikan nama route!)
        return redirect(url_for('input_barang'))

    return render_template('loading_konfirmasi.html')