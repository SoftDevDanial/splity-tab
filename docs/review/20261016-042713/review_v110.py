"""Stakeholder review drive of Danial's Splity Tab v1.1.0, for sdlc:review (stakeholder reviewer, agent).

usage, from the project root:   python -B docs/review/20261016-042713/review_v110.py <chromium|webkit> <out dir>
The out dir is relative to the project root and must exist. The script serves the project root itself
(python -m http.server on a free 127.0.0.1 port), stops that server by PID when it ends and checks that the port
then refuses a connection. Headless only. Every context loads the project's clipboard recorder (or its rejecter)
and the CSP listener before any page, so the system clipboard is never touched. Expected money figures are worked
out here from the brainstorm's rules in whole sen, never read from the app.
Writes results-<engine>.json, run-log-<engine>.txt and <engine>-<size>-<nn>-<slug>.png into the out dir.
"""
import json
import re
import socket
import subprocess
import sys
import time
import traceback
import urllib.parse
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ENGINE = sys.argv[1]
OUT = Path(sys.argv[2])
if ENGINE not in ("chromium", "webkit") or not OUT.is_dir():
    raise SystemExit("usage: review_v110.py <chromium|webkit> <existing out dir>")
ROOT = Path.cwd()
if not (ROOT / "index.html").is_file() or not (ROOT / "docs" / "design").is_dir():
    raise SystemExit("run from the project root")
CLIP = ROOT / "tests" / "browser" / "clipboard"
STORAGE = ROOT / "tests" / "browser" / "storage"
CSP = ROOT / "tests" / "browser" / "csp" / "listener.js"
DESIGN = ROOT / "docs" / "design"

results, log_lines = [], []
net = {"requests": [], "console": [], "pageerrors": [], "csp": [], "screenshots": 0}
CLASS_RE = re.compile("[\u0000-\u001f\u007f-\u009f  ؜‎‏‪-‮⁦-⁩]")


def log(line):
    print(line, flush=True)
    log_lines.append(line)


def check(group, name, ok, seen):
    results.append({"engine": ENGINE, "group": group, "check": name, "result": "PASS" if ok else "FAIL", "seen": seen})
    log(f"{'PASS' if ok else 'FAIL'} {ENGINE} | {group} | {name} | {str(seen)[:220]}")
    return ok


def info(group, name, seen):
    results.append({"engine": ENGINE, "group": group, "check": name, "result": "INFO", "seen": seen})
    log(f"INFO {ENGINE} | {group} | {name} | {str(seen)[:220]}")


# --- the brainstorm's rules, in whole sen (brainstorm "Rules the build must follow" and the v1.1.0 delta) -----------
def half_up(num, den):
    return (2 * num + den) // (2 * den)


def charges(sub, svc_bp=1000, sst_bp=600):
    service = half_up(sub * svc_bp, 10000)
    sst = half_up((sub + service) * sst_bp, 10000)
    return service, sst, sub + service + sst


def even(total, n, rule="top", one=None):
    base, left = divmod(total, n)
    shares = [base] * n
    if rule == "top":
        for i in range(left):
            shares[i] += 1
    elif rule == "one":
        shares[one] += left
    return shares, left


def by_item(items, n, rule="top", one=None):
    """items is a list of (price in sen, [person index]). Returns items, charges, shares, spare count, bill."""
    it, spare = [0] * n, 0
    for price, who in items:
        who = sorted(who)
        base, left = divmod(price, len(who))
        for p in who:
            it[p] += base
        spare += left
        if rule == "top":
            for p in who[:left]:
                it[p] += 1
        elif rule == "one":
            it[one] += left
    sub = sum(price for price, _ in items)
    service, sst, total = charges(sub)
    pool, weight = service + sst, sum(it)
    ch = [pool * it[i] // weight for i in range(n)]
    left = pool - sum(ch)
    spare += left
    if rule == "top":
        for i in [i for i in range(n) if it[i] > 0][:left]:
            ch[i] += 1
    elif rule == "one":
        ch[one] += left
    return it, ch, [it[i] + ch[i] for i in range(n)], spare, (sub, service, sst, total)


def amt(cents):
    return f"{cents // 100:,}.{cents % 100:02d}"


def rm(cents):
    return "RM " + amt(cents)


def summary(names, shares, sub, service, sst, total, svc="10%", sstr="6%"):
    lines = ["Bill split", f"Total {rm(total)} (subtotal {rm(sub)}, service {svc} {rm(service)}, SST {sstr} {rm(sst)})"]
    lines += [f"{n} {rm(s)}" for n, s in zip(names, shares)]
    return "\n".join(lines + [f"Adds up to {rm(total)}"])


K1_ITEMS = [("Nasi lemak ayam", "15.90", ["Aisyah"]), ("Char kuey teow", "13.50", ["Ben"]),
            ("Mee goreng mamak", "12.00", ["Chen"]), ("Satay, 10 sticks", "18.00", ["Aisyah", "Chen"])]
NAMES = ["Aisyah", "Ben", "Chen"]


def k1_cents(extra=()):
    rows = [(int(p.replace(".", "")), [NAMES.index(w) for w in who]) for _, p, who in K1_ITEMS]
    return rows + list(extra)


def expect_item_rows(names, it, ch, shares):
    return [[n, rm(s), f"Items {amt(i)} + charges {amt(c)}"] for n, i, c, s in zip(names, it, ch, shares)]


# --- server -------------------------------------------------------------------------------------------------------
def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def port_refuses(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return False
    except OSError:
        return True


def start_server():
    port = free_port()
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=str(ROOT),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 10
    while time.time() < deadline:
        if not port_refuses(port):
            return proc, port
        time.sleep(0.2)
    proc.kill()
    raise RuntimeError("the server did not answer within 10 s")


# --- page readers -------------------------------------------------------------------------------------------------
RECEIPT_JS = r"""(root) => {
  const r = document.querySelector(root);
  if (!r) return null;
  const t = (e) => (e ? e.textContent.replace(/\s+/g, ' ').trim() : null);
  const q = (s) => r.querySelector(s);
  const chip = q('.r-spare-acts button[aria-haspopup]');
  const copy = q('.r-copy');
  return {
    total: t(q('.r-total .r-amount')), label: t(q('.r-total .r-label')), empty: t(q('.r-empty p')), msg: t(q('.r-msg p')),
    lines: [...r.querySelectorAll('dl.r-lines > div')].map((d) => [t(d.querySelector('dt')), t(d.querySelector('dd'))]),
    splits: [...r.querySelectorAll('ul.r-splits > li')].map((li) => [t(li.querySelector('.nm')), t(li.querySelector('.amt')), t(li.querySelector('.wk'))]),
    proof: t(q('.r-check .amt')), proofWk: t(q('.r-check .wk')), spare: t(q('.r-spare p')),
    chip: chip ? chip.getAttribute('aria-label') : null, chipText: t(chip),
    pickAgain: !!q('.r-spare-acts button:not([aria-haspopup])'),
    copy: copy ? (copy.disabled ? 'disabled' : 'enabled') : null, status: t(q('p.status')),
    statusClass: q('p.status') ? q('p.status').className : null,
  };
}"""
STRIP_JS = r"""() => {
  const t = (e) => (e ? e.textContent.replace(/\s+/g, ' ').trim() : null);
  const strip = document.querySelector('#strip');
  return { shown: getComputedStyle(strip).display !== 'none',
    total: document.querySelector('#stripTotal') ? t(document.querySelector('#stripInfo .s-label')) + ' ' + t(document.querySelector('#stripTotal')) : null,
    msg: t(document.querySelector('#stripMsg')), copy: document.querySelector('#stripCopy').disabled ? 'disabled' : 'enabled',
    status: t(document.querySelector('#stripStatus')), statusClass: document.querySelector('#stripStatus').className,
    splitsExpanded: document.querySelector('#splitsBtn').getAttribute('aria-expanded') };
}"""
STATE_JS = r"""() => {
  const v = (s) => { const e = document.querySelector(s); return e ? e.value : null; };
  const raw = (() => { try { return localStorage.getItem('split.draft'); } catch (e) { return 'THROWS'; } })();
  return {
    people: [...document.querySelectorAll('#peopleList li.person input')].map((i) => i.value),
    removeDisabled: [...document.querySelectorAll('#peopleList li.person button')].map((b) => b.disabled),
    addPersonDisabled: document.querySelector('#addPerson') ? document.querySelector('#addPerson').disabled : null,
    even: document.querySelector('#modeEven').checked, item: document.querySelector('#modeItem').checked,
    evenSub: v('#evenSub'), evenErrShown: document.querySelector('#evenErr') ? !document.querySelector('#evenErr').hidden : null,
    svc: v('#svc'), sst: v('#sst'),
    peopleOpen: document.querySelector('#peopleBlk').dataset.open, chargesOpen: document.querySelector('#chargesBlk').dataset.open,
    peopleSum: document.querySelector('#peopleSum .sec-txt') ? document.querySelector('#peopleSum .sec-txt').textContent : null,
    chargesSum: document.querySelector('#chargesSum') ? document.querySelector('#chargesSum').textContent.trim() : null,
    chargesBad: document.querySelector('#chargesBtn').classList.contains('is-bad'),
    items: [...document.querySelectorAll('#itemList li.item')].map((li) => {
      const ins = li.querySelectorAll('.item-row input');
      return [ins[0].value, ins[1].value, [...li.querySelectorAll('button.tap')].filter((b) => b.getAttribute('aria-pressed') === 'true').map((b) => b.textContent.trim()), li.classList.contains('needs')];
    }),
    notes: [...document.querySelectorAll('#notes .note')].map((n) => [n.className, n.textContent.trim(), !!n.querySelector('button')]),
    draft: raw, storageLength: (() => { try { return localStorage.length; } catch (e) { return 'THROWS'; } })(),
  };
}"""
FOCUS_JS = r"""() => {
  const a = document.activeElement;
  if (!a || a === document.body) return 'body';
  if (a.id) return '#' + a.id;
  const l = a.getAttribute('aria-label');
  if (l) return l;
  if (a.classList.contains('sheet')) return 'div.sheet';
  if (a.matches('input[type=radio]')) return 'radio ' + a.name + '=' + a.value;
  return a.tagName.toLowerCase() + ':' + a.textContent.trim().slice(0, 30);
}"""
P1_JS = r"""() => {
  const d = document.querySelector('#spareDlg');
  const t = (e) => (e ? e.textContent.replace(/\s+/g, ' ').trim() : null);
  return { open: d.open, title: t(d.querySelector('#spareTitle')), sub: t(d.querySelector('#spareSub')),
    choices: [...d.querySelectorAll('label.choice')].map((l) => [t(l), l.querySelector('input').checked]),
    pills: [...d.querySelectorAll('#pickList label.pill')].map((l) => [t(l), l.querySelector('input').checked]),
    pickAgain: !!d.querySelector('#pickAgainSheet'), box: d.open ? d.getBoundingClientRect().toJSON() : null };
}"""
OVERFLOW_JS = r"""() => {
  const out = [...document.querySelectorAll('.r-amount, .amt, .r-lines dd, .s-fig, .wk')]
    .filter((e) => e.getClientRects().length && e.scrollWidth > e.clientWidth)
    .map((e) => [e.className, e.textContent.trim(), e.scrollWidth, e.clientWidth]);
  return { page: [document.documentElement.scrollWidth, window.innerWidth], clipped: out };
}"""


def settle(page):
    try:
        page.wait_for_function("() => document.getAnimations().every((a) => a.playState !== 'running')", timeout=4000)
    except Exception:
        pass


def diff_px(a, b):
    A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if A.size != B.size:
        return f"sizes differ {A.size} {B.size}"
    return ImageChops.difference(A, B).convert("L").point(lambda v: 255 if v else 0).histogram()[255]


class Ctx:
    """One browser context at one size. Touch contexts tap, desktop contexts click, both type with the keyboard."""

    def __init__(self, browser, base, size, touch, tag, clip="recorder.js", extra=(), scheme="dark"):
        self.browser, self.base, self.touch, self.tag = browser, base, touch, tag
        self.size = f"{size[0]}x{size[1]}"
        self.phone = size[0] < 1024
        self.ctx = browser.new_context(viewport={"width": size[0], "height": size[1]}, has_touch=touch,
                                       color_scheme=scheme, locale="en-GB")
        self.ctx.add_init_script(path=str(CLIP / clip))
        self.ctx.add_init_script(path=str(CSP))
        for script in extra:
            self.ctx.add_init_script(path=str(script))
        self.ctx.set_default_timeout(5000)
        self.last_tap, self.n = None, 0
        self.page = self.new_page()

    def new_page(self):
        page = self.ctx.new_page()
        page.on("request", lambda r: net["requests"].append([r.method, r.url]))
        page.on("console", lambda m: net["console"].append([self.tag, self.size, m.type, m.text]) if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: net["pageerrors"].append([self.tag, self.size, str(e)]))
        return page

    def harvest(self):
        try:
            v = self.page.evaluate("() => window.testCspViolations || []")
            net["csp"] += [[self.tag, self.size, x] for x in v]
        except Exception:
            pass

    def goto(self, path="/"):
        self.page.goto(self.base + path)
        self.page.wait_for_selector("#rbody > *", state="attached")

    def reload(self):
        self.harvest()
        self.page.reload()
        self.page.wait_for_selector("#rbody > *", state="attached")

    def press(self, locator):
        """A tap on a touch context at a person's pace (never within 600 ms and 30 px of the last), else a click."""
        if self.touch:
            locator.scroll_into_view_if_needed()
            box = locator.bounding_box()
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            if self.last_tap and abs(x - self.last_tap[0]) <= 30 and abs(y - self.last_tap[1]) <= 30:
                wait = 0.6 - (time.time() - self.last_tap[2])
                if wait > 0:
                    self.page.wait_for_timeout(int(wait * 1000))
            locator.tap()
            self.last_tap = (x, y, time.time())
        else:
            locator.click()

    def double(self, locator):
        """A quick double tap (two taps at one point) or a mouse double click."""
        if self.touch:
            locator.scroll_into_view_if_needed()
            box = locator.bounding_box()
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            self.page.touchscreen.tap(x, y)
            self.page.touchscreen.tap(x, y)
            self.last_tap = (x, y, time.time())
        else:
            locator.dblclick()

    def tap_point(self, x, y):
        if self.touch:
            self.page.touchscreen.tap(x, y)
            self.last_tap = (x, y, time.time())
        else:
            self.page.mouse.click(x, y)

    def type_into(self, locator, text):
        self.press(locator)
        self.page.keyboard.press("ControlOrMeta+A")
        if text:
            self.page.keyboard.type(text)
        else:
            self.page.keyboard.press("Backspace")

    def shot(self, slug, page=None, full=False, clip=None):
        page = page or self.page
        settle(page)
        self.n += 1
        name = f"{ENGINE}-{self.size}-{self.tag}{self.n:02d}-{slug}.png"
        kwargs = {"path": str(OUT / name), "full_page": full}
        if clip:
            kwargs["clip"] = clip
        page.screenshot(**kwargs)
        net["screenshots"] += 1
        return OUT / name

    def focus(self):
        return self.page.evaluate(FOCUS_JS)

    def state(self):
        return self.page.evaluate(STATE_JS)

    def receipt(self, root="#rbody"):
        return self.page.evaluate(RECEIPT_JS, root)

    def strip(self):
        return self.page.evaluate(STRIP_JS)

    def wait(self, js, ms=2000):
        try:
            self.page.wait_for_function(js, timeout=ms)
            return True
        except Exception:
            return False

    # Receipt the user sees: the card from 1024 px, the Splits sheet below (opened and closed here).
    def seen_receipt(self, keep_open=False):
        if not self.phone:
            return self.receipt("#rbody")
        opened = False
        if not self.page.evaluate("() => document.querySelector('#splitsDlg').open"):
            self.press(self.page.locator("#splitsBtn"))
            self.wait("() => document.querySelector('#splitsDlg').open")
            opened = True
        r = self.receipt("#splitsDlg .rbody")
        if opened and not keep_open:
            self.close_sheet()
        return r

    def close_sheet(self):
        self.press(self.page.locator("#splitsDlg .sheet-top button[aria-label=Close]"))
        self.wait("() => !document.querySelector('#splitsDlg').open")

    def copy(self, where="auto"):
        before = self.page.evaluate("() => window.testClipboardWrites")
        if where == "auto":
            where = "#stripCopy" if self.phone else "#copyBtn"
        self.press(self.page.locator(where))
        self.wait(f"() => (window.testClipboardWrites || 0) > {before or 0} || !!document.querySelector('p.status.is-fail:not(:empty)')")
        self.page.wait_for_timeout(100)
        return self.page.evaluate("() => [window.testClipboardWrites, window.testClipboardText]")

    def open_p1(self):
        if self.phone:
            if not self.page.evaluate("() => document.querySelector('#splitsDlg').open"):
                self.press(self.page.locator("#splitsBtn"))
                self.wait("() => document.querySelector('#splitsDlg').open")
            self.press(self.page.locator("#splitsDlg .r-spare-acts button[aria-haspopup]"))
        else:
            self.press(self.page.locator("#spareBtn"))
        self.wait("() => document.querySelector('#spareDlg').open")
        return self.page.evaluate(P1_JS)

    def choose(self, label):
        self.press(self.page.locator("#spareDlg label.choice", has_text=label))
        self.page.wait_for_timeout(150)

    def pill(self, name):
        self.press(self.page.locator("#pickList label.pill", has_text=name))
        self.page.wait_for_timeout(150)

    def close_p1(self, how="Close"):
        if how == "Escape":
            self.page.keyboard.press("Escape")
        else:
            self.press(self.page.locator("#spareDlg button[aria-label=Close]"))
        return self.wait("() => !document.querySelector('#spareDlg').open")

    def toggle(self, item, person):
        self.press(self.page.get_by_role("group", name=f"Who had {item}", exact=True).get_by_role("button", name=person, exact=True))

    def add_item(self, name, price, who=()):
        self.press(self.page.locator("#addItem"))
        if name:
            self.page.keyboard.type(name)
        self.page.keyboard.press("Tab")
        self.page.keyboard.type(price)
        for p in who:
            self.toggle(name or f"Item {self.page.locator('#itemList li.item').count()}", p)

    def open_section(self, key, want=True):
        if not self.phone:
            return
        btn = self.page.locator(f"#{key}Btn")
        if (btn.get_attribute("aria-expanded") == "true") != want:
            self.press(btn)
            self.page.wait_for_timeout(300)

    def close(self):
        self.harvest()
        self.ctx.close()


def golden_mark_path():
    html = (DESIGN / "bill-items.html").read_text(encoding="utf-8")
    m = re.search(r'<svg class="mark"[^>]*>\s*<path[^>]*\bd="([^"]+)"', html)
    return m.group(1) if m else None


def golden_icon_bytes():
    html = (DESIGN / "bill-items.html").read_text(encoding="utf-8")
    href = re.search(r'<link rel="icon"[^>]*href="([^"]+)"', html).group(1)
    return urllib.parse.unquote(href.split(",", 1)[1]).encode("utf-8")


def compare_golden(c, golden, slug, app_png):
    gp = c.ctx.new_page()
    gp.goto(c.base + "/docs/design/" + golden)
    settle(gp)
    gp.wait_for_timeout(300)
    path = OUT / f"{ENGINE}-{c.size}-{c.tag}{c.n:02d}-{slug}-golden.png"
    gp.screenshot(path=str(path))
    gp.close()
    d = diff_px(app_png, path)
    info(f"look {c.size}", f"pixels differing between the app and {golden} at this state (same engine, eye check in the captures)", d)
    return d


# --- the drive ----------------------------------------------------------------------------------------------------
def build_k1(c, G):
    """Rename to Aisyah and Ben, add Chen, switch to By item and enter the four K1 items with taps."""
    p = c.page
    c.open_section("people", True)
    c.type_into(p.get_by_label("Person 1 name", exact=True), "Aisyah")
    c.type_into(p.get_by_label("Person 2 name", exact=True), "Ben")
    if p.locator("#peopleList li.person").count() < 3:
        c.press(p.locator("#addPerson"))
        p.keyboard.type("Chen")
    c.press(p.locator("label[for=modeItem]"))
    for name, price, who in K1_ITEMS:
        c.add_item(name, price, who)


def main_flow(browser, base, size, touch):
    c = Ctx(browser, base, size, touch, "m")
    p, phone = c.page, size[0] < 1024
    G = f"main {c.size}"
    c.goto()
    sw = p.evaluate(r"""() => ({ writes: window.testClipboardWrites,
      nativeWrite: typeof Clipboard === 'function' ? /\[native code\]/.test(Clipboard.prototype.writeText.toString()) : 'no Clipboard',
      csp: Array.isArray(window.testCspViolations) })""")
    check(G, "clipboard stand-in and CSP listener in place before the first gesture", sw["writes"] == 0 and sw["nativeWrite"] is not True and sw["csp"], sw)

    # Name and logo (S6, S8, brainstorm v1.1.0 Name)
    head = p.evaluate(r"""() => ({ title: document.title, word: document.querySelector('header .brand h1.word').textContent,
      mark: document.querySelector('header .brand svg.mark path').getAttribute('d'),
      icon: [document.querySelector('link[rel=icon]').getAttribute('href'), document.querySelector('link[rel=icon]').type],
      named: [...document.querySelectorAll('body *')].filter((e) => !e.children.length && /Splity|Danial/.test(e.textContent)).map((e) => e.textContent.trim()) })""")
    check(G, "tab title is the full name", head["title"] == "Danial's Splity Tab", head["title"])
    check(G, "header shows the mark then 'Splity Tab' only, no Danial and no D", head["word"] == "Splity Tab" and not any("Danial" in t for t in head["named"]), [head["word"], head["named"]])
    check(G, "header mark path equals the golden's S12 mark", head["mark"] == golden_mark_path(), head["mark"][:40])
    check(G, "tab icon links src/icon.svg as SVG", head["icon"] == ["src/icon.svg", "image/svg+xml"], head["icon"])

    # Cold boot (R2): a new bill, never a seed
    s = c.state()
    r = c.receipt()
    st = c.strip()
    ok = (s["people"] == ["Person 1", "Person 2"] and s["removeDisabled"] == [True, True] and s["even"] and s["evenSub"] == ""
          and not s["evenErrShown"] and s["svc"] == "10" and s["sst"] == "6" and s["draft"] is None and s["storageLength"] == 0
          and r["label"] == "Total" and r["empty"] == "Enter the subtotal to see the splits." and not r["splits"])
    check(G, "cold boot is the empty new bill, nothing stored", ok, [s["people"], s["removeDisabled"], s["evenSub"], s["svc"], s["sst"], s["draft"], r["empty"]])
    if phone:
        check(G, "phone, People open and Charges folded on a new bill", [s["peopleOpen"], s["chargesOpen"]] == ["true", "false"], [s["peopleOpen"], s["chargesOpen"]])
        check(G, "phone, the strip shows the message with Copy summary disabled", st["shown"] and st["msg"] == "Enter the subtotal to see the splits." and st["copy"] == "disabled", st)
    else:
        check(G, "desktop, no strip", not st["shown"], st)
    p.wait_for_timeout(2500)
    app_png = c.shot("cold-boot")
    compare_golden(c, "bill-empty.html", "cold-boot", app_png)

    # Even split (flow 1)
    c.type_into(p.get_by_label("Person 1 name", exact=True), "Aisyah")
    c.type_into(p.get_by_label("Person 2 name", exact=True), "Ben")
    c.press(p.locator("#addPerson"))
    check(G, "Add person puts focus on the new empty name", c.focus() == "Person 3 name" and p.get_by_label("Person 3 name", exact=True).input_value() == "", c.focus())
    p.keyboard.type("Chen")
    c.type_into(p.locator("#evenSub"), "100")
    service, sst, total = charges(10000)
    shares, left = even(total, 3)
    want_lines = [["Subtotal", "RM 100.00"], ["Service 10%", rm(service)], ["SST 6%", rm(sst)]]
    if phone:
        check(G, "strip Total", c.strip()["total"] == "Total " + rm(total), c.strip())
    r = c.seen_receipt(keep_open=phone)
    check(G, "even, Total and bill lines", r["total"] == rm(total) and r["lines"] == want_lines, [r["total"], r["lines"]])
    check(G, "even, splits to the sen, top of the list", [x[:2] for x in r["splits"]] == [[n, rm(v)] for n, v in zip(NAMES, shares)], r["splits"])
    check(G, "even, 'Adds up to' and the spare sen line with Top of the list", r["proof"] == rm(total) and r["spare"] == f"{left} sen left over" and r["chip"] == "Spare sen: Top of the list. Change", [r["proof"], r["spare"], r["chip"]])
    if phone:
        info(G, "after Splits is pressed: the sheet matches :focus-visible, its outline style", p.evaluate("() => [document.activeElement.matches(':focus-visible'), getComputedStyle(document.activeElement).outlineStyle]"))
        check(G, "Splits sheet open, focus on the sheet, aria-expanded true",c.focus() == "div.sheet" and c.strip()["splitsExpanded"] == "true", [c.focus(), c.strip()["splitsExpanded"]])
        c.shot("even-splits-sheet")
        c.close_sheet()
        check(G, "sheet Close gives focus back to Splits", c.focus() == "#splitsBtn", c.focus())
    else:
        c.shot("even-split")
    writes, text = c.copy()
    want = summary(NAMES, shares, 10000, service, sst, total)
    check(G, "Copy summary gives the brainstorm's own example text", text == want and want.splitlines()[1] == "Total RM 116.60 (subtotal RM 100.00, service 10% RM 10.00, SST 6% RM 6.60)", text)
    status = c.strip() if phone else c.receipt()
    check(G, "status says 'Summary copied'", status["status"] == "Summary copied" and status["statusClass"] == "status", [status["status"], status["statusClass"]])
    d = json.loads(c.state()["draft"])
    check(G, "draft saved as version 2 with the bill", d["version"] == 2 and [x["name"] for x in d["bill"]["people"]] == NAMES and d["bill"]["subtotalText"] == "100" and d["bill"]["spare"] == {"rule": "top"}, d)

    # Amount rules (brainstorm: up to 2 decimals, above 0, at most 99,999.99)
    for text_in, valid in [("100,00", False), ("12", True), ("12.5", True), ("12.50", True), ("0", False), ("99999.99", True), ("100000", False), ("1.234", False)]:
        c.type_into(p.locator("#evenSub"), text_in)
        p.keyboard.press("Tab")
        p.wait_for_timeout(100)
        e = p.evaluate("() => [!document.querySelector('#evenErr').hidden, document.querySelector('#evenErr').textContent.trim(), document.querySelector('#evenSub').getAttribute('aria-invalid'), document.querySelector('#evenField').classList.contains('is-bad')]")
        check(G, f"subtotal '{text_in}' {'accepted' if valid else 'shows the error on leaving'}", (e[0] is (not valid)) and (valid or (e[1] == "Enter an amount like 12.50" and e[2] == "true" and e[3])), e)
        if text_in == "100,00":
            rr = c.receipt()
            check(G, "a bad subtotal blocks the receipt", rr["empty"] == "Enter the subtotal to see the splits.", rr["empty"])
            c.shot("amount-error")
    c.type_into(p.locator("#evenSub"), "100")
    p.keyboard.press("Tab")

    # Spare sen (C9): One person, its picker, At random, Pick again, Top of the list
    P = c.open_p1()
    info(G, "after P1 opens by a press: the checked radio matches :focus-visible (a ring drawn on open)", p.evaluate("() => document.activeElement.matches(':focus-visible')"))
    check(G, "P1 opens with title, count and three choices, Top of the list checked",P["title"] == "Spare sen" and P["sub"] == "2 sen left over" and P["choices"] == [["Top of the list", True], ["One person", False], ["At random", False]], P)
    check(G, "P1 focus on the checked choice", c.focus() == "radio spareRule=top", c.focus())
    if not phone:
        settle(p)  # P1 rises over 200 ms (system.md), so its place is read once the rise is over
        card = p.locator("#card").bounding_box()
        chip = p.locator("#spareBtn").bounding_box()
        box = p.evaluate(P1_JS)["box"]
        check(G, "desktop P1 sits 16 px right of the card, bottom level with the chip", abs(box["left"] - (card["x"] + card["width"] + 16)) < 1 and abs(box["bottom"] - (chip["y"] + chip["height"])) < 1, [box["left"], box["bottom"], card["x"] + card["width"], chip["y"] + chip["height"]])
    c.choose("One person")
    P = p.evaluate(P1_JS)
    one0, _ = even(total, 3, "one", 0)
    rr = c.receipt("#splitsDlg .rbody" if phone else "#rbody")
    check(G, "One person picks the first person at once", P["pills"] == [["Aisyah", True], ["Ben", False], ["Chen", False]] and [x[1] for x in rr["splits"]] == [rm(v) for v in one0], [P["pills"], rr["splits"]])
    c.pill("Ben")
    one1, _ = even(total, 3, "one", 1)
    rr = c.receipt("#splitsDlg .rbody" if phone else "#rbody")
    check(G, "Ben pays both spare sen (38.86, 38.88, 38.86)", [x[1] for x in rr["splits"]] == [rm(v) for v in one1] and rr["chip"] == "Spare sen: One person, Ben. Change", [rr["splits"], rr["chip"]])
    p.evaluate("() => document.activeElement && document.activeElement.blur()")
    app_png = c.shot("p1-one-person-ben")
    compare_golden(c, "spare-sen-one.html", "p1-one-person-ben", app_png)
    closed = c.close_p1("Escape")
    interim = c.focus()
    chip_sel = "#splitsDlg .r-spare-acts button[aria-haspopup]" if phone else "#spareBtn"
    landed = c.wait(f"() => document.activeElement === document.querySelector('{chip_sel}')")
    check(G, "Escape closes P1 and focus goes back to the chip (read after the close event, bounded 2 s)", closed and landed, [closed, landed, c.focus()])
    info(G, "focus read as soon as P1 reports closed after Escape (the interim focus of R59 (2))", interim)
    writes, text = c.copy("#splitsDlg .r-copy" if phone else "#copyBtn")
    check(G, "copied summary follows the choice", text == summary(NAMES, one1, 10000, service, sst, total), text.splitlines()[2:5] if text else text)
    c.open_p1()
    c.choose("At random")
    P = p.evaluate(P1_JS)
    rr = c.receipt("#splitsDlg .rbody" if phone else "#rbody")
    drawn = [x[1] for x in rr["splits"]]
    cents = [int(x.replace("RM ", "").replace(",", "").replace(".", "")) for x in drawn]
    check(G, "At random gives two different people one spare sen each, still adds up", P["pickAgain"] and sorted(cents) == [3886, 3887, 3887] and sum(cents) == total and rr["chip"] == "Spare sen: At random. Change" and rr["pickAgain"], [drawn, P["pickAgain"], rr["chip"]])
    tabs = 0
    while c.focus() != "#pickAgainSheet" and tabs < 5:
        p.keyboard.press("Tab")
        tabs += 1
    p.keyboard.press("Enter")
    p.wait_for_timeout(150)
    rr = c.receipt("#splitsDlg .rbody" if phone else "#rbody")
    again = [x[1] for x in rr["splits"]]
    check(G, "Pick again in P1 (Tab to it, Enter) draws a different split", again != drawn and sum(int(x.replace("RM ", "").replace(".", "")) for x in again) == total, [drawn, again, tabs])
    check(G, "focus stays on Pick again after a key press on it", c.focus() == "#pickAgainSheet", c.focus())
    c.shot("p1-at-random")
    c.close_p1("Close")
    receipt_pick = p.locator("#splitsDlg .r-spare-acts button:not([aria-haspopup])" if phone else "#pickAgain")
    c.press(receipt_pick)
    p.wait_for_timeout(150)
    rr = c.receipt("#splitsDlg .rbody" if phone else "#rbody")
    third = [x[1] for x in rr["splits"]]
    check(G, "Pick again on the receipt draws again", third != again, [again, third])
    if phone:
        c.close_sheet()
    c.reload()
    rr = c.seen_receipt()
    check(G, "the drawn order is kept, a reload shows the same splits", [x[1] for x in rr["splits"]] == third and rr["chip"] == "Spare sen: At random. Change", [rr["splits"], third])
    c.open_p1()
    c.choose("Top of the list")
    rr = c.receipt("#splitsDlg .rbody" if phone else "#rbody")
    check(G, "back to Top of the list gives the 1.0 split", [x[1] for x in rr["splits"]] == [rm(v) for v in shares], rr["splits"])
    if phone:
        c.tap_point(195, 40)
    else:
        p.mouse.click(1250, 20)
    closed = c.wait("() => !document.querySelector('#spareDlg').open")
    f = c.focus()
    check(G, "a click on P1's backdrop closes it, focus on the chip", closed and f == ("Spare sen: Top of the list. Change" if phone else "#spareBtn"), [closed, f])
    if phone and p.evaluate("() => document.querySelector('#splitsDlg').open"):
        c.close_sheet()

    # By item (flow 2)
    c.press(p.locator("label[for=modeItem]"))
    s = c.state()
    rr = c.receipt()
    check(G, "By item, Subtotal block gone, no item yet blocks with its message", s["item"] and p.locator("#evenBlock").count() == 0 and p.locator("#itemsBlock").count() == 1 and rr["empty"] == "Add each item and tap who had it to see the splits.", [s["item"], rr["empty"]])
    c.add_item("Nasi lemak ayam", "15.90")
    msg1 = c.strip()["msg"] if phone else c.receipt()["msg"]
    s = c.state()
    check(G, "an item with nobody tapped blocks: '1 item still needs a person...' and the amber marker", msg1 == "1 item still needs a person. Tap who had it to see the splits." and [x[3] for x in s["items"]] == [True], [msg1, s["items"]])
    c.press(p.locator("#addItem"))
    msg_d = c.strip()["msg"] if phone else c.receipt()["empty"]
    check(G, "a new item with no price: 'Give every item a price to see the splits.'", msg_d == "Give every item a price to see the splits.", msg_d)
    p.keyboard.type("Char kuey teow")
    p.keyboard.press("Tab")
    p.keyboard.type("13.50")
    msg2 = c.strip()["msg"] if phone else c.receipt()["msg"]
    check(G, "two untapped items: '2 items still need a person...'", msg2 == "2 items still need a person. Tap who had each one to see the splits.", msg2)
    c.toggle("Nasi lemak ayam", "Aisyah")
    c.toggle("Char kuey teow", "Ben")
    for name, price, who in K1_ITEMS[2:]:
        c.add_item(name, price, who)
    it, ch, sh, spare, (sub, svc_v, sst_v, tot) = by_item(k1_cents(), 3)
    if phone:
        check(G, "strip Total RM 69.26", c.strip()["total"] == "Total " + rm(tot), c.strip()["total"])
    rr = c.seen_receipt()
    check(G, "K1 Total and bill lines", rr["total"] == rm(tot) and rr["lines"] == [["Subtotal", rm(sub)], ["Service 10%", rm(svc_v)], ["SST 6%", rm(sst_v)]], [rr["total"], rr["lines"]])
    check(G, "K1 splits with items + charges working (satay shared, charges in proportion)", rr["splits"] == expect_item_rows(NAMES, it, ch, sh), rr["splits"])
    check(G, "K1 proof and '1 sen left over'", rr["proof"] == rm(tot) and rr["proofWk"] == f"{amt(sub)} + {amt(svc_v + sst_v)}" and rr["spare"] == f"{spare} sen left over", [rr["proof"], rr["proofWk"], rr["spare"]])
    writes, text = c.copy()
    check(G, "K1 copied summary in the 1.0 format", text == summary(NAMES, sh, sub, svc_v, sst_v, tot), text)
    c.press(p.locator("label[for=modeEven]"))
    rr = c.seen_receipt()
    check(G, "switch to Even keeps the subtotal and its splits", p.locator("#evenSub").input_value() == "100" and rr["total"] == rm(total), [p.locator("#evenSub").input_value(), rr["total"]])
    c.press(p.locator("label[for=modeItem]"))
    s = c.state()
    check(G, "switch back keeps every item and tap", [x[:3] for x in s["items"]] == [[n, pr, w] for n, pr, w in K1_ITEMS], s["items"])
    # the look, K1 as the golden draws it (sections folded on a phone, nothing focused)
    c.open_section("people", False)
    p.evaluate("() => document.activeElement && document.activeElement.blur()")
    p.wait_for_timeout(300)
    app_png = c.shot("k1")
    compare_golden(c, "bill-items.html", "k1", app_png)
    if phone:
        s = c.state()
        check(G, "folded People summary 'Aisyah, Ben, Chen', Charges 'Service 10%, SST 6%'", s["peopleSum"] == "Aisyah, Ben, Chen" and s["chargesSum"] == "Service 10%, SST 6%", [s["peopleSum"], s["chargesSum"]])
        p.locator("#chargesBtn").focus()
        p.keyboard.press("Enter")
        p.wait_for_timeout(300)
        opened = [c.state()["chargesOpen"], p.locator("#chargesBtn").get_attribute("aria-expanded")]
        p.keyboard.press("Space")
        p.wait_for_timeout(300)
        folded = [c.state()["chargesOpen"], p.locator("#chargesBtn").get_attribute("aria-expanded")]
        check(G, "a header row opens with Enter and folds with Space", opened == ["true", "true"] and folded == ["false", "false"], [opened, folded])
        p.evaluate("() => document.activeElement && document.activeElement.blur()")
    else:
        lay = p.evaluate(r"""() => ({ scroll: [document.documentElement.scrollHeight, innerHeight], card: document.querySelector('#card').getBoundingClientRect().toJSON(),
          rows: [...document.querySelectorAll('.sec-h')].map((h) => getComputedStyle(h).display), bodies: [...document.querySelectorAll('.sec-body')].map((b) => getComputedStyle(b).display),
          frame: [document.querySelector('#frameWrap').hasAttribute('data-up'), document.querySelector('#frameWrap').hasAttribute('data-down')] })""")
        check(G, "desktop 1280 x 800, the page does not scroll", lay["scroll"][0] <= lay["scroll"][1], lay["scroll"])
        check(G, "desktop card at 98, 84, 460 x 642, header rows hidden, both bodies shown", [round(lay["card"][k]) for k in ("x", "y", "width", "height")] == [98, 84, 460, 642] and set(lay["rows"]) == {"none"} and "none" not in lay["bodies"], lay)
        check(G, "desktop item frame scrolls inside itself (data-down, no data-up)", lay["frame"] == [False, True], lay["frame"])

    # One person in By item: only people on an item can be chosen
    c.open_section("people", True)
    c.press(p.locator("#addPerson"))
    p.keyboard.type("Dan")
    rr = c.seen_receipt()
    check(G, "a person on no item is listed with RM 0.00", rr["splits"][3] == ["Dan", "RM 0.00", "Items 0.00 + charges 0.00"], rr["splits"][3] if len(rr["splits"]) > 3 else rr["splits"])
    P = c.open_p1()
    c.choose("One person")
    P = p.evaluate(P1_JS)
    check(G, "the picker lists only people on an item (no Dan)", [x[0] for x in P["pills"]] == NAMES, P["pills"])
    c.pill("Ben")
    it1, ch1, sh1, _, _ = by_item(k1_cents(), 4, "one", 1)
    rr = c.receipt("#splitsDlg .rbody" if phone else "#rbody")
    check(G, "By item, Ben takes the spare sen (15.75, Aisyah 29.03)", rr["splits"] == expect_item_rows(NAMES + ["Dan"], it1, ch1, sh1), rr["splits"])
    c.choose("Top of the list")
    c.close_p1("Close")
    if phone:
        c.close_sheet()
    c.press(p.get_by_role("button", name="Remove Dan", exact=True))
    check(G, "removing the last person puts focus on the name before it", c.focus() == "Person 3 name" and c.state()["people"] == NAMES, c.focus())

    # Charges (C4): rate errors, 0 turns a charge off, the folded Check marker
    c.open_section("charges", True)
    c.type_into(p.locator("#svc"), "35")
    p.keyboard.press("Tab")
    e = p.evaluate("() => [!document.querySelector('#svcErr').hidden, document.querySelector('#svcErr').textContent.trim(), document.querySelector('#svc').getAttribute('aria-invalid')]")
    blocked = c.strip()["msg"] if phone else c.receipt()["empty"]
    check(G, "service 35 shows 'Enter a rate from 0 to 30' and blocks the receipt", e[:2] == [True, "Enter a rate from 0 to 30"] and e[2] == "true" and blocked == "Check the charges to see the splits.", [e, blocked])
    if phone:
        check(G, "strip Copy summary disabled while blocked", c.strip()["copy"] == "disabled", c.strip()["copy"])
        c.open_section("charges", False)
        s = c.state()
        check(G, "folded Charges says 'Check service charge' with the marker", s["chargesSum"] == "Check service charge" and s["chargesBad"], [s["chargesSum"], s["chargesBad"]])
        c.shot("rate-error-folded")
        c.open_section("charges", True)
    else:
        c.shot("rate-error")
    c.type_into(p.locator("#svc"), "0")
    p.keyboard.press("Tab")
    s0, t0, tot0 = charges(5940, 0, 600)
    rr = c.seen_receipt()
    check(G, "service 0 turns it off (Service 0% RM 0.00)", rr["lines"][1] == ["Service 0%", "RM 0.00"] and rr["total"] == rm(tot0), [rr["lines"], rr["total"]])
    c.type_into(p.locator("#sst"), "25")
    p.keyboard.press("Tab")
    e = p.evaluate("() => [!document.querySelector('#sstErr').hidden, document.querySelector('#sstErr').textContent.trim()]")
    check(G, "SST 25 shows 'Enter a rate from 0 to 20'", e == [True, "Enter a rate from 0 to 20"], e)
    check(G, "Charges summary 'Check SST'", c.state()["chargesSum"] == "Check SST", c.state()["chargesSum"])
    c.type_into(p.locator("#svc"), "")
    p.keyboard.press("Tab")
    s = c.state()
    check(G, "a blank rate shows no inline error but blocks, summary 'Check both rates'", p.locator("#svcErr").is_hidden() and s["chargesSum"] == "Check both rates", s["chargesSum"])
    c.type_into(p.locator("#svc"), "10")
    c.type_into(p.locator("#sst"), "6")
    p.keyboard.press("Tab")
    hint = p.locator("#chargeHint").text_content().strip()
    check(G, "the hint reads 'Set a charge to 0 if your bill already includes it.'", hint == "Set a charge to 0 if your bill already includes it.", hint)
    c.open_section("charges", False)
    price = p.get_by_label("Nasi lemak ayam price in RM", exact=True)
    c.type_into(price, "15,90")
    p.keyboard.press("Tab")
    e = p.evaluate("() => [!document.querySelector('#ie1').hidden, document.querySelector('#ie1').textContent.trim()]")
    blocked = c.strip()["msg"] if phone else c.receipt()["empty"]
    check(G, "a bad price shows 'Enter an amount like 12.50' and 'Give every item a price to see the splits.'", e == [True, "Enter an amount like 12.50"] and blocked == "Give every item a price to see the splits.", [e, blocked])
    c.shot("price-error")
    c.type_into(price, "15.90")
    p.keyboard.press("Tab")

    # Come back later (flow 3)
    before = c.state()
    c.reload()
    after = c.state()
    rr = c.seen_receipt()
    check(G, "reload shows the bill as it was", after["people"] == NAMES and after["item"] and [x[:3] for x in after["items"]] == [[n, pr, w] for n, pr, w in K1_ITEMS] and after["svc"] == "10" and after["sst"] == "6" and rr["splits"] == expect_item_rows(NAMES, it, ch, sh), [after["people"], after["items"]])
    check(G, "nothing is written at boot", after["draft"] == before["draft"], after["draft"] == before["draft"])
    if phone:
        check(G, "phone, a saved bill opens with People and Charges folded", [after["peopleOpen"], after["chargesOpen"]] == ["false", "false"], [after["peopleOpen"], after["chargesOpen"]])
    c.harvest()
    c.page.close()
    c.page = p = c.new_page()
    c.goto()
    again_state = c.state()
    check(G, "a closed tab opened again shows the same bill", again_state["people"] == NAMES and [x[:3] for x in again_state["items"]] == [[n, pr, w] for n, pr, w in K1_ITEMS], again_state["items"])

    # Tab order (R32)
    stops = []
    p.evaluate("() => document.activeElement && document.activeElement.blur()")
    for _ in range(45):
        p.keyboard.press("Tab")
        f = c.focus()
        if stops and f == stops[0]:
            break
        if f != "body":
            stops.append(f)
    if phone:
        check(G, "phone K1 Tab order, 31 stops from New bill to Copy summary", len(stops) == 31 and stops[0] == "#newBill" and stops[1] == "#peopleBtn" and stops[2] == "#chargesBtn" and stops[-2:] == ["#splitsBtn", "#stripCopy"], [len(stops), stops[:5], stops[-2:]])
    else:
        check(G, "desktop K1 Tab order starts New bill, chip, Copy summary, Add person", stops[:4] == ["#newBill", "#spareBtn", "#copyBtn", "#addPerson"], stops[:6])
    ring = p.evaluate("() => { const w = document.activeElement; const cs = getComputedStyle(w); return [cs.outlineStyle, cs.outlineWidth, cs.outlineOffset]; }")
    info(G, "outline on the last Tab stop (ring is drawn by the system's focus rule)", [stops[-1] if stops else None, ring])
    p.evaluate("() => document.activeElement && document.activeElement.blur()")

    # The strip and the Splits sheet (phone)
    if phone:
        c.press(p.locator("#splitsBtn"))
        c.wait("() => document.querySelector('#splitsDlg').open")
        app_png = c.shot("splits-sheet-k1")
        compare_golden(c, "splits-sheet.html", "splits-sheet-k1", app_png)
        c.close_sheet()
        fv = p.evaluate("() => [document.activeElement.id, document.querySelector('#splitsBtn').matches(':focus-visible')]")
        info(G, "after the sheet closes by a tap on Close: focus and :focus-visible on Splits (QA-S5-4)", fv)
        c.shot("after-sheet-close-strip", clip={"x": 0, "y": size[1] - 160, "width": size[0], "height": 160})
        c.press(p.locator("#splitsBtn"))
        c.wait("() => document.querySelector('#splitsDlg').open")
        was_open = p.evaluate("() => [document.querySelector('#splitsDlg').open, document.activeElement.className]")
        p.keyboard.press("Escape")
        closed = c.wait("() => !document.querySelector('#splitsDlg').open")
        interim = c.strip()["splitsExpanded"]
        focused = c.wait("() => document.activeElement.id === 'splitsBtn'")
        collapsed = c.wait("() => document.querySelector('#splitsBtn').getAttribute('aria-expanded') === 'false'")
        check(G, "Escape closes the sheet, focus on Splits, aria-expanded false (read after the close event, bounded 2 s)", closed and focused and collapsed, [was_open, closed, focused, collapsed, c.focus()])
        info(G, "aria-expanded on Splits read as soon as the sheet reports closed after Escape (before its close event)", interim)
        c.press(p.locator("#splitsBtn"))
        c.wait("() => document.querySelector('#splitsDlg').open")
        p.wait_for_timeout(400)
        c.tap_point(size[0] / 2, 30)
        ok = c.wait("() => !document.querySelector('#splitsDlg').open")
        check(G, "a tap on the sheet's backdrop closes it, focus on Splits", ok and c.focus() == "#splitsBtn", c.focus())
        writes0 = p.evaluate("() => window.testClipboardWrites")
        p.wait_for_timeout(700)
        c.double(p.locator("#splitsBtn"))
        p.wait_for_timeout(400)
        res = p.evaluate("() => [document.querySelector('#splitsDlg').open, window.testClipboardWrites]")
        check(G, "a double tap on Splits opens the sheet once and the second tap reaches nothing under it", res == [True, writes0], [res, writes0])
        c.close_sheet()

    # New bill (flow 4)
    draft_k1 = c.state()["draft"]
    c.press(p.locator("#newBill"))
    c.wait("() => document.querySelector('#newDlg').open")
    dlg = p.evaluate("() => [document.querySelector('#newTitle').textContent, document.querySelector('#newBody').textContent, [...document.querySelectorAll('#newDlg .acts button')].map((b) => b.textContent.trim())]")
    info(G, "after New bill is pressed: Cancel matches :focus-visible (a ring drawn on open)", p.evaluate("() => document.activeElement.matches(':focus-visible')"))
    check(G, "New bill asks 'Start a new bill? This clears the people, items and amounts.' with focus on Cancel",dlg == ["Start a new bill?", "This clears the people, items and amounts.", ["Start new bill", "Cancel"]] and c.focus() == "button:Cancel", [dlg, c.focus()])
    app_png = c.shot("new-bill-dialog")
    compare_golden(c, "new-bill-dialog.html", "new-bill-dialog", app_png)
    c.press(p.locator("#newDlg .acts button", has_text="Cancel"))
    ok = c.wait("() => !document.querySelector('#newDlg').open") and c.wait("() => document.activeElement.id === 'newBill'")
    check(G, "Cancel changes nothing, focus on New bill", ok and c.state()["draft"] == draft_k1, c.focus())
    c.press(p.locator("#newBill"))
    c.wait("() => document.querySelector('#newDlg').open")
    c.press(p.locator("#startNew"))
    ok = c.wait("() => !document.querySelector('#newDlg').open") and c.wait("() => document.activeElement.id === 'newBill'")
    s = c.state()
    d = json.loads(s["draft"])
    fresh = {"mode": "even", "people": [{"id": "p1", "name": "Person 1"}, {"id": "p2", "name": "Person 2"}], "subtotalText": "", "items": [],
             "serviceText": "10", "sstText": "6", "spare": {"rule": "top"}, "nextId": 3}
    check(G, "Start new bill returns to two people, even, 10% and 6%, Top of the list, focus New bill", ok and s["people"] == ["Person 1", "Person 2"] and s["even"] and s["evenSub"] == "" and d == {"version": 2, "bill": fresh}, [s["people"], d])
    if phone:
        check(G, "phone, after Start new bill People open and Charges folded", [s["peopleOpen"], s["chargesOpen"]] == ["true", "false"], [s["peopleOpen"], s["chargesOpen"]])
    c.shot("after-new-bill")

    # People rules (C1): double press adds one, 12 is the limit, 2 the floor, removal takes a person off every item
    c.double(p.locator("#addPerson"))
    p.wait_for_timeout(300)
    n = p.locator("#peopleList li.person").count()
    check(G, "a double press on Add person adds one person (R57 (b) for a tap)", n == 3 and c.focus() == "Person 3 name", [n, c.focus()])
    for _ in range(12):
        if p.locator("#addPerson").is_disabled():
            break
        c.press(p.locator("#addPerson"))
    s = c.state()
    check(G, "12 people, Add person disabled", len(s["people"]) == 12 and s["addPersonDisabled"], [len(s["people"]), s["addPersonDisabled"]])
    if phone:
        c.open_section("people", False)
        info(G, "folded People summary at 12 blank names", c.state()["peopleSum"])
        c.shot("twelve-folded")
        c.open_section("people", True)
    else:
        c.shot("twelve")
    while p.locator("#peopleList li.person").count() > 3:
        c.press(p.locator("#peopleList li.person button.icon-btn").last)
    c.type_into(p.get_by_label("Person 3 name", exact=True), "Chen")
    c.type_into(p.get_by_label("Person 1 name", exact=True), "Ben")
    c.type_into(p.get_by_label("Person 2 name", exact=True), "Ben")
    check(G, "duplicate names are allowed, two 'Remove Ben' buttons", p.get_by_role("button", name="Remove Ben", exact=True).count() == 2, p.get_by_role("button", name="Remove Ben", exact=True).count())
    c.type_into(p.get_by_label("Person 2 name", exact=True), "")
    check(G, "a blank name shows its placeholder 'Person 2'", p.get_by_label("Person 2 name", exact=True).get_attribute("placeholder") == "Person 2" and p.get_by_role("button", name="Remove Person 2", exact=True).count() == 1, p.get_by_label("Person 2 name", exact=True).get_attribute("placeholder"))
    c.press(p.locator("label[for=modeItem]"))
    c.add_item("Tea", "3", ["Chen"])
    c.press(p.get_by_role("button", name="Remove Chen", exact=True))
    s = c.state()
    msg = c.strip()["msg"] if phone else c.receipt()["msg"]
    check(G, "removing a person takes them off every item", s["items"] == [["Tea", "3", [], True]] and msg == "1 item still needs a person. Tap who had it to see the splits.", [s["items"], msg])
    check(G, "Remove disabled at two people", s["removeDisabled"] == [True, True], s["removeDisabled"])

    # Held Enter on the only item's Remove (S3, SEC-04)
    c.press(p.get_by_label("Item 1 name", exact=True))
    p.keyboard.press("Tab")
    p.keyboard.press("Tab")
    f0 = c.focus()
    next_before = json.loads(c.state()["draft"])["bill"]["nextId"]
    p.keyboard.down("Enter")
    p.wait_for_timeout(520)
    for _ in range(4):
        p.keyboard.down("Enter")
        p.wait_for_timeout(35)
    p.keyboard.up("Enter")
    p.wait_for_timeout(200)
    d = json.loads(c.state()["draft"])["bill"]
    check(G, "held Enter on the only item's Remove removes it and adds no blank item", f0 == "Remove Tea" and p.locator("#itemList li.item").count() == 0 and d["items"] == [] and d["nextId"] == next_before and c.focus() == "#addItem", [f0, p.locator("#itemList li.item").count(), d["nextId"], next_before, c.focus()])

    # Names stay plain (H-10)
    c.press(p.get_by_label("Person 1 name", exact=True))
    p.keyboard.press("ControlOrMeta+A")
    p.keyboard.insert_text("Ben‮")
    c.press(p.get_by_label("Person 2 name", exact=True))
    p.keyboard.press("ControlOrMeta+A")
    p.keyboard.insert_text("Ai syah")
    c.add_item("", "4.50")
    p.keyboard.press("Shift+Tab")
    p.keyboard.insert_text("Teh‮tarik")
    c.toggle("Tehtarik", "Ben")
    c.toggle("Tehtarik", "Aisyah")
    s = c.state()
    d = json.loads(s["draft"])["bill"]
    vals = [s["people"][0], s["people"][1], s["items"][0][0]]
    check(G, "pasted bidi and line separator characters are removed from names (field, draft)", vals == ["Ben", "Aisyah", "Tehtarik"] and [x["name"] for x in d["people"]] == ["Ben", "Aisyah"] and d["items"][0]["name"] == "Tehtarik", [ascii(v) for v in vals])
    check(G, "People summary holds no control, separator or bidi character", s["peopleSum"] is not None and not CLASS_RE.search(s["peopleSum"]) and s["peopleSum"].startswith("Ben, Aisyah"), ascii(s["peopleSum"]))
    _, _, shn, _, (sub_n, svc_n, sst_n, tot_n) = by_item([(450, [0, 1])], 2)
    writes, text = c.copy()
    check(G, "the copied summary reads the same plain names", text == summary(["Ben", "Aisyah"], shn, sub_n, svc_n, sst_n, tot_n), ascii(text))
    c.close()


def big_bill_flow(browser, base, size, touch):
    c = Ctx(browser, base, size, touch, "w")
    p = c.page
    G = f"big bill {c.size}"
    c.goto()
    build_k1(c, G)
    c.add_item("", "964.50", ["Aisyah"])
    it, ch, sh, spare, (sub, svc_v, sst_v, tot) = by_item(k1_cents([(96450, [0])]), 3)
    o = p.evaluate(OVERFLOW_JS)
    st = c.strip()
    priceq = p.evaluate("() => { const i = document.querySelector('[aria-label=\"Item 5 price in RM\"]'); return [i.value, i.scrollWidth, i.clientWidth]; }")
    check(G, "W1 at 360: no sideways scroll, 964.50 whole in its field, strip 'Total RM 1,193.87'", o["page"][0] <= o["page"][1] and not o["clipped"] and priceq[0] == "964.50" and priceq[1] <= priceq[2] and st["total"] == "Total " + rm(tot), [o, priceq, st["total"]])
    info(G, "W1 frame data-up, data-down", p.evaluate("() => [document.querySelector('#frameWrap').hasAttribute('data-up'), document.querySelector('#frameWrap').hasAttribute('data-down')]"))
    c.open_section("people", False)
    p.evaluate("() => document.activeElement && document.activeElement.blur()")
    box = p.locator("#frameWrap").bounding_box()
    p.mouse.move(box["x"] + box["width"] / 2, box["y"] + 40)
    p.mouse.wheel(0, -4000)
    p.wait_for_timeout(300)
    p.mouse.move(size[0] / 2, 80)
    p.mouse.wheel(0, -4000)
    p.wait_for_timeout(300)
    info(G, "W1 frame data-up, data-down after scrolling the frame back to its top", p.evaluate("() => [document.querySelector('#frameWrap').hasAttribute('data-up'), document.querySelector('#frameWrap').hasAttribute('data-down')]"))
    app_png = c.shot("w1")
    compare_golden(c, "bill-large.html", "w1", app_png)
    c.press(p.locator("#splitsBtn"))
    c.wait("() => document.querySelector('#splitsDlg').open")
    rr = c.receipt("#splitsDlg .rbody")
    o = p.evaluate(OVERFLOW_JS)
    check(G, "W1 sheet splits (Aisyah RM 1,153.65) and every figure fits", rr["splits"] == expect_item_rows(NAMES, it, ch, sh) and rr["total"] == rm(tot) and not o["clipped"], [rr["splits"], o])
    c.shot("w1-sheet")
    c.close_sheet()
    for j in range(1, 6):
        label = K1_ITEMS[j - 1][0] if j <= 4 else "Item 5"
        c.type_into(p.get_by_label(f"{label} price in RM", exact=True), "99999.99")
    p.keyboard.press("Tab")
    items = [(9999999, [NAMES.index(w) for w in who]) for _, _, who in K1_ITEMS] + [(9999999, [0])]
    it, ch, sh, spare, (sub, svc_v, sst_v, tot) = by_item(items, 3)
    o = p.evaluate(OVERFLOW_JS)
    st = c.strip()
    check(G, f"five items at RM 99,999.99 ({rm(tot)}): no sideways scroll, no clipped figure on the page or strip", o["page"][0] <= o["page"][1] and not o["clipped"] and st["total"] == "Total " + rm(tot), [o, st["total"]])
    info(G, "a price field holding 99999.99 at this width: value, scrollWidth, clientWidth (R60 promises 964.50 whole, not this)", p.evaluate("() => { const i = document.querySelector('[aria-label=\"Item 5 price in RM\"]'); return [i.value, i.scrollWidth, i.clientWidth]; }"))
    c.press(p.locator("#splitsBtn"))
    c.wait("() => document.querySelector('#splitsDlg').open")
    rr = c.receipt("#splitsDlg .rbody")
    o = p.evaluate(OVERFLOW_JS)
    check(G, "the same bill in the sheet, splits right and every figure fits", rr["splits"] == expect_item_rows(NAMES, it, ch, sh) and not o["clipped"], [rr["splits"], o["clipped"]])
    c.shot("max-sheet")
    c.close_sheet()
    c.close()


def save_warning_flow(browser, base, size, touch):
    G = f"save warning {size[0]}x{size[1]}"
    warn = "This bill is not being saved on this device. It will be lost when you close this tab."
    c = Ctx(browser, base, size, touch, "s", extra=[STORAGE / "fail-set.js"])
    p = c.page
    c.goto()
    check(G, "storage that reads but cannot write: no warning at boot", c.state()["notes"] == [], c.state()["notes"])
    c.type_into(p.get_by_label("Person 1 name", exact=True), "Aisyah")
    s = c.state()
    check(G, "the first failed save shows the warning, exact copy, no dismiss control", s["notes"] == [["note is-warn", warn, False]] and s["draft"] is None, s["notes"])
    c.type_into(p.locator("#evenSub"), "100")
    total = charges(10000)[2]
    rr = c.seen_receipt()
    check(G, "the app keeps working in memory", [x[1] for x in rr["splits"]] == [rm(v) for v in even(total, 2)[0]], rr["splits"])
    c.shot("save-warning")
    p.evaluate("() => window.dispatchEvent(new CustomEvent('test:storage', { detail: false }))")
    c.type_into(p.get_by_label("Person 2 name", exact=True), "Ben")
    s = c.state()
    d = json.loads(s["draft"]) if s["draft"] else None
    check(G, "the warning goes after the next save works, and the store holds the bill on screen", s["notes"] == [] and d and [x["name"] for x in d["bill"]["people"]] == ["Aisyah", "Ben"] and d["bill"]["subtotalText"] == "100", [s["notes"], d])
    c.close()
    c = Ctx(browser, base, size, touch, "s", extra=[STORAGE / "fail-get.js"])
    p = c.page
    c.goto()
    notes = p.evaluate("() => [...document.querySelectorAll('#notes .note')].map((n) => [n.className, n.textContent.trim()])")
    check(G, "storage refused from boot: the warning in the first render", notes == [["note is-warn", warn]], notes)
    p.evaluate("() => window.dispatchEvent(new CustomEvent('test:storage', { detail: false }))")
    c.type_into(p.get_by_label("Person 1 name", exact=True), "Aisyah")
    check(G, "storage that comes back clears the warning without a reload", c.state()["notes"] == [], c.state()["notes"])
    c.close()


def unreadable_flow(browser, base, size, touch):
    G = f"unreadable {size[0]}x{size[1]}"
    note = "Your saved bill could not be read, so a new one was started."
    c = Ctx(browser, base, size, touch, "u")
    p = c.page
    c.goto()
    p.evaluate("() => localStorage.setItem('split.draft', '{\"version\":2,\"bill\":')")
    c.reload()
    s = c.state()
    check(G, "a draft that cannot be read: the note with Dismiss, a new bill saved", s["notes"] == [["note", note, True]] and json.loads(s["draft"])["bill"]["people"][0]["name"] == "Person 1", s["notes"])
    if c.phone:
        check(G, "phone, People opens (the bill is new)", [s["peopleOpen"], s["chargesOpen"]] == ["true", "false"], [s["peopleOpen"], s["chargesOpen"]])
    c.shot("unreadable-note")
    draft = s["draft"]
    c.double(p.locator("#dismissNote"))
    ok = c.wait("() => document.activeElement.id === 'newBill'")
    p.wait_for_timeout(300)
    s = c.state()
    check(G, "a double press on Dismiss note acts once (A23): note gone, focus New bill, sections as they were", ok and s["notes"] == [] and c.focus() == "#newBill" and (not c.phone or [s["peopleOpen"], s["chargesOpen"]] == ["true", "false"]) and s["draft"] == draft and not p.evaluate("() => document.querySelector('#newDlg').open"), [s["notes"], c.focus(), s["peopleOpen"], s["chargesOpen"]])
    p.evaluate("() => localStorage.setItem('split.draft', 'not json')")
    c.reload()
    p.keyboard.press("Tab")
    f0 = c.focus()
    p.keyboard.down("Enter")
    p.wait_for_timeout(520)
    for _ in range(4):
        p.keyboard.down("Enter")
        p.wait_for_timeout(35)
    p.keyboard.up("Enter")
    p.wait_for_timeout(300)
    s = c.state()
    check(G, "Dismiss note is the first Tab stop, a held Enter on it opens no dialog", f0 == "#dismissNote" and s["notes"] == [] and c.focus() == "#newBill" and not p.evaluate("() => document.querySelector('#newDlg').open"), [f0, s["notes"], c.focus()])
    c.close()


def blocked_clipboard_flow(browser, base, size, touch):
    G = f"blocked clipboard {size[0]}x{size[1]}"
    c = Ctx(browser, base, size, touch, "b", clip="reject.js")
    p = c.page
    c.goto()
    c.type_into(p.locator("#evenSub"), "100")
    c.copy()
    st = c.strip() if c.phone else c.receipt()
    check(G, "a blocked clipboard says 'Could not copy. Your browser blocked the clipboard.'", st["status"] == "Could not copy. Your browser blocked the clipboard." and st["statusClass"] == "status is-fail", [st["status"], st["statusClass"]])
    c.shot("copy-blocked")
    c.type_into(p.locator("#evenSub"), "101")
    st = c.strip() if c.phone else c.receipt()
    check(G, "the next change clears the status", st["status"] == "", st["status"])
    c.close()


def icon_flow(browser, base):
    G = "tab icon"
    on_disk = (ROOT / "src" / "icon.svg").read_bytes()
    check(G, "src/icon.svg equals the golden's tab icon byte for byte", on_disk == golden_icon_bytes(), [len(on_disk), len(golden_icon_bytes())])
    for scheme, want in (("dark", (0xA3, 0xAA, 0xFF)), ("light", (0x1E, 0x21, 0x40))):
        ctx = browser.new_context(viewport={"width": 16, "height": 16}, device_scale_factor=4, color_scheme=scheme)
        page = ctx.new_page()
        page.goto(base + "/src/icon.svg")
        path = OUT / f"{ENGINE}-16x16-tab-icon-{scheme}.png"
        page.screenshot(path=str(path), omit_background=True)
        ctx.close()
        im = Image.open(path).convert("RGBA")
        solid = [px[:3] for px in im.getdata() if px[3] > 240]
        top = max(set(solid), key=solid.count) if solid else None
        check(G, f"the icon draws in {'#%02X%02X%02X' % want} under {scheme}", top == want, [top, len(solid)])


def main():
    proc, port = start_server()
    base = f"http://127.0.0.1:{port}"
    log(f"server STARTED pid {proc.pid} port {port}")
    started = time.time()
    try:
        with sync_playwright() as pw:
            browser = getattr(pw, ENGINE).launch(headless=True)
            log(f"{ENGINE} {browser.version}")
            plans = [(main_flow, (390, 844), True), (big_bill_flow, (360, 780), True), (save_warning_flow, (390, 844), True),
                     (unreadable_flow, (390, 844), True), (blocked_clipboard_flow, (390, 844), True)]
            if ENGINE == "chromium":
                plans = [(main_flow, (1280, 800), False), (unreadable_flow, (1280, 800), False), (blocked_clipboard_flow, (1280, 800), False)] + plans
            for fn, size, touch in plans:
                try:
                    fn(browser, base, size, touch)
                except Exception as e:
                    results.append({"engine": ENGINE, "group": f"{fn.__name__} {size}", "check": "flow ran to its end", "result": "ERROR", "seen": traceback.format_exc()})
                    log(f"ERROR {ENGINE} | {fn.__name__} {size} | {e!r}")
            try:
                icon_flow(browser, base)
            except Exception:
                results.append({"engine": ENGINE, "group": "tab icon", "check": "flow ran", "result": "ERROR", "seen": traceback.format_exc()})
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        refused = port_refuses(port)
        log(f"server STOPPED pid {proc.pid} port {port}, exited {proc.poll() is not None}, port refuses {refused}")
    G = "the whole run"
    allowed = [base + "/", base + "/favicon.ico"]
    odd = [r for r in net["requests"] if r[0] != "GET" or not (r[1] in allowed or r[1].startswith(base + "/src/"))]
    check(G, "every request of the app pages is a same-origin GET for the page, src/ or favicon.ico", not odd, [len(net["requests"]), odd[:5]])
    tool = [x for x in net["console"] if ENGINE == "webkit" and "Refused to apply a stylesheet" in x[3]]
    other = [x for x in net["console"] if x not in tool]
    check(G, "no console error or warning from the app, no page error", not other and not net["pageerrors"], [other[:5], net["pageerrors"][:5]])
    info(G, "WebKit screenshot stylesheet lines (R59 (4), the tool), against screenshots taken", [len(tool), net["screenshots"]])
    csp_app = [x for x in net["csp"] if not (ENGINE == "webkit" and x[2].get("violatedDirective", "").startswith("style-src"))]
    check(G, "no CSP violation from the app", not csp_app, [len(net["csp"]), csp_app[:5]])
    passed = sum(1 for r in results if r["result"] == "PASS")
    failed = [r for r in results if r["result"] in ("FAIL", "ERROR")]
    log(f"TOTAL {ENGINE} pass {passed} fail {len(failed)} info {sum(1 for r in results if r['result'] == 'INFO')} in {time.time() - started:.0f} s")
    (OUT / f"results-{ENGINE}.json").write_text(json.dumps({"engine": ENGINE, "results": results, "requests": len(net["requests"]),
                                                            "console": net["console"], "csp": net["csp"], "screenshots": net["screenshots"]}, indent=1, ensure_ascii=True), encoding="utf-8")
    (OUT / f"run-log-{ENGINE}.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
