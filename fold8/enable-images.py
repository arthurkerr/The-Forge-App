#!/usr/bin/env python3
"""Ajoute les visuels complémentaires Fold8 sans toucher aux données utilisateur."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
html = root / "www/index.html"
s = html.read_text(encoding="utf-8")

# 11 photos compatibles avec les IDs de la bibliothèque v23.
# Coordonnées dans l'atlas (3 colonnes, 4 lignes).
tiles = {
    18: (1, 0), 21: (2, 0),
    60: (0, 1), 63: (1, 1), 64: (2, 1),
    70: (0, 2), 72: (1, 2), 75: (2, 2),
    48: (0, 3), 42: (1, 3), 34: (2, 3)
}

js = """
/* Illustrations complémentaires Fold8. Les images utilisateur restent prioritaires. */
var FOLD8_ART_MAP = %s;
function fold8ArtTile(id) {
  var pos = FOLD8_ART_MAP[id];
  if (!pos) return '';
  var x = (pos[0] * 50) + '%%';
  var y = (pos[1] * (100 / 3)).toFixed(4) + '%%';
  return '<span class="f8-photo" aria-hidden="true" style="--f8-x:'+x+';--f8-y:'+y+'"></span>';
}
""" % json.dumps(tiles, ensure_ascii=False, separators=(",", ":"))

def replace_once(a, b):
    global s
    found = s.count(a)
    if found != 1:
        raise RuntimeError(f"Expected 1 match, found {found}: {a[:90]}")
    s = s.replace(a, b, 1)

replace_once("window.EXO_ART = EXO_ART;", "window.EXO_ART = EXO_ART;\n" + js)

replace_once(
    """    var art = artFor(x.id);
    return '<button class="exo-card'+(art ? ' illus' : '')+'" data-id="'+x.id+'">' +
      '<span class="rail" style="background:'+cat.hex+'"></span>' +
      (art ? '<span class="card-art"><img src="'+art+'" alt="" loading="lazy"></span>' : '') +""",
    """    var art = artFor(x.id);
    var f8tile = art ? '' : fold8ArtTile(x.id);
    return '<button class="exo-card'+((art || f8tile) ? ' illus' : '')+'" data-id="'+x.id+'">' +
      '<span class="rail" style="background:'+cat.hex+'"></span>' +
      (art ? '<span class="card-art"><img src="'+art+'" alt="" loading="lazy" decoding="async"></span>' : (f8tile ? '<span class="card-art">'+f8tile+'</span>' : '')) +"""
)

replace_once(
    """  var art = artFor(x.id);
  $("#sheet-content").innerHTML =
    (art ? '<div class="exo-hero"><img src="'+art+'" alt="" loading="lazy">' +
           '<span class="eh-cat" style="color:'+cat.hex+';border-color:'+cat.hex+'55">'+cat.label+'</span></div>' : '') +
    (art ? '' : '<div class="sheet-cat" style="color:'+cat.hex+'">'+cat.label+'</div>') +
    '<h2'+(art ? ' style="margin-top:12px"' : '')+'>'+esc(x.n)+'</h2>' +""",
    """  var art = artFor(x.id);
  var f8tile = art ? '' : fold8ArtTile(x.id);
  var hasArt = !!(art || f8tile);
  $("#sheet-content").innerHTML =
    (hasArt ? '<div class="exo-hero">'+(art ? '<img src="'+art+'" alt="" loading="lazy" decoding="async">' : f8tile) +
           '<span class="eh-cat" style="color:'+cat.hex+';border-color:'+cat.hex+'55">'+cat.label+'</span></div>' : '') +
    (hasArt ? '' : '<div class="sheet-cat" style="color:'+cat.hex+'">'+cat.label+'</div>') +
    '<h2'+(hasArt ? ' style="margin-top:12px"' : '')+'>'+esc(x.n)+'</h2>' +"""
)

extra_css = """
/* Atelier d'images : atlas léger, embarqué et accessible hors ligne. */
.card-art .f8-photo,.exo-hero .f8-photo{
  position:absolute;display:block;inset:0;width:100%;height:100%;
  background-image:url("./images/forge-exercises-atlas.webp");
  background-size:300% 400%;
  background-position:var(--f8-x) var(--f8-y);
  background-repeat:no-repeat;
}
.exo-hero .f8-photo{background-color:#171225}
.exo-card.illus .f8-photo{pointer-events:none}
@media (max-width:600px){
  .exo-card.illus .card-art .f8-photo{filter:brightness(.92) saturate(.95)}
}
"""
replace_once("</style>", extra_css + "\n</style>")
assert "forge-v1" in s, "Storage version unexpectedly changed"
assert s.count("function fold8ArtTile") == 1
assert s.count("class=\"exo-card") >= 1
assert (root / "www/images/forge-exercises-atlas.webp").is_file(), "Missing image atlas"
html.write_text(s, encoding="utf-8")
print("Image integration successful: 11 exercise illustrations; storage unchanged.")
