"""
diary_detail_view.py
"""
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
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.types import MainAxisAlignment, ScrollMode, TextAlign

from api_request import APIRequest


class DiaryDetailView(Column):
    def __init__(self, page, diary_info):
        super().__init__()
        self.page = page
        self.diary_info = diary_info
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
            # bottom=24,
            # right=16,
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
                    on_click=self.on_delete_note
                )
            ],
            icon_color=Colors.WHITE,
        )
        self.page.appbar = AppBar(
            title=Text(f'{self.diary_info.get("diary_date")}'),
            bgcolor=Colors.BLUE,
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
        self.controls = [content, self.dlg_info, self.dlg_delete_confirm]

    def on_fab_pressed(self, e):
        # note_type = NoteType(self.note_info.get('note_type'))
        # if note_type in [NoteType.TextNote, NoteType.CodeNote, NoteType.MarkdownNote]:
        #     self.page.go(f'/edit?id={self.note_id}')
        # else:
        #     snack_bar = SnackBar(Text("暂不支持此类笔记编辑!"))
        #     e.control.page.overlay.append(snack_bar)
        #     snack_bar.open = True
        #     e.control.page.update()
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

    def on_delete_note(self, e):
        delete_flag = self.note_info.get('delete_flag')
        if delete_flag:
            self.dlg_delete_confirm.open = True
            self.page.update()
        else:
            orig_delete_flag = self.note_info.get('delete_flag')
            dest_delete_flag = not orig_delete_flag
            update_result = APIRequest.update_note_delete_flag(
                self.page.client_storage.get('token'),
                self.note_id, dest_delete_flag)
            update_result_text = '成功' if update_result else '失败'
            snack_bar = SnackBar(Text(f"修改笔记删除状态{update_result_text}!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    def on_dlg_info_ok_click(self, e):
        self.dlg_info.open = False
        self.page.update()

    def on_dlg_delete_confirm_ok_click(self, e):
        if not APIRequest.delete_note(self.page.client_storage.get('token'), self.note_id):
            snack_bar = SnackBar(Text("删除笔记失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        self.page.go('/main_view')

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
        # 布局
        cols_body = Column(
            controls=[
                Column(
                    controls=[self.note_view],
                    scroll=ScrollMode.AUTO
                )
            ],
            alignment=MainAxisAlignment.START,
            expand=True,
            adaptive=True,
        )
        return cols_body
