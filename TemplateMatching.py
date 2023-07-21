import cv2
import numpy as np
class TemplateMatching:
    def __init__(self, image):
        self.image = image
    def preprocess_image(self, template):
        gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (1, 1), 0)
        _, binary = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        return morph

    def match_templates(self, template_files, template_names, processed_image):
        self.image = processed_image
        self.drawn_image = self.image.copy()
        template_matches = {}
        template_box_counts = {}
        for template_file, template_name in zip(template_files, template_names):
            template = cv2.imread(template_file)
            processed_template = self.preprocess_image(template)
            cv2.imwrite('ct/preprocessed_template_{}.png'.format(template_name), processed_template)  # 保存预处理后的模板
            if processed_image.shape[0] < processed_template.shape[0] or processed_image.shape[1] < \
                    processed_template.shape[1]:
                processed_template = cv2.resize(processed_template,
                                                (processed_image.shape[1], processed_image.shape[0]))
            result = cv2.matchTemplate(processed_image, processed_template, cv2.TM_SQDIFF_NORMED)
            threshold = 0.4
            locations = np.where(result <= threshold)
            match_count = len(locations[0])
            template_matches[template_name] = match_count

            drawn_rectangles = []
            for pt in zip(*locations[::-1]):
                top_left = pt
                h, w, _ = template.shape
                bottom_right = top_left[0] + w, top_left[1] + h
                overlapping = False
                for rect in drawn_rectangles:
                    if rect[0] < bottom_right[0] and rect[1] < bottom_right[1] and top_left[0] < rect[2] and top_left[
                        1] < rect[3]:
                        overlapping = True
                        break
                if overlapping:
                    continue
                cv2.rectangle(self.image, top_left, bottom_right, (0, 0, 255), 2)
                drawn_rectangles.append((top_left[0], top_left[1], bottom_right[0], bottom_right[1]))
                self.drawn_image = self.image.copy()  # 更新绘制过后的图片

            box_count = len(drawn_rectangles)
            template_box_counts[template_name] = box_count
            print(f'{template_name}: {match_count} 个, {box_count} 个框')

        return template_matches, template_box_counts
