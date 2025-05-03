from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': 'MysqlRules1!',
    'host': 'localhost',
    'database': 'tech-store',
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
        cursor.execute("SELECT * FROM sales_by_user ORDER BY total_ventas DESC")
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
        cursor.execute("SELECT * FROM low_stock_products ORDER BY stock ASC")
        result = cursor.fetchall()
        return jsonify({'data': result, 'count': len(result)})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders ORDER BY order_date DESC")
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
        cursor.execute("""
            SELECT od.*, p.price as precio_unitario 
            FROM order_details od
            JOIN products p ON od.producto = p.name
            ORDER BY od.fecha_pedido DESC
        """)
        result = cursor.fetchall()

        # Convertimos total a float
        result = convert_to_float(result, ['total', 'precio_unitario'])

        return jsonify({'data': result, 'count': len(result)})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/order-details/<int:order_id>', methods=['GET'])
def get_order_details_by_id(order_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM order_details 
            WHERE pedido = %s
            ORDER BY producto
        """, (order_id,))
        result = cursor.fetchall()

        # Convertimos total a float
        result = convert_to_float(result, ['total'])

        if not result:
            return jsonify({'error': 'Order not found'}), 404

        # Obtener información general del pedido
        cursor.execute("""
            SELECT o.*, u.name as cliente 
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
        """, (order_id,))
        order_info = cursor.fetchone()

        return jsonify({
            'order_info': order_info,
            'order_items': result,
            'item_count': len(result)
        })
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
        
        # Obtener el pedido actualizado
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        updated_order = cursor.fetchone()
        
        return jsonify({
            'message': 'Estado actualizado correctamente',
            'order': updated_order
        })
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
        cursor.execute("SELECT * FROM products ORDER BY name")
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
        
        # Obtener los detalles actualizados del pedido
        cursor.execute("""
            SELECT op.order_id, p.name as product_name, op.quantity, 
                   p.price, (p.price * op.quantity) as subtotal
            FROM order_products op
            JOIN products p ON op.product_id = p.id
            WHERE op.order_id = %s AND op.product_id = %s
        """, (data['order_id'], data['product_id']))
        added_item = cursor.fetchone()
        
        return jsonify({
            'message': 'Producto añadido correctamente',
            'added_item': added_item
        })
    except Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users ORDER BY name")
        result = cursor.fetchall()
        return jsonify({'data': result, 'count': len(result)})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)