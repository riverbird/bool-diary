# diary_editor_view.py
from asyncio import Future
from datetime import date, datetime
import tempfile
from pathlib import Path

import httpx

from flet.core import dropdown, alignment
from flet.core.alert_dialog import AlertDialog
from flet.core.app_bar import AppBar
from flet.core.colors import Colors
from flet.core.column import Column
from flet.core.container import Container
from flet.core.date_picker import DatePicker
from flet.core.dropdown import Dropdown
from flet.core.file_picker import FilePicker
from flet.core.icon import Icon
from flet.core.icon_button import IconButton
from flet.core.icons import Icons
from flet.core.image import Image
from flet.core.progress_bar import ProgressBar
from flet.core.row import Row
from flet.core.safe_area import SafeArea
from flet.core.snack_bar import SnackBar
from flet.core.stack import Stack
from flet.core.text import Text
from flet.core.text_button import TextButton
from flet.core.textfield import TextField
from flet.core.types import MainAxisAlignment, ScrollMode, ImageFit
from PIL import Image as PImage

from components.custom_text_field import CustomTextField
from common import diary_type_manager


class DiaryEditorView(Column):
    def __init__(self, page, diary_info):
        super().__init__()
        self.page = page
        self.diary_info = diary_info
        self.diary_date = diary_info.get('diary_date') if self.diary_info is not None else date.today().strftime('%Y-%m-%d')
        self.diary_mood = diary_info.get('diary_mood') if self.diary_info is not None else 0
        self.diary_weather = diary_info.get('diary_weather') if self.diary_info is not None else '晴'
        self.diary_location = diary_info.get('diary_location') if self.diary_info is not None else ''
        # self.diary_category_list = self.get_diary_type_list()
        # self.diary_category_list = SingletonList().diary_type_list
        self.diary_category_list = diary_type_manager.global_diary_type_list
        self.diary_type = diary_info.get('diary_type') if self.diary_info is not None else None

        # 心情对话框
        self.dropdown_emoji = Dropdown(
                        # width=120,
                        options=[
                            dropdown.Option('0', '普通'),
                            dropdown.Option('1', '微笑'),
                            dropdown.Option('2', '开心'),
                            dropdown.Option('3', '难过'),
                            dropdown.Option('4', '调皮'),
                            dropdown.Option('5', '偷着乐'),
                            dropdown.Option('6', '惊讶'),
                            dropdown.Option('7', '酷'),
                            dropdown.Option('8', '无奈'),
                            dropdown.Option('9', '难受'),
                            dropdown.Option('10', '怒'),
                            dropdown.Option('11', '大哭'),
                            dropdown.Option('12', '紧张')
                        ]
        )
        self.dlg_emoji = AlertDialog(
            modal=True,
            title=Text('心情'),
            content=Column(
                controls=[self.dropdown_emoji],
                alignment=MainAxisAlignment.CENTER,
                # width=300,
                height=80,
            ),
            actions=[
                TextButton("确定", on_click=self.on_emoji_ok_click),
                TextButton('取消', on_click=self.on_emoji_cancel_click),
            ],
            actions_alignment=MainAxisAlignment.END,
        )
        # 天气对话框
        self.dropdown_weather = Dropdown(
            # width=120,
            options=[
                dropdown.Option('晴', '晴'),
                dropdown.Option('阴', '阴'),
                dropdown.Option('多云', '多云'),
                dropdown.Option('阵雨', '阵雨'),
                dropdown.Option('小雨', '小雨'),
                dropdown.Option('中雨', '中雨'),
                dropdown.Option('大雨', '大雨'),
                dropdown.Option('暴雨', '暴雨'),
                dropdown.Option('雷阵雨', '雷阵雨'),
                dropdown.Option('小雪', '小雪'),
                dropdown.Option('中雪', '中雪'),
                dropdown.Option('大雪', '大雪'),
                dropdown.Option('暴雪', '暴雪'),
                dropdown.Option('暴雪', '暴雪'),
                dropdown.Option('雨夹雪', '雨夹雪'),
                dropdown.Option('雾', '雾'),
                dropdown.Option('霾', '霾'),
                dropdown.Option('沙尘暴', '沙尘暴'),
                dropdown.Option('冰雹', '冰雹')
            ]
        )
        self.dlg_weather = AlertDialog(
            modal=True,
            title=Text('天气'),
            content=Column(
                controls=[self.dropdown_weather],
                alignment=MainAxisAlignment.CENTER,
                # width=300,
                height=80,
            ),
            actions=[
                TextButton("确定", on_click=self.on_weather_ok_click),
                TextButton('取消', on_click=self.on_weather_cancel_click),
            ],
            actions_alignment=MainAxisAlignment.END,
        )

        # 城市/位置对话框
        self.tf_location = TextField(hint_text='所在城市或位置')
        self.dlg_location = AlertDialog(
            modal=True,
            title=Text('位置'),
            content=Column(
                controls=[self.tf_location],
                alignment=MainAxisAlignment.CENTER,
                # width=300,
                height=80,
            ),
            actions=[
                TextButton("确定", on_click=self.on_location_ok_click),
                TextButton('取消', on_click=self.on_location_cancel_click),
            ],
            actions_alignment=MainAxisAlignment.END,
        )

        # 分类对话框
        self.dropdown_category = Dropdown()
        self.dlg_category = AlertDialog(
            modal=True,
            title=Text('日记分类'),
            content=Column(
                controls=[self.dropdown_category],
                alignment=MainAxisAlignment.CENTER,
                # width=300,
                height=80,
            ),
            actions=[
                TextButton("确定", on_click=self.on_category_ok_click),
                TextButton('取消', on_click=self.on_category_cancel_click),
            ],
            actions_alignment=MainAxisAlignment.END,
        )
        self.page.appbar = AppBar(
            title=Text(''),
            bgcolor=Colors.BLUE,
            color=Colors.WHITE,
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

        self.page.floating_action_button = None
        self.page.drawer = None
        # self.init_diary_type()
        self.controls = [
            self.build_interface(),
            self.dlg_emoji,
            self.dlg_weather,
            self.dlg_location,
            self.dlg_category,
        ]

    def init_diary_type(self):
        if self.diary_category_list is None:
            # self.diary_category_list = self.get_diary_type_list()
            self.diary_category_list = diary_type_manager.global_diary_type_list
        if self.diary_category_list:
            diary_category_name = next(
                (opt.get('type_name') for opt in self.diary_category_list if opt.get('id') == self.diary_type),
                '分类'
            )
        else:
            diary_category_name = '分类'
        btn_sel_category = self.controls[0].controls[0].controls[4]
        if btn_sel_category:
            btn_sel_category.text = diary_category_name
            # self.page.update()

    def show_emoji_dialog(self, e):
        self.dlg_emoji.open = True
        self.dropdown_emoji.value = str(self.diary_mood)
        e.control.page.update()
        self.page.update()

    def on_emoji_ok_click(self, e):
        self.dlg_emoji.open = False
        if self.dropdown_emoji.value is not None:
            self.diary_mood = int(self.dropdown_emoji.value)
        btn_sel_mood = self.controls[0].controls[0].controls[1]
        if btn_sel_mood:
            btn_sel_mood.text = next(
                (opt.text for opt in self.dropdown_emoji.options if opt.key == self.dropdown_emoji.value),
                '普通'
        )
            e.control.page.update()
        self.page.update()

    def on_emoji_cancel_click(self, e):
        self.dlg_emoji.open = False
        self.page.update()

    def show_weather_dialog(self, e):
        self.dlg_weather.open = True
        self.dropdown_weather.value = self.diary_weather
        e.control.page.update()
        self.page.update()

    def on_weather_ok_click(self, e):
        self.dlg_weather.open = False
        self.diary_weather = self.dropdown_weather.value
        btn_sel_weather = self.controls[0].controls[0].controls[2]
        if btn_sel_weather:
            btn_sel_weather.text = next(
                (opt.text for opt in self.dropdown_weather.options if opt.key == self.dropdown_weather.value),
                '晴'
            )
            e.control.page.update()
        self.page.update()

    def on_weather_cancel_click(self, e):
        self.dlg_weather.open = False
        self.page.update()

    def show_current_location(self, e):
        # gl = Geolocator(
        #     location_settings=GeolocatorSettings(
        #         accuracy=GeolocatorPositionAccuracy.LOW
        #     ),
        #     on_position_change=handle_position_change,
        #     on_error=lambda e: page.add(ft.Text(f"Error: {e.data}")),
        # )
        # location_service_enabled = gl.is_location_service_enabled(wait_timeout=10)
        # if not location_service_enabled:
        #     self.page.dialog = AlertDialog(title="错误", content=Text("请开启位置服务"))
        #     self.page.dialog.open = True
        #     return
        # # 检查定位权限
        # permission = gl.get_permission_status(wait_timeout=10)
        # if permission == GeolocatorPermissionStatus.DENIED_FOREVER:
        #     self.page.dialog = AlertDialog(title="错误", content=Text("定位权限被永久拒绝."))
        #     self.page.dialog.open = True
        #     return
        # elif permission == GeolocatorPermissionStatus.DENIED:
        #     permission = gl.request_permission(wait_timeout=10)
        #     if permission != GeolocatorPermissionStatus.ALWAYS:
        #         self.page.dialog = AlertDialog(title="错误", content=Text("定位权限未授予"))
        #         self.page.dialog.open = True
        #         return
        # position = gl.get_current_position(wait_timeout=10)
        # if position is not None:
        #     return position
        self.dlg_location.open = True
        self.tf_location.value = self.diary_location
        e.control.page.update()
        self.page.update()

    def on_location_ok_click(self, e):
        self.dlg_location.open = False
        self.diary_location = self.tf_location.value
        btn_sel_location = self.controls[0].controls[0].controls[3]
        if btn_sel_location:
            btn_sel_location.text = self.tf_location.value
            e.control.page.update()
        self.page.update()

    def on_location_cancel_click(self, e):
        self.dlg_location.open = False
        self.page.update()

    def show_category_dialog(self, e):
        if self.diary_category_list is None:
            # self.diary_category_list = self.get_diary_type_list()
            self.diary_category_list = diary_type_manager.global_diary_type_list
        if self.diary_category_list:
            self.dropdown_category.clean()
            for diary in self.diary_category_list:
                self.dropdown_category.options.append(
                    dropdown.Option(
                        str(diary.get('id')),
                        diary.get('type_name')
                    )
                )
        if self.diary_type is not None:
            self.dropdown_category.value = str(self.diary_type)
            e.control.page.update()
        self.dlg_category.open = True
        self.page.update()

    def on_category_ok_click(self, e):
        self.dlg_category.open = False
        selected_category = self.dropdown_category.value
        if selected_category is not None:
            self.diary_type = int(selected_category)
        btn_sel_category = self.controls[0].controls[0].controls[4]
        if btn_sel_category:
            btn_sel_category.text = next(
                (opt.text for opt in self.dropdown_category.options if opt.key == self.dropdown_category.value),
                None
            )
            e.control.page.update()
        self.page.update()

    def on_category_cancel_click(self, e):
        self.dlg_category.open = False
        self.page.update()

    # def get_diary_type_list(self) -> list|None:
    #     cached_diary_type_list_value = self.page.client_storage.get('diary_type_list')
    #     cached_diary_type_list = json.loads(cached_diary_type_list_value) if cached_diary_type_list_value else []
    #     if cached_diary_type_list:
    #         return cached_diary_type_list
    #     user_id = self.page.client_storage.get('user_id')
    #     token = self.page.client_storage.get('token')
    #     url = f'https://restapi.10qu.com.cn/diarytype?user={user_id}'
    #     headers = {"Authorization": f'Bearer {token}'}
    #     resp = httpx.get(url, headers=headers, follow_redirects=True)
    #     if resp.status_code != 200:
    #         return None
    #     resp.raise_for_status()
    #     data = resp.json()
    #     lst_category = data.get('results')
    #     cached_diary_type_list_str = json.dumps(lst_category)
    #     self.page.client_storage.set('diary_type_list', cached_diary_type_list_str)
    #     return lst_category

    def on_date_picker_changed(self, e):
        today = e.control.value.date()
        self.diary_date = today.strftime('%Y-%m-%d')
        str_today = f'{today.year}年{today.month}月{today.day}日,{['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]}'
        btn_sel_date = self.controls[0].controls[0].controls[0]
        if btn_sel_date:
            btn_sel_date.text = str_today
            e.control.page.update()

    async def on_button_save_click(self, e):
        str_content = self.editor.value
        self.progress_bar.visible = True
        self.page.update()
        token = await self.page.client_storage.get_async('token')
        user_id = await self.page.client_storage.get_async('user_id')
        image_list = [x.data for x in self.row_images.controls if x.data is not None]
        content_data = [{'insert': str_content}]
        user_input = {'user': user_id,
                      'diary_type': self.diary_type,
                      'question': None,
                      'bmob_id': None,
                      'weather': self.diary_weather,
                      'location': self.diary_location,
                      'img_list': image_list,
                      'mood': self.diary_mood,
                      'content_data': content_data,
                      'content_html': str_content,
                      'date': self.diary_date}
        headers = {"Authorization": f'Bearer {token}'}
        if self.diary_info is None:
            url = f'https://restapi.10qu.com.cn/diary/'
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.post(
                        url,
                        headers=headers,
                        json=user_input,
                    )
                    resp.raise_for_status()
                    if resp.status_code != 201:
                        snack_bar = SnackBar(Text("笔记保存失败!"))
                        e.control.page.overlay.append(snack_bar)
                        snack_bar.open = True
                        e.control.page.update()
                        self.progress_bar.visible = False
                        self.page.update()
                        return
            except httpx.HTTPError as ex:
                snack_bar = SnackBar(Text(f"保存日记失败:{str(ex)}"))
                e.control.page.overlay.append(snack_bar)
                snack_bar.open = True
                e.control.page.update()
                self.progress_bar.visible = False
                self.page.update()
                return
            data = resp.json()
            diary_data = {
                'diary_id': data.get('id'),
                'diary_date': data.get('date'),
                'diary_type': data.get('diary_type'),
                'diary_type__colour': data.get('diary_type__colour'),
                'diary_text': data.get('content_html'),
                'diary_weather': data.get('weather'),
                'diary_location': data.get('location'),
                'diary_mood': data.get('mood'),
                'diary_image_list': data.get('img_list'),
                'create_time': data.get('create_time'),
                'update_time': data.get('update_time'),
            }
            self.progress_bar.visible = False
            self.page.update()

            self.page.controls.clear()
            from diary_detail_view import DiaryDetailView
            page_view = SafeArea(
                DiaryDetailView(self.page, diary_data),
                adaptive=True,
                expand=True
            )
            self.page.controls.append(page_view)
            self.page.update()
        else:
            url = f'https://restapi.10qu.com.cn/diary/{self.diary_info.get("diary_id")}/'
            user_input['diary_type_id'] = self.diary_type
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.put(
                        url,
                        headers=headers,
                        json=user_input,
                    )
                    resp.raise_for_status()
                    if resp.status_code != 200:
                        snack_bar = SnackBar(Text("日记更新失败!"))
                        e.control.page.overlay.append(snack_bar)
                        snack_bar.open = True
                        e.control.page.update()
                        return
            except httpx.HTTPError as ex:
                snack_bar = SnackBar(Text(f"更新日记失败:{str(ex)}"))
                e.control.page.overlay.append(snack_bar)
                snack_bar.open = True
                e.control.page.update()
                self.progress_bar.visible = False
                self.page.update()
                return

            self.progress_bar.visible = False
            self.page.update()

            self.page.controls.clear()
            from main_view import MainView
            page_view = SafeArea(
                MainView(self.page),
                adaptive=True,
                expand=True
            )
            self.page.controls.append(page_view)
            self.page.update()


    def on_button_undo_click(self, e):
        self.editor.undo()

    def on_button_redo_click(self, e):
        self.editor.redo()

    def compress_image(self, input_path: str, output_path: str, quality: int = 70, max_size=(800, 800)):
        """
        压缩图片
        :param input_path: 输入图片路径
        :param output_path: 输出图片路径
        :param quality: JPEG 质量（1-100）
        :param max_size: 最大宽高，超过会等比缩放
        """
        with PImage.open(input_path) as img:
            # 等比缩放
            img.thumbnail(max_size)
            # 保存为压缩后的文件
            img.save(output_path, optimize=True, quality=quality)

    async def upload_file(self, file_path):
        url = "https://restapi.10qu.com.cn/image_to_url/"
        # file_size = os.path.getsize(file_path)
        image_url = None
        token = await self.page.client_storage.get_async('token')
        headers = {"Authorization": f'Bearer {token}'}
        async with httpx.AsyncClient(timeout=None) as client:
            with open(file_path, "rb") as f:
                # uploaded = 0
                # chunk_size = 1024 * 64  # 每次上传64KB
                # async with client.stream("POST", url, files={"file": ("filename", f, "image/jpeg")}) as resp:
                #     async for chunk in resp.aiter_bytes():
                #         uploaded += len(chunk)
                #         progress = uploaded / file_size
                #         progress_bar.value = min(progress, 1.0)
                #         page.update()
                # files = {"file": (os.path.basename(file_path), f, "image/jpeg")}
                files = {'img': open(file_path, 'rb')}
                resp = await client.post(url, headers=headers, files=files)
                if resp.status_code == 200:
                    self.page.snack_bar = SnackBar(Text("上传完成！"))
                    image_url = resp.json().get('results')
                else:
                    self.page.snack_bar = SnackBar(Text(f"上传失败:{resp.text}"))
        # progress_bar.value = 1
        # 删除本地临时文件
        # temp_file = Path(file_path)
        # if temp_file.exists():
        #     temp_file.unlink()
        self.page.snack_bar.open = True
        self.page.update()
        return image_url

    def handle_uploaded_file(self, t:Future[str]):
        try:
            res = t.result()
        except Exception as ex:
            snack_bar = SnackBar(Text(f"获取照片地址失败:{str(ex)}"))
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.progress_bar.visible = False
            self.page.update()
        else:
            if not res:
                return
            image_url = res
            spacing = 40
            container_width = (self.page.width - spacing * 2) / 3
            image_container = Container(
                width=container_width,
                height=container_width,
                border_radius=5,
                content=Image(src=image_url, fit=ImageFit.COVER,
                                  width=container_width, height=container_width),
            )
            image_overlay = Container(
                content=Icon(
                    name=Icons.REMOVE,  # 减号图标
                    size=50,
                    color=Colors.RED,
                ),
                alignment=alignment.center,  # 居中放置
                bgcolor=Colors.with_opacity(0.5, Colors.BLACK),  # 半透明灰色
                width=container_width,
                height=container_width,
                border_radius=5,
                on_click=self.on_remove_image,
            )
            stacked = Stack(
                controls=[image_container, image_overlay],
                data=image_url
            )
            self.row_images.controls.insert(0,stacked)
            self.progress_bar.visible = False
            self.page.update()

    def on_remove_image(self, e):
        parent_stack = e.control.parent
        if parent_stack in self.row_images.controls:
            self.row_images.controls.remove(parent_stack)
            self.page.update()

    def on_file_picked(self, e):
        if e.files:
            file_path = e.files[0].path
            local_file_path = file_path
            # self.page.add(Text(f"选择文件: {file_path}"))
            # self.page.add(progress_bar)
            self.progress_bar.visible = True
            self.page.update()
            try:
                # with tempfile.TemporaryDirectory() as tmp_dir_name:
                tmp_dir_name = tempfile.gettempdir()
                compress_path = Path(tmp_dir_name) / Path("temp_photo.jpg")
                self.compress_image(file_path, compress_path.as_posix(), quality=85)
                local_file_path = compress_path.as_posix()
            except Exception as ex:
                snack_bar = SnackBar(Text(f"图片压缩失败，将以原图进行上传:{str(ex)}"))
                e.control.page.overlay.append(snack_bar)
                snack_bar.open = True
                e.control.page.update()
            else:
                local_file_path = compress_path.as_posix()
                # # 开启异步任务上传
            task_upload_file = self.page.run_task(self.upload_file, local_file_path)
            task_upload_file.add_done_callback(self.handle_uploaded_file)

    def on_add_picture(self, e):
        if len(self.row_images.controls) >= 10:
            snack_bar = SnackBar(Text("最多支持9张照片上传!"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        file_picker = FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["jpg", "png"],
        )

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

    def build_interface(self):
        # 日记日期
        if self.diary_info is not None:
            today = datetime.strptime(self.diary_date, '%Y-%m-%d')
        else:
            today = date.today()
        str_today = f'{today.year}年{today.month}月{today.day}日,{['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]}'
        # TextButton(
        #     str_today,
        #     icon=Icons.CALENDAR_TODAY,
        #     on_click=lambda e: e.control.page.open(
        #         DatePicker(
        #             value=today,
        #             open=True,
        #             on_change=self.on_date_picker_changed,
        #         )
        #     )
        # ),
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
                    on_click=lambda e: e.control.page.open(
                        DatePicker(
                            value=today,
                            open=True,
                            on_change=self.on_date_picker_changed,
                        )
                    )
                ),
                TextButton(
                    mood_set[self.diary_mood],
                    icon=Icons.ADD,
                    on_click=self.show_emoji_dialog,
                ),
                TextButton(
                    self.diary_weather,
                    icon=Icons.ADD,
                    on_click=self.show_weather_dialog,
                ),
                TextButton(
                    self.diary_location if self.diary_location else '城市',
                    icon=Icons.LOCATION_CITY,
                    on_click=self.show_current_location,
                ),
                TextButton(
                    diary_category_name,
                    icon=Icons.LABEL,
                    on_click=self.show_category_dialog,
                ),
            ],
            wrap=True,
        )
        self.editor = CustomTextField(
            value='',
            hint_text='正文',
            multiline=True,
            expand=True,
        )
        if self.diary_info is not None:
            self.editor.value = self.diary_info.get('diary_text')

        # 进度条
        self.progress_bar = ProgressBar(
            value=None,
            bar_height=3,
            bgcolor=Colors.GREY_100,
            color=Colors.GREY_300,
            width=self.page.width,
            visible=False
        )
        # 操作栏
        row_ops = Row(
            alignment=MainAxisAlignment.START,
            spacing=0,
            controls=[
                IconButton(
                    icon=Icons.UNDO,
                    tooltip='撤销',
                    on_click=self.on_button_undo_click
                ),
                IconButton(
                    icon=Icons.REDO,
                    tooltip='重做',
                    on_click=self.on_button_redo_click
                ),
            ]
        )
        self.ops_toolbar = Container(
            content=row_ops,
        )
        # 照片
        spacing = 40
        container_width = (self.page.width - spacing * 2) / 3
        self.row_images = Row(
            controls=[
                Container(
                    width=container_width,
                    height=container_width,
                    bgcolor=Colors.GREY_200,
                    alignment=alignment.center,
                    border_radius=5,
                    content=Icon(name=Icons.ADD),
                    on_click=self.on_add_picture,
                )
            ],
            wrap=True
        )
        if self.diary_info is not None:
            diary_image_list = self.diary_info.get('diary_image_list')
            if diary_image_list:
                for image_url in diary_image_list:
                    image_container = Container(
                        width=container_width, height=container_width,
                        border_radius=5,
                        content=Image(src=image_url, fit=ImageFit.COVER,
                                      width=container_width, height=container_width),
                    )
                    image_overlay = Container(
                        content=Icon(
                            name=Icons.REMOVE,  # 减号图标
                            size=50,
                            color=Colors.RED,
                        ),
                        alignment=alignment.center,  # 居中放置
                        bgcolor=Colors.with_opacity(0.5, Colors.BLACK),  # 半透明灰色
                        width=container_width,
                        height=container_width,
                        border_radius=5,
                        on_click=self.on_remove_image,
                    )
                    stacked = Stack(
                        controls=[image_container, image_overlay],
                        data=image_url
                    )
                    self.row_images.controls.insert(0, stacked)
        # 布局
        cols_body = Column(
            controls=[
                buttons_row,
                self.ops_toolbar,
                self.editor,
                self.row_images,
                self.progress_bar,
            ],
            expand=True,
            scroll=ScrollMode.AUTO,
            alignment=MainAxisAlignment.SPACE_BETWEEN
        )
        return cols_body
