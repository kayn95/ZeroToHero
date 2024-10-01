from app import app, db, Performance
from datetime import datetime

with app.app_context():
    performances_with_null_timestamp = Performance.query.filter_by(timestamp=None).all()
    for perf in performances_with_null_timestamp:
        perf.timestamp = datetime.utcnow()  # Ou une autre date par défaut
        db.session.add(perf)
    db.session.commit()
    print(f"Mis à jour {len(performances_with_null_timestamp)} enregistrements avec timestamp=None")
