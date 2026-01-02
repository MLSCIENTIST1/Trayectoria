import os
import sys
import configparser
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pathlib import Path

# Instancias globales
db = SQLAlchemy()
migrate = Migrate()

def read_config():
    """Lee la configuración buscando el archivo de forma dinámica."""
    # Obtiene la carpeta donde está este archivo database.py
    base_path = Path(__file__).resolve().parent
    config_file = base_path / 'database.conf'
    
    print(f"🔍 [LOG]: Buscando configuración en: {config_file}")
    
    if not config_file.exists():
        print(f"❌ [ERROR]: No se encontró database.conf en {base_path}")
        return None
        
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    return config

# --- PROCESO DE CARGA Y CONEXIÓN ---
config_data = read_config()

if config_data:
    host = config_data['database']['host']
    user = config_data['database']['user']
    password = config_data['database']['password']
    database = config_data['database']['database']
    
    # IMPORTANTE: Añadimos sslmode=require para NEON Cloud
    DATABASE_URL = f"postgresql://{user}:{password}@{host}/{database}?sslmode=require"
    print(f"📡 [LOG]: Intentando conectar a Host: {host} | DB: {database}")
else:
    # Opción de emergencia por si usas variables de entorno en el futuro
    DATABASE_URL = os.getenv('DATABASE_URL')
    print("⚠️ [LOG]: Usando DATABASE_URL de variable de entorno.")

# Probar la conexión inmediata con psycopg2
try:
    # Verificamos conexión física
    conn_test = psycopg2.connect(DATABASE_URL)
    conn_test.close()
    print("✅ [EXITO]: Conexión establecida con NEON Cloud (PostgreSQL).")
except Exception as e:
    print(f"💥 [ERROR CRÍTICO]: Falló la conexión a la base de datos: {e}")

def create_database():
    """
    Nota: En servicios Cloud como Neon, la base de datos se crea 
    desde el panel web, no por código. Este método se mantiene por compatibilidad local.
    """
    print("🛠️ [LOG]: Verificando existencia de base de datos (Modo compatible)...")
    try:
        # Intentar conexión a la base default para verificar
        tmp_conn = psycopg2.connect(DATABASE_URL.replace(database, 'postgres'))
        tmp_conn.autocommit = True
        cur = tmp_conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", [database])
        if not cur.fetchone():
            print(f"🚀 [LOG]: La base de datos {database} no existe. Créala en el panel de Neon.")
        else:
            print(f"✨ [LOG]: Confirmado: La base de datos '{database}' está lista.")
        cur.close()
        tmp_conn.close()
    except Exception as e:
        print(f"ℹ️ [INFO]: Omitiendo validación manual de creación: {e}")

def init_app(app):
    """Inicializa Flask con SQLAlchemy y Migrate."""
    if not DATABASE_URL:
        print("🛑 [ERROR]: No hay DATABASE_URL configurada. Revisa database.conf")
        return

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    print("🚀 [LOG]: Flask-SQLAlchemy inicializado correctamente.")