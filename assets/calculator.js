(function (root) {
  "use strict";
  const E = root.DestaEngine;
  class Calculator {
    constructor() {
      this.expression = "";
      this.answer = 0;
      this.mode = "DEG";
      this.evaluated = false;
      this.error = "";
      this.result = "0";
    }
    append(token) {
      if (this.evaluated) {
        this.expression = ["+", "-", "*", "/", "%", "**"].includes(token)
          ? "Ans"
          : "";
        this.evaluated = false;
      }
      let before = this.expression;
      if (
        before &&
        (/[\d)]$/.test(before) || /(?:pi|e|Ans)$/.test(before)) &&
        (["(", "pi", "e", "Ans"].includes(token) ||
          (/^\d/.test(token) && /(?:\)|pi|e|Ans)$/.test(before)))
      )
        before += "*";
      if (before.length + token.length > 256)
        throw Error("Ekspresi maksimum 256 karakter.");
      this.expression = before + token;
      this.error = "";
    }
    apply(name) {
      if (this.evaluated) this.expression = "Ans";
      const value = E.applyFunction(this.expression, name);
      if (value.length > 256) throw Error("Ekspresi maksimum 256 karakter.");
      this.expression = value;
      this.evaluated = false;
      this.error = "";
    }
    clear() {
      this.expression = "";
      this.result = "0";
      this.error = "";
      this.evaluated = false;
    }
    backspace() {
      if (this.evaluated) {
        this.clear();
        return;
      }
      this.expression = this.expression.replace(
        /(?:factorial|powten|square|sqrt|asin|acos|atan|sin|cos|tan|log|ln|exp|abs|inv|neg)\($|Ans$|pi$|\*\*$|.$/,
        "",
      );
      this.error = "";
    }
    calculate() {
      if (!this.expression) return;
      this.answer = E.evaluate(this.expression, this.mode, this.answer);
      this.result = E.formatResult(this.answer);
      this.evaluated = true;
      this.error = "";
    }
  }
  root.DestaCalculator = Calculator;
  root.initCalculator = function () {
    const state = new Calculator(),
      get = (id) => document.getElementById(id);
    const numeric = [
      ["AC", "clear", "Hapus semua"],
      ["C", "back", "Hapus terakhir"],
      ["Ans", "Ans", "Hasil terakhir"],
      ["÷", "/", "Bagi"],
      ["7", "7"],
      ["8", "8"],
      ["9", "9"],
      ["×", "*", "Kali"],
      ["4", "4"],
      ["5", "5"],
      ["6", "6"],
      ["−", "-", "Kurang"],
      ["1", "1"],
      ["2", "2"],
      ["3", "3"],
      ["+", "+", "Tambah"],
      ["±", "fn:neg", "Ubah tanda"],
      ["0", "0"],
      [".", ".", "Titik desimal"],
      ["=", "equals", "Hitung hasil"],
    ];
    const science = [
      ["sin", "fn:sin"],
      ["cos", "fn:cos"],
      ["tan", "fn:tan"],
      ["asin", "fn:asin"],
      ["acos", "fn:acos"],
      ["atan", "fn:atan"],
      ["log", "fn:log"],
      ["ln", "fn:ln"],
      ["√x", "fn:sqrt", "Akar kuadrat"],
      ["x²", "fn:square", "Kuadrat"],
      ["xʸ", "**", "Pangkat"],
      ["10ˣ", "fn:powten", "Sepuluh pangkat"],
      ["exp", "fn:exp"],
      ["1/x", "fn:inv", "Resiprokal"],
      ["n!", "fn:factorial", "Faktorial"],
      ["abs", "fn:abs"],
      ["%", "%", "Sisa bagi"],
      ["π", "pi", "Pi"],
      ["e", "e", "Konstanta Euler"],
      ["(", "(", "Kurung buka"],
      [")", ")", "Kurung tutup"],
    ];
    function render() {
      get("calc-expression").textContent =
        E.displayExpression(state.expression) || "0";
      get("calc-input").scrollLeft = get("calc-input").scrollWidth;
      get("calc-result").textContent = state.result;
      get("calc-result").classList.toggle(
        "scientific",
        state.result.includes("×"),
      );
      get("calc-error").textContent = state.error;
      get("calc-error").hidden = !state.error;
    }
    function act(action) {
      try {
        if (action === "clear") state.clear();
        else if (action === "back") state.backspace();
        else if (action === "equals") state.calculate();
        else if (action.startsWith("fn:")) state.apply(action.slice(3));
        else state.append(action);
      } catch (error) {
        state.error = error.message;
      }
      render();
    }
    for (const [id, keys] of [
      ["number-keys", numeric],
      ["science-keys", science],
    ])
      for (const [label, action, name] of keys) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = label;
        if (name) button.setAttribute("aria-label", name);
        if (action === "equals") button.className = "primary";
        if (["clear", "back"].includes(action)) button.className = "danger";
        button.addEventListener("click", () => act(action));
        get(id).append(button);
      }
    get("calc-mode").addEventListener("click", () => {
      state.mode = ["DEG", "RAD", "GRAD"][
        (["DEG", "RAD", "GRAD"].indexOf(state.mode) + 1) % 3
      ];
      get("calc-mode").textContent = state.mode;
      get("calc-mode").setAttribute(
        "aria-label",
        `Mode sudut: ${state.mode}. Klik untuk mengganti.`,
      );
      get("calc-mode-note").textContent = {
        DEG: "360° = 1 putaran",
        RAD: "2π rad = 1 putaran",
        GRAD: "400 grad = 1 putaran",
      }[state.mode];
      state.evaluated = false;
    });
    document.addEventListener("keydown", (event) => {
      if (
        get("tab-calc").hidden ||
        event.ctrlKey ||
        event.altKey ||
        event.metaKey ||
        event.target.matches("input,select,textarea")
      )
        return;
      const key = event.key;
      if (key === "Enter" && event.target.closest("button,summary")) return;
      let action;
      if (/^[0-9.+*/%()-]$/.test(key)) action = key;
      else
        action = {
          Enter: "equals",
          "=": "equals",
          Backspace: "back",
          Escape: "clear",
          "^": "**",
          ",": ".",
        }[key];
      if (action) {
        event.preventDefault();
        act(action);
      }
    });
    const media = matchMedia("(min-width:680px)");
    get("science-panel").open = media.matches;
    media.addEventListener(
      "change",
      (event) => (get("science-panel").open = event.matches),
    );
    return state;
  };
  if (typeof module !== "undefined") module.exports = Calculator;
})(globalThis);
