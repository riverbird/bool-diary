# coding:utf-8
import json

from flet.core.app_bar import AppBar
from flet.core.border import Border, BorderSide
from flet.core.colors import Colors
from flet.core.column import Column
from flet.core.container import Container
from flet.core.icon import Icon
from flet.core.icon_button import IconButton
from flet.core.icons import Icons
from flet.core.list_view import ListView
from flet.core.row import Row
from flet.core.safe_area import SafeArea
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.textfield import TextField

class SearchDiaryView(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.controls = [self.build_interface()]

        tf_search = TextField(
            hint_text='搜索笔记',
            color=Colors.WHITE,
            border_width=0,
            bgcolor=Colors.BLUE_600,
            expand=True,
            adaptive=True,
            on_submit=self.on_search_note,
        )
        self.page.appbar = AppBar(
            title=tf_search,
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            leading=IconButton(
                icon=Icons.ARROW_BACK,
                tooltip='返回',
                on_click=self.on_button_back_click,
            ),
        )
        self.page.floating_action_button = None
        self.page.drawer = None

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


    def on_search_note(self, e):
        str_keyword = e.control.value
        raw = self.page.client_storage.get('search_history')
        history = json.loads(raw) if raw else []
        history.append(str_keyword)
        self.page.client_storage.set('search_history', json.dumps(history))

        self.page.controls.clear()
        from search_result_view import SearchResultView
        page_view = SafeArea(
            SearchResultView(self.page, str_keyword),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_query_diary(self, e):
        str_keyword = e.control.data
        self.page.controls.clear()
        from search_result_view import SearchResultView
        page_view = SafeArea(
            SearchResultView(self.page, str_keyword),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def on_btn_remove_history_click(self, e):
        if self.page.client_storage.remove('search_history'):
            self.controls[0].controls[0].clean()

    def build_interface(self):
        # 搜索历史
        search_history_value = self.page.client_storage.get('search_history')
        search_history = json.loads(search_history_value) if search_history_value else []
        history_list = []
        for item in search_history:
            history_item_list = Container(
                content=Row(
                    controls=[
                        Icon(name=Icons.SEARCH),
                        Text(value=item, expand=True),
                    ],
                ),
                border=Border(
                    bottom=BorderSide(
                        width=1,
                        color=Colors.GREY_200,
                    )
                ),
                data = item,
                on_click=lambda e: self.on_query_diary(e),
            )
            history_list.append(history_item_list)
        list_history = ListView(
            controls = history_list,
            spacing=10,
            adaptive=True,
        )
        # 清空历史
        btn_remove_history = Row(
            controls=[
                TextButton(
                    text='清空输入历史',
                    on_click=self.on_btn_remove_history_click,
                ),
                Container(expand=True),
                Icon(name=Icons.DELETE),
            ]
        )

        # 布局
        cols_body = Column(
            controls=[
                # title_bar,
                list_history,
                btn_remove_history,
            ],
        )
        return cols_body
