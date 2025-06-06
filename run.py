from app import create_app
from app.models import db  # importa la instancia de db para crear las tablas
import os

app = create_app()

# Crea las tablas automáticamente al levantar la app (si no existen)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
