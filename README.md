# Tech Store - Panel Administrativo

Este proyecto es un panel administrativo simple para una tienda de tecnología ficticia. Permite visualizar información clave como ventas por usuario, productos con bajo stock, detalles de pedidos y la lista completa de productos. También ofrece funcionalidades para actualizar el estado de los pedidos y añadir productos a pedidos existentes.

## Tecnologías Utilizadas

- **Backend:** Python (Flask), MySQL Connector
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Base de Datos:** MySQL
- **Otros:** CORS

## Configuración

### Prerrequisitos

- Python 3.x
- MySQL Server
- Node.js (opcional, si se planea usar herramientas de frontend)

### Base de Datos

1.  Asegúrate de que tu servidor MySQL esté en funcionamiento.
2.  Crea una base de datos llamada `tech-store`.
3.  Importa el esquema de la base de datos (necesitarás crear las tablas `users`, `products`, `orders`, `order_products` y las vistas `sales_by_user`, `low_stock_products`, `order_details`, así como los procedimientos almacenados `UpdateOrderStatus` y `AddProductToOrder`).
4.  Actualiza las credenciales de la base de datos en `db_config` dentro de [`app.py`](app.py).

### Backend

1.  Navega al directorio del proyecto en tu terminal.
2.  Crea un entorno virtual (recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecuta la aplicación Flask:
    ```bash
    python app.py
    ```
    El backend estará disponible en `http://localhost:5000`.

### Frontend

1.  Abre el archivo [`index.html`](index.html) en tu navegador web.
2.  Asegúrate de que la constante `API_BASE_URL` en [`main.js`](main.js) apunte a la URL correcta de tu backend (por defecto debería funcionar si el backend corre en `http://localhost:5000`, pero está configurado para `https://tech-store-api.hectorgv00.online/api`).

## Funcionalidades

- **Dashboard:** Muestra tarjetas con resúmenes de:
  - Ventas totales por usuario.
  - Productos con bajo nivel de stock.
  - Lista completa de productos con precio y stock.
- **Detalles de Pedidos:** Muestra una tabla con información detallada de cada ítem de pedido, incluyendo cliente, fecha, estado, producto, cantidad y total.
- **Actualizar Estado de Pedido:** Permite cambiar el estado de un pedido específico (Pendiente, Procesando, Enviado, Entregado, Cancelado) usando su ID.
- **Añadir Producto a Pedido:** Permite añadir un producto específico (por ID) a un pedido existente (por ID) con una cantidad determinada.

## API Endpoints (definidos en [`app.py`](app.py))

- `GET /api/sales`: Obtiene las ventas agregadas por usuario.
- `GET /api/low-stock`: Obtiene los productos con bajo stock.
- `GET /api/orders`: Obtiene todos los pedidos.
- `GET /api/order-details`: Obtiene los detalles de todos los ítems de pedidos.
- `GET /api/order-details/<int:order_id>`: Obtiene los detalles de un pedido específico.
- `PUT /api/orders/<int:order_id>/status`: Actualiza el estado de un pedido.
- `GET /api/products`: Obtiene la lista de todos los productos.
- `POST /api/orders/add-product`: Añade un producto a un pedido existente.
- `GET /api/users`: Obtiene la lista de todos los usuarios.
