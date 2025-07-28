
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import (
    QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
)
from PyQt5.QtCore import Qt, QSize, QTimer

from dotenv import dotenv_values
import sys
import os


env_varrs = dotenv_values(".env")
Assistantname = env_varrs.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()


def SetMicrophoneStatus(command):
    with open(rf'{TempDirPath}\Mic.data', 'w', encoding='utf-8') as file:
        file.write(command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', 'r', encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', 'r', encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(filename):
    path = rf'{GraphicsDirPath}\{filename}'
    return path
def TempDirectoryPath(filename):
    path = rf'{TempDirPath}\{filename}'
    return path
def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Response.data', 'w', encoding='utf-8') as file:
        file.write(Text)    


class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)

        layout.addWidget(self.chat_text_edit)
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(0, 1)  # Corrected index to 0

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setStyleSheet("background-color: black;")

        # Optional: Set default text color format
        text_color = QColor(Qt.blue)
        text_color_format = QTextCharFormat()
        text_color_format.setForeground(text_color)
        # self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.chat_text_edit.setCurrentCharFormat(text_color_format)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie (GraphicsDirectoryPath('friday.gif'))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize (max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment (Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie (movie)
        movie.start()
        layout.addWidget(self.gif_label)
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment (Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing (-10)
        # layout.addWidget(self.gif_label)
        font = QFont()
        font.setPointSize(11)
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        # self.timer.timeout.connect(self.loadMessages)
        # self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecoText)
        self.timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
                QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
                }
                QScrollBar:: handle:vertical {
                background: white;
                min-height: 20px;
                }

                QScrollBar:: add-line: vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
                }
                QScrollBar:: sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
                }

                QScrollBar:: up-arrow: vertical, QScrollBar:: down-arrow: vertical {
                border: none;
                background: none;
                color: none;
                }
                QScrollBar:: add-page: vertical, QScrollBar:: sub-page: vertical {
                background: none;
                }
        """)
    def loadMessages(self):
        global old_chat_message

        with open(TempDirectoryPath('Response.data'), "r", encoding='utf-8') as file:
            messages = file.read()

            if None == messages:
                pass
            elif len(messages) <= 1:
                pass
            elif str(old_chat_message) == str(messages):
                pass
            else:
                self.addMessage(message=messages, color='white')
                old_chat_message = messages
    def SpeechRecoText(Self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            Self.label.setText(messages)
    
    def load_icons(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)
    
    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60,60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled
    
    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin (10)
        formatm.setLeftMargin (10)
        format.setForeground (QColor(color))
        cursor.setCharFormat (format)
        cursor.setBlockFormat (formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


# class InitialScreen(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         desktop = QApplication.desktop()
#         screen_width = desktop.screenGeometry().width()
#         screen_height = desktop.screenGeometry().height()
#         content_layout = QVBoxLayout()
#         content_layout.setContentsMargins(0, 0, 0, 0)
#         gif_label =QLabel()
#         movie = QMovie (GraphicsDirectoryPath('friday.gif'))
#         gif_label.setMovie (movie)
#         max_gif_size_H = int(screen_width / 16 * 9)
#         movie.setScaledSize (QSize (screen_width, max_gif_size_H))
#         gif_label.setAlignment (Qt. AlignCenter)
#         movie.start()
#         # gif_label.setSizePolicy (QSize. Policy. Expanding, QSize. Policy. Expanding)
#         gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self.icon_label = QLabel()
#         pixmap = QPixmap (GraphicsDirectoryPath('Mic_on.png'))
#         new_pixmap = pixmap.scaled(60, 60)
#         self.icon_label.setPixmap (new_pixmap)
#         self.icon_label.setFixedSize (150,150)
#         self.icon_label.setAlignment (Qt.AlignCenter)
#         self.toggled = True
#         self.toggle_icon()
#         self.icon_label.mousePressEvent = self.toggle_icon
#         self.label = QLabel("")
#         self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
#         content_layout.addWidget(gif_label, alignment=Qt. AlignCenter)
#         content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
#         content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
#         content_layout.setContentsMargins(0, 0, 0, 150)
#         self.setLayout(content_layout)
#         self.setFixedHeight (screen_height)
#         self.setFixedWidth (screen_width)
#         self.setStyleSheet("background-color: black;")
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.SpeechRecogText)
#         self.timer.start(5)

#     def SpeechRecogText(self):
#         with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
#             messages = file.read()
#             self.label.setText(messages)

#     # def load_icon(self, path, width=60, height=60):
#     #     pixmap = QPixmap(path)
#     #     new_pixmap = pixmap.scaled (width, height)
#     #     self.icon_label.setPixmap (new_pixmap)
#     def load_icon(self, path, width=60, height=60):
#         if not os.path.exists(path):
#             print(f"❌ Image not found: {path}")
#         else:
#             print(f"✅ Image found: {path}")
#         pixmap = QPixmap(path)
#         if pixmap.isNull():
#             print(f"❌ Failed to load pixmap: {path}")
#         new_pixmap = pixmap.scaled(width, height)
#         self.icon_label.setPixmap(new_pixmap)
    

#     def toggle_icon (self, event=None):
#         if self.toggled:
#             self.load_icon (GraphicsDirectoryPath('Mic_on.png'), 60, 60)
#             MicButtonInitialed()
#         else:
#             self.load_icon (GraphicsDirectoryPath('Mic_off.png'), 60, 60)
#             MicButtonClosed()
#         self.toggled = not self.toggled

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Screen size
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # ====== GIF Section ======
        self.gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('friday.gif'))

        # Adjust GIF size based on screen
        gif_width = int(screen_width * 0.5)
        gif_height = int(gif_width * 9 / 16)
        movie.setScaledSize(QSize(gif_width, gif_height))

        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        # ====== Assistant Status Label ======
        self.label = QLabel("Available ...")
        self.label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: 600;
            padding: 10px;
        """)
        self.label.setAlignment(Qt.AlignCenter)

        # ====== Mic Button ======
        self.icon_label = QLabel()
        self.toggled = True
        self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.mousePressEvent = self.toggle_icon


        # Add widgets to layout
        layout.addStretch()
        layout.addWidget(self.gif_label)
        layout.addWidget(self.label)
        # layout.addWidget(self.icon_label)
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        layout.addStretch()

        # Set final UI properties
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

        # Timer for assistant status update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    def load_icon(self, path):
        pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'))
            MicButtonClosed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
            MicButtonInitialed()
        self.toggled = not self.toggled

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages if messages else "Available ...")


class MessageScreen (QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight (screen_height)
        self.setFixedWidth (screen_width)

# class CustomTopBar(QWidget):
#     def __init__(self, parent, stacked_widget):
#         super().__init__(parent)
#         self.initUI()
#         self.current_screen = None
#         self.stacked_widget = stacked_widget

#     def initUI(self):
#         self.setFixedHeight (50)
#         layout =  QHBoxLayout(self)
#         layout.setAlignment (Qt. AlignRight)
#         home_button = QPushButton()
#         home_icon = QIcon (GraphicsDirectoryPath("Home.png"))
#         home_button.setIcon(home_icon)
#         home_button.setText(" Home")
#         home_button.setStyleSheet ("height: 40px; line-height: 40px; background-color: white; color: black")
#         message_button = QPushButton()
#         message_icon = QIcon (GraphicsDirectoryPath("Chats.png"))
#         message_button.setIcon(message_icon)
#         message_button.setText(" Chat")
#         message_button.setStyleSheet ("height: 40px; line-height: 40px; background-color: white; color: black")
#         minimize_button = QPushButton()
#         minimize_icon = QIcon(GraphicsDirectoryPath( 'Minimize2.png'))
#         minimize_button.setIcon(minimize_icon)
#         minimize_button.setStyleSheet ("background-color: white")
#         minimize_button.clicked.connect(self.minimizeWindow)
#         self.maximize_button = QPushButton()
#         self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
#         self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
#         self.maximize_button.setIcon(self.maximize_icon)
#         self.maximize_button.setFlat (True)
#         self.maximize_button.setStyleSheet ("background-color:white")
#         self.maximize_button.clicked.connect(self.maximizeWindow)
#         close_button = QPushButton()
#         close_icon = QIcon (GraphicsDirectoryPath('Close.png'))
#         close_button.setIcon(close_icon)
#         close_button.setStyleSheet("background-color:white")
#         close_button.clicked.connect(self.closeWindow)
#         line_frame = QFrame()
#         line_frame.setFixedHeight (1)
#         line_frame.setFrameShape (QFrame. HLine)
#         line_frame.setFrameShadow (QFrame. Sunken)
#         line_frame.setStyleSheet ("border-color: black;")
#         title_label = QLabel(f" {str(Assistantname). capitalize()} AI ")
#         title_label.setStyleSheet("color: black; font-size: 18px;; background-color:white")
#         home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
#         message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
#         layout.addWidget(title_label)
#         layout.addStretch (1)
#         layout.addWidget(home_button)
#         layout.addWidget(message_button)
#         layout.addStretch (1)
#         layout.addWidget(minimize_button)
#         layout.addWidget(self.maximize_button)
#         layout.addWidget(close_button)
#         layout.addWidget(line_frame)
#         self.draggable = True
#         self.offset = None
    
#     def paintEvent(self, event):
#         painter = QPainter(self)
#         # painter.fillRect(self.react(), Qt.white)
#         painter.fillRect(self.rect(), Qt.white)
#         super().paintEvent(event)

#     def minimizeWindow(self):
#         self.parent().showMinimized()

#     def maximizeWindow(self):
#         if self.parent().isMaximized():
#             self.parent().showNormal()
#             self.maximize_button.setIcon(self.maximize_icon)
#         else:
#             self.parent().showMaximized()
#             self.maximize_button.setIcon(self.restore_icon)

#     def closeWindow(self):
#         self.parent().close()
    
#     def mousePressEvent(self, event):
#         if self.draggable:
#             self.offset = event.pos()
    
#     def mouseMoveEvent(self, event):
#         if self.draggable and self.offset:
#             new_pos = event.globalPos() - self.offset
#             self.parent().move(new_pos)

#     def showMessageScreen (self):
#         if self.current_screen is not None:
#             self.current_screen.hide()
#             message_screen = MessageScreen(self)
#             layout = self.parent().layout()
#             if layout is not None:
#                 layout.addWidget(message_screen)
#             self.current_screen=message_screen
#     def showInitialScreen(self):
#         if self.current_screen is not None:
#             self.current_screen.hide()

#         initial_screen = InitialScreen(self)
#         layout = self.parent().layout()
#         if layout is not None:
#             layout.addWidget(initial_screen)
#         self.current_screen = initial_screen

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize title bar with modern black theme"""
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)
        
        # Title label with app name and glowing effect
        title_label = QLabel(f" {Assistantname} AI ")
        title_label.setStyleSheet("""
            QLabel {
                color: #2367FA;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                padding-left: 10px;
            }
        """)
        
        # Add glow effect to the title
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(15)
        glow.setColor(QColor("#2367FA"))
        glow.setOffset(0, 0)
        title_label.setGraphicsEffect(glow)
        
        # Navigation buttons with hover effects
        self.home_btn = self.create_nav_button("Home.png", "Home", "#2367FA")
        self.chat_btn = self.create_nav_button("Chats.png", "Chat", "#2367FA")
        
        # Spacer to push window controls to the right
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.home_btn)
        layout.addWidget(self.chat_btn)
        layout.addStretch()
        
        # Modern window controls with consistent blue hover
        self.minimize_btn = self.create_control_button("Minimize.png", "#5E5E5E", "#2367FA")
        self.maximize_btn = self.create_control_button("Maximize.png", "#5E5E5E", "#2367FA")
        self.close_btn = self.create_control_button("Close.png", "#5E5E5E", "#FF5555")
        
        # ===== Restart Button =====
        self.restart_btn = QPushButton("⭯")
        self.restart_btn.setToolTip("Restart Assistant")
        self.restart_btn.setFixedSize(32, 32)
        self.restart_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 18px;
                color: #AAAAAA;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #2367FA;
                color: white;
            }
        """)
        self.restart_btn.clicked.connect(self.restart_app)
        layout.addWidget(self.restart_btn)

        # Add window controls
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        
        # Connect signals
        self.home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.chat_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.minimize_btn.clicked.connect(self.parent().showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent().close)
        
        # Draggable window setup
        self.draggable = True
        self.offset = None
        
        # Set background style
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #333;
            }
        """)
        
    def create_nav_button(self, icon, text, hover_color):
        """Create navigation button with hover effect"""
        btn = QPushButton(text)
        btn.setIcon(QIcon(GraphicsDirectoryPath(icon)))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #AAAAAA;
                border: none;
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                color: {hover_color};
                background-color: rgba(35, 103, 250, 0.2);
            }}
        """)
        return btn
        
    def create_control_button(self, icon, normal_color, hover_color):
        """Create window control button with hover effect"""
        btn = QPushButton()
        btn.setIcon(QIcon(GraphicsDirectoryPath(icon)))
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        return btn
        
    def toggle_maximize(self):
        """Toggle between maximized and normal window state with icon change"""
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_btn.setIcon(QIcon(GraphicsDirectoryPath("Maximize.png")))
            self.maximize_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 16px;
                }
                QPushButton:hover {
                    background-color: #2367FA;
                }
            """)
        else:
            self.parent().showMaximized()
            self.maximize_btn.setIcon(QIcon(GraphicsDirectoryPath("Restore.png")))
            self.maximize_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 16px;
                }
                QPushButton:hover {
                    background-color: #2367FA;
                }
            """)
            
    def paintEvent(self, event):
        """Paint the title bar background with rounded corners"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rectangle background
        painter.setBrush(QColor("#121212"))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        
        # Draw bottom border
        painter.setPen(QColor("#333"))
        painter.drawLine(0, self.height()-1, self.width(), self.height()-1)
        
        super().paintEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.offset)
    def restart_app(self):
        import os
        import sys
        os.execl(sys.executable, sys.executable, *sys.argv)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
    
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen(self)
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()