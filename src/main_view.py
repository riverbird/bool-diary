from datetime import datetime

import httpx
from flet import Column, Row, Icons, Colors
from flet.core import border, border_radius, alignment
from flet.core.alert_dialog import AlertDialog
from flet.core.app_bar import AppBar
from flet.core.border import BorderSide, BorderSideStrokeAlign
from flet.core.container import Container
from flet.core.divider import Divider
from flet.core.floating_action_button import FloatingActionButton
from flet.core.icon import Icon
from flet.core.icon_button import IconButton
from flet.core.image import Image
from flet.core.list_tile import ListTile
from flet.core.list_view import ListView
from flet.core.navigation_drawer import NavigationDrawer, NavigationDrawerPosition
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.types import FontWeight, MainAxisAlignment, CrossAxisAlignment, ImageFit
from flet.core.vertical_divider import VerticalDivider

from api_request import APIRequest


class MainView(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.selected_idx = -1
        self.page_idx = 1

        self.alignment = MainAxisAlignment.SPACE_BETWEEN,
        self.spacing = 0
        self.tight = True

        self.token = self.page.client_storage.get('token')
        self.user_id = self.page.client_storage.get('user_id')

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

        self.drawer = NavigationDrawer(
            position=NavigationDrawerPosition.START,
            controls=[
                Container(
                    content=self.build_drawer(),
                    expand=1,
                    padding=0,
                    margin=0,
                )
            ]
        )

        floating_btn = FloatingActionButton(
            icon=Icons.ADD,
            bgcolor=Colors.BLUE,
            foreground_color=Colors.WHITE,
            data=0,
            # bottom=24,
            # right=16,
            on_click=self.on_fab_pressed,
        )

        self.page.appbar = AppBar(
            title=Text('布尔日记'),
            bgcolor=Colors.BLUE,
            actions=[
                IconButton(icon=Icons.SEARCH)
            ],
        )

        content = self.build_interface()

        self.page.floating_action_button = floating_btn
        self.page.drawer = self.drawer

        self.controls = [content, self.dlg_about]

        self.page.run_task(self.query_diary_list)

    def query_note_list(self, flag='recent'):
        self.note_list.controls.clear()
        token = self.page.client_storage.get('token')
        user_id = self.page.client_storage.get('user_id')
        # match flag:
        #     case 'favorites':
        #         notes = APIRequest.query_favorite_notes(token)
        #     case 'trash':
        #         notes = APIRequest.query_trash_notes(token)
        #     case _:
        #         notes = APIRequest.query_notes(token, user_id)
        notes = []
        if not notes:
            return
        lst_note_type = ['文本笔记', '代码笔记', 'Markdown笔记',
                         '备忘笔记', '富文本笔记', '表格笔记',
                         '大纲笔记', '绘画笔记', '图表笔记',
                         'PDF笔记', '时间轴笔记']
        for note in notes:
            dt_time = datetime.strptime(note.get('update_time'), '%Y-%m-%dT%H:%M:%S.%f')
            str_update_time = dt_time.strftime("%Y-%m-%d %H:%M:%S")
            note_item = Container(
                content=Column(
                    controls=[
                        Row(controls=[
                            Text(value=note.get('title', '--'),
                                 size=15,
                                 color=Colors.BLACK),
                            Text(value=lst_note_type[note.get('note_type')],
                                 size=10,
                                 color=Colors.GREY_600),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        ),
                        Text(value=str_update_time,
                             size=9,
                             color=Colors.BLUE_600),
                    ],
                ),
                data = note,
                adaptive=True,
                border_radius=2,
                on_click=self.on_note_item_click,
                border=border.only(None, None, None,
                                   BorderSide(1, Colors.GREY_200,BorderSideStrokeAlign.INSIDE))
            )
            self.note_list.controls.append(note_item)

    async def query_diary_list(self):
        self.note_list.controls.clear()
        url = f'https://restapi.10qu.com.cn/my_diary?user={self.user_id}&page={self.page_idx}&size=20'
        headers = {"Authorization": f'Bearer {self.token}'}
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
                        # dt_diary = datetime.strptime(diary_date, '%Y-%m-%d')
                        diary_info = info.get('diary_info')
                        if isinstance(diary_info, list):
                            continue
                        diary_type_color = diary_info.get('diary_type_color')
                        diary_text = diary_info.get('text')
                        diary_weather = diary_info.get('weather')
                        diary_location = diary_info.get('location')
                        dct_diary = {
                            'diary_date': diary_date,
                            'diary_type_color': diary_type_color,
                            'diary_text': diary_text,
                            'diary_weather': diary_weather,
                            'diary_location': diary_location,
                        }
                        diary_list.append(dct_diary)
            for diary in diary_list:
                if not diary.get('diary_text'):
                    continue
                diary_date = diary.get('diary_date')
                diary_text = diary.get('diary_text')[:200]
                diary_location = diary.get('diary_location')
                diary_item = Container(
                    content=Column(
                        controls=[
                            Row(
                                controls=[
                                    VerticalDivider(
                                        thickness=3,
                                        width=3,
                                        color=diary.get('diary_type_color') if diary.get('diary_type_color') else Colors.BLUE,
                                    ),
                                    Text(value=diary_date,
                                         size=11,
                                         color=Colors.BLUE_600),
                                    Container(expand=True),
                                    Text(value=diary_weather,
                                         size=11,
                                         color=Colors.BLUE_600),
                                    Text(value=diary_location,
                                         no_wrap=False,
                                         size=11,
                                         color=Colors.BLUE_600),
                                ]
                            ),
                            Text(value=diary_text,
                                 size=13,
                                 color=Colors.BLACK87),

                        ],
                    ),
                    data=diary,
                    adaptive=True,
                    border_radius=2,
                    on_click=self.on_note_item_click,
                    border=border.only(None, None, None,
                                       BorderSide(1, Colors.GREY_200, BorderSideStrokeAlign.INSIDE))
                )
                self.note_list.controls.append(diary_item)
                self.page.update()
        except httpx.HTTPError as e:
            snack_bar = SnackBar(Text("用户退出登录请求失败!"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

    def query_summary_info(self):
        dct_info = {}
        token = self.page.client_storage.get('token')
        dct_ret = APIRequest.query_user_info(token)
        dct_info['nickname'] = dct_ret.get('nick_name', '用户名')
        return dct_info

    def on_fab_pressed(self, e):
        self.page.go('/edit?id=null')

    def on_button_refresh_click(self, e):
        self.page.run_task(self.query_diary_list)

    def on_note_item_click(self, e):
        note_data = e.control.data
        note_id = note_data.get('id')
        if True:
            self.page.go(f'/view?id={note_id}')
        else:
            snack_bar = SnackBar(Text("暂不支持此类笔记查看!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    def on_menu_click(self, e):
        self.drawer.open = True
        e.control.page.update()

    def on_about_click(self, e):
        self.page.dialog = self.dlg_about
        self.dlg_about.open = True
        self.page.update()

    def on_about_ok_click(self, e):
        self.dlg_about.open = False
        self.page.update()

    def on_logout(self, e):
        req_result = APIRequest.logout(self.page.client_storage.get('token'))
        if req_result is True:
            self.page.client_storage.clear()
            from login_view import LoginControl
            page_view = SafeArea(
                LoginControl(self.page),
                adaptive=True,
                expand=True
            )
            self.page.appbar = None
            self.page.drawer = None
            self.page.controls.clear()
            self.page.controls.append(page_view)
            self.page.update()
            return
        snack_bar = SnackBar(Text("用户退出登录请求失败!"))
        e.control.page.overlay.append(snack_bar)
        snack_bar.open = True
        e.control.page.update()

    def open_drawer(self, e):
        if self.page:
            if self.drawer not in self.page.controls:
                pass
            self.drawer.open = True
            self.page.update()

    def on_recent_note_click(self, e):
        self.query_note_list(flag='recent')
        self.title_text.value = '近期笔记'
        self.selected_idx = 0
        self.drawer.open = False
        self.page.update()

    def on_favorites_note_click(self, e):
        self.query_note_list(flag='favorites')
        self.title_text.value = '收藏笔记'
        self.selected_idx = 1
        self.drawer.open = False
        self.page.update()

    def on_trash_note_click(self, e):
        self.query_note_list(flag='trash')
        self.title_text.value = '回收箱'
        self.selected_idx = 2
        self.drawer.open = False
        self.page.update()

    def on_search_note(self, e):
        # str_keyword = e.control.value
        # self.page.go(f'/search?text={str_keyword}')
        self.page.go('/query')

    def get_diary_type_list(self) -> list|None:
        url = f'https://restapi.10qu.com.cn/diarytype?user={self.user_id}'
        headers = {"Authorization": f'Bearer {self.token}'}
        resp = httpx.get(url, headers=headers, follow_redirects=True)
        if resp.status_code != 200:
            return None
        resp.raise_for_status()
        data = resp.json()
        lst_category = data.get('results')
        return lst_category

    def build_drawer(self):
        user_info = APIRequest.query_user_info(self.page.client_storage.get('token'))
        avatar_url = user_info.get('avatar_url', f'/icons/head.png')
        text_user = Text(
            user_info.get('nick_name', '用户名'),
            size=14,
            color=Colors.WHITE
        )
        img_avatar = Image(src=avatar_url,
                           width=32,
                           height=32,
                           fit=ImageFit.CONTAIN,
                           border_radius=border_radius.all(30)
        )
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
        lst_category = self.get_diary_type_list()
        cate_list_tiles = [
            head,
            ListTile(title=Text('所有'),
                     selected=self.selected_idx == 0,
                     selected_tile_color=Colors.BLUE_100,
                     hover_color=Colors.BLUE_50,
                     leading=Icon(Icons.ALL_INBOX),
                     on_click=self.on_recent_note_click,
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
                    # selected=self.selected_idx == 1,
                    leading=Container(
                        bgcolor=cate.get('colour'),
                        width=18, height=18,
                    ),
                    selected_tile_color=Colors.BLUE_100,
                    hover_color=Colors.BLUE_50,
                    on_click=self.on_favorites_note_click,
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
        col_drawer.controls.append(ListTile(title=Text('退出登录'),
                         leading=Icon(Icons.EXIT_TO_APP),
                         on_click=self.on_logout,
                         ))
        return col_drawer

    def build_interface(self):
        # 标题栏
        # self.title_text = Text('布尔日记', size=20, weight=FontWeight.BOLD, color=Colors.WHITE)
        # title_bar = Container(
        #     content=Row(
        #         controls=[
        #             IconButton(icon=Icons.MENU,
        #                        icon_color=Colors.WHITE,
        #                        on_click=self.on_menu_click),
        #             self.title_text,
        #             Container(expand=True),
        #             # IconButton(icon=Icons.REFRESH,
        #             #            icon_color=Colors.WHITE,
        #             #            on_click=self.on_button_refresh_click),
        #             IconButton(icon=Icons.SEARCH,
        #                        icon_color=Colors.WHITE,
        #                        on_click=self.on_search_note,
        #             ),
        #             # tf_search,
        #             # Container(width=3),
        #         ],
        #     ),
        #     height=45,
        #     border_radius=3,
        #     adaptive=True,
        #     bgcolor=Colors.BLUE_600,
        #     # padding=padding.all(0),
        #     # margin=margin.only(top=2, bottom=2)
        # )

        # 笔记列表
        self.note_list = ListView(
            spacing=10,
            padding=20,
            expand=True,
            height=self.page.height - 10)

        col_notes = Column(
            controls = [
                # title_bar,
                self.note_list,
            ],
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.START,
            adaptive=True,
            width=self.page.width,
            spacing=0,
            tight=True,
        )
        return col_notes
