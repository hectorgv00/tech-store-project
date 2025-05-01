# app.py
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
db_config = {
    'user': '',
    'password': '',
    'host': '',
    'database': '',
    'raise_on_warnings': True
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def convert_to_float(data_list, fields):
    """
    Convierte campos específicos a float si existen y no son None
    """
    for row in data_list:
        for field in fields:
            if field in row and row[field] is not None:
                row[field] = float(row[field])
    return data_list

# Endpoints para las vistas
@app.route('/api/sales', methods=['GET'])
def get_sales_by_user():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sales_by_user")
        result = cursor.fetchall()
        
        # Convertimos total_ventas a float
        result = convert_to_float(result, ['total_ventas'])

        return jsonify({'data': result, 'count': len(result)})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/low-stock', methods=['GET'])
def get_low_stock():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM low_stock_products")
        result = cursor.fetchall()
        return jsonify({'data': result, 'count': len(result)})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/order-details', methods=['GET'])
def get_order_details():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM order_details")
        result = cursor.fetchall()

        # Convertimos total a float
        result = convert_to_float(result, ['total'])

        return jsonify({'data': result, 'count': len(result)})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Endpoints para procedimientos almacenados
@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    new_status = request.json.get('new_status')
    if not new_status:
        return jsonify({'error': 'Missing new_status parameter'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.callproc('UpdateOrderStatus', [order_id, new_status])
        conn.commit()
        return jsonify({'message': 'Estado actualizado correctamente'})
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        result = cursor.fetchall()
        return jsonify({'data': result, 'count': len(result)})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/api/orders/add-product', methods=['POST'])
def add_product_to_order():
    data = request.json
    required_fields = ['order_id', 'product_id', 'quantity']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.callproc('AddProductToOrder', [
            data['order_id'],
            data['product_id'],
            data['quantity']
        ])
        conn.commit()
        return jsonify({'message': 'Producto añadido correctamente'})
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
