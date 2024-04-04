from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.gridlayout import GridLayout
import subprocess
import threading



LabelBase.register('Roboto', 'STFANGSO.TTF')
sm = None

def read_stream(stream, process,update_msg):
    try:
        for line in iter(stream.readline, b''):
            msg = line.decode('utf-8').strip()
            update_msg(msg)  # 打印输出
    except Exception as e:
        update_msg(f'读取流时发生错误: {e}')
    finally:
        stream.close()  # 关闭流
class MC_chat(Screen):
    # 聊天界面
    message_text = StringProperty("")

    def __init__(self, **kwargs):
        super(MC_chat, self).__init__(**kwargs)
        self.bot = None

        self.orientation = 'vertical'

        # 创建新的BoxLayout放置退出按钮和Label
        header_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=70)
        self.exit_button = Button(text='退出', on_press=self.on_exit,size_hint_y=None)
        self.header_label = Label(text='Pichat - Minecraft Chat Interface',size_hint_y=None)

        header_box.add_widget(self.header_label)
        header_box.add_widget(self.exit_button)

        # 将新的BoxLayout添加到主BoxLayout的顶部
        # self.add_widget(header_box) # TODO:存在BUG，内容绘制在屏幕下方，导致重叠

        # 创建一个布局来放置显示框，并允许其内容自动扩展
        self.content_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        self.display_label = Label(
            size_hint_y=None,
            halign='left',
            height=40,
        )
        self.content_layout.add_widget(self.display_label)
        # 创建滚动视图
        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height-header_box.height))
        self.scroll_view.add_widget(self.content_layout)
        self.add_widget(self.scroll_view)


        # 添加输入框和发送按钮
        self.input_text = TextInput(multiline=False)
        self.input_text.bind(on_text_validate=self.on_enter)
        self.send_button = Button(text='发送', on_press=self.on_send)

        # 创建一个BoxLayout来放置输入框和按钮
        input_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=70)
        input_box.add_widget(self.input_text)
        input_box.add_widget(self.send_button)

        # 将输入框和按钮的BoxLayout添加到主BoxLayout中

        self.add_widget(input_box)

        # mc登录
        self.mc_login()



    def on_send(self,*args):
        # 在这里处理消息发送逻辑
        self.send_message(self.input_text.text)
        self.input_text.text = ''


    def on_enter(self):
        self.on_send()

    def send_message(self, message:str):
        """发送消息到Minecraft服务器"""
        # 创建线程来管理stdin的写入
        self.process.stdin.write(f"{message}\n".encode())
        self.process.stdin.flush()


    def update_box(self,message):
        def update_box(dt):
            display_label = Label(
            text=f'[pichat]{message}',
            text_size=(Window.width, 50),
            size_hint_y=None,
            halign='left',
            font_size='20dp',
            )
            self.content_layout.add_widget(display_label)
            # 如果content_layout的高度需要重新计算，也需要在这里进行更新
            self.content_layout.height = self.display_label.texture_size[1]
            # self.scroll_view.scroll_y = 0

        Clock.schedule_once(update_box, 0)

    def mc_login(self):
        # 调用并执行另一个Python脚本
        self.process = subprocess.Popen(['python', 'mm.py'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        shell=True,
                                        bufsize=0)
        # 创建线程来读取标准输出和标准错误
        stdout_thread = threading.Thread(target=read_stream, args=(self.process.stdout, self.process,self.update_box))
        stderr_thread = threading.Thread(target=read_stream, args=(self.process.stderr, self.process,self.update_box))
        # 启动线程
        stdout_thread.start()
        stderr_thread.start()





    def on_exit(self):
        # 检查子进程是否还在运行，如果在运行则强制结束它
        self.process.stdin.write('$$exit\n'.encode())
        self.process.stdin.flush()
        self.process.stdin.close()
        self.process.stderr.close()
        self.process.stdout.close()
        self.process.terminate()  # 发送终止信号给子进程
        if self.process.poll() is None:
            self.process.kill()  # 如果进程还在运行，强制结束它
        global sm
        sm.current = 'menu_screen'



class AnotherScreen(Screen):
    # TODO:编写一个主页，实现账户登陆和服务器添加功能
    pass

class MyApp(App):
    def build(self):
        self.mc = MC_chat()
        self.title = 'pichat'
        self.mc.app = self  # 让 MC_chat 类能够访问到 App 对象
        global sm
        sm = ScreenManager()
        sm.add_widget(MC_chat(name='chat_screen'))
        sm.add_widget(AnotherScreen(name='menu_screen'))
        sm.current = 'chat_screen'
        return sm







if __name__ == "__main__":
    MyApp().run()