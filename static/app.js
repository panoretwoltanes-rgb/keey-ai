document.getElementById("btn").onclick = async function () {
    const text = document.getElementById("input").value;
    const res = await fetch("/api/quote", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({content: text})
    });
    const data = await res.json();
    const el = document.getElementById("result");

    if (data.success && data.file_url) {
        el.innerHTML = '报价已生成<br><a class="download-btn" href="' + data.file_url + '">下载报价单</a>';
    } else {
        el.textContent = data.message || "处理失败";
    }
    el.classList.remove("hidden");
};

async function loadHistory() {
    const res = await fetch("/api/history?limit=10");
    const data = await res.json();
    const el = document.getElementById("history");
    if (!data.success || !data.data.length) { el.innerHTML = ""; return; }
    el.innerHTML = "<h3>历史报价</h3>" + data.data.map(function (r) {
        return "<div><a href='/download/" + r.filename + "'>" + r.customer + " " + r.project + " (" + r.create_time + ")</a></div>";
    }).join("");
}

window.onload = loadHistory;
