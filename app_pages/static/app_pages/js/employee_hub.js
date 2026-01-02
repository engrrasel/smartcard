document.addEventListener("DOMContentLoaded", () => {

    /* ================= REMOVE EMPLOYEE CONFIRM ================= */
    document.querySelectorAll(".btn-remove-employee").forEach(btn => {
        btn.addEventListener("click", e => {
            if (!confirm("Are you sure you want to remove this employee?")) {
                e.preventDefault();
            }
        });
    });

    /* ================= LIVE SEARCH ================= */
    const input = document.getElementById("liveSearchInput");
    const resultsBox = document.getElementById("liveSearchResults");
    const companyId = document.getElementById("companyId")?.value;

    if (!input || !resultsBox || !companyId) return;

    let timer = null;

    input.addEventListener("keyup", () => {
        clearTimeout(timer);

        const query = input.value.trim();

        if (query.length < 2) {
            hideResults();
            return;
        }

        timer = setTimeout(() => {
            fetch(`/pages/employee/live-search/?company=${companyId}&q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => renderResults(data.results || []))
                .catch(() => hideResults());
        }, 300);
    });

    /* ================= CLICK OUTSIDE TO CLOSE ================= */
    document.addEventListener("click", e => {
        if (!e.target.closest(".hub-search")) {
            hideResults();
        }
    });

    /* ================= RENDER RESULTS ================= */
    function renderResults(results) {
        if (!results.length) {
            resultsBox.innerHTML = `<div class="empty">No results</div>`;
            resultsBox.style.display = "block";
            return;
        }

        resultsBox.innerHTML = results.map(u => `
            <div class="result-item">
                <img src="${u.avatar}">
                <div>
                    <div class="name">${u.name}</div>
                    <div class="email">${u.email}</div>
                </div>
                <a href="/pages/employee/send-request/${u.id}/?company=${companyId}"
                   class="btn btn-sm btn-outline-warning">
                   Invite
                </a>
            </div>
        `).join("");

        resultsBox.style.display = "block";
    }

    /* ================= HIDE RESULTS ================= */
    function hideResults() {
        resultsBox.style.display = "none";
        resultsBox.innerHTML = "";
    }

});
