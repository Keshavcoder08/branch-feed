const chips = document.querySelectorAll(".chip");
const titleEl = document.getElementById("branchTitle");
const statusEl = document.getElementById("status");
let latestRequest = 0;

function render(id, items) {
  const list = document.getElementById(id);
  list.innerHTML = "";
  if (!items || !items.length) {
    const li = document.createElement("li");
    li.className = "empty";
    li.textContent = "Nothing found. Try another branch.";
    list.appendChild(li);
    return;
  }
  items.forEach(function (it) {
    const li = document.createElement("li");

    const a = document.createElement("a");
    a.href = it.url;
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = it.title || it.url;

    const site = document.createElement("span");
    site.className = "site";
    site.textContent = it.site || "";

    const p = document.createElement("p");
    p.className = "snippet";
    p.textContent = it.snippet || "";

    li.append(a, site, p);
    list.appendChild(li);
  });
}

function clearLists() {
  ["news", "hackathons", "tech"].forEach(function (id) {
    document.getElementById(id).innerHTML = "";
  });
}

async function loadFeed(branch) {
  const requestId = ++latestRequest;

  chips.forEach(function (c) {
    c.setAttribute("aria-pressed", c.dataset.branch === branch ? "true" : "false");
  });
  titleEl.textContent = branch;
  document.body.dataset.branch = branch;
  statusEl.className = "";
  statusEl.textContent = "Loading " + branch + " feed...";
  clearLists();

  try {
    const res = await fetch("/api/feed?branch=" + encodeURIComponent(branch));
    const data = await res.json();
    if (requestId !== latestRequest) return; // user clicked another branch meanwhile

    if (data.error) {
      statusEl.className = "error";
      statusEl.textContent = data.error;
      return;
    }
    statusEl.textContent = "";
    render("news", data.news);
    render("hackathons", data.hackathons);
    render("tech", data.tech);
  } catch (e) {
    if (requestId !== latestRequest) return;
    statusEl.className = "error";
    statusEl.textContent = "Could not reach the server. Check that app.py is still running.";
  }
}

chips.forEach(function (chip) {
  chip.addEventListener("click", function () {
    loadFeed(chip.dataset.branch);
  });
});

if (chips.length) loadFeed(chips[0].dataset.branch);
