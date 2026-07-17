const state = { rows: [], query: "", family: "", sort: "score", direction: -1 };

function parseCsv(text) {
  const records = [];
  let record = [], field = "", quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (quoted) {
      if (char === '"' && text[index + 1] === '"') { field += '"'; index += 1; }
      else if (char === '"') quoted = false;
      else field += char;
    } else if (char === '"') quoted = true;
    else if (char === ",") { record.push(field); field = ""; }
    else if (char === "\n") { record.push(field); records.push(record); record = []; field = ""; }
    else if (char !== "\r") field += char;
  }
  if (field || record.length) { record.push(field); records.push(record); }
  const [headers, ...rows] = records;
  return rows.filter(row => row.length === headers.length).map(row =>
    Object.fromEntries(headers.map((header, index) => [header, row[index]]))
  );
}

function averageByModel(rows) {
  const groups = new Map();
  rows.forEach(row => {
    const values = groups.get(row.model) || [];
    values.push(Number(row.score));
    groups.set(row.model, values);
  });
  return [...groups].map(([model, scores]) => ({
    model,
    score: scores.reduce((sum, value) => sum + value, 0) / scores.length
  })).sort((a, b) => b.score - a.score);
}

function renderLeaderboard() {
  const target = document.querySelector("#leaderboard-bars");
  target.replaceChildren(...averageByModel(state.rows).map((row, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "bar-row";
    wrapper.innerHTML = `
      <div class="bar-label" title="${row.model}">${row.model.replace(/^.*\//, "")}</div>
      <div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width:${row.score}%;animation-delay:${index * 25}ms"></div></div>
      <div class="bar-score">${row.score.toFixed(1)}</div>`;
    return wrapper;
  }));
}

function filteredRows() {
  const query = state.query.toLowerCase();
  return state.rows.filter(row =>
    (!state.family || row.family === state.family) &&
    (!query || `${row.model} ${row.effort}`.toLowerCase().includes(query))
  ).sort((a, b) => {
    const left = state.sort === "score" ? Number(a.score) : a[state.sort].toLowerCase();
    const right = state.sort === "score" ? Number(b.score) : b[state.sort].toLowerCase();
    if (left === right) return a.model.localeCompare(b.model);
    return (left > right ? 1 : -1) * state.direction;
  });
}

function renderTable() {
  const rows = filteredRows();
  const body = document.querySelector("#results-body");
  document.querySelector("#result-count").textContent = `${rows.length} result${rows.length === 1 ? "" : "s"}`;
  if (!rows.length) {
    body.innerHTML = '<tr><td colspan="6" class="empty">No responses match those filters.</td></tr>';
    return;
  }
  body.replaceChildren(...rows.map(row => {
    const tr = document.createElement("tr");
    const exactHaiku = row.haiku_syllables === "5/7/5";
    tr.innerHTML = `
      <td><span class="model-name">${row.model}</span></td>
      <td>${row.effort}</td>
      <td><span class="score">${row.score}</span></td>
      <td><span class="grade ${row.grade === "B" ? "grade-b" : ""}">${row.grade}</span></td>
      <td>${exactHaiku ? "5 / 7 / 5" : row.haiku_syllables || "—"}</td>
      <td><a class="response-link" href="results/${row.path}">Read →</a></td>`;
    return tr;
  }));
}

function setSort(button) {
  const sort = button.dataset.sort;
  if (state.sort === sort) state.direction *= -1;
  else { state.sort = sort; state.direction = sort === "score" ? -1 : 1; }
  document.querySelectorAll("th").forEach(item => item.removeAttribute("aria-sort"));
  button.closest("th").setAttribute("aria-sort", state.direction === 1 ? "ascending" : "descending");
  renderTable();
}

async function init() {
  try {
    const response = await fetch("results/scores.csv");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.rows = parseCsv(await response.text());
    const familyFilter = document.querySelector("#family-filter");
    [...new Set(state.rows.map(row => row.family))].sort().forEach(family => {
      const option = document.createElement("option");
      option.value = family;
      option.textContent = family;
      familyFilter.append(option);
    });
    document.querySelector("#search").addEventListener("input", event => { state.query = event.target.value; renderTable(); });
    familyFilter.addEventListener("change", event => { state.family = event.target.value; renderTable(); });
    document.querySelectorAll("th button").forEach(button => button.addEventListener("click", () => setSort(button)));
    renderLeaderboard();
    renderTable();
  } catch (error) {
    const message = "Results could not be loaded. Open the full evaluation instead.";
    document.querySelector("#leaderboard-bars").innerHTML = `<p class="empty">${message}</p>`;
    document.querySelector("#results-body").innerHTML = `<tr><td colspan="6" class="empty">${message}</td></tr>`;
    console.error(error);
  }
}

init();
