import cv2 as cv
import numpy as np

class Vision:
    template_image = None
    template_width = 0
    template_height = 0
    method = None
    
    def __init__(self, template_image_path, method = cv.TM_CCOEFF_NORMED):
        self.template_image = cv.imread(template_image_path, cv.IMREAD_COLOR)
        if self.template_image is None:
            raise Exception(f"Could not load template image: {template_image_path}")
        self.template_width = self.template_image.shape[1]
        self.template_height = self.template_image.shape[0]
        self.method = method
        
        if len(self.template_image.shape) == 3 and self.template_image.shape[2] == 4:
            self.template_image = cv.cvtColor(self.template_image, cv.COLOR_BGRA2BGR)
        
        self.template_image = np.ascontiguousarray(self.template_image, dtype=np.uint8)

    def find(self, game_img, threshold = 0.50):
        if len(game_img.shape) == 3 and game_img.shape[2] == 4:
            game_img = cv.cvtColor(game_img, cv.COLOR_BGRA2BGR)
        
        game_img = np.ascontiguousarray(game_img, dtype=np.uint8)

        result = cv.matchTemplate(game_img, self.template_image, self.method)

        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.template_width, self.template_height]
            rectangles.append(rect)
            rectangles.append(rect)

        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold = 1, eps = 0.5)
        points = []
        if len(rectangles):
            for (x, y, w, h) in rectangles:
                center_x = x + int(w/2)
                center_y = y + int(h/2)
                if points != []:
                    points.pop(0)
                points.insert(0,(center_x, center_y))

        return points
        
    def find_rectangles(self, game_img, threshold = 0.50):
        if len(game_img.shape) == 3 and game_img.shape[2] == 4:
            game_img = cv.cvtColor(game_img, cv.COLOR_BGRA2BGR)
        
        game_img = np.ascontiguousarray(game_img, dtype=np.uint8)

        result = cv.matchTemplate(game_img, self.template_image, self.method)

        locations = np.where(result >= threshold)
        if len(locations[0]) == 0:
            return []
        
        locations = list(zip(*locations[::-1]))

        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.template_width, self.template_height]
            rectangles.append(rect)
            rectangles.append(rect)

        if len(rectangles) > 0:
            rectangles, weights = cv.groupRectangles(rectangles, groupThreshold = 1, eps = 0.5)
        
        return rectangles

