from .base import db, BaseModel
from models.base import db

class DataPerusahaan(BaseModel):
    __tablename__ = 'data_perusahaan'
    
    nama = db.Column(db.String(255), nullable=False)
    alamat = db.Column(db.String(255), nullable=False)
    telepon = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<DataPerusahaan {self.nama}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'alamat': self.alamat,
            'telepon': self.telepon,
            'email': self.email
        }
    
    def update(self, data):
        self.nama = data.get('nama', self.nama)
        self.alamat = data.get('alamat', self.alamat)
        self.telepon = data.get('telepon', self.telepon)
        self.email = data.get('email', self.email)
        db.session.commit()
        return self
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    