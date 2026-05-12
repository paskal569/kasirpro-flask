from import_export import resources
from .models import Item
from models.base import db
from models.kategori import Kategori

app = Flask(__name__)

with app.app_context():
    icon_mapping = {
        'Makanan'        : ('fas fa-utensils',      '#F97316'),
        'Minuman'        : ('fas fa-glass-water',   '#3B82F6'),
        'Snack & Cemilan': ('fas fa-cookie-bite',   '#EAB308'),
        'Sembako'        : ('fas fa-basket-shopping','#10B981'),
        'Rokok'          : ('fas fa-smoking',        '#6B7280'),
        'Lainnya'        : ('fas fa-box',            '#8B5CF6'),
    }
    
    for kat in Kategori.query.all():
        if kat.nama in icon_mapping:
            kat.icon, kat.warna = icon_mapping[kat.nama]
        else:
            kat.icon  = 'fas fa-tag'
            kat.warna = '#6B7280'

    db.session.commit()
    print("Icon berhasil diupdate!")