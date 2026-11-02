# 一加 15T（PLZ110，ColorOS 17.0.0.107 / Android 17）机型脚本。
# 路径实测：2026-11-02 真机（一加 15T，PLZ110_17.0.0.107(CN01)）。
# 覆盖：广告跟踪、软件商店、浏览器、主题商店、视频、游戏中心、小布建议、负一屏、下拉搜索，共九段。
#
# 与 oneplus-PLR110（ColorOS 17.0.0.101）的差异，均为本机实测：
#   1. 广告跟踪：ColorOS 17 起是「按应用的开关列表」（每行一个 App，开关旁写着「开启/关闭」状态字），
#      不是单个「限制广告跟踪」总开关。入口在 设置 → 隐私与安全 → 设备标识与广告 → 广告跟踪（跳转行）。
#   2. 软件商店：没有「服务管理」了。隐私入口改名「隐私授权管理」（下设「个性化推荐」）；
#      「全部服务」只剩应用管家（应用卸载/我的预约/我的应用），已无营销开关；
#      通知分类在「消息管理」，本机 7 类推送默认全关。
#   3. 主题商店：启动直接落在「我的」页，右上角齿轮没有文字（text 和 content-desc 都空），只能按图标点。
#   4. 视频：com.heytap.yoli 只有本地播放器（LocalVideosListActivity，视频/文件夹两个 tab），
#      没有「我的」和个性化入口。全机也没有别的在线视频 App。
#   5. 小布建议：「内容资讯」入口能点开，但页内没找到可关的开关（核对 0 项），等同无广告可关。
#   6. 负一屏：桌面右滑进速览**不稳定**——同一次实跑里进过一次（能看到「推荐服务」「热点资讯」），
#      之后手动复现连滑多次都停在 launcher。脚本按页面内容判断进没进，进不去就跳过；
#      进去了但「推荐服务」里的轮播选项名与本脚本不符（找不到「不显示轮播推荐」），需人工核对。
#   7. 下拉搜索：桌面下拉打开的是通知栏（SystemUI）而不是全局搜索，脚本打印原因后跳过，不会误点。
#      com.heytap.quicksearchbox 没有 LAUNCHER Activity，SearchSettingActivity 也未导出。
# 用法：python3 tool/run.py -s 序列号 recipe [段名…]   不带段名=全跑
BUILD = "PLZ110_17.0.0.107"

import time

ONLY = globals().get("ONLY") or []


def step(name):
    def deco(f):
        if (not ONLY or name in ONLY) and p.locked():
            print(f"\n== {name}：手机锁屏了，后面的都不跑")
            return f
        if not ONLY or name in ONLY:
            print(f"\n== {name}")
            p.miss = 0
            t = time.time()
            try:
                f()
            except Exception as e:
                print(f"  ✗ 出错：{e}")
            print(f"  ({time.time()-t:.0f} 秒)")
        return f
    return deco


def settings_page(*path):
    p.d.shell("am start -f 0x10008000 -a android.settings.SETTINGS")
    time.sleep(1.2)
    for t in path:
        if not p.tap(t, exact=True):
            return False
    return True


def maybe(name, scrolls=6):
    """可选入口：有就点，没有不报「走丢」。"""
    p.miss = 0
    ok = p.tap(name, exact=True, scrolls=scrolls)
    p.miss = 0
    return ok


@step("广告跟踪")
def _():
    # ColorOS 17 设置首页叫「隐私与安全」（聚合页，隐私/安全两个 tab）
    if not settings_page("隐私与安全", "设备标识与广告"):
        p.miss = 0
        if not settings_page("隐私", "设备标识与广告"):
            return
    if not p.tap("广告跟踪", exact=True):
        print("  ✗ 没找到「广告跟踪」入口")
        return
    # 这页是「按应用」的开关列表：标题是应用名，开关旁的「开启/关闭」是状态字，由 title_of 过滤掉，
    # 不会被 NEG_PREFIX 当成「关闭xx」的保护开关反向拨开。列表很长（本机 165 个应用），要翻到底。
    p.miss = 0
    p.off(page="广告跟踪", max_screens=40)


# 本机没有「服务管理」；「全部服务」只剩应用管家，营销开关已不存在，因此不设 keep 名单
@step("软件商店")
def _():
    p.start("com.heytap.market")
    p.go("我的", "设置")
    p.tap("设置", exact=True, scrolls=0)
    # ColorOS 17：隐私入口改名「隐私授权管理」，「个性化推荐」是跳转行，进去才是开关
    if maybe("隐私授权管理"):
        if p.tap("个性化推荐", exact=True):
            p.off(only=["个性化推荐"], page="商店·隐私授权")
            p.back()
        p.back()
    if maybe("消息管理"):
        # 自更新/下载/安装/更新提醒都是功能通知；本机这 7 类默认全关，这里只兜底关营销类
        p.off(only=["热门内容推送", "精彩推荐", "活动推荐", "福利通知"], page="商店·消息管理")
        p.back()
    p.back(2)


@step("浏览器")
def _():
    p.start("com.heytap.browser")
    # ColorOS 17 首页读不到「我的」/菜单入口，用实测可直达的设置页 Activity；带清栈参数会立刻退出
    p.d.shell("am start -f 0x10008000 -n com.heytap.browser/.settings.component.BrowserPreferencesPage")
    time.sleep(1.2)
    if "com.heytap.browser" not in p.focus():
        print("  ✗ 浏览器设置页没有打开")
        return
    if p.tap("主页设置", exact=True):
        # 本机默认已经是「简洁」，有「页面布局」才需要改
        if p.tap("页面布局", exact=True):
            p.tap("简洁", exact=True, scrolls=0)
            p.back()
        p.back()
    if p.tap("隐私", exact=True):
        if p.tap("广告管理", exact=True):
            # 摇一摇广告随上级开关灰置（开屏/资讯列表都关了就不会展示），不点它
            p.off(only=["开屏广告", "资讯列表广告"], page="浏览器·广告管理")
            p.back()
        if maybe("个性化内容"):
            p.off(only=["个性化推荐", "个性化广告推荐"], page="浏览器·个性化内容")
            p.back()
        p.back()
    if maybe("消息管理"):
        p.off(only=["精彩推荐", "重点时事", "本地资讯", "个性化推荐"], page="浏览器·消息管理")
        p.back()
    p.back(2)


@step("主题商店")
def _():
    p.start("com.heytap.themestore", settle=2.5)
    # 启动直接落在「我的」页；右上角齿轮 text / content-desc 都为空，只能按图标点
    if not p.tap_icon(["服务管理", "隐私"]):
        print("  ✗ 没找到右上角设置齿轮")
        return
    if p.tap("服务管理", exact=True):
        # 「全部服务/基础服务」保持全部服务；锁屏三个开关是功能项
        if maybe("消息与广告"):
            p.off(only=["消息通知", "开屏广告"], page="主题·消息与广告")
            p.back()
        p.back()
    if p.tap("隐私", exact=True):
        p.off(only=["个性化推荐"], page="主题·个性化推荐")
        p.back()
    p.back(2)


@step("视频")
def _():
    # 本机 com.heytap.yoli 只有本地播放器（视频/文件夹），没有在线信息流
    try:
        p.start("com.heytap.yoli", settle=2)
    except Exception as e:
        print(f"  · 视频 App 没起来（{e}），跳过")
        return
    if not p.find("我的", exact=True, edge_ok="tab"):
        print("  · 本机「视频」只有本地播放器，没有「我的」和个性化入口，跳过")
        p.back()
        return
    if not p.go("我的", "设置"):
        print("  ✗ 没找到「我的」标签")
        p.back()
        return
    p.tap("设置", exact=True, scrolls=0)
    if p.tap("个性化管理", exact=True):
        p.off(only=["个性化广告推荐", "个性化内容推荐"], page="视频·个性化管理")
        p.back()
    if p.tap("消息通知", exact=True):
        p.off(only=["热点时事", "精彩推荐", "个性化推荐", "本地新闻"], page="视频·消息通知")
        p.back()
    p.back(2)


@step("游戏中心")
def _():
    p.start("com.nearme.gamecenter", settle=2.5)
    # 首次进来会弹「要允许发送通知吗」和「未成年人模式」「我的页面升级」，统一按拒绝/知道了处理
    p.dismiss()
    if not p.tap("我的", exact=True, scrolls=0):
        raise RuntimeError("没找到底部「我的」")
    time.sleep(1.2)
    p.dismiss()                        # 「我的」页面升级提示
    # 「设置」是右上角图标，content-desc 读作「设置,有新通知」
    if not p.tap("设置", exact=False, scrolls=0) and not p.tap_icon(["隐私开关设置", "隐私"]):
        raise RuntimeError("没找到设置入口")
    if p.tap("隐私开关设置", exact=True) and p.tap("个性化推荐管理", exact=True):
        # 关这个开关会弹「要关闭个性化推荐吗？」，确认按钮叫「继续关闭」，已在 CONFIRM 里
        p.off(only=["个性化推荐"], page="游戏中心·个性化推荐管理")
    p.back(4)


@step("小布建议")
def _():
    if not settings_page("OPPO AI", "小布建议"):
        return
    # 本机点开「小布建议」页看不到启用按钮之外的开关，服务项多为「已卸载」
    if not p.tap("资讯服务", exact=True):
        print("  · 本机小布建议没有「资讯服务」入口，跳过")
        p.back()
        return
    p.off(only=["资讯服务"], page="小布建议·内容资讯")
    p.back(2)


@step("负一屏")
def _():
    # ColorOS 17：速览内嵌在桌面进程里，焦点仍是 launcher，按页面内容判断进没进
    p.d.shell("input keyevent HOME"); time.sleep(0.6); p.d.shell("input keyevent HOME"); time.sleep(0.6)
    entered = False
    for _ in range(3):
        p.d.shell(f"input swipe {p.W//7} {p.H//2} {p.W*6//7} {p.H//2} 250"); time.sleep(1.2)
        if p.find("我的服务") or p.find("添加卡片", exact=True) or "assistantscreen" in p.focus():
            entered = True
            break
    if not entered:
        print("  · 右滑没进速览（负一屏）：本机右滑不稳定，跳过")
        return
    if not p.go("我的", "设置"):
        print("  ✗ 没找到「我的」入口")
        p.back()
        return
    p.tap("设置", exact=True, scrolls=0)
    # ⚠ 「推荐服务」总开关不要关：会删掉天气/步数/清理卡片；只把轮播推荐拨到「不显示」
    if p.tap("推荐服务", exact=True):
        def carousel_off():
            return any("RadioButton" in (n.get("class") or "") and n.get("checked") == "true"
                       and any((c.get("text") or "").strip() == "不显示轮播推荐" for c in n)
                       for n in p.tree().iter("node"))
        sel = False
        for _ in range(3):
            sel = carousel_off()
            if sel:
                break
            time.sleep(0.8)
        if not sel:
            p.tap("不显示轮播推荐", exact=True, scrolls=0)
            time.sleep(0.8)
            if carousel_off():
                p.changed.append(("负一屏·推荐服务", "轮播推荐 → 不显示"))
        p.back()
    if p.tap("热点资讯", exact=True):
        p.off(only=["热点资讯"], page="负一屏·热点资讯")
        p.back()
    p.back(3)


@step("下拉搜索")
def _():
    p.d.shell("input keyevent HOME"); time.sleep(0.6)
    p.d.shell(f"input swipe {p.W//2} {p.H*3//10} {p.W//2} {p.H*7//10} 300"); time.sleep(1.5)
    if "quicksearchbox" not in p.focus():
        # 本机实测：桌面下拉打开的是通知栏（焦点 NotificationShade）；quicksearchbox 没有 LAUNCHER
        # Activity，SearchSettingActivity 也不是导出组件（am start 被拒），没有别的入口能进
        p.d.shell("input keyevent KEYCODE_CLOSE_SYSTEM_DIALOGS"); time.sleep(0.5)
        print(f"  · 下拉打开的是 {p.focus()}，不是全局搜索页，跳过")
        return
    p.tap("收起键盘", exact=True, scrolls=0)
    time.sleep(0.8)
    cands = [((l + r) // 2, (tp + b) // 2) for t, (l, tp, r, b), _ in p.texts()
             if t == "设置" and tp > p.H * 0.8]
    if not cands:
        print("  ✗ 底部没有「设置」")
        p.back()
        return
    before = p.sig()
    p.click(*cands[-1])
    p.settle(before, 1.5)
    if "SearchSetting" not in p.focus():
        print("  ✗ 没进搜索设置")
        return
    if p.tap("搜索范围", exact=True):
        p.off(only=["榜单", "小说", "购物", "个性化推荐", "精选资讯"], page="下拉搜索·搜索范围")
        p.back()
    if p.tap("首页卡片管理", exact=True):
        p.off(only=["未下载应用推荐", "应用建议小卡", "热搜应用", "精选推荐", "热搜榜单", "活动皮肤", "推荐卡片"],
              page="下拉搜索·首页卡片管理")
        p.back()
    if p.tap("功能管理", exact=True):
        p.off(only=["搜索框提示词"], page="下拉搜索·功能管理")
        p.back()
    if p.tap("账号与隐私", exact=True) and p.tap("隐私", exact=True):
        p.off(only=["个性化推荐"], page="下拉搜索·隐私")
        p.back(2)
    p.back(2)
