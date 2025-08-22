# coding:utf-8
import flet
from flet import Page, Theme
from flet.core.safe_area import SafeArea
from flet.core.theme import DatePickerTheme
from flet.core.types import VisualDensity, MainAxisAlignment, CrossAxisAlignment, ThemeMode, PagePlatform, ScrollMode, \
    Locale

from login_view import LoginControl
from main_view import MainView
from api_request import APIRequest


def main(page: Page):
    # 页面属性
    page.title = '布尔日记'
    page.window.icon = '/icons/app_icon.png'
    page.adaptive = True
    page.scroll = ScrollMode.ADAPTIVE
    # page.padding=padding.only(bottom=28)
    # page.margin=margin.all(0)
    # page.padding=padding.only(left=0, right=0, top=10, bottom=10),
    page.platform=PagePlatform.ANDROID
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.theme_mode = ThemeMode.SYSTEM
    page.theme = Theme(
        color_scheme_seed="blue",
        font_family='微软雅黑',
        date_picker_theme=DatePickerTheme(locale=Locale('zh', 'CN')),
        visual_density=VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
        use_material3=False)
    page.dark_theme = Theme(
        color_scheme_seed="green",
        font_family='微软雅黑',
        date_picker_theme=DatePickerTheme(locale=Locale('zh', 'CN')),
        visual_density=VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
        use_material3=False)

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
                    # maintain_bottom_view_padding=True,
                    adaptive=True,
                    expand=True
                )
        page.controls.append(page_view)


    # 初始页面
    token = page.client_storage.get('token')
    if token is not None:
        token = token.strip('"')
        dct_ret = APIRequest.query_user_info(token)
        if dct_ret is not None:
            switch_page('main_view')
        else:
            switch_page('login_view')
    else:
        switch_page('login_view')

    page.window.center()


flet.app(
    target=main,
    assets_dir='../assets',
    view=flet.AppView.FLET_APP)
