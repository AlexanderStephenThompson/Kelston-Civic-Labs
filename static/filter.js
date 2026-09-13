// Progressive enhancement: live filter for the standards listing.
// Without JS the full listing renders and is fully usable.
(function () {
  var box = document.querySelector("[data-search]");
  if (!box) return;
  box.hidden = false;
  var input = box.querySelector("input");
  var count = box.querySelector("[data-count]");
  var rows = [];
  document.querySelectorAll("table[data-filterable] tbody tr").forEach(function (row) {
    rows.push(row);
  });
  var total = rows.length;

  function apply() {
    var needle = input.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (row) {
      var haystack = (row.getAttribute("data-name") || row.textContent).toLowerCase();
      var match = needle === "" || haystack.indexOf(needle) !== -1;
      row.hidden = !match;
      if (match) shown += 1;
    });
    count.textContent = needle === "" ? "" : shown + " of " + total + " standards";
  }
  input.addEventListener("input", apply);
})();
