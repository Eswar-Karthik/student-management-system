// ===== EduManage front-end helpers =====

// Theme persistence
(function () {
  const saved = localStorage.getItem("edu-theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
})();

function toggleTheme() {
  const cur = document.documentElement.getAttribute("data-theme") || "light";
  const next = cur === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("edu-theme", next);
}

// Toasts (from flash)
function showToast(msg, type = "info") {
  let host = document.getElementById("toast-host");
  if (!host) {
    host = document.createElement("div");
    host.id = "toast-host";
    document.body.appendChild(host);
  }
  const t = document.createElement("div");
  t.className = `toast-item ${type}`;
  const icon = { success: "check-circle", danger: "exclamation-circle",
                 warning: "exclamation-triangle", info: "info-circle" }[type] || "info-circle";
  t.innerHTML = `<i class="fa fa-${icon}"></i><div>${msg}</div>`;
  host.appendChild(t);
  setTimeout(() => { t.style.opacity = 0; setTimeout(() => t.remove(), 300); }, 3500);
}

// Animated counters
function animateCounters() {
  document.querySelectorAll("[data-counter]").forEach(el => {
    const target = parseFloat(el.dataset.counter) || 0;
    const decimals = (el.dataset.decimals | 0);
    let cur = 0;
    const step = target / 40;
    const tick = () => {
      cur += step;
      if (cur >= target) { el.textContent = target.toFixed(decimals); return; }
      el.textContent = cur.toFixed(decimals);
      requestAnimationFrame(tick);
    };
    tick();
  });
}

// Sidebar toggle (mobile)
function toggleSidebar() {
  document.querySelector(".sidebar")?.classList.toggle("open");
}

// Page loader
window.addEventListener("load", () => {
  document.querySelector(".page-loader")?.classList.add("hide");
  animateCounters();
});

// Confirm delete
function confirmDelete(e) {
  if (!confirm("Are you sure you want to delete this record?")) {
    e.preventDefault(); return false;
  }
  return true;
}
