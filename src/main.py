# coding:utf-8
import flet
import httpx
from flet import Page, Theme
from flet.core.colors import Colors
from flet.core.safe_area import SafeArea
from flet.core.theme import DatePickerTheme, SystemOverlayStyle
from flet.core.types import VisualDensity, MainAxisAlignment, CrossAxisAlignment, ThemeMode, PagePlatform, ScrollMode, \
    Locale, Brightness

from login_view import LoginControl
from main_view import MainView


def main(page: Page):
    # 页面属性
    page.title = '布尔日记'
    page.window.icon = '/icons/app_icon.png'
    page.adaptive = True
    page.scroll = ScrollMode.ADAPTIVE
    page.platform=PagePlatform.ANDROID
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.theme_mode = ThemeMode.SYSTEM
    page.theme = Theme(
        color_scheme_seed="blue",
        font_family='微软雅黑',
        date_picker_theme=DatePickerTheme(locale=Locale('zh', 'CN')),
        visual_density=VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
        use_material3=True,
        system_overlay_style=SystemOverlayStyle(
            status_bar_color=Colors.BLACK,  # 状态栏背景设为黑色
            status_bar_brightness=Brightness.DARK,  # 适用于 iOS（整个状态栏亮模式）
            status_bar_icon_brightness=Brightness.LIGHT,
        ),
    )
    page.dark_theme = Theme(
        color_scheme_seed="green",
        font_family='微软雅黑',
        date_picker_theme=DatePickerTheme(locale=Locale('zh', 'CN')),
        visual_density=VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
        use_material3=True
    )

    def switch_page(page_flag:str):
        page.controls.clear()
        match page_flag:
            case 'login_view':
                page_view = SafeArea(
                    LoginControl(page),
                    maintain_bottom_view_padding=True,
                    adaptive=True,
                    expand=True
                )
            case _:
                page_view = SafeArea(
                    MainView(page),
                    maintain_bottom_view_padding=True,
                    adaptive=True,
                    expand=True
                )
        page.controls.append(page_view)


    # 初始页面
    token = page.client_storage.get('token')
    if token is not None:
        token = token.strip('"')
        url = 'https://restapi.10qu.com.cn/user_info/'
        headers = {'Authorization': f'Bearer {token}'}
        try:
            resp = httpx.get(url, headers=headers)
            if resp.status_code != 200:
                switch_page('login_view')
            json_req = resp.json()
            dct_ret = json_req.get('results')
            if dct_ret is not None:
                switch_page('main_view')
            else:
                switch_page('login_view')
        except httpx.HTTPError as e:
            switch_page('login_view')
    else:
        switch_page('login_view')

    page.window.center()


flet.app(
    target=main,
    assets_dir='../assets',
    view=flet.AppView.FLET_APP)
