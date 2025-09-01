"""
main_view.py
"""
# coding:utf-8
from datetime import date

import httpx
from flet import Column, Row, Icons, Colors
from flet.core import border, border_radius, alignment, padding
from flet.core.alert_dialog import AlertDialog
from flet.core.app_bar import AppBar
from flet.core.border import BorderSide, BorderSideStrokeAlign
from flet.core.box import BoxShadow
from flet.core.container import Container
from flet.core.divider import Divider
from flet.core.floating_action_button import FloatingActionButton
from flet.core.icon import Icon
from flet.core.icon_button import IconButton
from flet.core.image import Image
from flet.core.list_tile import ListTile
from flet.core.list_view import ListView
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.progress_bar import ProgressBar
from flet.core.progress_ring import ProgressRing
from flet.core.safe_area import SafeArea
from flet.core.scrollable_control import OnScrollEvent
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.types import MainAxisAlignment, CrossAxisAlignment, ImageFit, FontWeight


class MainView(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.selected_idx = -1
        self.page_idx = 1
        self.loading = False
        self.diary_type_list = None

        self.alignment = MainAxisAlignment.SPACE_BETWEEN,
        self.spacing = 0
        self.tight = True

        self.dlg_about = AlertDialog(
            modal=True,
            title=Text('关于'),
            content=Column(
                controls=[Divider(height=1, color='gray'),
                          Text('布尔日记v0.1.0'),
                          Text('浙江舒博特网络科技有限公司 出品'),
                          Text('官网: http://https://www.zjsbt.cn/service/derivatives'),
                          ],
                alignment=MainAxisAlignment.START,
                width=300,
                height=90,
            ),
            actions=[TextButton("确定", on_click=self.on_about_ok_click), ],
            actions_alignment=MainAxisAlignment.END,
        )

        # 抽屉
        self.page.run_task(self.build_drawer)
        # self.drawer = NavigationDrawer(
        #     position=NavigationDrawerPosition.START,
        #     controls=[
        #         Container(
        #             content=self.build_drawer(),
        #             expand=1,
        #             padding=0,
        #             margin=0,
        #         )
        #     ]
        # )

        # 浮动按钮
        self.page.floating_action_button = FloatingActionButton(
            icon=Icons.ADD,
            bgcolor=Colors.BLUE,
            foreground_color=Colors.WHITE,
            data=0,
            on_click=self.on_fab_pressed,
        )

        self.btn_previous_page = IconButton(
            icon=Icons.ARROW_LEFT,
            on_click=self.on_previous_page,
            disabled=True,
        )
        self.btn_next_page = IconButton(
            icon=Icons.ARROW_RIGHT,
            on_click=self.on_next_page,
            disabled=False,
        )
        self.page.appbar = AppBar(
            title=Text('布尔日记', color=Colors.WHITE),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            actions=[
                self.btn_previous_page,
                self.btn_next_page,
                # VerticalDivider(
                #     thickness=2,
                #     color=Colors.WHITE,
                #     leading_indent=2,
                #     trailing_indent=2,
                # ),
                IconButton(
                    icon=Icons.SEARCH,
                    on_click=self.on_button_search_click
                ),
                # IconButton(
                #     icon=Icons.REFRESH,
                #     on_click=self.on_button_refresh_click
                # ),
            ],
        )

        content = self.build_interface()

        self.page.bottom_appbar = None
        # self.page.drawer = self.drawer
        self.controls = [content, self.dlg_about]
        self.page.run_task(self.query_diary_list)

    async def on_previous_page(self, e):
        if self.page_idx > 2:
            self.page_idx -= 1
            self.btn_previous_page.disabled = False
            self.page.appbar.update()
        else:
            self.page_idx = 1
            self.btn_previous_page.disabled = True
            self.page.appbar.update()
        await self.query_diary_list(append_mode='restart', cate_id=None)

    async def on_next_page(self, e):
        self.page_idx += 1
        self.btn_previous_page.disabled = False
        self.page.appbar.update()
        await self.query_diary_list(append_mode='restart', cate_id=None)


    async def query_diary_list(self, append_mode='restart', cate_id=None):
        self.progress_bar.visible = True
        self.page.update()
        if append_mode == 'restart':
            self.note_list.controls.clear()
        token = await self.page.client_storage.get_async('token')
        user_id = await self.page.client_storage.get_async('user_id')
        url = f'https://restapi.10qu.com.cn/my_diary?user={user_id}&page={self.page_idx}&size=20'
        headers = {"Authorization": f'Bearer {token}'}
        try:
            diary_list = []
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                lst_diary = data.get('result')
                for diary in lst_diary:
                    lst_info = diary.get('info')
                    if not lst_info:
                        continue
                    for info in lst_info:
                        diary_date = info.get('diary_date')
                        diary_info = info.get('diary_info')
                        if isinstance(diary_info, list):
                            continue
                        diary_type = diary_info.get('diary_type')
                        if cate_id is not None:
                            if diary_type != cate_id:
                                continue
                        diary_type_color = diary_info.get('diary_type__colour')
                        diary_text = diary_info.get('text')
                        diary_weather = diary_info.get('weather')
                        diary_location = diary_info.get('location')
                        diary_mood = diary_info.get('mood')
                        dct_diary = {
                            'diary_id': diary_info.get('id'),
                            'diary_date': diary_date,
                            'diary_type': diary_type,
                            'diary_type_color': diary_type_color,
                            'diary_text': diary_text,
                            'diary_weather': diary_weather,
                            'diary_location': diary_location,
                            'diary_mood': diary_mood,
                            'create_time': diary_info.get('create_time'),
                            'update_time': diary_info.get('update_time'),
                        }
                        diary_list.append(dct_diary)
            for diary in diary_list:
                if not diary.get('diary_text'):
                    continue
                diary_date = diary.get('diary_date')
                diary_text = diary.get('diary_text')[:200]
                diary_weather = diary.get('diary_weather')
                diary_location = diary.get('diary_location')
                diary_item = Container(
                    data=diary,
                    margin=3,
                    adaptive=True,
                    border_radius=2,
                    # height=80,
                    on_click=self.on_diary_item_click,
                    border=border.only(
                        None, None, None,
                        BorderSide(1, Colors.GREY_200, BorderSideStrokeAlign.OUTSIDE)),
                    shadow=BoxShadow(spread_radius=0, blur_radius=0,
                                     color=Colors.WHITE, offset=(1, 1)),
                    content=Row(
                        controls=[
                            Container(
                                bgcolor=diary.get('diary_type_color') if diary.get('diary_type_color') else Colors.BLUE,
                                width=3,
                                height=25,
                                padding=padding.only(left=0, top=3, right=5, bottom=3)
                            ),
                            Column(
                                expand=True,
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                value=diary_date,
                                                size=14,
                                                weight=FontWeight.BOLD,
                                                color=Colors.BLUE_600,
                                            ),
                                            Container(expand=True),
                                            Text(
                                                value=diary_weather,
                                                size=14,
                                                # bgcolor=Colors.ORANGE_600,
                                                color=Colors.BLACK54
                                            ),
                                        ]
                                    ),
                                    Text(
                                        value=diary_text,
                                        size=16,
                                        no_wrap=False,
                                        color=Colors.BLACK87
                                    ),
                                    Row(
                                        alignment=MainAxisAlignment.START,
                                        controls=[
                                            Text(
                                                value=diary_location,
                                                no_wrap=False,
                                                size=14,
                                                bgcolor=Colors.GREEN_600,
                                                color=Colors.WHITE
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
                self.note_list.controls.append(diary_item)
                self.progress_bar.visible = False
                self.page.update()
        except httpx.HTTPError as e:
            snack_bar = SnackBar(Text(f"查询用户日记列表请求失败，请刷新重试。{str(e)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.progress_bar.visible = False
            self.page.update()

    # def on_done_get_diary_type_list(self, task:asyncio.Task):
    #     return task.result()

    def on_fab_pressed(self, e):
        self.page.controls.clear()
        from diary_editor_view import DiaryEditorView
        page_view = SafeArea(
            DiaryEditorView(self.page, None),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    async def on_button_refresh_click(self, e):
        # self.page.run_task(self.query_diary_list)
        await self.query_diary_list(append_mode='restart', cate_id=None)

    def on_button_search_click(self, e):
        self.page.controls.clear()
        from search_diary_view import SearchDiaryView
        page_view = SafeArea(
            SearchDiaryView(self.page),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_diary_item_click(self, e):
        diary_data = e.control.data
        self.page.controls.clear()
        from diary_detail_view import DiaryDetailView
        page_view = SafeArea(
            DiaryDetailView(self.page, diary_data),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_about_click(self, e):
        self.page.dialog = self.dlg_about
        self.dlg_about.open = True
        self.page.update()

    def on_about_ok_click(self, e):
        self.dlg_about.open = False
        self.page.update()

    async def on_logout(self, e):
        url = 'https://restapi.10qu.com.cn/logout/'
        token = await self.page.client_storage.get_async('token')
        headers = {"Authorization": f'Bearer {token}'}
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        e.control.page.overlay.append(progress_ring)
        e.control.page.update()
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("退出登录失败，请稍后重新再试。"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    progress_ring.visible = False
                    e.control.page.update()
                    return
                data = resp.json()
                if data.get('code') != '0':
                    snack_bar = SnackBar(Text("退出登录失败，请稍后重新再试。"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    progress_ring.visible = False
                    e.control.page.update()
                    return
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"退出登录失败:{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            progress_ring.visible = False
            e.control.page.update()
        progress_ring.visible = False
        # 跳转至登录界面
        await self.page.client_storage.clear_async()
        from login_view import LoginControl
        page_view = SafeArea(
            LoginControl(self.page),
            adaptive=True,
            expand=True
        )
        self.page.controls.clear()
        self.page.controls.append(page_view)
        self.page.update()

    def open_drawer(self, e):
        if self.page:
            if self.drawer not in self.page.controls:
                pass
            self.drawer.open = True
            self.page.update()

    async def on_query_all_diary_click(self, e):
        self.page.drawer.open = False
        self.page.update()
        await self.query_diary_list(append_mode='restart', cate_id=None)

    async def on_query_category_diary_click(self, e):
        cate_info = e.control.data
        cate_id = cate_info.get('id')
        self.page.drawer.open = False
        self.page.update()
        await self.query_diary_list(append_mode='restart', cate_id=cate_id)

    async def get_diary_type_list(self) -> list|None:
        user_id = await self.page.client_storage.get_async('user_id')
        token = await self.page.client_storage.get_async('token')
        url = f'https://restapi.10qu.com.cn/diarytype?user={user_id}'
        headers = {"Authorization": f'Bearer {token}'}
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers=headers,
                    follow_redirects=True)
                resp.raise_for_status()
                if resp.status_code != 200:
                    return None
                data = resp.json()
                lst_category = data.get('results')
                return lst_category
        except httpx.HTTPError as e:
            snack_bar = SnackBar(Text(f"查询用户日记类型请求失败:{str(e)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

    async def load_more(self):
        self.loading = True

        self.page_idx += 1
        await self.query_diary_list(append_mode='append', cate_id=None)

        snack_bar = SnackBar(Text(f"第{self.page_idx}页加载完成。"))
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.progress_bar.visible = False
        self.loading = False
        self.page.update()

    def on_list_view_scroll(self, e: OnScrollEvent):
        # e.pixels: 当前滚动条位置
        # e.max_scroll_extent: 最大滚动位置
        if e.pixels >= e.max_scroll_extent - 50 and not self.loading:
            # 距离底部小于50像素时触发加载
            self.page.run_task(self.load_more)

    async def build_drawer(self):
        token = await self.page.client_storage.get_async('token')
        # user_info = APIRequest.query_user_info(token)
        url='https://restapi.10qu.com.cn/user_info/'
        headers = {'Authorization': f'Bearer {token}'}
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("获取用户信息失败."))
                    self.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    self.page.update()
                    user_info = {}
                else:
                    data = resp.json()
                    user_info = data.get('results')
                    avatar_url = user_info.get('avatar_url', 'assets/default_avatar.png')
                text_user = Text(
                    user_info.get('nick_name', '用户名'),
                    size=14,
                    color=Colors.WHITE
                )
                img_avatar = Image(
                    src=avatar_url,
                    width=32,
                    height=32,
                    fit=ImageFit.CONTAIN,
                    border_radius=border_radius.all(30)
                )
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"获取用户信息失败：{str(ex)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

        head = Container(
            content=Row(
                controls=[img_avatar,
                          text_user],
                alignment=MainAxisAlignment.SPACE_AROUND,
                # vertical_alignment=CrossAxisAlignment.CENTER,
                # spacing=10
            ),
            bgcolor=Colors.BLUE_600,
            height=100,
            alignment=alignment.center_left,
            adaptive=True,
        )
        # 获得日记类型列表
        lst_category = await self.get_diary_type_list()
        cate_list_tiles = [
            head,
            ListTile(title=Text('所有'),
                     selected=self.selected_idx == 0,
                     selected_tile_color=Colors.BLUE_100,
                     hover_color=Colors.BLUE_50,
                     leading=Icon(Icons.ALL_INBOX),
                     on_click=self.on_query_all_diary_click,
                     ),
        ]
        col_drawer = Column(
            controls=cate_list_tiles
            # alignment=MainAxisAlignment.START,
        )

        for cate in lst_category:
            col_drawer.controls.append(
                ListTile(
                    title=Text(cate.get('type_name')),
                    leading=Container(
                        bgcolor=cate.get('colour'),
                        width=18, height=18,
                    ),
                    selected_tile_color=Colors.BLUE_100,
                    hover_color=Colors.BLUE_50,
                    data=cate,
                    on_click=self.on_query_category_diary_click,
                )
            )
        col_drawer.controls.append(Container(expand=True))
        col_drawer.controls.append(
            Divider(
                thickness=1,
                color=Colors.GREY_200,
            )
        )
        col_drawer.controls.append(ListTile(title=Text('关于我们'),
                         leading=Icon(Icons.HELP),
                         on_click=self.on_about_click,
                         ))
        col_drawer.controls.append(
            ListTile(
                title=Text('退出登录'),
                leading=Icon(Icons.EXIT_TO_APP),
                on_click=self.on_logout,
            )
        )
        # return col_drawer
        self.drawer = NavigationDrawer(
            position=NavigationDrawerPosition.START,
            open=False,
            controls=[
                Container(
                    content=col_drawer,
                    expand=1,
                    padding=0,
                    margin=0,
                )
            ]
        )
        self.page.drawer = self.drawer
        self.page.update()

    def build_interface(self):
        # 笔记列表
        self.note_list = ListView(
            spacing=10,
            padding=padding.only(left=2, top=5, right=2, bottom=5),
            expand=True,
            # height=self.page.height - 10,
            # on_scroll= self.on_list_view_scroll,
        )

        self.progress_bar = ProgressBar(
            value=None,
            bar_height=3,
            bgcolor=Colors.GREY_100,
            color=Colors.GREY_300,
            width=self.page.width
        )

        today = date.today()
        str_today = f'{today.year}年{today.month}月{today.day}日,{['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]}'
        col_notes = Column(
            controls = [
                Text(
                    f'今天是{str_today}',
                    size=16,
                    weight=FontWeight.BOLD,
                ),
                self.progress_bar,
                self.note_list,
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=CrossAxisAlignment.START,
            adaptive=True,
            width=self.page.width,
            spacing=0,
            tight=True,
        )
        return col_notes
