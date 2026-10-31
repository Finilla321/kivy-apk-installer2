import os
import zipfile
import json
import shutil
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform

class InstallerWidget(BoxLayout):
    def __init__(self, file_to_install=None, **kwargs):
        super().__init__(orientation='vertical', padding=30, spacing=20, **kwargs)
        self.file_path = file_to_install
        self.temp_dir = "/sdcard/Download/.installer_temp"
        
        # Название файла
        display_name = os.path.basename(self.file_path) if self.file_path else "Файл не выбран"
        self.lbl_title = Label(text=display_name, font_size='18sp', bold=True, halign='center')
        self.add_widget(self.lbl_title)
        
        # Статус
        self.lbl_status = Label(text="Готов к установке в 1 клик", font_size='14sp', color=(0.7, 0.7, 0.7, 1))
        self.add_widget(self.lbl_status)
        
        # Анимированный прогресс-бар
        self.progress = ProgressBar(max=100, value=0)
        self.add_widget(self.progress)
        
        # Кнопка установки
        self.btn_install = Button(text="Установить", size_hint=(1, 0.3), background_color=(0.1, 0.5, 0.8, 1))
        self.btn_install.bind(on_press=self.start_install_process)
        self.add_widget(self.btn_install)

    def start_install_process(self, instance):
        if not self.file_path or not os.path.exists(self.file_path):
            self.lbl_status.text = "Ошибка: Файл не найден!"
            return
        
        self.btn_install.disabled = True
        # Запуск установки в фоновом потоке Android, чтобы UI не зависал и шла анимация
        threading.Thread(target=self.run_installer, daemon=True).start()

    def set_ui_state(self, status_text, progress_val):
        # Безопасное обновление интерфейса из фонового потока
        Clock.schedule_once(lambda dt: self._update_ui(status_text, progress_val))

    def _update_ui(self, status_text, progress_val):
        self.lbl_status.text = status_text
        self.progress.value = progress_val

    def run_installer(self):
        ext = os.path.splitext(self.file_path)[1].lower()
        
        # Очищаем временную папку
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        try:
            if ext == ".apk":
                self.set_ui_state("Отправка одиночного APK...", 30)
                # Команда тихой установки через Shizuku (утилита risu / pm)
                cmd = f"shizuku -c 'pm install -r -d {self.file_path}'"
                os.system(cmd)
                
            elif ext in [".xapk", ".apks", ".zip"]:
                self.set_ui_state("Распаковка сплит-пакетов...", 20)
                with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_dir)
                
                # Собираем все сплиты
                all_files = os.listdir(self.temp_dir)
                apk_files = [os.path.join(self.temp_dir, f) for f in all_files if f.endswith('.apk')]
                
                if not apk_files:
                    raise Exception("Внутри пакета не найдено APK!")
                
                self.set_ui_state(f"Подготовка {len(apk_files)} компонентов...", 50)
                
                # Формируем единый массив путей для выполнения команды pm install-multiple
                paths_str = " ".join([f"'{p}'" for p in apk_files])
                
                self.set_ui_state("Тихая установка в систему...", 75)
                # Вызов через встроенный в HyperOS шелл Shizuku
                cmd = f"shizuku -c 'pm install-multiple -r -d {paths_str}'"
                os.system(cmd)
                
            self.set_ui_state("Приложение успешно установлено!", 100)
            Clock.schedule_once(lambda dt: setattr(self.btn_install, 'text', 'Готово'))
            
        except Exception as e:
            self.set_ui_state(f"Ошибка установки: {str(e)}", 0)
            Clock.schedule_once(lambda dt: setattr(self.btn_install, 'disabled', False))
            
        finally:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

class MobileInstallerApp(App):
    def build(self):
        # Перехват интента открытия файла Android (если передан путь)
        # В реальной сборке здесь считывается sys.argv или Android Intent Context
        target_file = "/sdcard/Download/app.xapk" # Тестовый путь
        return InstallerWidget(file_to_install=target_file)

if __name__ == "__main__":
    MobileInstallerApp().run()
