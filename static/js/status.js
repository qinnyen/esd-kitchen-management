document.getElementById("orderForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const customerId = document.getElementById("customerId").value;

    fetch(`/order-fulfillment/${customerId}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById("orderResults");
            resultsContainer.innerHTML = "";

            if (data.error) {
                resultsContainer.innerHTML = `<p>${data.error}</p>`;
            } else {
                const order = data;
                const orderDiv = document.createElement("div");
                console.log(order.MenuItems);
                orderDiv.innerHTML = `
                    <div>
                        <h3>Order ID: ${order.OrderID}</h3>
                        <p>Status: ${order.OrderStatus}</p>
                        <p>Total Price: $${order.TotalPrice}</p>
                        <p>Created At: ${order.CreatedAt}</p>
                        <h4>Items:</h4>
                        <ul>${order.MenuItems.map(item => `
                            <li>Item: ${item.name}</li>
                        `).join("")}</ul>
                    </div>
                `
                resultsContainer.appendChild(orderDiv);
                
            }
        })
        .catch(error => console.error("Error fetching orders:", error));
});
