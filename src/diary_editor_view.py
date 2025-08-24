from datetime import date, datetime

from flet.core import padding
from flet.core.app_bar import AppBar
from flet.core.bottom_app_bar import BottomAppBar
from flet.core.bottom_sheet import BottomSheet
from flet.core.colors import Colors
from flet.core.column import Column
from flet.core.container import Container
from flet.core.date_picker import DatePicker
from flet.core.form_field_control import InputBorder
from flet.core.icon_button import IconButton
from flet.core.icons import Icons
from flet.core.row import Row
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.textfield import TextField
from flet.core.types import MainAxisAlignment, ScrollMode, CrossAxisAlignment, FontWeight

from src.api_request import APIRequest
from components.custom_text_field import CustomTextField


class DiaryEditorView(Column):
    def __init__(self, page, diary_info):
        super().__init__()
        self.page = page
        self.diary_info = diary_info
        self.diary_date = diary_info.get('diary_date') if self.diary_info is not None else date.today().strftime('%Y-%m-%d')
        self.dest_notebook_id = None
        self.dest_notebook_name = None

        self.controls = [self.build_interface()]
        self.page.appbar = AppBar(
            title=Text(''),
            bgcolor=Colors.BLUE,
            leading=IconButton(
                icon=Icons.SAVE,
                tooltip='保存并返回',
                on_click=self.on_button_save_click,
            ),
            actions=[
                IconButton(icon=Icons.CANCEL,
                           tooltip='取消保存',
                           on_click=self.on_button_cancel_click),
            ],
        )
        self.page.bottom_appbar = BottomAppBar(
            bgcolor=Colors.BLUE,
            content=Row(
                controls=[
                    IconButton(
                        icon=Icons.UNDO,
                        icon_color=Colors.WHITE,
                        tooltip='撤销',
                        on_click=self.on_button_undo_click
                    ),
                    IconButton(
                        icon=Icons.REDO,
                        icon_color=Colors.WHITE,
                        tooltip='重做',
                        on_click=self.on_button_redo_click
                    ),
                ]
            )
        )
        self.page.floating_action_button = None
        self.page.drawer = None

    def on_button_save_click(self, e):
        str_content = self.editor.value
        if self.diary_info is None:
            resp = APIRequest.add_note(
                self.page.client_storage.get('token'),
                self.page.client_storage.get('user_id'),
                self.dest_notebook_id,
                str_title,
                str_content,
                NoteType.TextNote.value
            )
            content_data = [{'insert': str_content}]
            user_input = {'user': self.page.client_storage.get('user_id'),
                          'diary_type': diary_type,
                          'question': None,
                          'bmob_id': None,
                          'weather': weather,
                          'location': location,
                          'img_list': None,
                          'mood': mood,
                          'content_data': content_data,
                          'content_html': str_content,
                          'date': diary_date}
        else:
            resp = APIRequest.update_note(
                self.page.client_storage.get('token'),
                self.note_info.get('id'),
                self.page.client_storage.get('user_id'),
                self.note_info.get('notebook'),
                str_title,
                str_content,
                self.note_info.get('note_type'),
                self.note_info.get('favorite', False),
                self.note_info.get('delete_flag', False),
                self.note_info.get('top_flag', False)
            )
        if resp.status_code not in [200, 201]:
            snack_bar = SnackBar(Text("笔记保存失败!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
        self.page.go('/main_view')

    def on_button_undo_click(self, e):
        self.editor.undo()

    def on_button_redo_click(self, e):
        self.editor.redo()

    def on_button_cancel_click(self, e):
        self.page.controls.clear()
        from main_view import MainView
        page_view = SafeArea(
            MainView(self.page),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_date_picker_changed(self, e):
        today = e.control.value.date()
        self.diary_date = today.strftime('%Y-%m-%d')
        str_today = f'{today.year}年{today.month}月{today.day}日,{['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]}'
        btn_sel_date = self.controls[0].controls[0].controls[0]
        if btn_sel_date:
            btn_sel_date.text = str_today
            e.control.page.update()

    def build_interface(self):
        if self.diary_info is not None:
            today = datetime.strptime(self.diary_date, '%Y-%m-%d')
        else:
            today = date.today()
        str_today = f'{today.year}年{today.month}月{today.day}日,{['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]}'
        TextButton(
            str_today,
            icon=Icons.CALENDAR_TODAY,
            on_click=lambda e: e.control.page.open(
                DatePicker(
                    value=today,
                    open=True,
                    on_change=self.on_date_picker_changed,
                )
            )
        ),
        buttons_row = Row(
            controls=[
                TextButton(
                    str_today,
                    icon=Icons.CALENDAR_TODAY,
                    on_click=lambda e: e.control.page.open(
                        DatePicker(
                            value=date.today(),
                            open=True,
                            on_change=self.on_date_picker_changed,
                        )
                    )
                ),
                TextButton('心情', icon=Icons.ADD),
                TextButton('天气', icon=Icons.ADD),
                TextButton('城市', icon=Icons.LOCATION_CITY),
                TextButton('类型', icon=Icons.LABEL),
            ],
            wrap=True,
        )
        self.editor = CustomTextField(
            value='',
            hint_text='正文',
            multiline=True,
            expand=True,
            height=self.page.height - 20,
        )
        if self.diary_info is not None:
            self.editor.value = self.diary_info.get('diary_text')

        # 布局
        cols_body = Column(
            controls=[
                buttons_row,
                self.editor
            ],
            expand=True,
            scroll=ScrollMode.AUTO,
        )
        return cols_body
