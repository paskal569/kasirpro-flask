from flask import render_template, session, redirect, url_for, Blueprint
from flask_login import login_required

loading_bp = Blueprint('loading', __name__)

@loading_bp.route("/loading", methods=["GET"], endpoint="loading")
@login_required
def loading():
    if "loading" not in session:
        return redirect(url_for("pembayaran.pembayaran"))
    
    # Jangan pop di sini, biarkan JS redirect ke endpoint lain
    return render_template("loading_konfirmasi.html")


# Endpoint yang dipanggil setelah loading selesai
@loading_bp.route("/loading/done", methods=["POST"], endpoint="loading_done")
@login_required
def loading_done():
    session.pop("pembayaran", None)
    session.pop("detail_transaksi", None)
    session.modified = True
    return redirect(url_for("detail_transaksi.detail_transaksi"))