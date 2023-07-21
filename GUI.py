import tkinter as tk
from tkinter import ttk, messagebox

class GUI:
    def __init__(self, counter, player_card_names=None):
        self.counter = counter
        self.root = tk.Tk()
        self.root.title('够级记牌器')
        self.card_names = ['大', '小', '2', 'A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3']
        self.remaining_values = [tk.StringVar() for _ in range(15)]
        self.player_names = ['对家', '上联', '下联', '上家', '下家']
        self.player_hand_cards = [tk.StringVar() for _ in range(5)]
        self.player_card_names = [self.card_names for _ in range(5)]
        self.num_decks = 4  # 添加num_decks属性并设置默认值为4
        self.initialize_ui()
        self.player_card_names = player_card_names if player_card_names is not None else []


    def initialize_ui(self):
        self.initialize_card_names_frame()
        self.initialize_hand_cards_frame()
        self.initialize_buttons_frame()
        self.initialize_remaining_values_frame()
        self.initialize_styles()

    def initialize_card_names_frame(self):
        frame_card_names = self.create_frame(self.root, 1, 0, 10, 0)
        for i, card_name in enumerate(self.card_names):
            color = 'red' if card_name == '大' else 'gray' if card_name == '小' else None
            self.create_label(frame_card_names, card_name, 0, i, 5, 5, ('Arial', 12), color)

    def initialize_hand_cards_frame(self):
        self.frame_hand_cards = self.create_frame(self.root, 0, 0, 10, 10)
        self.update_hand_cards(4)

    def initialize_buttons_frame(self):
        self.frame_buttons = self.create_frame(self.root, 3, 0, 10, 10)
        button_names_commands = [
            ('4 副牌', self.set_4_decks),
            ('统计进贡', self.stat_jinggong),
            ('6 副牌', self.set_6_decks),
            ('开始记牌', self.start_count),
            ('初始化', self.reset_count),
            ('关闭程序', self.close_window),
        ]
        for i, (button_name, command) in enumerate(button_names_commands):
            self.create_button(self.frame_buttons, button_name, command, 0, i)

    def initialize_remaining_values_frame(self):
        self.frame_remaining_values = self.create_frame(self.root, 2, 0, 10, 10)
        for i in range(len(self.remaining_values)):
            self.create_label(self.frame_remaining_values, self.remaining_values[i], 0, i, 8, 8, ('Arial', 12))

    def initialize_styles(self):
        self.style = ttk.Style(self.root)
        self.style.configure('Custom.TLabel', foreground='black', font=('Arial', 12, 'bold'), padx=5)
        self.style.configure('Red.TLabel', foreground='red', font=('宋体', 12))
        self.style.configure('Blue.TLabel', foreground='blue', font=('宋体', 12))

    def create_frame(self, parent, row, column, padx, pady):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=column, padx=padx, pady=pady, sticky='nsew')
        return frame

    def create_label(self, parent, text, row, column, padx, pady, font=None, fg=None):
        label = ttk.Label(parent, text=text, font=font, foreground=fg)
        label.grid(row=row, column=column, padx=padx, pady=pady)
        return label

    def create_button(self, parent, text, command, row, column):
        button = ttk.Button(parent, text=text, command=command)
        button.grid(row=row, column=column)
        return button

    def on_button_click(self):
        self.counter.on_button_click()
    def update_display(self, processed_data):
        for i in range(len(self.card_names)):
            remaining_value = self.remaining_values[i]
            remaining_value.set(str(processed_data['remaining_cards'][i]))
        for i in range(5):
            player_value = self.player_hand_cards[i]
            player_hand = processed_data['player_hand_cards'][i]
            player_value.set(f"{self.player_names[i]}：{player_hand} {'  '.join(self.player_card_names[i])}")
            label_hand_cards = ttk.Label(self.frame_hand_cards, textvariable=player_value, font=('宋体', 12), style='Red.TLabel')
            if len(player_hand) < 10:
                label_hand_cards.configure(style='Red.TLabel')
            else:
                label_hand_cards.configure(style='Blue.TLabel')
            label_hand_cards.grid(row=i, column=0, padx=5, pady=5, sticky='nsew')

    def start_count(self):
        self.counter.num_decks = self.num_decks
        self.show_message_box("提示", "记牌")
        self.counter.on_button_click(event="start")
        self.update_remaining_cards(self.num_decks)  # 将self.num_decks作为参数传递

    def stat_jinggong(self):
        self.show_message_box("提示", "进贡")
        self.counter.on_button_click("stat_jinggong")

    def reset_count(self):
        self.show_message_box("提示", "初始化")
        self.counter.on_button_click("initialize")

    def set_4_decks(self):
        self.counter.on_button_click("set_4_decks")

    def set_6_decks(self):
        self.counter.on_button_click("set_6_decks")

    def close_window(self):
        self.show_message_box("提示", "关闭程序")
        self.counter.on_button_click("close")

    def run_gui(self):
        self.root.mainloop()

    # 定义更新手牌的函数
    def update_hand_cards(self, num_decks):
        self.num_decks = num_decks  # 更新num_decks属性的值
        total_cards = num_decks * 52
        hand_cards = {
            "对家": 33 if num_decks == 4 else 51,
            "上联": 33 if num_decks == 4 else 51,
            "下联": 33 if num_decks == 4 else 51,
            "上家": 33 if num_decks == 4 else 51,
            "下家": 33 if num_decks == 4 else 51
        }
        for player_name, player in self.counter.players.items():
            player_hand_cards = self.player_hand_cards[self.player_names.index(player_name)]
            player_hand_cards.set(
                f"{player_name}：{hand_cards[player_name]} {'  '.join(self.player_card_names[self.player_names.index(player_name)])}")
            label_hand_cards = ttk.Label(self.frame_hand_cards, textvariable=player_hand_cards, font=('宋体', 12),
                                         style='Red.TLabel', foreground='red')

            if hand_cards[player_name] < 10:
                label_hand_cards.configure(style='Red.TLabel')
            else:
                label_hand_cards.configure(style='Blue.TLabel')
            label_hand_cards.grid(row=self.player_names.index(player_name), column=0, padx=5, pady=5)
        self.update_remaining_cards_ui(num_decks)  # 传递num_decks参数

    def update_remaining_cards(self, num_decks):
        self.num_decks = num_decks  # 更新num_decks属性的值
        self.update_remaining_cards_ui(num_decks)  # 将num_decks作为参数传递给update_remaining_cards_ui方法
        remaining_cards = []
        if num_decks == 4:
            remaining_cards = [4, 4, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 8, 6]
        elif num_decks == 6:
            remaining_cards = [6, 6, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 6]
        for i in range(len(self.card_names)):
            remaining_value = self.remaining_values[i]
            remaining_value.set(str(remaining_cards[i]))
        self.root.update()

    def update_remaining_cards_ui(self, num_decks):
        remaining_cards = []
        if num_decks == 4:
            remaining_cards = [4, 4, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 8, 6]
        elif num_decks == 6:
            remaining_cards = [6, 6, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 6]
        for i in range(len(self.card_names)):
            remaining_value = self.remaining_values[i]
            remaining_value.set(str(remaining_cards[i]))
        self.root.update()


    def show_message_box(self, title, message):
        messagebox.showinfo(title, message)