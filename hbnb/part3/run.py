from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
with app.app_context():
    # ✅ Afficher la configuration de la base de données
    print(f"=== DEBUG BASE DE DONNÉES ===")
    print(f"📊 SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"📂 Répertoire de l'app: {app.instance_path}")
    
    # ✅ Afficher le chemin absolu de la base
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'sqlite:///' in db_uri:
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.instance_path, db_path)
        print(f"📍 Chemin absolu de la base: {db_path}")
        print(f"💾 Fichier existe: {os.path.exists(db_path)}")
        if os.path.exists(db_path):
            print(f"📏 Taille du fichier: {os.path.getsize(db_path)} bytes")
    
    # ✅ Lister les tables disponibles
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📋 Tables disponibles: {tables}")
    except Exception as e:
        print(f"❌ Erreur récupération tables: {e}")
    
    print("============================")