"""Draw the ec02 thumbnail (1280x720) with the channel engine's palette: python ec02/thumbnail.py"""
import base64, pathlib, sys
sys.path.insert(0, "youtube/pipeline")
from playwright.sync_api import sync_playwright
import render
ep = pathlib.Path(__file__).resolve().parent
JS = r"""() => {
  const c = document.createElement('canvas'); c.width = 1280; c.height = 720; const x = c.getContext('2d');
  x.fillStyle = C.bg; x.fillRect(0, 0, 1280, 720);
  // the real tracks, scaled into the thumbnail; the equator in red
  const sx = 1280 / W, sy = 720 / H; x.save(); x.scale(sx, sy); x.translate(0, 60); x.drawImage(tracksUpTo(EP.data.tracks.length), 0, 0); x.restore();
  x.fillStyle = 'rgba(243,237,226,0.55)'; x.fillRect(0, 0, 1280, 720);
  const ye = (MAP.y0 + ((MAP.latT - 0) / (MAP.latT - MAP.latB)) * MAP.h + 60) * sy; x.fillStyle = C.ember; x.fillRect(0, ye - 7, 1280, 14);
  x.fillStyle = C.ink; x.font = '900 120px Lato'; x.textAlign = 'center'; x.fillText('NONE CROSSED', 640, ye - 50);
  x.fillStyle = C.ember; x.font = '900 64px Lato'; x.fillText('8,457 storms on record', 640, ye + 100);
  return c.toDataURL('image/png').split(',')[1]; }"""
with sync_playwright() as pw:
    b, p = render.open_page(pw, render.write_page(ep))
    out = ep / "publish" / "thumbnail.png"; out.write_bytes(base64.b64decode(p.evaluate(JS))); b.close()
print("wrote", out)
