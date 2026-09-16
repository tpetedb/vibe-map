from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=b.new_page(viewport={"width":420,"height":860})
    errs=[]; pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto("file:///mnt/user-data/outputs/grimoire-of-vibe.html")
    pg.evaluate("localStorage.setItem('grimoire3',JSON.stringify({name:'Lotte',done:[1,2,3,4],rolls:[],versions:[],bridges:{},date:null,wine:null,world:'campus',creature:{name:'Gilded Sphinx',str:1,wis:2,cha:3,cloak:false,hue:10}}))")
    pg.reload(); pg.wait_for_timeout(800); pg.click("text=Resume in-flight workstream"); pg.wait_for_timeout(2500); pg.screenshot(path="w_campus.png",clip={"x":0,"y":0,"width":420,"height":640})
    for w in ["winter","desert","prod"]:
        pg.evaluate(f"setWorld('{w}')"); pg.wait_for_timeout(2500); pg.screenshot(path=f"w_{w}.png",clip={"x":0,"y":0,"width":420,"height":640})
    pg.evaluate("wantJump=true"); pg.wait_for_timeout(300)
    print("ERRS:",errs); b.close()
