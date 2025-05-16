function showNotification(msg, error=false) {
    const n = document.getElementById("notification");
    n.innerText = msg;
    n.className = error ? "notification error" : "notification";
    n.style.display = "block";
    setTimeout(() => { n.style.display = "none"; }, 3000);
}

async function loadConfig() {
    const res = await fetch("/api/config");
    const data = await res.json();
    document.getElementById("topics").value = data.topics || "";
    document.getElementById("behavior").value = data.behavior || "";
    document.getElementById("current-config").innerHTML = `
        <strong>Current Topics:</strong> ${data.topics || "<em>None</em>"}<br>
        <strong>Current Behavior:</strong> <pre>${data.behavior || "<em>None</em>"}</pre>
    `;
}

document.getElementById("config-form").onsubmit = async function(e) {
    e.preventDefault();
    const topics = document.getElementById("topics").value;
    const behavior = document.getElementById("behavior").value;
    const res = await fetch("/api/config", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({topics, behavior})
    });
    if (res.ok) {
        showNotification("Config updated!");
        loadConfig();
    } else {
        showNotification("Failed to update config.", true);
    }
};

async function startAgent() {
    const res = await fetch("/api/start", {method: "POST"});
    if (res.ok) {
        showNotification("Agent started!");
    } else {
        showNotification("Failed to start agent.", true);
    }
    loadAgentState();
}

async function stopAgent() {
    const res = await fetch("/api/stop", {method: "POST"});
    if (res.ok) {
        showNotification("Agent stopped!");
    } else {
        showNotification("Failed to stop agent.", true);
    }
    loadAgentState();
}

async function loadAnalytics() {
    const res = await fetch("/api/analytics");
    const data = await res.json();
    document.getElementById("analytics").innerHTML = `
        <ul>
            <li>Likes: ${data.like}</li>
            <li>Follows: ${data.follow}</li>
            <li>Comments: ${data.comment}</li>
            <li>Posts: ${data.post}</li>
            <li>Connections: ${data.connect}</li>
        </ul>
    `;
}

async function loadAgentState() {
    const res = await fetch("/api/state");
    const data = await res.json();
    const state = document.getElementById("agent-state");
    if (data.running) {
        state.innerHTML = '<span style="color:green;">Running</span>';
        document.getElementById("start-btn").disabled = true;
        document.getElementById("stop-btn").disabled = false;
    } else {
        state.innerHTML = '<span style="color:#a00;">Stopped</span>';
        document.getElementById("start-btn").disabled = false;
        document.getElementById("stop-btn").disabled = true;
    }
}

window.onload = function() {
    loadConfig();
    loadAnalytics();
    loadAgentState();
    setInterval(loadAnalytics, 5000);
    setInterval(loadAgentState, 2000);
};