"""
diary_detail_view.py
"""
import json
from datetime import datetime, date

import httpx
from flet.core.alert_dialog import AlertDialog
from flet.core.app_bar import AppBar
from flet.core.colors import Colors
from flet.core.column import Column
from flet.core.divider import Divider
from flet.core.floating_action_button import FloatingActionButton
from flet.core.icon_button import IconButton
from flet.core.icons import Icons
from flet.core.list_view import ListView
from flet.core.popup_menu_button import PopupMenuButton, PopupMenuItem
from flet.core.row import Row
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.types import MainAxisAlignment, ScrollMode, TextAlign

class DiaryDetailView(Column):
    def __init__(self, page, diary_info):
        super().__init__()
        self.page = page
        self.diary_info = diary_info
        self.diary_date = diary_info.get('diary_date') if self.diary_info is not None else date.today().strftime(
            '%Y-%m-%d')
        self.diary_mood = diary_info.get('diary_mood') if self.diary_info is not None else 0
        self.diary_weather = diary_info.get('diary_weather') if self.diary_info is not None else '晴'
        self.diary_location = diary_info.get('diary_location') if self.diary_info is not None else ''
        self.diary_category_list = self.get_diary_type_list()
        self.diary_type = diary_info.get('diary_type') if self.diary_info is not None else None
        content = self.build_interface()

        # 删除对话框
        self.dlg_delete_confirm = AlertDialog(
            modal=True,
            title=Text('删除确认'),
            content=Column(
                controls=[Divider(height=1, color='gray'),
                          Text('您确定要删除此日记吗?'),
                          ],
                alignment=MainAxisAlignment.START,
                width=200,
                height=50,
            ),
            actions=[TextButton("确定", on_click=self.on_dlg_delete_confirm_ok_click),
                     TextButton('取消', on_click=self.on_dlg_delete_confirm_cancel_click)],
            actions_alignment=MainAxisAlignment.END,
            # on_dismiss=lambda e: print("对话框已关闭!"),
        )

        # 笔记信息
        self.dlg_info = AlertDialog(
            modal=True,
            title=Text('笔记信息'),
            # icon=Icon(Icons.INFO),
            content=ListView(
                controls=[
                    Text(f'字数:{len(self.diary_info["diary_text"])}'),
                    Divider(thickness=1, color='gray'),
                    # Text(f'创建日期:{str_update_time}'),
                    # Text(f'更新日期:{str_create_time}'),
                    # Divider(thickness=1, color='gray'),
                ],
                height=100,
            ),
            actions=[TextButton("确定", on_click=self.on_dlg_info_ok_click), ],
            actions_alignment=MainAxisAlignment.END,
            # on_dismiss=lambda e: print("对话框已关闭!"),
        )

        floating_btn = FloatingActionButton(
            icon=Icons.EDIT_NOTE,
            bgcolor=Colors.BLUE,
            foreground_color=Colors.WHITE,
            data=0,
            on_click=self.on_fab_pressed,
        )

        diary_menu_btn = PopupMenuButton(
            items=[
                PopupMenuItem(
                    icon=Icons.INFO,
                    text='信息',
                    on_click=self.on_view_info
                ),
                PopupMenuItem(
                    icon=Icons.DELETE,
                    text='删除',
                    on_click=self.on_delete_diary
                )
            ],
            icon_color=Colors.WHITE,
        )
        self.page.appbar = AppBar(
            title=Text(f'{self.diary_info.get("diary_date")}'),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            leading=IconButton(
                icon=Icons.ARROW_BACK,
                tooltip='返回',
                on_click=self.on_button_back_click,
            ),
            actions=[
                diary_menu_btn,
            ],
        )

        self.page.floating_action_button = floating_btn
        self.page.drawer = None
        self.page.bottom_appbar = None
        self.controls = [content, self.dlg_info, self.dlg_delete_confirm]

    def get_diary_type_list(self) -> list|None:
        cached_diary_type_list_value = self.page.client_storage.get('diary_type_list')
        cached_diary_type_list = json.loads(cached_diary_type_list_value) if cached_diary_type_list_value else []
        if cached_diary_type_list:
            return cached_diary_type_list
        user_id = self.page.client_storage.get('user_id')
        token = self.page.client_storage.get('token')
        url = f'https://restapi.10qu.com.cn/diarytype?user={user_id}'
        headers = {"Authorization": f'Bearer {token}'}
        resp = httpx.get(url, headers=headers, follow_redirects=True)
        if resp.status_code != 200:
            return None
        resp.raise_for_status()
        data = resp.json()
        lst_category = data.get('results')
        cached_diary_type_list_str = json.dumps(lst_category)
        self.page.client_storage.set('diary_type_list', cached_diary_type_list_str)
        return lst_category

    def on_fab_pressed(self, e):
        self.page.controls.clear()
        from diary_editor_view import DiaryEditorView
        page_view = SafeArea(
            DiaryEditorView(self.page, self.diary_info),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_button_back_click(self, e):
        self.page.controls.clear()
        from main_view import MainView
        page_view = SafeArea(
            MainView(self.page),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_view_info(self, e):
        self.dlg_info.open = True
        self.page.update()

    def on_delete_diary(self, e):
        self.dlg_delete_confirm.open = True
        self.page.update()

    def on_dlg_info_ok_click(self, e):
        self.dlg_info.open = False
        self.page.update()

    async def on_dlg_delete_confirm_ok_click(self, e):
        token = await self.page.client_storage.get_async('token')
        diary_id = self.diary_info.get("diary_id")
        url = f'https://restapi.10qu.com.cn/diary/{diary_id}/'
        headers = {"Authorization": f'Bearer {token}'}
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.delete(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 204:
                    snack_bar = SnackBar(Text("删除笔记失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"删除笔记失败:{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        # 关闭对话框
        self.dlg_delete_confirm.open = False
        self.page.update()
        # 跳转至主页
        self.page.controls.clear()
        from main_view import MainView
        page_view = SafeArea(
            MainView(self.page),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_dlg_delete_confirm_cancel_click(self, e):
        self.dlg_delete_confirm.open = False
        self.page.update()

    def build_interface(self):
        self.note_view = Text(
            value=self.diary_info.get('diary_text'),
            size=16,
            text_align=TextAlign.LEFT,
            no_wrap=False,
            expand=True,
        )
        # self.note_view = Markdown(
        #     value=self.diary_info.get('diary_text'),
        #     expand=True
        # )
        if self.diary_info is not None:
            today = datetime.strptime(self.diary_date, '%Y-%m-%d')
        else:
            today = date.today()
        str_today = f'{today.year}年{today.month}月{today.day}日,{['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]}'
        mood_set = (
            '普通',
            '微笑',
            '开心',
            '难过',
            '调皮',
            '偷着乐',
            '惊讶',
            '酷',
            '无奈',
            '难受',
            '怒',
            '大哭',
            '紧张'
        )
        if self.diary_category_list:
            diary_category_name = next(
                (opt.get('type_name') for opt in self.diary_category_list if opt.get('id') == self.diary_type),
                '分类'
            )
        else:
            diary_category_name = '分类'
        buttons_row = Row(
            controls=[
                TextButton(
                    str_today,
                    icon=Icons.CALENDAR_TODAY,
                ),
                TextButton(
                    mood_set[self.diary_mood],
                    icon=Icons.EMOJI_SYMBOLS,
                ),
                TextButton(
                    self.diary_weather,
                    icon=Icons.SUNNY_SNOWING,
                ),
                TextButton(
                    self.diary_location if self.diary_location else '城市',
                    icon=Icons.LOCATION_CITY,
                ),
                TextButton(
                    diary_category_name,
                    icon=Icons.LABEL,
                ),
            ],
            wrap=True,
        )
        # 布局
        cols_body = Column(
            controls=[
                Column(
                    controls=[
                        buttons_row,
                        self.note_view
                    ],
                    scroll=ScrollMode.AUTO
                )
            ],
            alignment=MainAxisAlignment.START,
            expand=True,
            adaptive=True,
        )
        return cols_body
