"""Draw the ec01 thumbnail (1280x720) with the channel engine's palette: python ec01/thumbnail.py"""
import base64, pathlib, sys
sys.path.insert(0, "youtube/pipeline")
from playwright.sync_api import sync_playwright
import render
ep = pathlib.Path(__file__).resolve().parent
JS = r"""() => {
  const c = document.createElement('canvas'); c.width = 1280; c.height = 720; const x = c.getContext('2d');
  x.fillStyle = C.bg; x.fillRect(0, 0, 1280, 720); x.fillStyle = C.grid; for (let i = 0; i < 1280; i += 32) x.fillRect(i, 0, 1, 720); for (let j = 0; j < 720; j += 32) x.fillRect(0, j, 1280, 1);
  // ground rising to the right, the flood wedge behind a runner
  x.fillStyle = C.land; x.beginPath(); x.moveTo(0, 720); x.lineTo(0, 600); x.lineTo(1280, 470); x.lineTo(1280, 720); x.fill();
  x.fillStyle = C.sea; x.beginPath(); x.moveTo(0, 720); x.lineTo(0, 330); x.bezierCurveTo(260, 300, 470, 380, 600, 548); x.lineTo(0, 610); x.fill();
  x.strokeStyle = '#fbf8f1'; x.lineWidth = 8; x.beginPath(); x.moveTo(0, 330); x.bezierCurveTo(260, 300, 470, 380, 600, 548); x.stroke();
  ctx = x; figure(760, 520, C.ember, 3.2);
  x.fillStyle = C.ink; x.font = '900 110px Lato'; x.textAlign = 'right'; x.fillText('OUTRUN A', 1240, 140); x.fillStyle = C.ember; x.fillText('TSUNAMI?', 1240, 250);
  x.fillStyle = C.ink; x.font = '900 46px Lato'; x.fillText('30 km/h on land', 1240, 330);
  return c.toDataURL('image/png').split(',')[1]; }"""
with sync_playwright() as pw:
    b, p = render.open_page(pw, render.write_page(ep))
    out = ep / "publish" / "thumbnail.png"; out.write_bytes(base64.b64decode(p.evaluate(JS))); b.close()
print("wrote", out)
