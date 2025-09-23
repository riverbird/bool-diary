# coding:utf-8
import json
from asyncio import Future

import httpx
from flet.core import padding
from flet.core.alert_dialog import AlertDialog
from flet.core.app_bar import AppBar
from flet.core.buttons import RoundedRectangleBorder
from flet.core.colors import Colors
from flet.core.column import Column
from flet.core.container import Container
from flet.core.floating_action_button import FloatingActionButton
from flet.core.grid_view import GridView
from flet.core.icon_button import IconButton
from flet.core.icons import Icons
from flet.core.list_tile import ListTile
from flet.core.list_view import ListView
from flet.core.popup_menu_button import PopupMenuButton, PopupMenuItem
from flet.core.progress_bar import ProgressBar
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.textfield import TextField
from flet.core.types import MainAxisAlignment

from material_colors import MATERIAL_COLORS
from common import diary_type_manager
# from flet_contrib.color_picker import ColorPicker


class TagManageView(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page

        self.last_tag_info = None
        self.selected_color_add = TextField('#cdcdcd')
        self.selected_color_edit = TextField('#cdcdcd')

        def pick_color_add(name):
            self.selected_color_add.value = name
            self.selected_color_add.update()

        def pick_color_edit(name):
            self.selected_color_edit.value = name
            self.selected_color_edit.update()


        self.grid_add = GridView(expand=True, max_extent=40, spacing=5, run_spacing=5)
        self.grid_edit = GridView(expand=True, max_extent=40, spacing=5, run_spacing=5)
        for k, v in MATERIAL_COLORS.items():
            self.grid_add.controls.append(
                Container(
                    bgcolor=v,
                    border_radius=5,
                    on_click=lambda e, name=v: pick_color_add(name),
                )
            )
            self.grid_edit.controls.append(
                Container(
                    bgcolor=v,
                    border_radius=5,
                    on_click=lambda e, name=v: pick_color_edit(name),
                )
            )

        self.tf_tag = TextField(hint_text='请输入新分类')
        # self.color_picker_new = ColorPicker()
        self.dlg_add_tag = AlertDialog(
            modal=True,
            title=Text('创建新分类'),
            content=Column(
                controls=[
                    self.tf_tag,
                    # self.btn_new_select_color,
                    self.grid_add,
                    self.selected_color_add
                ],
                alignment=MainAxisAlignment.START,
                width=300,
                height=350,
            ),
            actions=[TextButton("确定", on_click=self.on_dlg_add_tag_ok_click),
                     TextButton("取消", on_click=self.on_dlg_add_tag_cancel_click)],
            actions_alignment=MainAxisAlignment.END,
            title_padding=20,
            # on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        self.tf_edit_tag = TextField(hint_text='请输入分类')
        # self.color_picker_edit = ColorPicker()

        self.dlg_edit_tag = AlertDialog(
            modal=True,
            title=Text('修改标签'),
            content=Column(
                controls=[
                    self.tf_edit_tag,
                    self.grid_edit,
                    self.selected_color_edit
                ],
                alignment=MainAxisAlignment.START,
                width=300,
                height=350,
            ),
            actions=[TextButton("确定", on_click=self.on_dlg_edit_tag_ok_click),
                     TextButton("取消", on_click=self.on_dlg_edit_tag_cancel_click)],
            actions_alignment=MainAxisAlignment.END,
            title_padding=20,
            # on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )

        self.page.appbar = AppBar(
            title=Text('日记类型'),
            bgcolor=Colors.WHITE,
            color=Colors.BLACK,
            leading=IconButton(
                icon=Icons.ARROW_BACK,
                tooltip='返回',
                on_click=self.on_button_back_click,
            ),
        )
        self.page.floating_action_button = FloatingActionButton(
            icon=Icons.ADD,
            bgcolor=Colors.BLUE,
            foreground_color=Colors.WHITE,
            shape=RoundedRectangleBorder(radius=50),
            data=0,
            on_click=self.on_fab_pressed,
        )
        self.page.drawer = None
        self.controls = [self.dlg_add_tag, self.dlg_edit_tag, self.build_interface()]

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

    async def get_diary_type_list(self) -> list | None:
        self.progress_bar.visible = True
        self.page.update()
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
                    return []
                data = resp.json()
                lst_category = data.get('results')
                cached_diary_type_list_str = json.dumps(lst_category)
                await self.page.client_storage.set_async('diary_type_list', cached_diary_type_list_str)
                return lst_category
        except httpx.HTTPError as e:
            snack_bar = SnackBar(Text(f"查询用户日记类型请求失败:{str(e)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
        return []

    def on_tag_edit_click(self, e):
        tag_info = e.control.data
        if tag_info:
            self.page.dialog = self.dlg_edit_tag
            self.tf_edit_tag.value = tag_info.get('type_name')
            self.selected_color_edit.value = tag_info.get('colour')
            self.last_tag_info = tag_info
            self.dlg_edit_tag.open = True
            self.page.update()

    async def update_tag_name(self, tag_id, name, color_str):
        self.progress_bar.visible = True
        self.page.update()
        token = await self.page.client_storage.get_async('token')
        user_id = await self.page.client_storage.get_async('user_id')
        user_input = {'user': user_id,
                      'type_name': name,
                      'colour': color_str,}
        headers = {"Authorization": f'Bearer {token}'}
        url = f'https://restapi.10qu.com.cn/diarytype/{tag_id}/'
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.put(
                    url,
                    headers=headers,
                    json=user_input,
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("日记分类更新失败!"))
                    self.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    self.page.update()
                    return
                else:
                    task_query_diary_type_list = self.page.run_task(self.get_diary_type_list)
                    task_query_diary_type_list.add_done_callback(self.handle_diary_type_list)
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"更新日记分类失败:{str(ex)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
            self.progress_bar.visible = False
            self.page.update()
            return

        self.progress_bar.visible = False
        self.page.update()

    def on_tab_delete_click(self, e):
        tag_info = e.control.data
        if tag_info:
            tag_id = tag_info.get('id')
            self.page.run_task(self.delete_memo_tag, tag_id, e)

    async def delete_memo_tag(self, tag_id, e):
        token = await self.page.client_storage.get_async('token')
        url = f'https://restapi.10qu.com.cn/diarytype/{tag_id}/'
        headers = {"Authorization": f'Bearer {token}'}
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.delete(
                    url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 204:
                    snack_bar = SnackBar(Text("删除日记分类失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                else:
                    task_query_diary_type_list = self.page.run_task(self.get_diary_type_list)
                    task_query_diary_type_list.add_done_callback(self.handle_diary_type_list)
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"删除日记分类失败:{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return

    def on_fab_pressed(self, e):
        self.page.dialog = self.dlg_add_tag
        self.dlg_add_tag.open = True
        self.page.update()

    async def on_dlg_add_tag_ok_click(self, e):
        token = await self.page.client_storage.get_async('token')
        user_id = await self.page.client_storage.get_async('user_id')
        type_color = self.selected_color_add.value
        url = 'https://restapi.10qu.com.cn/diarytype/'
        headers = {'Authorization': f'Bearer {token}'}
        user_input = {
            'user': user_id,
            'type_name': self.tf_tag.value,
            'colour': type_color,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.post(
                    url,
                    headers=headers,
                    json=user_input,
                )
                resp.raise_for_status()
                if resp.status_code != 201:
                    snack_bar = SnackBar(Text("添加分类失败!"))
                    e.control.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    e.control.page.update()
                    return
                # await self.update_todolist()
                task_query_diary_type_list = self.page.run_task(self.get_diary_type_list)
                task_query_diary_type_list.add_done_callback(self.handle_diary_type_list)
                self.dlg_add_tag.open = False
                self.page.update()
        except httpx.HTTPError as ex:
            snack_bar = SnackBar(Text(f"添加标签失败：{str(ex)}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    def on_dlg_add_tag_cancel_click(self, e):
        self.dlg_add_tag.open = False
        self.page.update()

    async def on_dlg_edit_tag_ok_click(self, e):
        self.dlg_edit_tag.open = False
        self.page.update()
        await self.update_tag_name(
            self.last_tag_info.get('id'),
            self.tf_edit_tag.value,
            self.selected_color_edit.value,
        )

    def on_dlg_edit_tag_cancel_click(self, e):
        self.dlg_edit_tag.open = False
        self.page.update()

    def handle_diary_type_list(self, t:Future[list]):
        try:
            res = t.result()
        except Exception as ex:
            snack_bar = SnackBar(Text(f"获取日记分类请求失败:{str(ex)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.progress_bar.visible = False
            self.page.update()
        else:
            lst_types = res
            # SingletonList().diary_type_list = lst_types
            diary_type_manager.global_diary_type_list = lst_types
            self.list_tags.controls.clear()
            for tag in lst_types:
                self.list_tags.controls.append(
                    ListTile(
                        title=Text(tag.get('type_name')),
                        leading=Container(
                            bgcolor=tag.get('colour'),
                            width=18, height=18,
                        ),
                        trailing=PopupMenuButton(
                            items=[
                                PopupMenuItem(
                                    text="编辑",
                                    icon=Icons.EDIT,
                                    data=tag,
                                    on_click=self.on_tag_edit_click,
                                ),
                                PopupMenuItem(
                                    text="删除",
                                    icon=Icons.DELETE,
                                    data=tag,
                                    on_click=self.on_tab_delete_click,
                                ),
                            ]
                        )
                    )
                )
            self.list_tags.update()
            self.progress_bar.visible = False
            self.page.update()

    def build_interface(self):
        self.list_tags = ListView(
            spacing=10,
            padding=padding.only(left=2, top=0, right=2, bottom=5),
            expand=True,
        )
        self.progress_bar = ProgressBar(
            value=None,
            bar_height=3,
            bgcolor=Colors.GREY_100,
            color=Colors.GREY_300,
            width=self.page.width
        )
        # 布局
        cols_body = Column(
            controls=[
                self.progress_bar,
                self.list_tags,
            ],
        )
        task_query_diary_type_list = self.page.run_task(self.get_diary_type_list)
        task_query_diary_type_list.add_done_callback(self.handle_diary_type_list)
        return cols_body
