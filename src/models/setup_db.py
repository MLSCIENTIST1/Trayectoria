from src.app import create_app
from src.models.database import db

app = create_app()
with app.app_context():
    print("⏳ Creando tablas en Neon Cloud...")
    db.create_all()
    print("✅ ¡Tablas creadas exitosamente!")