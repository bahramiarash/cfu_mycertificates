import os
from flask import Flask, request, send_file, jsonify
import MySQLdb
import io

app = Flask(__name__)

# Get database credentials from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '12#qwEasDzxC')
DB_NAME = os.getenv('DB_NAME', 'cert_db')

# Database connection
db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME)
cursor = db.cursor()

@app.route('/certificates/<national_id>', methods=['GET'])
def list_certificates(national_id):
    cursor.execute("""
        SELECT c.id, c.cert_name FROM certificates c
        JOIN users u ON c.user_id = u.id
        WHERE u.national_id = %s
    """, (national_id,))
    certs = cursor.fetchall()
    return jsonify([{"cert_id": c[0], "cert_name": c[1]} for c in certs])

@app.route('/certificate/<cert_id>', methods=['GET'])
def get_certificate(cert_id):
    cursor.execute("SELECT cert_file, cert_name FROM certificates WHERE id = %s", (cert_id,))
    cert = cursor.fetchone()
    if cert:
        return send_file(io.BytesIO(cert[0]), mimetype="image/svg+xml", as_attachment=True, download_name=f"{cert[1]}.svg")
    return jsonify({"error": "Certificate not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
