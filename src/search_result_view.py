# coding:utf-8
import httpx
from flet import Column, Row, Icons, Colors
from flet.core import border, padding
from flet.core.app_bar import AppBar
from flet.core.border import BorderSide, BorderSideStrokeAlign
from flet.core.box import BoxShadow
from flet.core.container import Container
from flet.core.icon_button import IconButton
from flet.core.list_view import ListView
from flet.core.progress_bar import ProgressBar
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.text import Text
from flet.core.types import MainAxisAlignment, CrossAxisAlignment


class SearchResultView(Column):
    def __init__(self, page, str_keyword):
        super().__init__()
        self.page = page
        self.str_keyword:str = str_keyword

        content = self.build_interface()
        self.controls = [content]
        self.page.appbar = AppBar(
            title=Text(f'搜索结果:{self.str_keyword}'),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
            leading=IconButton(
                icon=Icons.ARROW_BACK,
                tooltip='返回',
                on_click=self.on_btn_back_click,
            ),
            actions=[],
        )
        self.page.floating_action_button = None
        self.page.drawer = None
        self.page.run_task(self.query_diary_list, str_keyword)

    async def query_diary_list(self, str_keyword):
        self.progress_bar.visible = True
        self.page.update()
        self.note_list.controls.clear()
        req_url = f'https://restapi.10qu.com.cn/diary_search?keyword={str_keyword}'
        token = await self.page.client_storage.get_async('token')
        headers = {"Authorization": f'Bearer {token}'}
        try:
            diary_list = []
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    req_url,
                    headers=headers,
                )
                resp.raise_for_status()
                if resp.status_code != 200:
                    snack_bar = SnackBar(Text("搜索用户日记列表请求失败，请刷新重试。"))
                    self.page.overlay.append(snack_bar)
                    snack_bar.open = True
                    self.progress_bar.visible = False
                    self.page.update()
                    return
                data = resp.json()
                diaries = data.get('result')
                if not diaries:
                    self.progress_bar.visible = False
                    self.page.update()
                    return
                for diary in diaries:
                    diary_info = diary
                    dct_diary = {
                        'diary_id': diary.get('id'),
                        'diary_date': diary.get('date'),
                        'diary_type': diary.get('diary_type'),
                        'diary_type_color': diary_info.get('diary_type__colour'),
                        'diary_text': diary_info.get('content_html'),
                        'diary_weather': diary_info.get('weather'),
                        'diary_location': diary_info.get('location'),
                        'diary_mood': diary_info.get('mood'),
                        'create_time': diary_info.get('create_time'),
                        'update_time': diary_info.get('update_time'),
                    }
                    diary_list.append(dct_diary)
            for diary in diary_list:
                if not diary.get('diary_text'):
                    continue
                diary_date = diary.get('diary_date')
                diary_text = diary.get('diary_text')
                diary_location = diary.get('diary_location')
                diary_weather = diary.get('diary_weather')
                diary_item = Container(
                    content=Row(
                        controls=[
                            Container(
                                bgcolor=diary.get('diary_type_color') if diary.get('diary_type_color') else Colors.BLUE,
                                width=3,
                                height=25,
                                padding=padding.only(left=0, top=3, right=5, bottom=3)
                            ),
                            Column(
                                controls=[
                                    Row(
                                        controls=[
                                            Text(
                                                value=diary_date,
                                                size=12,
                                                color=Colors.BLUE_600
                                            ),
                                            Container(expand=True),
                                            Text(
                                                value=diary_weather,
                                                size=12,
                                                color=Colors.BLUE_600
                                            ),
                                            Text(
                                                value=diary_location,
                                                no_wrap=False,
                                                size=12,
                                                color=Colors.BLUE_600),
                                        ]
                                    ),
                                    Text(value=diary_text,
                                         size=16,
                                         no_wrap=False,
                                         color=Colors.BLACK87),

                                ],
                            ),
                        ],
                    ),
                    data=diary,
                    margin=3,
                    adaptive=True,
                    border_radius=2,
                    height=80,
                    on_click=self.on_diary_item_click,
                    border=border.only(
                        None, None, None,
                        BorderSide(1, Colors.GREY_200, BorderSideStrokeAlign.OUTSIDE)),
                    shadow=BoxShadow(spread_radius=0, blur_radius=0,
                                     color=Colors.WHITE, offset=(1, 1)),
                )
                self.note_list.controls.append(diary_item)
                self.page.update()
        except httpx.HTTPError as e:
            snack_bar = SnackBar(Text(f"查询用户日记列表请求失败，请刷新重试。{str(e)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.progress_bar.visible = False
            self.page.update()
            return
        self.progress_bar.visible = False
        self.page.update()

    async def on_button_refresh_click(self, e):
        await self.query_diary_list(self.str_keyword)

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

    def on_btn_back_click(self, e):
        self.page.controls.clear()
        from search_diary_view import SearchDiaryView
        page_view = SafeArea(
            SearchDiaryView(self.page),
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()

    def build_interface(self):
        # 笔记列表
        self.note_list = ListView(
            spacing=10,
            padding=5,
            # height=self.page.height - 120
            expand=True,
        )
        self.progress_bar = ProgressBar(
            value=None,
            bar_height=3,
            bgcolor=Colors.GREY_100,
            color=Colors.GREY_300,
            width=self.page.width,
            visible=False,
        )
        col_notes = Column(
            controls = [
                self.progress_bar,
                self.note_list,
            ],
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.START,
            adaptive=True,
            width=self.page.width,
        )
        return col_notes
