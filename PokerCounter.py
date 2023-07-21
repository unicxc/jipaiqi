import cv2
import time
from ctypes import windll
from Card import Card
from WindowCapture import WindowCapture
from TemplateMatching import TemplateMatching
from Player import Player
from GUI import GUI
import json
class PokerCounter:
    def __init__(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.own_template_files = self.config["own_template_files"]
        self.own_template_names = self.config["own_template_names"]
        self.other_players_template_files = self.config["other_players_template_files"]
        self.other_players_template_names = self.config["other_players_template_names"]
        self.player_hand_cards = [[0] * len(self.own_template_names) for _ in range(6)]
        self.num_decks = 4  # 初始设为4副牌
        self.remaining_cards = [self.num_decks * 4] * len(self.own_template_names)  # 假设每副牌中每张牌4张
        self.first_capture = True  # 添加标志位，表示是否是第一次截图
        self.players = {
            "对家": Player("对家"),
            "上联": Player("上联"),
            "下联": Player("下联"),
            "上家": Player("上家"),
            "下家": Player("下家")
        }
        self.player_card_names = [
            ['大', '小', '2', 'A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3'] for _ in range(6)
        ]  # 这个列表用来记录每个玩家手中还未出现在窗口中的牌
        self.gui = GUI(self, self.player_card_names)

    def start_count(self):
        self.window_capture = WindowCapture("雷电模拟器")
        self.template_matching = TemplateMatching(
            self.window_capture.capture_area(100, 644, 1425, 180))
        self.capture_and_match_templates(self.num_decks)  # 将num_decks作为参数传递
        self.update_gui()
        self.continuous_capture()

    def capture_and_match_templates(self, num_decks):
        image = self.window_capture.capture_area(60, 500, 1425, 180)
        processed_image = self.window_capture.preprocess_image(image)
        cv2.imwrite('ct/preprocessed_image.png', processed_image)  # 保存预处理后的图像
        template_matches, template_box_counts = self.template_matching.match_templates(
            self.own_template_files + self.other_players_template_files,
            self.own_template_names + self.other_players_template_names,
            processed_image)
        for template_name, box_count in template_matches.items():
            # 在牌出现在窗口中后，我们需要将它从列表中移除
            # 我们只有在 template_name 确实在 self.player_card_names[0] 时才尝试删除它
            if template_name in self.player_card_names[0]:
                self.player_card_names[0].remove(template_name)
            if self.first_capture:
                self.update_remaining_cards(template_name, box_count, 0, num_decks,
                                            update_hand_cards=False)  # 添加num_decks参数
            else:
                self.update_remaining_cards(template_name, box_count, 0, num_decks,
                                            update_hand_cards=True)  # 添加num_decks参数

        self.first_capture = False

        drawn_image = self.template_matching.drawn_image
        cv2.imwrite('ct/final_image_own.png', drawn_image)
        print(f"预扣: {template_matches}, 框: {template_box_counts}")

    def update_remaining_cards(self, template_name, box_count, player_index, num_decks, update_hand_cards=True):  # 添加num_decks参数
        if template_name in self.own_template_names:
            card_index = self.own_template_names.index(template_name)
        elif template_name in self.other_players_template_names:
            card_index = self.other_players_template_names.index(template_name)
        else:
            raise ValueError(f"Invalid template_name: {template_name}")

        # 扣除整个牌堆的牌
        self.remaining_cards[card_index] -= box_count

        # 如果需要更新玩家的手牌，那么只需要更新特定玩家的手牌和剩余的牌
        if update_hand_cards:
            # 更新特定玩家的手牌
            self.player_hand_cards[player_index][card_index] -= box_count

        # 更新GUI显示
        self.gui.update_remaining_cards(self.num_decks)

    def update_gui(self):
        # 更新每种牌的剩余数量
        for i, remaining in enumerate(self.remaining_cards):
            self.gui.remaining_values[i].set(str(remaining))

        # 更新每个玩家的手牌
        for player_name, player in self.players.items():
            player_index = self.player_names.index(player_name)
            if player_index < len(self.gui.player_hand_cards):
                player_cards = self.player_hand_cards[player_index]
                self.gui.player_hand_cards[player_index].set(
                    ' '.join([f"{card}:{count}" for card, count in zip(self.own_template_names, player_cards)]))
            else:
                print(f"Warning: player index ({player_index}) out of range.")

        # 刷新界面
        self.gui.root.update()

    def stat_jinggong(self):
        self.jinggong_areas = self.config["jinggong_areas"]
        windll.user32.SetCursorPos(*self.jinggong_button_pos)
        windll.user32.mouse_event(2, 0, 0, 0, 0)
        windll.user32.mouse_event(4, 0, 0, 0, 0)
        time.sleep(1)

        window_capture = WindowCapture("雷电模拟器")
        for idx, (x, y, w, h) in enumerate(self.jinggong_areas):
            image = window_capture.capture_area(x, y, w, h)
            template_matching = TemplateMatching(image)

            template_matches, template_box_counts = template_matching.match_templates(
                self.own_template_files + self.other_players_template_files,
                self.own_template_names + self.other_players_template_names)

            for template_name, match_count in template_matches.items():
                if match_count > 0:
                    self.players[idx].add_card(Card(template_name, match_count))

            cv2.imshow("Screenshot", image)
            cv2.waitKey(0)

        self.update_remaining_cards_from_players()
        self.update_gui()

    def update_remaining_cards_from_players(self):
        self.remaining_cards = [4 * self.num_decks] * len(self.own_template_names)
        for player in self.players.values():
            for card_index, card_name in enumerate(self.own_template_names):
                total_cards = player.get_card_count(card_name)
                self.remaining_cards[card_index] -= total_cards

        for player in self.players.values():
            for card_index, card_name in enumerate(self.other_players_template_names):
                total_cards = player.get_card_count(card_name)
                self.remaining_cards[len(self.own_template_names) + card_index] -= total_cards

    def continuous_capture(self):
        self.player_areas = self.config["player_areas"]
        window_capture = WindowCapture("雷电模拟器")
        for idx, area in enumerate(self.player_areas):
            x, y, w, h = area["coordinates"]
            image = window_capture.capture_area(x, y, w, h)
            processed_image = window_capture.preprocess_image(image)
            template_matching = TemplateMatching(processed_image)
            template_matches, template_box_counts = template_matching.match_templates(
                self.own_template_files + self.other_players_template_files,
                self.own_template_names + self.other_players_template_names,
                processed_image)
            cv2.imwrite(f'ct/final_image_player_{idx}.png', template_matching.image)
            for template_name, match_count in template_matches.items():
                if match_count > 0 and not self.players[idx].has_card(template_name):
                    self.players[idx].add_card(Card(template_name, match_count))
                    # update remaining_cards
                    card_index = self.other_players_template_names.index(template_name)
                    remaining_count = self.remaining_cards[len(self.own_template_names) + card_index] - match_count
                    self.remaining_cards[len(self.own_template_names) + card_index] = remaining_count
                    # hide the card name in the window
                    if idx + 1 < len(self.player_card_names) and template_name in self.player_card_names[idx + 1]:
                        self.player_card_names[idx + 1].remove(template_name)

        self.update_remaining_cards_from_players()
        self.update_gui()
        print("Capture and match process completed.")

    def capture_and_match_templates_own_area(self):
        image = self.window_capture.capture_area(60, 500, 1425, 180)
        template_matching = TemplateMatching(image)
        template_matches, template_box_counts = template_matching.match_templates(self.own_template_files,
                                                                                  self.own_template_names)

        for template_name, match_count in template_matches.items():
            box_count = template_box_counts.get(template_name, 0)
            self.update_remaining_cards(template_name, match_count, 0, update_hand_cards=True)

    def capture_and_match_templates_players(self):
        for idx, (x, y, w, h) in enumerate(self.player_areas):
            image = self.window_capture.capture_area(x, y, w, h)
            template_matching = TemplateMatching(image)
            template_matches, template_box_counts = template_matching.match_templates(
                self.other_players_template_files,
                self.other_players_template_names)

            for template_name, match_count in template_matches.items():
                if match_count > 0 and not self.players[idx].has_card(template_name):
                    self.players[idx].add_card(Card(template_name, match_count))
                    self.update_remaining_cards(template_name, match_count, 0, update_hand_cards=True)

    def reset_count(self):
        self.remaining_cards = [0] * len(self.own_template_names)
        for player in self.players.values():
            player.reset_hand_cards()
        self.gui.update_remaining_cards(self.num_decks)

    def run(self):
        self.gui.run_gui()

    def on_button_click(self, event):
        if event == 'close':
            self.gui.close_window()
        elif event == 'initialize':
            self.reset_count()
        elif event == 'start':
            self.start_count()
        elif event == 'set_4_decks':
            self.set_num_decks(4)
        elif event == 'set_6_decks':
            self.set_num_decks(6)
        else:
            print("Unknown event")

    def set_num_decks(self, num_decks):
        self.num_decks = num_decks
        self.gui.update_hand_cards(num_decks)
        self.gui.update_remaining_cards(self.num_decks)

if __name__ == '__main__':
    counter = PokerCounter()
    counter.players = {
        "对家": Player("对家"),
        "上联": Player("上联"),
        "下联": Player("下联"),
        "上家": Player("上家"),
        "下家": Player("下家"),
    }
    counter.run()
