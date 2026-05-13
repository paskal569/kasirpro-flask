from flask import Blueprint, app, redirect, render_template, request, jsonify, session, url_for
from routes.auth import login_required
kembalian_bp = Blueprint('kembalian', __name__, url_prefix='/kembalian')
from routes.pembayaran import pembayaran_bp
from routes.barcode import barcode_bp
@kembalian_bp.before_request
def before_request():
    """Pastikan user sudah login sebelum mengakses halaman kembalian"""
    if 'user_id' not in session:
        return  redirect(url_for('auth.login'))

    

@app.route("/kembalian", methods=["POST","GET"])
def get_kembalian():
    return {"message": "Selamat datang di halaman kemablian"}
