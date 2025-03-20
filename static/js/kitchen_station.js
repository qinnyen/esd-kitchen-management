document.addEventListener("DOMContentLoaded", function () {
    const stationContainer = document.getElementById("station-container");

    // Fetch all stations and their tasks from the backend
    fetch("/kitchen/stations")
        .then((response) => response.json())
        .then((data) => {
            stationContainer.innerHTML = ""; // Clear container before populating
            data.forEach((station) => {
                const stationCard = document.createElement("div");
                stationCard.className = "card mb-3"; // Bootstrap card class
                stationCard.innerHTML = `
                    <div class="card-body">
                        <h2 class="card-title">Station ID: ${station.station_id}</h2>
                        <p class="card-text">Tasks:</p>
                        <ul class="list-group list-group-flush" id="task-list-${station.station_id}">
                            ${station.tasks
                                .map((task) => {
                                    if (task.task_status === "In Progress") {
                                        // Fetch menu items and ingredients for tasks already "In Progress"
                                        fetchMenuItemsAndIngredients(task.task_id, task.order_id);
                                    }
                                    if (task.task_status === "Completed") {
                                        return `
                                            <li class="list-group-item" id="task-${task.task_id}">
                                                Task ID: ${task.task_id}, Order ID: ${task.order_id}, Status:
                                                <span class="badge bg-success text-white">Completed</span>
                                            </li>`;
                                    } else {
                                        return `
                                            <li class="list-group-item" id="task-${task.task_id}">
                                                Task ID: ${task.task_id}, Order ID: ${task.order_id}, Status: ${task.task_status}
                                                
                                            </li>
                                            ${getTaskButton(task.task_id, task.task_status, task.order_id)}
                                            `;
                                    }
                                })
                                .join("")}
                        </ul>
                    </div>
                `;
                stationContainer.appendChild(stationCard);
            });
        })
        .catch((error) => console.error("Error fetching stations:", error));
});

function fetchMenuItemsAndIngredients(taskId, orderId) {
    fetch(`/menu/${orderId}`) // Fetch menu items and ingredients for this order
        .then((response) => response.json())
        .then((data) => {
            const taskElement = document.getElementById(`task-${taskId}`);
            const menuItemsWithIngredients = data.menu_items.map((menuItem) => {
                const ingredientsForMenuItem = data.ingredients.filter(
                    (ingredient) => ingredient.menu_item_id === menuItem.id
                );

                const ingredientList = ingredientsForMenuItem
                    .map(
                        (ingredient) =>
                            `<li>${ingredient.name}: ${ingredient.quantity_required} ${ingredient.unit_of_measure}</li>`
                    )
                    .join("");

                return `
                    <p><strong>${menuItem.name}</strong></p>
                    <p>Quantity: ${menuItem.quantity}</p>
                    <p>Ingredients:</p>
                    <ul>${ingredientList}</ul>
                `;
            });

            taskElement.innerHTML += `
                ${menuItemsWithIngredients.join("")}
            `;
        })
        .catch((error) =>
            console.error("Error fetching menu items or updating task:", error)
        );
}

function getTaskButton(taskId, status, orderId) {
    if (status === "Assigned") {
        return `<button class="btn btn-primary mt-2" onclick="acceptTask(${taskId}, ${orderId})">Accept</button>`;
    } else if (status === "In Progress") {
        return `<button class="btn btn-success mt-2" onclick="markTaskCompleted(${taskId})">Mark as Completed</button>`;
    }
}

function acceptTask(taskId, orderId) {
    fetch(`/menu/${orderId}`) // Fetch menu items and ingredients for this order
        .then((response) => response.json())
        .then((data) => {
            const taskElement = document.getElementById(`task-${taskId}`);
            const menuItemsWithIngredients = data.menu_items.map((menuItem) => {
                const ingredientsForMenuItem = data.ingredients.filter(
                    (ingredient) => ingredient.menu_item_id === menuItem.id
                );

                const ingredientList = ingredientsForMenuItem
                    .map(
                        (ingredient) =>
                            `<li>${ingredient.name}: ${ingredient.quantity_required} ${ingredient.unit_of_measure}</li>`
                    )
                    .join("");

                return `
                    <p><strong>${menuItem.name}</strong></p>
                    <p>Quantity: ${menuItem.quantity}</p>
                    <p>Ingredients:</p>
                    <ul>${ingredientList}</ul>
                `;
            });

            taskElement.innerHTML = `
                Task ID: ${taskId}, Order ID: ${orderId}, Status: In Progress
                ${menuItemsWithIngredients.join("")}
                <button class="btn btn-success mt-2" onclick="markTaskCompleted(${taskId})">Mark as Completed</button>
            `;

            // Update the task status to "In Progress"
            fetch(`/kitchen/task/${taskId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task_status: "In Progress" }),
            });
        })
        .catch((error) =>
            console.error("Error fetching menu items or updating task:", error)
        );
}

function markTaskCompleted(taskId) {
    fetch(`/kitchen/task/${taskId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_status: "Completed" }),
    })
        .then((response) => response.json())
        .then(() => location.reload()) // Reload the page to refresh tasks
        .catch((error) => console.error("Error marking task as completed:", error));
}