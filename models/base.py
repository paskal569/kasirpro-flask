from datetime import datetime
from models.db import db
from datetime import datetime, timezone

class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def save(self):
        db.session.add(self)
        db.session.commit()