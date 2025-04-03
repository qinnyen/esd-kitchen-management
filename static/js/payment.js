// Retrieve total price from URL query parameters
const urlParams = new URLSearchParams(window.location.search);
const totalPrice = urlParams.get('totalPrice');

// Display total price on the payment page
document.getElementById('total-price').textContent = totalPrice;

// Initialize Stripe (replace with your publishable key)
const stripe = Stripe("pk_test_51R9mXXBOyJ3Yy6tJ0jDBIoEzjntIOyMgvAWs7vzpzweYivhW0pMZIJcagl2gG0hizGLK1B6CaB2MHlcVTGcRU55p00ztObLIWW");

document.addEventListener("DOMContentLoaded", async () => {
    const paymentForm = document.getElementById("payment-form");
    const submitButton = document.getElementById("submit");
    const paymentMessage = document.getElementById("payment-message");

    // Initialize Stripe Elements
    const elements = stripe.elements();
    const cardElement = elements.create("card");
    cardElement.mount("#card-element");

    // Fetch client secret from backend
    const { clientSecret } = await fetch("/create-payment-intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount: Math.round(totalPrice * 100) }) // Convert dollars to cents
    }).then((res) => res.json());

    // Handle form submission
    paymentForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        submitButton.disabled = true;

        const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: cardElement,
                billing_details: {
                    name: "Customer Name", // Replace with actual customer name input if available
                },
            },
        });

        if (error) {
            paymentMessage.style.display = "block";
            paymentMessage.className = "alert alert-danger"; // Bootstrap error styling
            paymentMessage.textContent = error.message;
            submitButton.disabled = false;
        } else if (paymentIntent.status === "succeeded") {
            paymentMessage.style.display = "block";
            paymentMessage.className = "alert alert-success"; // Bootstrap success styling
            paymentMessage.textContent = "Payment successful!";
            console.log("PaymentIntent:", paymentIntent);
        }
    });
});
