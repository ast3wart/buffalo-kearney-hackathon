"""Build docs/pitch/data-map-judges.html: Brandon's data map v2 content + a visual layer (his file untouched).

Rebuild after he updates docs/build/data-map.html:
    git show origin/docs/data-map:docs/build/data-map.html > /tmp/dm.html   # or the merged file
    python scripts/build_judges_map.py /tmp/dm.html docs/pitch/data-map-judges.html docs/pitch/data-map-judges.css
"""
import sys

src, out = sys.argv[1], sys.argv[2]
s = open(src).read()


def r(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


CSS = open(sys.argv[3]).read()
r("</style>\n", "</style>\n<style>\n" + CSS + "\n</style>\n")
r("<h1>Afterlife Data Map</h1>", '<h1>Afterlife Data Map<span class="ed">Judges’ edition</span></h1>')
r("<span>contract <b>v4</b> (PR #6, in review)</span>", "<span>contract <b>v4</b> (merged)</span>")
r("contract v4 (PR #6) ·", "contract v4 ·")

nav_start = s.index('  <nav class="toc" aria-label="Sections">')
nav_end = s.index("</nav>", nav_start) + len("</nav>")
nav = s[nav_start:nav_end]
s = s[:nav_start] + s[nav_end:]
nav = nav.replace('<nav class="toc"', '<nav class="toc sticky"').replace(
    '<a href="#flow">Data flow</a>', '<a href="#flow">Data flow</a><a href="#your-view">Your view</a>')
glance = """
<div class="glance" aria-label="At a glance">
  <div class="kpi" style="--c: var(--shared)"><span class="s">Companies</span><span class="v">3</span><span class="l">Tuning, holdout (raw SAP extract + acquired plant), and an HVAC control with no planted problem</span></div>
  <div class="kpi" style="--c: var(--spend)"><span class="s">Purchase lines → parts</span><span class="v">97.8–100%</span><span class="l">Precision and recall on holdout companies the matcher was never tuned on</span></div>
  <div class="kpi" style="--c: var(--warranty)"><span class="s">Supplier attribution</span><span class="v">58 / 74</span><span class="l">Seal-kit claims (Apr–Jun) tied to one supplier's lot; the rest shown as supplier unresolved</span></div>
  <div class="kpi" style="--c: var(--ai)"><span class="s">False alerts, clean data</span><span class="v">0 / 300</span><span class="l">Synthetic clean series, with Benjamini–Hochberg control across every series tested</span></div>
</div>
"""
r("</header>\n", "</header>\n" + glance + nav + "\n")

view = """
<section id="your-view">
  <div class="view">
    <div class="sec-head"><div class="eyebrow">We'd value your view</div><h2>Where does this match how your clients really work?</h2>
      <p>Five questions where practitioner judgment beats our assumptions. Any answer helps us set the bar for the demo.</p></div>
    <div class="qs">
      <div><span class="ref">Supplier attribution</span><b>Is a lot-level spike enough to open a supplier conversation?</b><span>Or do clients need serial-to-batch traceability before anyone names a supplier?</span></div>
      <div><span class="ref">Contract compliance</span><b>How often do clients pay above their own contract price?</b><span>Including spares bought above a "spares at series price" clause. Is ~0.3–0.5% of spend a believable leakage rate?</span></div>
      <div><span class="ref">Spare-part pricing</span><b>How much more does service pay than production for the same part?</b><span>We found no published benchmark, so we treat our markup range as a scenario.</span></div>
      <div><span class="ref">Ownership</span><b>Do these owners match your clients?</b><span>Supplier quality reviews alerts, procurement reviews terms, a warranty-recovery manager submits, finance books.</span></div>
      <div><span class="ref">Early warning</span><b>False alarm or a late catch: which costs a quality team more?</b><span>That decides how strict the alert rule should be.</span></div>
    </div>
  </div>
</section>
"""
r("<footer>", view + "\n<footer>")

r("\n</body>", """
<script>
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll("nav.toc.sticky a"));
  if (!("IntersectionObserver" in window) || !links.length) return;
  var byId = {}; links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting && byId[e.target.id]) { links.forEach(function (a) { a.classList.remove("on"); }); byId[e.target.id].classList.add("on"); }
    });
  }, { rootMargin: "-45% 0px -50% 0px" });
  Object.keys(byId).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
})();
</script>
</body>""")
open(out, "w").write(s)
print("written", len(s))
