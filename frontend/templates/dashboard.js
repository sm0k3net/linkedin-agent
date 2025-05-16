// frontend/static/dashboard.js

document.getElementById("config-form").onsubmit = async function(e) {
    e.preventDefault();
    const topics = document.getElementById("topics").value;
    const behavior = document.getElementById("behavior").value;
    await fetch("/api/config", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({topics, behavior})
    });
    alert("Config updated!");
};

async function startAgent() {
    await fetch("/api/start", {method: "POST"});
    alert("Agent started!");
}

async function stopAgent() {
    await fetch("/api/stop", {method: "POST"});
    alert("Agent stopped!");
}

async function loadAnalytics() {
    const res = await fetch("/api/analytics");
    const data = await res.json();
    document.getElementById("analytics").innerHTML = `
        <ul>
            <li>Likes: ${data.like}</li>
            <li>Follows: ${data.follow}</li>
            <li>Comments: ${data.comment}</li>
        </ul>
    `;
}
loadAnalytics();
setInterval(loadAnalytics, 5000);