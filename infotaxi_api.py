from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import mysql.connector
from mysql.connector import Error
import os

# -----------------------------------------------------------
#  CONFIG BASE
# -----------------------------------------------------------

app = Flask(__name__)

# CORS global
CORS(app, resources={r"/*": {"origins": "*"}})

# Swagger configuration
app.config["SWAGGER"] = {
    "title": "Infotaxi API",
    "uiversion": 3
}
swagger = Swagger(app)

# -----------------------------------------------------------
#  BASE DE DATOS (VALORES POR DEFECTO + VARIABLES DE ENTORNO)
# -----------------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "31.97.130.20"),
    "port": int(os.getenv("DB_PORT", 4646)),
    "database": os.getenv("DB_NAME", "electo"),
    "user": os.getenv("DB_USER", "mariadb"),
    "password": os.getenv("DB_PASSWORD", "9204a8246f7ed4fe49e6"),
}

# -----------------------------------------------------------
#  FUNCIÓN DE CONEXIÓN
# -----------------------------------------------------------

def get_db():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        return conn
    except Error as e:
        print("❌ Error conectando a MySQL:", str(e))
        return None

# -----------------------------------------------------------
#  HEALTH CHECK
# -----------------------------------------------------------

@app.get("/api/health")
def health():
    """API health check
    ---
    responses:
      200:
        description: API funcionando correctamente
    """
    return jsonify({"status": "ok"}), 200

# -----------------------------------------------------------
#  LOGIN
# -----------------------------------------------------------

@app.post("/api/login")
def login():
    """Login de usuario
    ---
    parameters:
      - name: body
        in: body
        schema:
          properties:
            Usuario:
              type: string
            Contrasena:
              type: string
    responses:
      200:
        description: Login correcto
    """
    data = request.json
    usuario = data.get("Usuario")
    contrasena = data.get("Contrasena")

    if not usuario or not contrasena:
        return jsonify({"error": "Usuario y Contrasena son obligatorios"}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"error": "No se puede conectar a la base de datos"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM usuarios
            WHERE Usuario = %s AND Contrasena = %s
        """, (usuario, contrasena))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return jsonify(result), 200
        return jsonify({"error": "Credenciales incorrectas"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------
#  GUARDAR POSICIÓN
# -----------------------------------------------------------

@app.post("/api/guardar_posicion")
def guardar_posicion():
    """Guardar posición GPS
    ---
    parameters:
      - name: body
        in: body
        schema:
          properties:
            usuario:
              type: string
            lat:
              type: number
            lon:
              type: number
            velocidad:
              type: number
            rumbo:
              type: number
    """
    data = request.json
    usuario = data.get("usuario")
    lat = data.get("lat")
    lon = data.get("lon")
    velocidad = data.get("velocidad")
    rumbo = data.get("rumbo")

    if not usuario or lat is None or lon is None:
        return jsonify({"error": "usuario, lat y lon son obligatorios"}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"error": "No se puede conectar a la base de datos"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO posiciones (usuario, lat, lon, velocidad, rumbo)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario, lat, lon, velocidad, rumbo))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "posicion_guardada"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------
#  MANEJO GLOBAL DE ERRORES
# -----------------------------------------------------------

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Ruta no encontrada"}), 404

@app.errorhandler(500)
def server_error(_):
    return jsonify({"error": "Error interno del servidor"}), 500

# -----------------------------------------------------------
#  MAIN
# -----------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
