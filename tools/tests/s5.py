from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=b.new_page(viewport={"width":420,"height":860})
    errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto("file:///mnt/user-data/outputs/grimoire-of-vibe.html"); pg.wait_for_timeout(1000)
    pg.click("text=Kick off the engagement"); pg.wait_for_timeout(1500)
    pg.click("button:has-text(\"Vault\")"); pg.wait_for_timeout(2500); pg.screenshot(path="v1.png")
    pg.click("#vnote .wl >> nth=1"); pg.wait_for_timeout(1500); pg.screenshot(path="v2.png")
    print("ERRS:",errs); b.close()
