document.addEventListener("DOMContentLoaded", function () {
  fetch("/menu/all")
    .then((response) => response.json())
    .then((data) => {
      const menuContainer = document.getElementById("menu-container");
      data.forEach((item) => {
        if (item.availability_status) {
          const menuItem = document.createElement("div");
          menuItem.className = "col-md-4 mb-4";
          menuItem.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">${item.name}</h5>
                            <p class="card-text">${item.description}</p>
                            <p class="card-text text-primary">$${item.price.toFixed(
                              2
                            )}</p>
                            <button class="btn btn-primary" onclick="addToCart(${
                              item.id
                            }, '${item.name}', ${
            item.price
          })">Add to Cart</button>
                        </div>
                    </div>
                `;
          menuContainer.appendChild(menuItem);
        }
      });
      updateCartCount();
    })
    .catch((error) => console.error("Error fetching menu items:", error));
});

function addToCart(id, name, price) {
  let cart = JSON.parse(localStorage.getItem("cart")) || [];
  const existingItem = cart.find((item) => item.id === id);

  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({ id, name, price, quantity: 1 });
  }
  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  const cart = JSON.parse(localStorage.getItem("cart")) || [];
  const cartCount = Array.isArray(cart)
    ? cart.reduce((total, item) => total + (item.quantity || 0), 0)
    : 0;
  console.log(cartCount);
  console.log(cart);
  document.getElementById("cart-count").innerText = cartCount;
}

function viewCart() {
  window.location.href = "/cart";
}

function viewStatus() {
  window.location.href = "/status";
}