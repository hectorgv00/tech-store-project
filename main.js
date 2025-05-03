// URL base de tu API Flask
const API_BASE_URL = "https://tech-store-api.hectorgv00.online/api";

// Utility class for common functions
class Utils {
  // Show a message to the user
  static showMessage(message, type = "success") {
    const messageContainer = document.getElementById("message-container");
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    messageContainer.appendChild(alertDiv);

    setTimeout(() => {
      alertDiv.remove();
    }, 5000);
  }

  // Format a date string
  static formatDate(dateString) {
    const options = { year: "numeric", month: "short", day: "numeric" };
    return new Date(dateString).toLocaleDateString("es-ES", options);
  }

  // Format a currency value
  static formatCurrency(amount) {
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "EUR",
    }).format(amount);
  }

  // Get CSS class for a status
  static getStatusClass(status) {
    return `status-${status.toLowerCase()}`;
  }
}

// Class to handle sales data
class Sales {
  static async loadSalesData() {
    const loading = document.getElementById("loading-sales");
    const tableBody = document.querySelector("#sales-table tbody");

    loading.style.display = "block";
    tableBody.innerHTML = "";

    try {
      const response = await fetch(`${API_BASE_URL}/sales`);
      const data = await response.json();

      if (data.data && data.data.length > 0) {
        data.data.forEach((sale) => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${sale.usuario}</td>
            <td>${Utils.formatCurrency(sale.total_ventas)}</td>
          `;
          tableBody.appendChild(row);
        });
      } else {
        const row = document.createElement("tr");
        row.innerHTML = '<td colspan="2">No hay datos disponibles</td>';
        tableBody.appendChild(row);
      }
    } catch (error) {
      Utils.showMessage(`Error al cargar ventas: ${error.message}`, "error");
    } finally {
      loading.style.display = "none";
    }
  }
}

// Class to handle stock data
class Stock {
  static async loadLowStockProducts() {
    const loading = document.getElementById("loading-stock");
    const stockList = document.getElementById("stock-list");

    loading.style.display = "block";
    stockList.innerHTML = "";

    try {
      const response = await fetch(`${API_BASE_URL}/low-stock`);
      const data = await response.json();

      if (data.data && data.data.length > 0) {
        data.data.forEach((product) => {
          const productItem = document.createElement("div");
          productItem.className = "product-item";
          productItem.innerHTML = `
            <span>${product.producto}</span>
            <span class="low-stock">${product.stock} unidades</span>
          `;
          stockList.appendChild(productItem);
        });
      } else {
        stockList.innerHTML = "<p>No hay productos con bajo stock</p>";
      }
    } catch (error) {
      Utils.showMessage(`Error al cargar productos: ${error.message}`, "error");
    } finally {
      loading.style.display = "none";
    }
  }
}

// Class to handle product data
class Products {
  static async loadAllProducts() {
    const loading = document.getElementById("loading-products");
    const productsList = document.getElementById("products-list");

    loading.style.display = "block";
    productsList.innerHTML = "";

    try {
      const response = await fetch(`${API_BASE_URL}/products`);
      const data = await response.json();

      if (data.data && data.data.length > 0) {
        data.data.forEach((product) => {
          const productItem = document.createElement("div");
          productItem.className = "product-item";
          productItem.innerHTML = `
            <span>${product.name}</span>
            <span>${Utils.formatCurrency(product.price)} (${
            product.stock
          } unidades)</span>
          `;
          productsList.appendChild(productItem);
        });
      } else {
        productsList.innerHTML = "<p>No hay productos disponibles</p>";
      }
    } catch (error) {
      Utils.showMessage(`Error al cargar productos: ${error.message}`, "error");
    } finally {
      loading.style.display = "none";
    }
  }
}

// Class to handle order details
class Orders {
  static async loadOrderDetails() {
    const loading = document.getElementById("loading-orders");
    const tableBody = document.querySelector("#orders-table tbody");

    loading.style.display = "block";
    tableBody.innerHTML = "";

    try {
      const response = await fetch(`${API_BASE_URL}/order-details`);
      const data = await response.json();

      if (data.data && data.data.length > 0) {
        data.data.forEach((order) => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${order.pedido}</td>
            <td>${order.cliente}</td>
            <td>${Utils.formatDate(order.fecha_pedido)}</td>
            <td class="${Utils.getStatusClass(order.estado)}">${
            order.estado.charAt(0).toUpperCase() + order.estado.slice(1)
          }</td>
            <td>${order.producto}</td>
            <td>${order.cantidad}</td>
            <td>${Utils.formatCurrency(order.total)}</td>
          `;
          tableBody.appendChild(row);
        });
      } else {
        const row = document.createElement("tr");
        row.innerHTML = '<td colspan="7">No hay pedidos registrados</td>';
        tableBody.appendChild(row);
      }
    } catch (error) {
      Utils.showMessage(`Error al cargar pedidos: ${error.message}`, "error");
    } finally {
      loading.style.display = "none";
    }
  }

  static async updateOrderStatus(orderId, newStatus) {
    try {
      const response = await fetch(`${API_BASE_URL}/orders/${orderId}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ new_status: newStatus }),
      });

      const data = await response.json();

      if (response.ok) {
        Utils.showMessage(data.message || "Estado actualizado correctamente");
        Orders.loadOrderDetails(); // Reload order details
      } else {
        throw new Error(data.error || "Error al actualizar el estado");
      }
    } catch (error) {
      Utils.showMessage(error.message, "error");
    }
  }

  static async addProductToOrder(orderId, productId, quantity) {
    try {
      const response = await fetch(`${API_BASE_URL}/orders/add-product`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          order_id: orderId,
          product_id: productId,
          quantity: quantity,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        Utils.showMessage(data.message || "Producto añadido correctamente");
        Orders.loadOrderDetails(); // Reload order details
        Products.loadAllProducts(); // Reload product list
      } else {
        throw new Error(data.error || "Error al añadir el producto");
      }
    } catch (error) {
      Utils.showMessage(error.message, "error");
    }
  }
}

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  Sales.loadSalesData();
  Stock.loadLowStockProducts();
  Orders.loadOrderDetails();
  Products.loadAllProducts();

  // Event listener for updating order status
  document
    .getElementById("update-status-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const orderId = document.getElementById("order-id").value;
      const newStatus = document.getElementById("new-status").value;
      Orders.updateOrderStatus(orderId, newStatus);
      this.reset();
    });

  // Event listener for adding a product to an order
  document
    .getElementById("add-product-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const orderId = document.getElementById("add-order-id").value;
      const productId = document.getElementById("product-id").value;
      const quantity = document.getElementById("quantity").value;
      Orders.addProductToOrder(orderId, productId, quantity);
      this.reset();
    });
});
