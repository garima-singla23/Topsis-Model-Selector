const API = "http://127.0.0.1:8000";
let latestResult = [];
let chartInstance = null;

function renderChart(data) {
    const labels = data.map(r => r.Model);
    const scores = data.map(r => r["Topsis Score"]);

    const ctx = document.getElementById("scoreChart").getContext("2d");

    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "TOPSIS Score",
                data: scores,
                backgroundColor: "#38bdf8"
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

function updateCount() {
    const boxes = document.querySelectorAll("#models-box input[type='checkbox']");
    const checked = [...boxes].filter(b => b.checked).length;

    boxes.forEach(b => b.disabled = checked >= 5 && !b.checked);

    document.getElementById("selection-count").innerText =
        `Selected: ${checked} / 5`;
}

async function loadModels() {
    const res = await fetch(`${API}/available-models`);
    const models = await res.json();

    const box = document.getElementById("models-box");
    box.innerHTML = "";

    models.forEach(model => {
        const div = document.createElement("div");
        div.className = "model-item";

        div.innerHTML = `
            <label>
                <input type="checkbox" value="${model}" onchange="updateCount()">
                <span class="model-text">${model}</span>
            </label>
        `;
        box.appendChild(div);
    });

    updateCount();
}

function renderTable(data) {
    const tbody = document.getElementById("result");
    tbody.innerHTML = "";

    data.forEach((row, index) => {
        const tr = document.createElement("tr");

        if (index === 0) {
            tr.style.background = "#14532d";
            tr.style.fontWeight = "bold";
        }

        tr.innerHTML = `
            <td>${row.Rank}</td>
            <td>${row.Model}</td>
            <td>${Number(row["Topsis Score"]).toFixed(4)}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function runTopsis() {
    const selected = [...document.querySelectorAll(
        "#models-box input[type='checkbox']:checked"
    )].map(cb => cb.value);

    if (selected.length < 4 || selected.length > 5) {
        alert("Please select 4–5 models.");
        return;
    }

    const weights = {
        accuracy: parseFloat(document.getElementById("accuracy").value),
        latency: parseFloat(document.getElementById("latency").value),
        size: parseFloat(document.getElementById("size").value),
        languages: parseFloat(document.getElementById("languages").value)
    };

    if (Object.values(weights).some(isNaN)) {
        alert("All weights must be numeric.");
        return;
    }

    const res = await fetch(`${API}/rank-models`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ models: selected, weights })
    });

    if (!res.ok) {
        const err = await res.json();
        alert(err.detail || "Server error");
        return;
    }

    const data = await res.json();
    latestResult = data;

    document.getElementById("download-btn").disabled = false;
    renderTable(data);
    renderChart(data);
}

function downloadCSV() {
    if (!latestResult.length) {
        alert("No data to download");
        return;
    }

    let csv = "Rank,Model,TOPSIS Score\n";
    latestResult.forEach(r => {
        csv += `${r.Rank},"${r.Model}",${r["Topsis Score"]}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "topsis_model_ranking.csv";
    link.click();
}

function filterModels() {
    const query = document.getElementById("model-search").value.toLowerCase();
    document.querySelectorAll(".model-item").forEach(item => {
        item.style.display =
            item.innerText.toLowerCase().includes(query) ? "flex" : "none";
    });
}

document.addEventListener("DOMContentLoaded", loadModels);

