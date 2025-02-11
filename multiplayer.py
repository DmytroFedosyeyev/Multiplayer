from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QColor, QLinearGradient, QBrush, QPalette, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider,
    QLabel, QFileDialog, QHBoxLayout, QListWidget, QScrollArea, QMessageBox
)
import os
import sys

class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация медиаплеера и виджета для видео
        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: black;")  # Проверка отображения
        self.video_widget.setMinimumSize(640, 480)  # Установите минимальный размер

        # Виджет для отображения картинки (для аудио и логотипа)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.image_label.setMinimumSize(640, 480)

        # Список для хранения путей к медиафайлам
        self.playlist = []
        self.current_index = -1  # Текущий индекс в плейлисте

        # Основной макет
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)  # Отступы
        self.layout.setSpacing(10)  # Расстояние между элементами

        # Градиентный фон
        self.setAutoFillBackground(True)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(40, 40, 40))  # Тёмно-серый
        gradient.setColorAt(1, QColor(20, 20, 20))  # Почти чёрный

        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        # Метка для отображения текущего файла
        self.label = QLabel("No file selected")
        self.label.setStyleSheet("color: white; font-size: 14px;")
        self.layout.addWidget(self.label)

        # Кнопка для добавления медиафайлов
        self.open_button = QPushButton("Add Media")
        self.open_button.setStyleSheet(
            "QPushButton { background-color: #444; color: white; border: none; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #555; }"
        )
        self.open_button.clicked.connect(self.open_files)
        self.layout.addWidget(self.open_button)

        # Список для отображения добавленных медиафайлов
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.media_list = QListWidget()
        self.media_list.setStyleSheet(
            "QListWidget { background-color: #333; color: white; border: 1px solid #555; border-radius: 4px; }"
            "QListWidget::item { padding: 5px; }"
            "QListWidget::item:hover { background-color: #444; }"
        )
        scroll_area.setWidget(self.media_list)
        self.media_list.itemDoubleClicked.connect(self.select_media)
        self.layout.addWidget(scroll_area)

        # Кнопка для удаления выбранного трека
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setStyleSheet(
            "QPushButton { background-color: #555; color: white; border: none; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #666; }"
        )
        self.remove_button.clicked.connect(self.remove_selected_media)
        self.layout.addWidget(self.remove_button)

        # Виджет для отображения видео или картинки
        self.layout.addWidget(self.video_widget)
        self.layout.addWidget(self.image_label)
        self.player.setVideoOutput(self.video_widget)

        # По умолчанию скрываем видео и показываем логотип
        self.video_widget.hide()
        self.image_label.show()
        self.load_image(r"C:\Dima\Программирование\Projects\Player_Valera\Multiplayer\phone-with-music.jpg"
)  # Загружаем логотип при запуске

        # Слайдер для перемотки
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setStyleSheet(
            "QSlider::groove:horizontal { background: #444; height: 8px; border-radius: 4px; }"
            "QSlider::handle:horizontal { background: white; width: 16px; height: 16px; margin: -4px 0; border-radius: 8px; }"
        )
        self.position_slider.setEnabled(False)
        self.position_slider.sliderReleased.connect(self.seek_media)
        self.layout.addWidget(self.position_slider)

        # Панель управления (кнопки)
        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.play_button = QPushButton("▶️ Play")
        self.play_button.setStyleSheet(
            "QPushButton { background-color: #555; color: white; border: none; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #666; }"
        )
        self.play_button.clicked.connect(self.play_media)
        controls.addWidget(self.play_button)

        self.pause_button = QPushButton("⏸ Pause")
        self.pause_button.setStyleSheet(
            "QPushButton { background-color: #555; color: white; border: none; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #666; }"
        )
        self.pause_button.clicked.connect(self.pause_media)
        controls.addWidget(self.pause_button)

        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: #555; color: white; border: none; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #666; }"
        )
        self.stop_button.clicked.connect(self.stop_media)
        controls.addWidget(self.stop_button)

        self.prev_button = QPushButton("⏮ Previous")
        self.prev_button.setStyleSheet(
            "QPushButton { background-color: #555; color: white; border: none; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #666; }"
        )
        self.prev_button.clicked.connect(self.previous_media)
        controls.addWidget(self.prev_button)

        self.next_button = QPushButton("⏭ Next")
        self.next_button.setStyleSheet(
            "QPushButton { background-color: #555; color: white; border: none; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #666; }"
        )
        self.next_button.clicked.connect(self.next_media)
        controls.addWidget(self.next_button)

        # Кнопка для полноэкранного режима
        self.fullscreen_button = QPushButton("⛶ Fullscreen")
        self.fullscreen_button.setStyleSheet(
            "QPushButton { background-color: #555; color: white; border: none; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #666; }"
        )
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        controls.addWidget(self.fullscreen_button)

        self.layout.addLayout(controls)

        # Слайдер для регулировки громкости
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setStyleSheet(
            "QSlider::groove:horizontal { background: #444; height: 8px; border-radius: 4px; }"
            "QSlider::handle:horizontal { background: white; width: 16px; height: 16px; margin: -4px 0; border-radius: 8px; }"
        )
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.layout.addWidget(QLabel("Volume"))
        self.layout.addWidget(self.volume_slider)

        self.setLayout(self.layout)

        # Подключение сигналов
        self.player.positionChanged.connect(self.update_slider)
        self.player.durationChanged.connect(self.set_slider_range)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.error.connect(self.handle_error)

    def open_files(self):
        """Открытие медиафайлов и добавление их в плейлист."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Media Files", "", "Media Files (*.mp3 *.wav *.mp4 *.avi)"
        )
        if files:
            for file_path in files:
                if os.path.exists(file_path):
                    self.playlist.append(file_path)
                    self.media_list.addItem(os.path.basename(file_path))
                    print(f"Added to playlist: {file_path}")  # Отладочное сообщение
                else:
                    self.label.setText(f"File not found: {file_path}")
                    print(f"File not found: {file_path}")  # Отладочное сообщение

    def remove_selected_media(self):
        """Удаление выбранного трека из плейлиста."""
        selected_item = self.media_list.currentRow()
        if selected_item >= 0:
            self.media_list.takeItem(selected_item)
            self.playlist.pop(selected_item)
            if self.current_index >= selected_item:
                self.current_index -= 1
            print(f"Removed item at index: {selected_item}")  # Отладочное сообщение
        else:
            QMessageBox.warning(self, "Warning", "No item selected to remove.")

    def select_media(self):
        """Выбор медиафайла из списка."""
        self.current_index = self.media_list.currentRow()
        self.play_media_at_index()

    def play_media_at_index(self):
        """Воспроизведение медиафайла по индексу."""
        if 0 <= self.current_index < len(self.playlist):
            file_path = self.playlist[self.current_index]
            self.label.setText(f"Playing: {os.path.basename(file_path)}")
            print(f"Attempting to play: {file_path}")  # Отладочное сообщение

            media_content = QMediaContent(QUrl.fromLocalFile(file_path))
            self.player.setMedia(media_content)
            self.player.play()
            self.position_slider.setEnabled(True)

            # Определяем, аудио это или видео
            if file_path.endswith((".mp3", ".wav")):  # Аудиофайл
                self.video_widget.hide()
                self.image_label.show()
                self.load_image(r"C:\Dima\Программирование\Projects\Player_Valera\My_variant\5276349319089350565.jpg")  # Загружаем картинку
            else:  # Видеофайл
                self.image_label.hide()
                self.video_widget.show()

            # Убедитесь, что виджет обновляется
            self.video_widget.update()
        else:
            print("Invalid index or empty playlist")  # Отладочное сообщение

    def load_image(self, image_path):
        """Загрузка и отображение картинки."""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            print(f"Image not found: {image_path}")  # Отладочное сообщение

    def update_slider(self, position):
        """Обновление позиции слайдера."""
        self.position_slider.setValue(position)

    def set_slider_range(self, duration):
        """Установка диапазона слайдера."""
        self.position_slider.setRange(0, duration)

    def seek_media(self):
        """Перемотка медиа."""
        pos = self.position_slider.value()
        self.player.setPosition(pos)

    def play_media(self):
        """Воспроизведение медиа."""
        if self.current_index == -1 and self.playlist:
            self.current_index = 0
            self.play_media_at_index()
        else:
            self.player.play()

    def pause_media(self):
        """Пауза."""
        self.player.pause()

    def stop_media(self):
        """Остановка воспроизведения."""
        self.player.stop()
        self.position_slider.setValue(0)
        self.show_logo()  # Показываем логотип при остановке

    def show_logo(self):
        """Показ логотипа."""
        self.video_widget.hide()
        self.image_label.show()
        self.load_image("logo.jpg")  # Загружаем логотип

    def previous_media(self):
        """Переход к предыдущему медиафайлу."""
        if self.current_index > 0:
            self.current_index -= 1
            self.play_media_at_index()

    def next_media(self):
        """Переход к следующему медиафайлу."""
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.play_media_at_index()

    def change_volume(self, value):
        """Изменение громкости."""
        self.player.setVolume(value)

    def toggle_fullscreen(self):
        """Переключение в полноэкранный режим."""
        if self.video_widget.isFullScreen():
            self.video_widget.setFullScreen(False)
            QMessageBox.information(self, "Fullscreen", "Вы вышли из полноэкранного режима.")
        else:
            self.video_widget.setFullScreen(True)
            QMessageBox.information(self, "Fullscreen", "Вы вошли в полноэкранный режим. Нажмите Esc для выхода.")

    def keyPressEvent(self, event: QKeyEvent):
        """Обработка нажатия клавиш."""
        if event.key() == Qt.Key_Escape and self.video_widget.isFullScreen():
            self.video_widget.setFullScreen(False)
            QMessageBox.information(self, "Fullscreen", "Вы вышли из полноэкранного режима.")

    def on_media_status_changed(self, status):
        """Обработка изменения статуса медиа."""
        if status == QMediaPlayer.EndOfMedia:
            self.next_media()

    def handle_error(self):
        """Обработка ошибок."""
        error = self.player.error()
        error_string = self.player.errorString()
        self.label.setText(f"Error: {error} - {error_string}")
        print(f"Media error: {error} - {error_string}")  # Отладочное сообщение
        QMessageBox.critical(self, "Error", f"Media playback error: {error_string}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Player")
        self.setGeometry(100, 100, 800, 600)
        self.media_player = MediaPlayer()
        self.setCentralWidget(self.media_player)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())