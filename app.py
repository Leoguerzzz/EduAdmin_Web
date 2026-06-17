from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
import psycopg2

app = Flask(__name__)
CORS(app)

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de BD
#DB_CONFIG = {
    #"host": os.environ.get("DB_HOST", "localhost"),
    #"database": os.environ.get("DB_NAME", "SISTEMA_ARCADENOE"),
    #"user": os.environ.get("DB_USER", "postgres"),
    #"password": os.environ.get("DB_PASSWORD", "1234"), 
    #"port": os.environ.get("DB_PORT", "5432")
#}

# Render nos dará la variable DATABASE_URL, si no está, usa una por defecto (opcional)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_TSXaq9NkbKB5@ep-green-king-adst3yeh.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")

def get_db_connection():
    try:
        # psycogp2 puede conectarse directamente usando solo el enlace
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.error(f"Error de conexión a PostgreSQL: {e}")
        return None

# ==============================================================================
# RUTAS FRONTEND
# ==============================================================================
# 1. Ahora la raíz del servidor cargará el LOGIN obligatoriamente
@app.route('/')
def index():
    return send_from_directory('.', 'Login.html')

# 2. Creamos una nueva ruta exclusiva para el PANEL DE CONTROL
@app.route('/dashboard')
def dashboard():
    return send_from_directory('.', 'index.html')

# ==============================================================================
# ENDPOINTS API (BACKEND)
# ==============================================================================

@app.route('/api/cuentas_por_cobrar', methods=['GET'])
def get_cuentas():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD Offline"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM v_cuentas_por_cobrar;")
            return jsonify(cur.fetchall()), 200
    finally:
        conn.close()

@app.route('/api/ingresos', methods=['GET', 'POST'])
def handle_ingresos():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD Offline"}), 500
    try:
        if request.method == 'GET':
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM ingresos ORDER BY fecha_pago DESC;")
                return jsonify(cur.fetchall()), 200
        else:
            data = request.json
            with conn.cursor() as cur:
                query = "INSERT INTO ingresos (numero_recibo, concepto, metodo_pago, monto_pagado) VALUES (%s, %s, %s, %s);"
                cur.execute(query, (data.get('recibo_id'), data.get('concepto'), data.get('metodo'), data.get('monto')))
                conn.commit()
            return jsonify({"status": "success"}), 201
    finally:
        conn.close()

@app.route('/api/egresos', methods=['GET', 'POST'])
def handle_egresos():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD Offline"}), 500
    try:
        if request.method == 'GET':
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM egresos ORDER BY fecha DESC;")
                return jsonify(cur.fetchall()), 200
        else:
            data = request.json
            with conn.cursor() as cur:
                query = "INSERT INTO egresos (numero_comprobante, categoria, descripcion, monto, metodo_pago) VALUES (%s, %s, %s, %s, %s);"
                cur.execute(query, (data.get('comprobante_id'), data.get('categoria'), data.get('descripcion'), data.get('monto'), data.get('metodo')))
                conn.commit()
            return jsonify({"status": "success"}), 201
    finally:
        conn.close()

@app.route('/api/inventario', methods=['GET'])
def get_inventario():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD Offline"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM inventario ORDER BY nombre ASC;")
            return jsonify(cur.fetchall()), 200
    finally:
        conn.close()

@app.route('/api/reportes/resultados', methods=['GET'])
def get_estado_resultados():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "BD Offline"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM v_estado_resultados;")
            return jsonify(cur.fetchall()), 200
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)