import sys
sys.path.insert(0, '.')

from app import app, db
from models.item_transaksi import ItemTransaksi
from models.transaksi import transaksi
from sqlalchemy import func
from datetime import date

with app.app_context():
    today = date.today()
    print('Hari ini:', today)
    
    semua = transaksi.query.all()
    for t in semua:
        print(f'  ID={t.id}, status={t.status}, created_at={t.created_at}, total={t.total}')
    
    items = ItemTransaksi.query.all()
    for i in items:
        print(f'  item: transaksi_id={i.transaksi_id}, subtotal={i.subtotal}')