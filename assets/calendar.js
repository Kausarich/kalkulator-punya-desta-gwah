(function (root) {
  "use strict";
  const E = root.DestaEngine,
    D = root.DestaData;
  root.initCalendar = function () {
    const get = (id) => document.getElementById(id),
      now = new Date();
    const state = {
      year: now.getFullYear(),
      month: now.getMonth() + 1,
      selected: now.getDate(),
      table: "hijri",
    };
    function guard(fn) {
      try {
        fn();
        get("calendar-error").hidden = true;
      } catch (error) {
        get("calendar-error").textContent = error.message;
        get("calendar-error").hidden = false;
      }
    }
    function yearRange(y, min = 623, max = 9998) {
      if (!Number.isInteger(y) || y < min || y > max)
        throw Error(`Tahun harus ${min}–${max}.`);
      return y;
    }
    const gregText = (y, m, d) => `${d} ${D.GREG_MONTHS[m - 1]} ${y} M`;
    const hijriText = (h) =>
      `${h.day} ${D.HIJRI_MONTHS[h.month - 1]} ${h.year} H`;
    function select(day, focus = false) {
      state.selected = day;
      const h = E.gregorianToHijri(state.year, state.month, day),
        dow = E.utcDate(state.year, state.month, day).getUTCDay();
      get("calendar-selected").textContent =
        `${D.DAYS_ID[dow]}, ${gregText(state.year, state.month, day)}\n${hijriText(h)}${E.holiday(h.month, h.day) ? "\n" + E.holiday(h.month, h.day) : ""}`;
      get("calendar-days")
        .querySelectorAll("button")
        .forEach((button) => {
          const selected = Number(button.dataset.day) === day;
          button.setAttribute("aria-pressed", String(selected));
          button.tabIndex = selected ? 0 : -1;
          if (selected && focus) button.focus();
        });
    }
    function focusDate(date) {
      state.year = yearRange(date.getUTCFullYear());
      state.month = date.getUTCMonth() + 1;
      state.selected = date.getUTCDate();
      render();
      get("calendar-days")
        .querySelector(`[data-day="${state.selected}"]`)
        ?.focus();
    }
    function render() {
      const now = new Date();
      yearRange(state.year);
      const y = state.year,
        m = state.month,
        days = E.utcDate(y, m + 1, 0).getUTCDate(),
        first = E.gregorianToHijri(y, m, 1),
        last = E.gregorianToHijri(y, m, days);
      get("calendar-title").textContent = `${D.GREG_MONTHS[m - 1]} ${y}`;
      get("calendar-hijri").textContent =
        first.year === last.year
          ? `${D.HIJRI_MONTHS[first.month - 1]}${first.month === last.month ? "" : " – " + D.HIJRI_MONTHS[last.month - 1]} ${first.year} H`
          : `${D.HIJRI_MONTHS[first.month - 1]} ${first.year} – ${D.HIJRI_MONTHS[last.month - 1]} ${last.year} H`;
      get("cal-month").value = m;
      get("cal-year").value = y;
      const grid = get("calendar-days");
      grid.replaceChildren();
      for (let i = 0; i < E.utcDate(y, m, 1).getUTCDay(); i++) {
        const blank = document.createElement("span");
        blank.setAttribute("aria-hidden", "true");
        grid.append(blank);
      }
      for (let day = 1; day <= days; day++) {
        const h = E.gregorianToHijri(y, m, day),
          event = E.holiday(h.month, h.day),
          button = document.createElement("button");
        button.className = "calendar-day";
        button.dataset.day = day;
        button.type = "button";
        button.setAttribute(
          "aria-label",
          `${gregText(y, m, day)}, ${hijriText(h)}${event ? ", " + event : ""}`,
        );
        button.classList.toggle(
          "today",
          y === now.getFullYear() &&
            m === now.getMonth() + 1 &&
            day === now.getDate(),
        );
        if (button.classList.contains("today"))
          button.setAttribute("aria-current", "date");
        const g = document.createElement("strong");
        g.textContent = day;
        const badge = document.createElement("span");
        badge.className = "hijri-number";
        badge.textContent = h.day;
        const short = document.createElement("span");
        short.className = "month-short";
        short.textContent = D.HIJRI_MONTHS_SHORT[h.month - 1];
        button.append(g, badge, short);
        if (event) {
          const dot = document.createElement("span");
          dot.className = "event-dot";
          dot.setAttribute("aria-hidden", "true");
          button.append(dot);
        }
        button.addEventListener("click", () => select(day));
        button.addEventListener("keydown", (e) => {
          const step = {
            ArrowLeft: -1,
            ArrowRight: 1,
            ArrowUp: -7,
            ArrowDown: 7,
          }[e.key];
          if (step !== undefined) {
            e.preventDefault();
            guard(() =>
              focusDate(E.utcDate(state.year, state.month, day + step)),
            );
          } else if (e.key === "Home" || e.key === "End") {
            e.preventDefault();
            const weekday = E.utcDate(state.year, state.month, day).getUTCDay(),
              offset = e.key === "Home" ? -weekday : 6 - weekday;
            guard(() =>
              focusDate(E.utcDate(state.year, state.month, day + offset)),
            );
          }
        });
        grid.append(button);
      }
      select(Math.min(state.selected, days));
      get("cal-prev").disabled = y === 623 && m === 1;
      get("cal-next").disabled = y === 9998 && m === 12;
    }
    function move(delta) {
      guard(() => {
        const next = E.utcDate(state.year, state.month + delta, 1);
        yearRange(next.getUTCFullYear());
        state.year = next.getUTCFullYear();
        state.month = next.getUTCMonth() + 1;
        state.selected = 1;
        render();
      });
    }
    D.GREG_MONTHS.forEach((name, i) =>
      get("cal-month").add(new Option(name, i + 1)),
    );
    D.HIJRI_MONTHS.forEach((name, i) =>
      get("hijri-month").add(new Option(name, i + 1)),
    );
    D.DAYS_ID.forEach((name) => {
      const span = document.createElement("span");
      span.textContent = name.slice(0, 3);
      get("calendar-weekdays").append(span);
    });
    get("cal-prev").onclick = () => move(-1);
    get("cal-next").onclick = () => move(1);
    get("cal-today").onclick = () =>
      guard(() => {
        const today = new Date();
        state.year = today.getFullYear();
        state.month = today.getMonth() + 1;
        state.selected = today.getDate();
        render();
      });
    get("cal-jump").onsubmit = (event) => {
      event.preventDefault();
      guard(() => {
        const y = yearRange(Number(get("cal-year").value)),
          m = Number(get("cal-month").value);
        E.validateDate(y, m, 1);
        state.year = y;
        state.month = m;
        state.selected = 1;
        render();
      });
    };
    function convertGreg() {
      const parts = get("greg-date").value.split("-").map(Number);
      yearRange(parts[0]);
      const h = E.gregorianToHijri(...parts);
      get("greg-result").textContent = hijriText(h);
    }
    function convertHijri() {
      const y = Number(get("hijri-year").value),
        m = Number(get("hijri-month").value),
        d = Number(get("hijri-day").value);
      const g = E.jdToGregorian(E.hijriToJD(y, m, d));
      get("hijri-result").textContent = gregText(g.year, g.month, g.day);
    }
    for (const [form, action, result] of [
      ["greg-convert", convertGreg, "greg-result"],
      ["hijri-convert", convertHijri, "hijri-result"],
    ]) {
      get(form).addEventListener(
        "input",
        () => (get(result).textContent = "Tanggal berubah — tekan Konversi."),
      );
      get(form).onsubmit = (e) => {
        e.preventDefault();
        get(result).textContent = "";
        guard(action);
      };
    }
    function table() {
      const hijri = state.table === "hijri",
        y = yearRange(
          Number(get("month-year").value),
          hijri ? 1 : 623,
          hijri ? 9665 : 9998,
        ),
        rows = [];
      for (let month = 1; month <= 12; month++) {
        const jd = hijri
            ? E.hijriToJD(y, month, 1)
            : E.gregorianToJD(y, month, 1),
          g = E.jdToGregorian(jd),
          h = E.jdToHijri(jd),
          duration = hijri
            ? E.hijriMonthDays(y, month)
            : E.utcDate(y, month + 1, 0).getUTCDate();
        const tr = document.createElement("tr");
        for (const text of [
          hijri ? D.HIJRI_MONTHS[month - 1] : D.GREG_MONTHS[month - 1],
          D.DAYS_ID[E.utcDate(g.year, g.month, g.day).getUTCDay()],
          hijri ? gregText(g.year, g.month, g.day) : hijriText(h),
          `${duration} hari`,
        ]) {
          const td = document.createElement("td");
          td.textContent = text;
          tr.append(td);
        }
        rows.push(tr);
      }
      get("month-body").replaceChildren(...rows);
      get("month-caption").textContent =
        `Awal bulan ${hijri ? "Hijriah" : "Masehi"} ${y}`;
    }
    function setTable(type) {
      state.table = type;
      get("month-hijri").setAttribute("aria-pressed", String(type === "hijri"));
      get("month-greg").setAttribute("aria-pressed", String(type === "greg"));
      get("month-year").min = type === "hijri" ? 1 : 623;
      get("month-year").max = type === "hijri" ? 9665 : 9998;
      get("month-year").value =
        type === "hijri"
          ? E.gregorianToHijri(
              now.getFullYear(),
              now.getMonth() + 1,
              now.getDate(),
            ).year
          : now.getFullYear();
      guard(table);
    }
    get("month-hijri").onclick = () => setTable("hijri");
    get("month-greg").onclick = () => setTable("greg");
    get("month-form").onsubmit = (e) => {
      e.preventDefault();
      guard(table);
    };
    for (const [id, delta] of [
      ["month-prev", -1],
      ["month-next", 1],
    ])
      get(id).onclick = () =>
        guard(() => {
          const input = get("month-year"),
            value = yearRange(
              Number(input.value) + delta,
              Number(input.min),
              Number(input.max),
            );
          input.value = value;
          table();
        });
    get("greg-date").value = E.localDateString(now);
    const h = E.gregorianToHijri(
      now.getFullYear(),
      now.getMonth() + 1,
      now.getDate(),
    );
    get("hijri-day").value = h.day;
    get("hijri-month").value = h.month;
    get("hijri-year").value = h.year;
    guard(() => {
      render();
      convertGreg();
      convertHijri();
    });
    setTable("hijri");
    return state;
  };
})(globalThis);
