from app import app, db, User

with app.app_context():
    user1 = User(name='Kayn')  # Remplacez par votre nom
    user2 = User(name='Nexie')  # Remplacez par le nom de l'autre personne

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    print("Les utilisateurs ont été ajoutés avec succès.")
