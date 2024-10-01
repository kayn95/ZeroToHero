from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import os

app = Flask(__name__)

# Configuration de la base de données
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'performances.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Données fictives pour les exercices avec descriptions
sessions = {
    1: [
        {'name': 'Développé incliné', 'description': 'S1 : 4-6 rép | S2 : 6-8 rép | S3 : 8-10 rép | Repos 2min30 | Commentaire : Top set puis -10% à chaque série '},
        {'name': 'Tractions lestées', 'description': 'S1 : 4-6 rép | S2 : 6-8 rép | S3 : 8-10 rép | Repos 2min | Commentaire : Top set puis -10% à chaque série '},
        {'name': 'Elévation frontales', 'description': 'S1 : 10-15 rép | S2 : 10-15 rép | S3 : 10-15 rép | Repos 1min30 | Commentaire : Pic de contraction 2 secondes en haut '},
        {'name': 'Curl incliné haltères', 'description': 'S1 : 8-12 rép | S2 : 8-12 rép | S3 : 8-12 rép | Repos 1min30 | Commentaire : /'},
        {'name': 'Elévations latérales', 'description': 'S1 : 15-20 rép | S2 : 10-15 rép | S3 : 8-10 triche into upright row | Repos 1min | Commentaire : Raptor Set : Dernière série en dégressive mécanique '}
    ],
    2: [
        {'name': 'High bar squat ou deadlift', 'description': 'S1 : 6-10 rép | S2 : 6-10 rép | S3 : 6-10 rép | Repos 2min | Commentaire : /'},
        {'name': 'Romanian deadlift ou Fentes', 'description': 'S1 : 10-15 rép | S2 : 10-15 rép | S3 : 10-15 rép | Repos 1min30 | Commentaire : /'},
        {'name': 'Leg Curl superset + Leg extension', 'description': 'S1 : 8-12 rép | S2 : 8-12 rép | S3 : 8-12 rép | Repos 0min30 | Commentaire : Se reposer 30 secondes entre chaque exercice'},
        {'name': 'Extension mollets', 'description': 'S1 : 12-15 rép | S2 : 8-12 rép | S3 : 6-10 rép puis dégressive amrap | Repos 1min | Commentaire : Tempo 1-2-2-1'},
        {'name': 'Upright row penché', 'description': 'S1 : 15-20 rép | S2 : 10-15 rép | S3 : 6-10 rép puis dégressive amrap | Repos 1min | Commentaire : Augmenter le poids à chaque série'}
    ],
    3: [
        {'name': 'Overhead press', 'description': 'S1 : 4-6 rép | S2 : 6-8 rép | S3 : 8-10 rép | Repos 2min30 | Commentaire : Top set puis -10% à chaque série'},
        {'name': 'Développé couché', 'description': 'S1 : 4-6 rép | S2 : 6-8 rép | S3 : 8-10 rép | Repos 2min | Commentaire : Top set puis -10% à chaque série'},
        {'name': 'Tractions neutres focus bras', 'description': 'S1 : 8-12 rép | S2 : 8-12 rép | S3 : 8-12 rép | Repos 1min30 | Commentaire : Tirer avec les bras, pas le dos'},
        {'name': 'Oiseau assis prise neutre', 'description': 'S1 : 10-15 rép | S2 : 10-15 rép | S3 : 10-15 rép | Repos 1min | Commentaire : Coudes perpendiculaires au corps'},
        {'name': 'Upright row', 'description': 'S1 : 12-15 rép | S2 : 8-12 rép | S3 : 6-10 rép puis dégressive amrap | Repos 1min | Commentaire : Augmenter le poids à chaque série'}
    ]
}

# Modèle pour les performances
class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, nullable=False)
    exercise = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Performance {self.exercise} - {self.value}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    performances = db.relationship('Performance', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'


@app.route('/')
def home():
    users = User.query.all()
    return render_template('sessions.html', sessions=sessions, users=users)


@app.route('/user/<int:user_id>/session/<int:session_id>')
def session(user_id, session_id):
    user = User.query.get_or_404(user_id)
    exercises = sessions.get(session_id)
    if exercises:
        return render_template('session.html', session_id=session_id, exercises=exercises, user=user)
    else:
        return "Séance non trouvée", 404


@app.route('/user/<int:user_id>/track/<int:session_id>', methods=['GET', 'POST'])
def track_performance(user_id, session_id):
    user = User.query.get_or_404(user_id)
    exercises = sessions.get(session_id)
    if not exercises:
        return "Séance non trouvée", 404

    if request.method == 'POST':
        for exercise in exercises:
            exercise_name = exercise['name']
            value = request.form.get(exercise_name)
            if value:
                try:
                    value = float(value)
                except ValueError:
                    return f"Valeur invalide pour {exercise_name}", 400
                performance = Performance(session_id=session_id, exercise=exercise_name, value=value, user_id=user.id)
                db.session.add(performance)
        db.session.commit()
        return redirect(url_for('user_sessions', user_id=user.id))
    return render_template('track.html', session_id=session_id, exercises=exercises, user=user)

@app.route('/user/<int:user_id>/performances')
def user_performances(user_id):
    user = User.query.get_or_404(user_id)
    all_performances = Performance.query.filter_by(user_id=user.id).order_by(Performance.timestamp).all()

    # Préparer les données pour le graphique
    exercises = list(set([perf.exercise for perf in all_performances]))
    data = {}
    for exercise in exercises:
        data[exercise] = {
            'dates': [],
            'values': []
        }
        perfs = Performance.query.filter_by(exercise=exercise, user_id=user.id).order_by(Performance.timestamp).all()
        for perf in perfs:
            if perf.timestamp:
                date_str = perf.timestamp.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = 'Date inconnue'
            data[exercise]['dates'].append(date_str)
            data[exercise]['values'].append(perf.value)

    return render_template('performances.html', performances=all_performances, data=data, user=user)

@app.route('/user/<int:user_id>/sessions')
def user_sessions(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_sessions.html', sessions=sessions, user=user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
