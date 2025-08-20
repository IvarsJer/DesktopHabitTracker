// app/static/js/habits.js
(() => {
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];

  const postJSON = (url, body) =>
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {})
    }).then(r => {
      if (!r.ok) throw new Error("Request failed");
      return r.json();
    });

  // Toggle for boolean habits
  $$(".js-toggle-today").forEach(chk => {
    chk.addEventListener("change", async () => {
      const habitId = +chk.dataset.habitId;
      try {
        const res = await postJSON("/api/toggle_today", { habit_id: habitId });
        // Update the week last dot (today)
        const row = chk.closest("tr");
        const dots = $$(".week .wk", row);
        if (dots.length) {
          const todayDot = dots[dots.length - 1];
          todayDot.classList.toggle("on", res.done === true || (res.total || 0) > 0);
        }
      } catch (e) {
        alert("Could not toggle today");
        chk.checked = !chk.checked; // revert UI
      }
    });
  });

  // Quick add for numeric habits
  $$(".js-quick-add").forEach(btn => {
    btn.addEventListener("click", async () => {
      const habitId = +btn.dataset.habitId;
      const row = btn.closest("tr");
      const input = $(".js-quick-amount", row);
      const delta = parseFloat(input.value || "0");
      if (!delta || isNaN(delta)) return alert("Enter a number to add");

      btn.disabled = true;
      try {
        const res = await postJSON("/api/quick_add", { habit_id: habitId, delta });
        // Mark today's dot as on if total > 0
        const dots = $$(".week .wk", row);
        if (dots.length) dots[dots.length - 1].classList.toggle("on", (res.total || 0) > 0);
        // Flash small inline note of today's total
        let label = $(".label", row.cells[1]);
        if (!label) {
          label = document.createElement("div");
          label.className = "label";
          row.cells[1].appendChild(label);
        }
        const unit = row.cells[0].querySelector(".label").textContent.replace(/^.*\((.*)\).*$/, "$1");
        label.textContent = `Today: ${res.total.toFixed(2)} ${unit}`;
        input.value = "";
      } catch (e) {
        alert("Could not add value");
      } finally {
        btn.disabled = false;
      }
    });
  });
})();
