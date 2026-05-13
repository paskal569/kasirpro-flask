from flask import Blueprint, render_template, request
from flask import request, session, flash
from flask import Blueprint, render_template, redirect, url_for
barcode_bp = Blueprint('barcode', __name__, url_prefix='/barcode')

@barcode_bp.route('', methods=['GET', 'POST'])
def barcode_route():
    if request.method == 'POST':
        immage = request.files.get('image')
        if immage:immage.save('static/barcode_image.jpg')
        kode = request.form.get('kode')
        return redirect(url_for('barcode_route'))
    return render_template('barcode.html')

def generateBarcode():
    # Ambil data dari session
    barang_draft = session.get('barang_draft')
    
    if barang_draft:
        # Ambil kode dari data draft
        kode = barang_draft.get('kode', [''])[0]
        if not kode:
            flash('Kode harus diisi!', 'danger')
            return redirect(url_for('input_barang'))
        # Generate barcode image
      
        # Hapus data dari session setelah digunakan
        session.pop('barang_draft', None)
        
    # Redirect ke halaman input barang

    return redirect(url_for('input_barang'))
