import os
import sys
import threading
import cv2
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import pystray
from pystray import MenuItem as item

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        # Arayüzü önizleme ve çubuk için biraz büyüttük
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = 800
        height = 650
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
        
        self.config(bg="#000000")
        self.attributes("-alpha", 0.0)
        self.fade_in()

        self.video_path = None
        self.cap = None  # VideoCapture objesini tutmak için
        self.current_frame = None # Ekranda görünen son kareyi tutmak için

        self.main_frame = ctk.CTkFrame(self, corner_radius=30, fg_color="#1a1a1a")
        self.main_frame.pack(expand=True, fill="both", padx=0, pady=0)

        self.main_frame.bind("<ButtonPress-1>", self.start_move)
        self.main_frame.bind("<B1-Motion>", self.do_move)

        # Tüm pencereyi sürükle-bırak hedefi yapıyoruz
        self.main_frame.drop_target_register(DND_FILES)
        self.main_frame.dnd_bind("<<Drop>>", self.on_drop)

        self.close_btn = ctk.CTkButton(
            self.main_frame, 
            text="✕", 
            width=40, 
            height=40,
            fg_color="transparent", 
            hover_color="#c0392b",
            text_color="white",
            font=("Arial", 16, "bold"),
            corner_radius=20,
            command=self.on_closing
        )
        self.close_btn.place(relx=0.95, rely=0.04, anchor="center")

        self.minimize_btn = ctk.CTkButton(
            self.main_frame,
            text="—",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color="#2c3e50",
            text_color="white",
            font=("Arial", 16, "bold"),
            corner_radius=20,
            command=self.minimize_to_tray
        )
        self.minimize_btn.place(relx=0.89, rely=0.04, anchor="center")

        self.tray_icon = None

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#ecf0f1"
        )
        self.title_label.pack(pady=(30, 0))
        self.animate_text("🎞️ Frame Extractor", 0)

        self.subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Video bırak, istediğin kareyi seç ve kayıpsız PNG olarak kaydet.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#95a5a6"
        )
        self.subtitle.pack(pady=(0, 15))

        # --- ÖNİZLEME ALANI ---
        self.preview_label = ctk.CTkLabel(
            self.main_frame,
            text="📥 Video Sürükleyip Bırakın",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            fg_color="#2c3e50",
            corner_radius=15,
            width=640,
            height=360
        )
        self.preview_label.pack(pady=10)
        self.preview_label.pack_propagate(False)

        # --- KONTROL ÇUBUĞU (SLIDER) ---
        self.slider_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.slider_frame.pack(fill="x", padx=80, pady=(10, 0))
        
        self.frame_slider = ctk.CTkSlider(
            self.slider_frame, 
            from_=0, 
            to=100, 
            command=self.on_slider_move,
            state="disabled", # Video yüklenene kadar kapalı
            button_color="#3498db",
            button_hover_color="#2980b9"
        )
        self.frame_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.frame_slider.set(0)

        self.frame_count_label = ctk.CTkLabel(
            self.slider_frame, text="0 / 0", font=ctk.CTkFont(size=12), text_color="#bdc3c7"
        )
        self.frame_count_label.pack(side="right")

        # --- KAYDET BUTONU ---
        self.save_btn = ctk.CTkButton(
            self.main_frame,
            text="📸 Seçili Kareyi Kaydet",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#27ae60",
            hover_color="#2ecc71",
            corner_radius=8,
            height=40,
            state="disabled",
            command=self.save_current_frame
        )
        self.save_btn.pack(pady=20)

        self.status = ctk.CTkLabel(
            self.main_frame, 
            text="", 
            font=ctk.CTkFont(size=13), 
            text_color="#2ecc71"
        )
        self.status.pack(pady=0)

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.03
            self.attributes("-alpha", alpha)
            self.after(10, self.fade_in)

    def animate_text(self, text, index):
        if index < len(text):
            self.title_label.configure(text=self.title_label.cget("text") + text[index])
            self.after(16, self.animate_text, text, index + 1)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def on_drop(self, event):
        path = event.data.strip("{}")
        if not path.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            self.status.configure(text="❌ Geçersiz video formatı", text_color="#e74c3c")
            return

        self.video_path = path
        self.status.configure(text="⏳ Video yükleniyor...", text_color="#f39c12")
        self.update()

        # Eski video açıksa kapat
        if self.cap is not None:
            self.cap.release()

        self.cap = cv2.VideoCapture(self.video_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if self.total_frames <= 0:
            self.status.configure(text="❌ Video okunamadı", text_color="#e74c3c")
            return

        # Slider ayarlarını güncelle
        self.frame_slider.configure(state="normal", from_=0, to=self.total_frames - 1, number_of_steps=self.total_frames)
        self.frame_slider.set(0)
        self.save_btn.configure(state="normal")
        
        self.status.configure(text="✅ Video yüklendi. Çubuğu kaydırarak kare seçin.", text_color="#3498db")
        
        # İlk kareyi göster
        self.show_frame(0)

    def on_slider_move(self, value):
        frame_idx = int(float(value))
        self.show_frame(frame_idx)

    def show_frame(self, frame_idx):
        if self.cap is None:
            return

        # Videoyu istenen kareye sar
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()

        if ret:
            self.current_frame = frame
            self.frame_count_label.configure(text=f"{frame_idx} / {self.total_frames - 1}")
            
            # OpenCV (BGR) formatını PIL (RGB) formatına çevir
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)

            # Görüntüyü önizleme alanına (640x360) sığacak şekilde yeniden boyutlandır (Aspect Ratio koruyarak)
            pil_img.thumbnail((640, 360), Image.Resampling.LANCZOS)
            
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            self.preview_label.configure(image=ctk_img, text="")
        else:
            self.status.configure(text="❌ Kare okunamadı", text_color="#e74c3c")

    def save_current_frame(self):
        if self.current_frame is None or self.video_path is None:
            return

        # Şu anki frame numarasını al
        current_idx = int(self.frame_slider.get())
        
        base_name = os.path.splitext(self.video_path)[0]
        output_path = f"{base_name}_frame_{current_idx}.png"

        # OpenCV PNG formatını varsayılan olarak kayıpsız kaydeder.
        # Maksimum kalite (sıfır sıkıştırma) istersen parametre ekleyebiliriz ama 
        # varsayılan ayar zaten görsel kayıp yaşatmaz, sadece dosya boyutunu optimize eder.
        cv2.imwrite(output_path, self.current_frame)

        filename = os.path.basename(output_path)
        self.status.configure(
            text=f"✅ Kaydedildi: {filename}",
            text_color="#2ecc71"
        )

    def minimize_to_tray(self):
        self.withdraw()
        if self.tray_icon is None:
            self._start_tray_icon()

    def _start_tray_icon(self):
        resource_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(resource_dir, "app.jpeg")
        try:
            icon_image = Image.open(icon_path).resize((64, 64))
        except (FileNotFoundError, IOError, OSError):
            icon_image = Image.new("RGB", (64, 64), color=(26, 26, 26))

        menu = pystray.Menu(
            item("Aç", self._restore_from_tray, default=True),
            item("Kapat", self._quit_from_tray)
        )
        self.tray_icon = pystray.Icon("FrameExtractor", icon_image, "Frame Extractor", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore_from_tray(self, icon=None, tray_item=None):
        self.after(0, self._show_window)

    def _show_window(self):
        if self.tray_icon is not None:
            self.tray_icon.stop()
            self.tray_icon = None
        self.deiconify()
        self.lift()
        self.focus_force()

    def _quit_from_tray(self, icon=None, tray_item=None):
        self.after(0, self._quit_app)

    def _quit_app(self):
        if self.tray_icon is not None:
            self.tray_icon.stop()
            self.tray_icon = None
        self.on_closing()

    def on_closing(self):
        if self.cap is not None:
            self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
