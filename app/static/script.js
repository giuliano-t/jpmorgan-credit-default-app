document.getElementById("predictForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData.entries());

    // Convert string inputs to floats
    for (let key in payload) {
        payload[key] = parseFloat(payload[key]);
    }

    const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const result = await response.json();
    const output = `
        <p><strong>Will it default?:</strong> ${result.will_default}</p>
    `;
    document.getElementById("result").innerHTML = output;
});