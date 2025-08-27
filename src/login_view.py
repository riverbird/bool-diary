# coding:utf-8
import json
from enum import Enum

from flet import Text, Card, Container, Column, Row, TextButton, TextField, Image, \
    FilledButton, Tabs, Tab, Colors, border_radius, \
    SnackBar
from flet.core.form_field_control import InputBorder
from flet.core.icons import Icons
from flet.core.progress_ring import ProgressRing
from flet.core.safe_area import SafeArea
from flet.core.types import MainAxisAlignment, CrossAxisAlignment, ImageFit, FontWeight

from api_request import APIRequest


class LoginViewStatus(Enum):
    ViewLoginUsername = 0,
    ViewLoginSmsView = 1,
    ViewRegistration = 2


class LoginControl(Column):
    def __init__(self, page):
        super().__init__()
        self.str_password :str|None = None
        self.str_username : str|None = None
        self.str_verify_code : str|None = None
        self.page = page
        self.adaptive = True
        self.alignment = MainAxisAlignment.START

        self.view_status:LoginViewStatus = LoginViewStatus.ViewLoginUsername  # 用于甄别具体是何登录注册视图
        container_login = self.build_interface()
        self.controls = [container_login]
        self.page.appbar = None
        self.page.drawer = None
        self.page.floating_action_button = None
        self.page.bottom_appbar = None

    def on_tab_change(self, e):
        match e.control.selected_index:
            case 0:
                self.view_status = LoginViewStatus.ViewLoginUsername
            case 1:
                self.view_status = LoginViewStatus.ViewRegistration

    def on_id_code_login_click(self, e):
        # 切换至短信验证码登录
        self.view_status = LoginViewStatus.ViewLoginSmsView
        tf_verify_code = TextField(label='验证码',
                                   width=260,
                                   prefix_icon=Icons.VERIFIED,
                                   border=InputBorder.OUTLINE,
                                   on_change=self.on_tf_verify_code_change)
        card_login_id_code = Card(
            elevation=0,
            content=Container(
                content=Column(
                    controls = [
                        self.tf_phone_num,
                        Row(
                            controls=[tf_verify_code,
                             TextButton('获取验证码', on_click=self.on_send_sms)],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        ),
                        FilledButton(text='登录',
                                     icon=Icons.LOGIN,
                                     width=400,
                                     on_click=self.on_code_login_click),
                        TextButton('密码登录', on_click=self.on_password_login_click)
                    ]
                ),
                # width=400,
                padding=2,
                # bgcolor=Colors.TRANSPARENT
            )
        )
        tabs_login = self.controls[0].controls[2].tabs[0]
        tabs_login.content = Container(
                        content=card_login_id_code,
                        # alignment=alignment.center,
                        padding=5,
                        margin=5,
                        # bgcolor=Colors.TRANSPARENT
        )
        e.page.update()

    def on_password_login_click(self, e):
        # 切换至用户名密码登录
        self.view_status = LoginViewStatus.ViewLoginUsername
        card_login = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        self.tf_password,
                        FilledButton(text='登录',
                                     icon=Icons.LOGIN,
                                     width=400,
                                     on_click=self.on_login_click),
                        TextButton('验证码登录', on_click=self.on_id_code_login_click)
                    ]
                ),
                width=400,
                padding=10,
            )
        )
        tabs_login = self.controls[0].controls[2].tabs[0]
        tabs_login.content = Container(
            content=card_login,
            # alignment=alignment.center,
            padding=10,
            margin=10,
            # bgcolor=Colors.TRANSPARENT,
        )
        e.page.update()

    def on_send_sms(self, e):
        # 发送短信验证码
        phone_num = self.str_username
        if not phone_num:
            snack_bar = SnackBar(Text("手机号码不得为空！"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        req_result = APIRequest.send_sms(phone_num)
        # if req_result.status_code in [200, 201, 202]:
        str_msg = req_result.text.replace('"', '')
        snack_bar = SnackBar(Text(f"{str_msg}"))
        e.control.page.overlay.append(snack_bar)
        snack_bar.open = True
        e.control.page.update()

    def on_tf_phone_num_change(self, e):
        self.str_username = e.control.value

    def on_tf_password_change(self, e):
        self.str_password = e.control.value

    def on_tf_verify_code_change(self, e):
        self.str_verify_code = e.control.value

    def on_login_click(self, e):
        # 用户名密码登录
        if self.view_status != LoginViewStatus.ViewLoginUsername:
            return
        if not self.str_username or not self.str_password:
            snack_bar = SnackBar(Text("用户名或密码不得为空！"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        e.control.page.overlay.append(progress_ring)
        e.control.page.update()
        # user_name = self.tf_phone_num.value
        # pass_word = self.tf_password.value
        # tf_phone_num = self.controls[0].content.content.controls[0]
        req = APIRequest.login_by_password(self.str_username, self.str_password)
        json_req = json.loads(req.text)

        if req.status_code != 200 or json_req.get('code') != '0':
            snack_bar = SnackBar(Text(f"{json_req.get('msg')}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            progress_ring.visible = False
            e.control.page.update()
            return

        dct_ret = json_req.get('result')
        self.page.client_storage.set('username', dct_ret.get('username'))
        self.page.client_storage.set('user_id', dct_ret.get('user_id'))
        self.page.client_storage.set('nickname', dct_ret.get('nickname'))
        self.page.client_storage.set('avatar', dct_ret.get('avatar'))
        self.page.client_storage.set('token', dct_ret.get('token'))
        # x = self.page.client_storage.get('nickname')
        # self.page.client_storage.update()

        # self.show_main_interface(dct_ret.get('token'))

        # self.left_drawer = NavigationDrawer(
        #     controls=[Container(content=NavControl(dct_ret.get('token')),
        #                         expand=1,
        #                         padding=padding.only(right=10, top=10, bottom=10),
        #                         # margin=margin.only(right=10, bottom=10),
        #                         bgcolor=Colors.WHITE,
        #                         )]
        # )
        # self.page.add(left_drawer)
        # self.page.drawer = self.left_drawer

        self.page.controls.clear()
        from main_view import MainView
        page_view = SafeArea(
            MainView(self.page),
            # maintain_bottom_view_padding=True,
            adaptive=True,
            expand=True
        )
        self.page.controls.append(page_view)
        self.page.update()
        progress_ring.visible = False

    def on_code_login_click(self, e):
        # 短信验证码登录
        if self.view_status != LoginViewStatus.ViewLoginSmsView:
            return
        progress_ring = ProgressRing(width=32, height=32, stroke_width=2)
        progress_ring.top = self.page.height / 2 - progress_ring.height / 2
        progress_ring.left = self.page.width / 2 - progress_ring.width / 2
        e.control.page.overlay.append(progress_ring)
        e.control.page.update()

        req = APIRequest.login_by_code(self.str_username, self.str_verify_code)
        json_req = req
        if json_req.get('code') != '0':
            snack_bar = SnackBar(Text(f"{json_req.get('msg')}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return

        dct_ret = json_req.get('result')
        self.page.client_storage.set('username', dct_ret.get('username'))
        self.page.client_storage.set('user_id', dct_ret.get('user_id'))
        self.page.client_storage.set('nickname', dct_ret.get('nickname'))
        self.page.client_storage.set('avatar', dct_ret.get('avatar'))
        self.page.client_storage.set('token', dct_ret.get('token'))
        # self.page.client_storage.update()

        self.page.go('/main_view')
        progress_ring.visible = False

    # 用户通过用户名密码进行注册
    def on_reg_click(self, e):
        if len(self.tf_phone_num.value) == 0 or len(self.tf_pass_1.value) == 0 or len(self.tf_pass_2.value) == 0:
            snack_bar = SnackBar(Text("用户名或密码不得为空！"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        if self.tf_pass_1.value != self.tf_pass_2.value:
            snack_bar = SnackBar(Text("两次输入的密码不一致！"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        ret_result = APIRequest.registry(self.tf_phone_num.value, self.tf_pass_1.value)
        if ret_result.get('code') != '0':
            snack_bar = SnackBar(Text(f"{ret_result.get('msg')}"))
            e.control.page.overlay.append(snack_bar)
            snack_bar.open = True
            e.control.page.update()
            return
        snack_bar = SnackBar(Text(f"{ret_result.get('msg')}, 请跳转至登录页进行登录！"))
        e.control.page.overlay.append(snack_bar)
        snack_bar.open = True
        e.control.page.update()
        self.page.update()

    def build_interface(self):
        self.tf_phone_num = TextField(label='手机号',
                                      prefix_icon=Icons.PHONE,
                                      border=InputBorder.OUTLINE,
                                      # value='13588459825',
                                      on_change=self.on_tf_phone_num_change,
                                      )
        self.tf_password = TextField(label='密码',
                                     prefix_icon=Icons.PASSWORD,
                                     border=InputBorder.OUTLINE,
                                     # value='iloveyou365',
                                     password=True,
                                     can_reveal_password=True,
                                     on_change=self.on_tf_password_change)
        self.tf_verify_code = TextField(label='验证码',
                                        prefix_icon=Icons.VERIFIED,
                                        border=InputBorder.OUTLINE,
                                        on_change=self.on_tf_verify_code_change)
        self.tf_pass_1 = TextField(label='请输入密码',
                                   prefix_icon=Icons.PASSWORD,
                                   border=InputBorder.OUTLINE,
                                   password=True,
                                   can_reveal_password=True)
        self.tf_pass_2 = TextField(label='请确认密码',
                                   prefix_icon=Icons.PASSWORD,
                                   border=InputBorder.OUTLINE,
                                   password=True,
                                   can_reveal_password=True)
        card_login = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        self.tf_password,
                        FilledButton(text='登录',
                                     icon=Icons.LOGIN,
                                     # width=400,
                                     # expand=True,
                                     on_click=self.on_login_click),
                        TextButton(text='验证码登录',
                                   disabled=False,
                                   on_click=self.on_id_code_login_click)
                    ],
                ),
                width=400,
                padding=10,
                # bgcolor=Colors.WHITE
            )
        )

        card_reg = Card(
            elevation=0,
            content=Container(
                content=Column(
                    [
                        self.tf_phone_num,
                        self.tf_pass_1,
                        self.tf_pass_2,
                        FilledButton(text='注册',
                                     width=400,
                                     icon=Icons.APP_REGISTRATION,
                                     on_click=self.on_reg_click),
                    ]
                ),
                width=400,
                padding=10,
            )
        )

        tabs_login = Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                Tab(
                    text="登录",
                    content=Container(
                        content=card_login,
                        # alignment=alignment.center,
                        padding=5,
                        margin=5,
                        # bgcolor=Colors.WHITE
                    ),
                ),
                Tab(
                    text="注册",
                    content=Container(
                        content=card_reg,
                        # alignment=alignment.center,
                        padding=5,
                        margin=5,
                        # bgcolor=Colors.WHITE
                    ),
                ),
            ],
            expand=True,
            on_change=self.on_tab_change,
        )

        col_login = Column(
            controls = [
                Container(
                    height=80,  # 控制空白高度
                    # bgcolor=Colors.WHITE,  # 透明背景
                ),
                Row(
                    controls=[
                        Image(src=f'assets/icon.png',
                            width=64, height=64,
                            fit=ImageFit.CONTAIN,
                            border_radius=border_radius.all(30)),
                        Text('布尔日记', size=24, color=Colors.BLUE,
                            weight=FontWeight.BOLD,
                        ),
                    ]
                ),
                tabs_login,
            ],

            horizontal_alignment=CrossAxisAlignment.CENTER,
            adaptive=True,
            width=self.page.width,
            height=self.page.height
        )

        # return container_login
        return col_login
