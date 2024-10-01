from app import app, db, Performance

with app.app_context():
    performances_with_null_timestamp = Performance.query.filter_by(timestamp=None).all()
    print(f"Nombre d'enregistrements avec timestamp=None : {len(performances_with_null_timestamp)}")
    for perf in performances_with_null_timestamp:
        print(f"ID: {perf.id}, Exercice: {perf.exercise}, Valeur: {perf.value}, Timestamp: {perf.timestamp}")
