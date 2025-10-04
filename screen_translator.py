import pytesseract
from PIL import ImageGrab, Image, ImageTk, ImageEnhance
import mss
import time
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class RegionSelector:
    def __init__(self, monitor):
        self.monitor = monitor
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        
        self.canvas = tk.Canvas(self.root, cursor="cross", bg='grey')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Escape>", lambda e: self.cancel())
        
        # 顯示提示
        self.canvas.create_text(
            self.root.winfo_screenwidth()//2, 50,
            text="拖曳滑鼠選擇要擷取的區域 (按 ESC 取消)",
            fill="white", font=("Arial", 16, "bold")
        )
        
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=3
        )
        
    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
        
    def on_release(self, event):
        end_x, end_y = event.x, event.y
        
        # 確保座標順序正確
        x1 = min(self.start_x, end_x) + self.monitor["left"]
        y1 = min(self.start_y, end_y) + self.monitor["top"]
        x2 = max(self.start_x, end_x) + self.monitor["left"]
        y2 = max(self.start_y, end_y) + self.monitor["top"]
        
        width = x2 - x1
        height = y2 - y1
        
        # 檢查區域大小
        if width < 50 or height < 50:
            messagebox.showwarning("區域太小", "請選擇更大的區域（至少 50x50 像素）")
            self.root.destroy()
            return
            
        self.region = {"left": x1, "top": y1, "width": width, "height": height}
        self.root.destroy()
        
    def cancel(self):
        self.region = None
        self.root.destroy()
        
    def get_region(self):
        self.root.wait_window()
        return self.region

class ScreenTranslator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("螢幕即時翻譯器")
        self.window.geometry("700x550")
        
        self.is_running = False
        self.translator = GoogleTranslator(source='en', target='zh-TW')
        self.last_text = ""
        self.capture_region = None
        self.current_monitor = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 頂部控制區
        control_frame = ttk.Frame(self.window, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 監視器選擇
        monitor_frame = ttk.Frame(control_frame)
        monitor_frame.pack(fill=tk.X, pady=(0,5))
        
        ttk.Label(monitor_frame, text="選擇監視器:").pack(side=tk.LEFT)
        self.monitor_var = tk.StringVar()
        
        with mss.mss() as sct:
            monitors = [f"監視器 {i}" for i in range(len(sct.monitors))]
        
        self.monitor_combo = ttk.Combobox(monitor_frame, textvariable=self.monitor_var, 
                                          values=monitors, state="readonly", width=15)
        self.monitor_combo.current(1 if len(monitors) > 1 else 0)
        self.monitor_combo.pack(side=tk.LEFT, padx=10)
        
        # 區域選擇按鈕
        self.region_btn = ttk.Button(monitor_frame, text="選擇擷取區域", 
                                     command=self.select_region)
        self.region_btn.pack(side=tk.LEFT, padx=5)
        
        self.region_label = ttk.Label(monitor_frame, text="尚未選擇區域", foreground="gray")
        self.region_label.pack(side=tk.LEFT, padx=10)
        
        # 更新間隔設定
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill=tk.X)
        
        ttk.Label(settings_frame, text="更新間隔(秒):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="2")
        ttk.Entry(settings_frame, textvariable=self.interval_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # 影像處理選項
        self.enhance_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="影像增強（提升準確度）", 
                       variable=self.enhance_var).pack(side=tk.LEFT, padx=20)
        
        # 控制按鈕
        button_frame = ttk.Frame(self.window, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.start_btn = ttk.Button(button_frame, text="▶ 開始擷取", command=self.start_capture)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏸ 停止擷取", command=self.stop_capture, 
                                   state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="清空", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        # 原文顯示區
        original_frame = ttk.LabelFrame(self.window, text="擷取的英文", padding="10")
        original_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.original_text = tk.Text(original_frame, height=8, wrap=tk.WORD, font=("Arial", 10))
        self.original_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        original_scroll = ttk.Scrollbar(original_frame, command=self.original_text.yview)
        original_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.original_text.config(yscrollcommand=original_scroll.set)
        
        # 翻譯顯示區
        translation_frame = ttk.LabelFrame(self.window, text="中文翻譯", padding="10")
        translation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.translation_text = tk.Text(translation_frame, height=8, wrap=tk.WORD, 
                                       font=("Microsoft YaHei UI", 10))
        self.translation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        translation_scroll = ttk.Scrollbar(translation_frame, command=self.translation_text.yview)
        translation_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.translation_text.config(yscrollcommand=translation_scroll.set)
        
        # 提示資訊
        info_frame = ttk.Frame(self.window, padding="5")
        info_frame.pack(fill=tk.X, padx=10)
        
        ttk.Label(info_frame, text="💡 建議：選擇 300x100 到 1920x300 像素的區域效果最佳", 
                 foreground="blue", font=("Arial", 9)).pack(anchor=tk.W)
        
        # 狀態列
        self.status_label = ttk.Label(self.window, text="就緒 - 請先選擇擷取區域", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
    
    def select_region(self):
        monitor_idx = self.monitor_combo.current()
        with mss.mss() as sct:
            monitor = sct.monitors[monitor_idx]
            self.current_monitor = monitor
            
        selector = RegionSelector(monitor)
        region = selector.get_region()
        
        if region:
            self.capture_region = region
            width = region["width"]
            height = region["height"]
            self.region_label.config(
                text=f"已選擇: {width}x{height} 像素",
                foreground="green"
            )
            
            # 給出優化建議
            if width < 200 or height < 50:
                self.status_label.config(text="⚠️ 區域較小，可能影響識別準確度")
            elif width > 2000 or height > 1000:
                self.status_label.config(text="⚠️ 區域較大，處理速度可能較慢")
            else:
                self.status_label.config(text="✓ 區域大小適中，可以開始擷取")
        else:
            self.status_label.config(text="已取消選擇區域")
    
    def enhance_image(self, img):
        """增強影像以提升 OCR 準確度"""
        # 轉換為灰階
        img = img.convert('L')
        
        # 增強對比度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # 增強銳利度
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        return img
    
    def capture_and_translate(self):
        with mss.mss() as sct:
            while self.is_running:
                try:
                    if not self.capture_region:
                        self.status_label.config(text="錯誤：未選擇擷取區域")
                        break
                    
                    # 擷取指定區域
                    screenshot = sct.grab(self.capture_region)
                    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    
                    # 影像增強
                    if self.enhance_var.get():
                        img = self.enhance_image(img)
                    
                    # OCR 識別 - 使用更好的配置
                    custom_config = r'--oem 3 --psm 6'
                    text = pytesseract.image_to_string(img, lang='eng', config=custom_config)
                    text = text.strip()
                    
                    if text and text != self.last_text:
                        self.last_text = text
                        
                        # 更新原文
                        self.original_text.delete(1.0, tk.END)
                        self.original_text.insert(1.0, text)
                        
                        # 翻譯
                        if text:
                            try:
                                translation = self.translator.translate(text)
                                self.translation_text.delete(1.0, tk.END)
                                self.translation_text.insert(1.0, translation)
                                
                                word_count = len(text.split())
                                self.status_label.config(
                                    text=f"✓ 已更新翻譯 ({word_count} 個字) - {time.strftime('%H:%M:%S')}"
                                )
                            except Exception as e:
                                self.status_label.config(text=f"翻譯錯誤: {str(e)}")
                    
                    # 等待指定間隔
                    interval = float(self.interval_var.get())
                    time.sleep(interval)
                    
                except Exception as e:
                    self.status_label.config(text=f"錯誤: {str(e)}")
                    time.sleep(1)
    
    def start_capture(self):
        if not self.capture_region:
            messagebox.showwarning("未選擇區域", "請先選擇要擷取的螢幕區域！")
            return
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.monitor_combo.config(state=tk.DISABLED)
        self.region_btn.config(state=tk.DISABLED)
        self.status_label.config(text="正在擷取中...")
        
        # 在新執行緒中執行擷取
        self.capture_thread = threading.Thread(target=self.capture_and_translate, daemon=True)
        self.capture_thread.start()
    
    def stop_capture(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.monitor_combo.config(state="readonly")
        self.region_btn.config(state=tk.NORMAL)
        self.status_label.config(text="已停止")
    
    def clear_text(self):
        self.original_text.delete(1.0, tk.END)
        self.translation_text.delete(1.0, tk.END)
        self.last_text = ""
        self.status_label.config(text="已清空內容")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    # 需要安裝的套件:
    # pip install pytesseract pillow mss deep-translator
    # 
    # 還需要安裝 Tesseract OCR:
    # Windows: 從 https://github.com/UB-Mannheim/tesseract/wiki 下載安裝
    # 如果需要，在程式開頭加入：
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    app = ScreenTranslator()
    app.run()
