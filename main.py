import cv2 as cv
import os
import time
import warnings
import datetime

warnings.filterwarnings("ignore", category=DeprecationWarning)

from vision import Vision
from capture import Capture

os.chdir(os.path.dirname(os.path.abspath(__file__)))

MONSTER_SYSTEM = {
    'monsters': {
        'rats 1': {
            'folder': 'templates/rat_1',
            'color': (0, 0, 255),
            'display_name': 'Rat 1',
            'enabled': True,
            'vision_objects': []
        }
    },
    'threshold': 0.70
}

wincap = None
scan_count = 0
detection_count = 0

def initialize_monster_system():
    print(" Initializing Universal Monster Detection System...")
    
    for monster_type, config in MONSTER_SYSTEM['monsters'].items():
        if config['enabled']:
            print(f" Loading {config['display_name']} templates from {config['folder']}...")

            folder_path = config['folder']
            if not os.path.exists(folder_path):
                print(f"  ❌ Folder not found: {folder_path}")
                continue

            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
            
            loaded_count = 0
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    try:
                        vision_obj = Vision(file_path)
                        
                        name_without_ext = os.path.splitext(filename)[0]
                        template_name = f"{config['display_name']}_{name_without_ext.title()}"
                        angle = name_without_ext.lower()
                        
                        config['vision_objects'].append({
                            'vision': vision_obj,
                            'name': template_name,
                            'angle': angle,
                            'filename': filename
                        })
                        
                        print(f"   {template_name} loaded ({filename})")
                        loaded_count += 1
                        
                    except Exception as e:
                        print(f"  ❌ Error loading {filename}: {e}")
            
            print(f" Total: {loaded_count} templates loaded for {config['display_name']}")
    
    print(" Universal Monster Detection System ready!")

def universal_monster_detection(screenshot):
    if screenshot is None:
        return [], []
    
    all_detections = []
    detection_info = []
    
    for monster_type, config in MONSTER_SYSTEM['monsters'].items():
        if not config['enabled']:
            continue
            
        monster_detections = []
        
        for template_obj in config['vision_objects']:
            vision_obj = template_obj['vision']
            template_name = template_obj['name']
            angle = template_obj['angle']
            threshold = MONSTER_SYSTEM['threshold']
            
            rectangles = vision_obj.find_rectangles(screenshot, threshold=threshold)
            
            if len(rectangles) > 0:
                monster_detections.extend(rectangles)
                
                detection_info.append({
                    'monster': config['display_name'],
                    'template': template_name,
                    'angle': angle,
                    'threshold': threshold,
                    'count': len(rectangles),
                    'color': config['color']
                })
        
        if len(monster_detections) > 1:
            monster_detections = remove_duplicate_detections(monster_detections)
        
        all_detections.extend(monster_detections)
    
    return all_detections, detection_info

def remove_duplicate_detections(rectangles, overlap_threshold=0.5):
    if len(rectangles) <= 1:
        return rectangles
    
    rectangles = sorted(rectangles, key=lambda r: r[2] * r[3], reverse=True)
    unique_rects = []
    
    for rect in rectangles:
        x1, y1, w1, h1 = rect
        is_duplicate = False
        
        for unique_rect in unique_rects:
            x2, y2, w2, h2 = unique_rect
            
            if (abs(x1 - x2) > max(w1, w2) or abs(y1 - y2) > max(h1, h2)):
                continue
                
            overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
            overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
            overlap_area = overlap_x * overlap_y
            
            area1 = w1 * h1
            area2 = w2 * h2
            
            if overlap_area > overlap_threshold * min(area1, area2):
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_rects.append(rect)
    
    return unique_rects

def draw_detections_on_image(image, detections, detection_info):
    result_image = image.copy()
    
    for i, rect in enumerate(detections):
        x, y, w, h = rect
        
        color = (255, 255, 255)
        monster_name = "Unknown"
        
        if i < len(detection_info):
            color = detection_info[i].get('color', (255, 255, 255))
            monster_name = detection_info[i]['monster']
        
        cv.rectangle(result_image, (x, y), (x + w, y + h), color, 2)
        
        center_x = x + w // 2
        center_y = y + h // 2
        cv.circle(result_image, (center_x, center_y), 3, color, -1)
        
        cv.putText(result_image, monster_name, (x, max(15, y - 5)), 
                  cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return result_image

def save_screenshot_with_detections(image, detections, detection_info):
    global detection_count
    
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if len(detections) > 0:
        detection_count += 1
        annotated_image = draw_detections_on_image(image, detections, detection_info)
        filename = f"screenshots/detection_{timestamp}_{len(detections)}monsters.png"
        cv.imwrite(filename, annotated_image)
        print(f" Screenshot saved: {filename} (Found {len(detections)} monsters)")
    else:
        filename = f"screenshots/screenshot_{timestamp}_no_detections.png"
        cv.imwrite(filename, image)
        print(f"Screenshot saved: {filename} (No detections)")

def main():
    global wincap, scan_count, detection_count
    
    print(" Starting Monster Detection System - Screenshot Mode")
    print("Taking screenshots every 10 seconds")
    print("=" * 60)
    
    print(" Initializing screen capture...")
    try:
        wincap = Capture()
        print(" Screen capture initialized")
    except Exception as e:
        print(f"❌ Error initializing screen capture: {e}")
        return
    
    print("Initializing monster detection system...")
    try:
        initialize_monster_system()
        print(" Monster system initialized")
    except Exception as e:
        print(f"❌ Error initializing monster system: {e}")
        return
    
    print(" System ready! Starting screenshot loop...")
    print("Screenshots will be saved in 'screenshots/' folder")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            start_time = time.time()
            
            screenshot = wincap.get_screenshot()
            
            if screenshot is None:
                print("⚠️ Could not get screenshot")
                time.sleep(10)
                continue
            
            scan_count += 1
            
            try:
                detections, detection_info = universal_monster_detection(screenshot)
                
                save_screenshot_with_detections(screenshot, detections, detection_info)
                
                print(f" Scan #{scan_count} completed - Detections: {len(detections)} | Total detections saved: {detection_count}")
                
            except Exception as e:
                print(f"❌ Detection error: {e}")
            
            elapsed_time = time.time() - start_time
            sleep_time = max(0, 10 - elapsed_time)
            
            if sleep_time > 0:
                print(f" Waiting {sleep_time:.1f}s until next screenshot...")
                time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n Stopping system...")
        print(" Final Statistics:")
        print(f"    Total scans: {scan_count}")
        print(f"   Screenshots with detections: {detection_count}")
        print(" System stopped successfully!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()