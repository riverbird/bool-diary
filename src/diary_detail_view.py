from datetime import datetime

from flet.core import padding
from flet.core.alert_dialog import AlertDialog
from flet.core.colors import Colors
from flet.core.column import Column
from flet.core.container import Container
from flet.core.divider import Divider
from flet.core.floating_action_button import FloatingActionButton
from flet.core.form_field_control import InputBorder
from flet.core.icon_button import IconButton
from flet.core.icons import Icons
from flet.core.list_view import ListView
from flet.core.markdown import Markdown
from flet.core.pagelet import Pagelet
from flet.core.popup_menu_button import PopupMenuButton, PopupMenuItem
from flet.core.row import Row
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.textfield import TextField
from flet.core.types import MainAxisAlignment, ScrollMode
from flet.core.webview import WebView

from src.api_request import APIRequest


class DiaryDetailView(Column):
    def __init__(self, page, note_id):
        super().__init__()
        self.page = page
        self.note_id = note_id
        self.note_info = self.get_note_info(note_id)
        content = self.build_interface()

        # 删除对话框
        self.dlg_delete_confirm = AlertDialog(
            modal=True,
            title=Text('删除确认'),
            content=Column(
                controls=[Divider(height=1, color='gray'),
                          Text('您确定要删除此笔记吗?'),
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
        dt_update_time = datetime.strptime(self.note_info.get('update_time'), '%Y-%m-%dT%H:%M:%S.%f')
        str_update_time = dt_update_time.strftime("%Y-%m-%d %H:%M:%S")
        dt_create_time = datetime.strptime(self.note_info.get('create_time'), '%Y-%m-%dT%H:%M:%S.%f')
        str_create_time = dt_create_time.strftime("%Y-%m-%d %H:%M:%S")
        self.dlg_info = AlertDialog(
            modal=True,
            title=Text('笔记信息'),
            # icon=Icon(Icons.INFO),
            content=ListView(
                controls=[
                    Text(f'标题:{self.note_info["title"]}'),
                    Divider(thickness=1, color='gray'),
                    Text(f'创建日期:{str_update_time}'),
                    Text(f'更新日期:{str_create_time}'),
                    Divider(thickness=1, color='gray'),
                ],
                height=100,
            ),
            # alignment=alignment.top_left,
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

        pagelet = Pagelet(
            floating_action_button=floating_btn,
            content=content,
            width=self.page.width,
            height=self.page.height,
            expand=True,
            adaptive=True,
        )
        if NoteType(self.note_info.get('note_type')) in [NoteType.RichNote, NoteType.PDFNote]:
            pagelet.floating_action_button = None
        self.controls = [pagelet, self.dlg_info, self.dlg_delete_confirm]

    def get_note_info(self, note_id):
        token = self.page.client_storage.get('token')
        note_info = APIRequest.query_note_by_id(token, note_id)
        return note_info

    def on_fab_pressed(self, e):
        note_type = NoteType(self.note_info.get('note_type'))
        if note_type in [NoteType.TextNote, NoteType.CodeNote, NoteType.MarkdownNote]:
            self.page.go(f'/edit?id={self.note_id}')
        else:
            snack_bar = SnackBar(Text("暂不支持此类笔记编辑!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()

    def on_button_back_click(self, e):
        self.page.go('/main_view')

    def on_make_note_top(self, e):
        orig_top_flag = self.note_info.get('top_flag')
        dest_top_flag = not orig_top_flag
        update_result = APIRequest.update_note_top_flag(
            self.page.client_storage.get('token'), self.note_id, dest_top_flag)
        update_result_text = '成功' if update_result else '失败'
        snack_bar = SnackBar(Text(f"修改笔记置顶状态{update_result_text}!"))
        e.control.page.overlay.append(snack_bar)
        snack_bar.open = True
        e.control.page.update()

    def on_make_note_favorite(self, e):
        orig_favorite_flag = self.note_info.get('favorite')
        dest_favorite_flag = not orig_favorite_flag
        update_result = APIRequest.update_note_favorite_status(
            self.page.client_storage.get('token'),
            self.note_id,
            dest_favorite_flag)
        update_result_text = '成功' if update_result else '失败'
        snack_bar = SnackBar(Text(f"修改笔记收藏状态{update_result_text}!"))
        e.control.page.overlay.append(snack_bar)
        snack_bar.open = True
        e.control.page.update()

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
        # 标题栏
        note_menu_btn = PopupMenuButton(
            items=[
                PopupMenuItem(
                    icon=Icons.VERTICAL_ALIGN_TOP,
                    text='置顶',
                    checked=self.note_info.get('top_flag'),
                    on_click=self.on_make_note_top
                ),
                PopupMenuItem(
                    icon=Icons.STAR,
                    text='收藏',
                    checked=self.note_info.get('favorite'),
                    on_click=self.on_make_note_favorite
                ),
                Divider(thickness=1, color=Colors.GREY_100),
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
        title_bar = Container(
            content=Row(
                controls=[
                    IconButton(icon=Icons.ARROW_BACK,
                               icon_color=Colors.WHITE,
                               on_click=self.on_button_back_click),
                    note_menu_btn,
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN
            ),
            height=45,
            border_radius=3,
            bgcolor=Colors.BLUE_600,
            padding=padding.all(0),
        )

        # 标题及内容
        self.edit_title = TextField(
            value=self.note_info.get('title'),
            read_only=True,
            border=InputBorder.UNDERLINE,
            border_color=Colors.BLACK26,
        )
        match NoteType(self.note_info.get('note_type')):
            case NoteType.MarkdownNote:
                self.note_view = Markdown(
                    value=self.note_info.get('content'),
                    # expand=True,
                )
            case NoteType.RichNote:
                self.note_view = WebView(
                    url="data:text/html;charset=utf-8," + self.note_info.get('rich_content'),
                    height=self.page.height - 110,
                    expand=True,
                )
            case NoteType.PDFNote:
                self.note_view = WebView(
                    url=self.note_info.get('picture_content'),
                    height=self.page.height - 110,
                    expand=True,
                )
            case _:
                self.note_view = Text(
                    value=self.note_info.get('content'),
                    no_wrap=False,
                    # expand=True
                )
        # 布局
        cols_body = Column(
            controls=[
                title_bar,
                self.edit_title,
                Column(
                    controls=[self.note_view],
                    # auto_scroll=True,
                    scroll=ScrollMode.AUTO
                )
            ],
        )
        return cols_body
