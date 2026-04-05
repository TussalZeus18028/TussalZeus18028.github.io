import sys
import os
import json
import shutil
import re
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
    QLabel, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QSplitter, QGroupBox, QSpinBox, QCheckBox, QComboBox,
    QColorDialog, QScrollArea, QTextBrowser
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QIcon

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

# ---------- 配置 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "cyber_config.json")
ARTICLES_JSON = os.path.join(BASE_DIR, "date", "articles.json")
DOWNLOADS_JSON = os.path.join(BASE_DIR, "download.json")
DATE_DIR = os.path.join(BASE_DIR, "date")
FILES_DIR = os.path.join(BASE_DIR, "Files")

os.makedirs(DATE_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

if not os.path.exists(ARTICLES_JSON):
    with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)
if not os.path.exists(DOWNLOADS_JSON):
    with open(DOWNLOADS_JSON, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)


def slugify(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    return s[:50]


def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KiB', 'MiB', 'GiB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}" if unit != 'B' else f"{size_bytes} B"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GiB"


# ---------- 主题管理器 ----------
class ThemeManager:
    def __init__(self):
        self.themes = {
            "dark": self.get_dark_theme(),
            "light": self.get_light_theme(),
            "custom": self.get_dark_theme()
        }

    def get_dark_theme(self):
        return """
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #363636;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: #ffa300;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #999;
            }
            QPushButton.danger {
                background-color: #f44336;
            }
            QPushButton.danger:hover {
                background-color: #da190b;
            }
            QLineEdit, QComboBox, QTextEdit, QListWidget, QTableWidget {
                padding: 8px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: #404040;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #4CAF50;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 60px;
            }
            QTableWidget QPushButton:hover {
                background-color: #45a049;
            }
            QCheckBox {
                spacing: 8px;
                color: #ccc;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #555;
                background-color: #404040;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4CAF50;
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #363636;
            }
            QTabBar::tab {
                background-color: #404040;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #555;
            }
            QHeaderView::section {
                background-color: #151b2b;
                padding: 6px;
                border: none;
                font-weight: bold;
                color: #ffa300;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777;
            }
        """

    def get_light_theme(self):
        return """
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: #2e7d32;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
            QPushButton.danger {
                background-color: #f44336;
            }
            QPushButton.danger:hover {
                background-color: #da190b;
            }
            QLineEdit, QComboBox, QTextEdit, QListWidget, QTableWidget {
                padding: 8px;
                border: 2px solid #cccccc;
                border-radius: 4px;
                background-color: #ffffff;
                color: #333333;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #4CAF50;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 60px;
            }
            QTableWidget QPushButton:hover {
                background-color: #45a049;
            }
            QCheckBox {
                spacing: 8px;
                color: #333333;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #cccccc;
                background-color: #ffffff;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4CAF50;
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                color: #333333;
                font-weight: bold;
                background-color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #333333;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 6px;
                border: none;
                font-weight: bold;
                color: #2e7d32;
            }
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #cccccc;
                border-radius: 7px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #aaaaaa;
            }
        """

    def get_custom_theme(self, colors):
        bg = colors.get("background", "#2b2b2b")
        text = colors.get("text", "#ffffff")
        accent = colors.get("accent", "#4CAF50")
        border = colors.get("border", "#555555")
        group_bg = colors.get("group_bg", "#363636")
        input_bg = colors.get("input_bg", "#404040")
        button_bg = colors.get("button_bg", "#4CAF50")
        button_hover = colors.get("button_hover", "#45a049")
        return f"""
            QMainWindow, QWidget {{
                background-color: {bg};
                color: {text};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {border};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: {group_bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: {accent};
            }}
            QPushButton {{
                background-color: {button_bg};
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 70px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:disabled {{
                background-color: #666;
                color: #999;
            }}
            QPushButton.danger {{
                background-color: #f44336;
            }}
            QPushButton.danger:hover {{
                background-color: #da190b;
            }}
            QLineEdit, QComboBox, QTextEdit, QListWidget, QTableWidget {{
                padding: 8px;
                border: 2px solid {border};
                border-radius: 4px;
                background-color: {input_bg};
                color: {text};
                font-size: 12px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {accent};
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QTableWidget QPushButton {{
                background-color: {button_bg};
                border: none;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 60px;
            }}
            QTableWidget QPushButton:hover {{
                background-color: {button_hover};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {text};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {border};
                background-color: {input_bg};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {accent};
                background-color: {accent};
                border-radius: 3px;
            }}
            QProgressBar {{
                border: 2px solid {border};
                border-radius: 5px;
                text-align: center;
                color: {text};
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {accent};
                width: 20px;
            }}
            QTabWidget::pane {{
                border: 1px solid {border};
                background-color: {group_bg};
            }}
            QTabBar::tab {{
                background-color: {input_bg};
                color: {text};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {accent};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {border};
            }}
            QHeaderView::section {{
                background-color: {input_bg};
                padding: 6px;
                border: none;
                font-weight: bold;
                color: {accent};
            }}
            QScrollBar:vertical {{
                background-color: {bg};
                width: 15px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {border};
                border-radius: 7px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {accent};
            }}
        """

    def set_custom_colors(self, colors):
        self.themes["custom"] = self.get_custom_theme(colors)

    def get_theme(self, name):
        return self.themes.get(name, self.themes["dark"])


# ---------- 文章管理组件 ----------
class ArticleManager(QWidget):
    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_filename = None
        self.init_ui()
        self.load_articles()

    def init_ui(self):
        layout = QHBoxLayout(self)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.article_list = QListWidget()
        self.article_list.setMaximumWidth(280)
        self.article_list.itemClicked.connect(self.on_article_selected)
        btn_new = QPushButton("➕ 新建文章")
        btn_new.clicked.connect(self.new_article)
        left_layout.addWidget(QLabel("📄 文章列表"))
        left_layout.addWidget(self.article_list)
        left_layout.addWidget(btn_new)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        form = QWidget()
        form_layout = QFormLayout(form)
        self.title_edit = QLineEdit()
        self.date_edit = QLineEdit(datetime.now().strftime("%Y.%m.%d"))
        self.category_edit = QLineEdit("TECH")
        self.excerpt_edit = QTextEdit()
        self.excerpt_edit.setMaximumHeight(80)
        form_layout.addRow("标题:", self.title_edit)
        form_layout.addRow("日期:", self.date_edit)
        form_layout.addRow("分类:", self.category_edit)
        form_layout.addRow("摘要:", self.excerpt_edit)

        self.md_edit = QTextEdit()
        self.md_edit.setPlaceholderText("Markdown 内容...")
        self.preview = QTextBrowser() if MARKDOWN_AVAILABLE else None
        if self.preview:
            self.preview.setOpenExternalLinks(True)

        btn_bar = QHBoxLayout()
        btn_save = QPushButton("💾 保存")
        btn_save.clicked.connect(self.save_article)
        btn_delete = QPushButton("🗑️ 删除")
        btn_delete.clicked.connect(self.delete_article)
        btn_preview = QPushButton("👁️ 预览")
        if btn_preview and self.preview:
            btn_preview.clicked.connect(self.preview_markdown)
        btn_bar.addWidget(btn_save)
        btn_bar.addWidget(btn_delete)
        if btn_preview:
            btn_bar.addWidget(btn_preview)
        btn_bar.addStretch()

        right_layout.addWidget(form)
        right_layout.addWidget(QLabel("📝 Markdown 内容:"))
        right_layout.addWidget(self.md_edit)
        if self.preview:
            splitter = QSplitter(Qt.Vertical)
            splitter.addWidget(self.md_edit)
            splitter.addWidget(self.preview)
            right_layout.addWidget(splitter)
        else:
            right_layout.addWidget(self.md_edit)
        right_layout.addLayout(btn_bar)

        layout.addWidget(left, 1)
        layout.addWidget(right, 3)

    def load_articles(self):
        try:
            with open(ARTICLES_JSON, "r", encoding="utf-8") as f:
                self.articles = json.load(f)
        except:
            self.articles = []
        self.refresh_list()

    def refresh_list(self):
        self.article_list.clear()
        for art in self.articles:
            item = QListWidgetItem(f"{art.get('title','')}  [{art.get('date','')}]")
            item.setData(Qt.UserRole, art.get("filename"))
            self.article_list.addItem(item)
        if self.articles:
            self.article_list.setCurrentRow(0)
            self.on_article_selected(self.article_list.item(0))

    def on_article_selected(self, item):
        filename = item.data(Qt.UserRole)
        self.current_filename = filename
        article = next((a for a in self.articles if a.get("filename") == filename), None)
        if not article:
            return
        self.title_edit.setText(article.get("title", ""))
        self.date_edit.setText(article.get("date", ""))
        self.category_edit.setText(article.get("category", ""))
        self.excerpt_edit.setPlainText(article.get("excerpt", ""))
        md_path = os.path.join(DATE_DIR, filename)
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                self.md_edit.setPlainText(f.read())
        else:
            self.md_edit.clear()

    def new_article(self):
        self.current_filename = None
        self.title_edit.clear()
        self.date_edit.setText(datetime.now().strftime("%Y.%m.%d"))
        self.category_edit.setText("TECH")
        self.excerpt_edit.clear()
        self.md_edit.clear()
        self.article_list.clearSelection()

    def save_article(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "警告", "标题不能为空")
            return
        date = self.date_edit.text().strip()
        category = self.category_edit.text().strip()
        excerpt = self.excerpt_edit.toPlainText().strip()
        content = self.md_edit.toPlainText()

        if self.current_filename:
            filename = self.current_filename
        else:
            base = slugify(title)
            filename = base + ".md"
            counter = 1
            while os.path.exists(os.path.join(DATE_DIR, filename)):
                filename = f"{base}_{counter}.md"
                counter += 1

        md_path = os.path.join(DATE_DIR, filename)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)

        if self.current_filename:
            for art in self.articles:
                if art.get("filename") == self.current_filename:
                    art.update({"title": title, "date": date, "category": category, "excerpt": excerpt})
                    if filename != self.current_filename:
                        shutil.move(md_path, os.path.join(DATE_DIR, filename))
                        art["filename"] = filename
                    break
        else:
            self.articles.append({"filename": filename, "title": title, "date": date, "category": category, "excerpt": excerpt})
            self.current_filename = filename

        with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=4)
        self.load_articles()
        QMessageBox.information(self, "成功", "文章已保存")

    def delete_article(self):
        if not self.current_filename:
            return
        reply = QMessageBox.question(self, "确认", f"删除《{self.title_edit.text()}》及其文件？", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        md_path = os.path.join(DATE_DIR, self.current_filename)
        if os.path.exists(md_path):
            os.remove(md_path)
        self.articles = [a for a in self.articles if a.get("filename") != self.current_filename]
        with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=4)
        self.load_articles()
        self.new_article()

    def preview_markdown(self):
        if not self.preview:
            return
        md_text = self.md_edit.toPlainText()
        if not MARKDOWN_AVAILABLE:
            self.preview.setPlainText("请安装 markdown 库: pip install markdown")
            return
        try:
            html = markdown.markdown(md_text, extensions=['extra', 'codehilite'])
            style = """
            <style>
                body { font-family: 'Segoe UI', monospace; background: #0a0e1a; color: #ccc; padding: 20px; }
                h1,h2,h3 { color: #ffa300; }
                code { background: #1e1e2e; padding: 2px 6px; border-radius: 6px; }
                pre { background: #111; padding: 12px; border-radius: 12px; }
                a { color: #ff9285; }
            </style>
            """
            self.preview.setHtml(style + html)
        except Exception as e:
            self.preview.setPlainText(f"预览错误: {e}")


# ---------- 下载管理组件 ----------
class DownloadManager(QWidget):
    def __init__(self):
        super().__init__()
        self.downloads = []
        self.init_ui()
        self.load_downloads()

    def init_ui(self):
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        btn_add = QPushButton("➕ 添加")
        btn_add.clicked.connect(self.add_item)
        btn_refresh = QPushButton("🔄 刷新")
        btn_refresh.clicked.connect(self.load_downloads)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_refresh)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["显示名称", "文件名", "大小", "描述", "图标", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # 设置行高以适应按钮
        self.table.verticalHeader().setDefaultSectionSize(40)
        layout.addWidget(self.table)

    def load_downloads(self):
        try:
            with open(DOWNLOADS_JSON, "r", encoding="utf-8") as f:
                self.downloads = json.load(f)
        except:
            self.downloads = []
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.downloads))
        for row, item in enumerate(self.downloads):
            self.table.setItem(row, 0, QTableWidgetItem(item.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("filename", "")))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("size", "")))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("description", "")))
            self.table.setItem(row, 4, QTableWidgetItem(item.get("icon", "")))
            # 操作按钮容器
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_edit = QPushButton("编辑")
            btn_edit.setFixedSize(60, 28)
            btn_edit.clicked.connect(lambda _, r=row: self.edit_item(r))
            btn_delete = QPushButton("删除")
            btn_delete.setFixedSize(60, 28)
            btn_delete.clicked.connect(lambda _, r=row: self.delete_item(r))
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)
            btn_layout.addStretch()
            self.table.setCellWidget(row, 5, btn_widget)

    def add_item(self):
        dialog = DownloadItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                self.downloads.append(data)
                self.save_downloads()
                self.load_downloads()

    def edit_item(self, row):
        item = self.downloads[row].copy()
        dialog = DownloadItemDialog(self, item)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            if new_data:
                old_fn = item.get("filename")
                new_fn = new_data.get("filename")
                if old_fn != new_fn:
                    old_path = os.path.join(FILES_DIR, old_fn)
                    new_path = os.path.join(FILES_DIR, new_fn)
                    if os.path.exists(old_path):
                        shutil.move(old_path, new_path)
                self.downloads[row] = new_data
                self.save_downloads()
                self.load_downloads()

    def delete_item(self, row):
        item = self.downloads[row]
        reply = QMessageBox.question(self, "确认", f"删除「{item.get('name')}」？同时删除文件？", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if reply == QMessageBox.Cancel:
            return
        if reply == QMessageBox.Yes:
            fp = os.path.join(FILES_DIR, item.get("filename"))
            if os.path.exists(fp):
                os.remove(fp)
        self.downloads.pop(row)
        self.save_downloads()
        self.load_downloads()

    def save_downloads(self):
        with open(DOWNLOADS_JSON, "w", encoding="utf-8") as f:
            json.dump(self.downloads, f, ensure_ascii=False, indent=4)


class DownloadItemDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("下载项")
        self.data = data or {}
        self.init_ui()
        if data:
            self.load_data()

    def init_ui(self):
        layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        self.filename_edit = QLineEdit()
        self.filename_edit.setReadOnly(True)
        self.size_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.icon_edit = QLineEdit()
        btn_file = QPushButton("选择文件 (复制到Files)")
        btn_file.clicked.connect(self.select_file)

        layout.addRow("显示名称:", self.name_edit)
        layout.addRow("文件名:", self.filename_edit)
        layout.addRow("大小:", self.size_edit)
        layout.addRow("描述:", self.desc_edit)
        layout.addRow("图标类:", self.icon_edit)
        layout.addRow(btn_file)

        btns = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

    def load_data(self):
        self.name_edit.setText(self.data.get("name", ""))
        self.filename_edit.setText(self.data.get("filename", ""))
        self.size_edit.setText(self.data.get("size", ""))
        self.desc_edit.setPlainText(self.data.get("description", ""))
        self.icon_edit.setText(self.data.get("icon", ""))

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if not path:
            return
        base = os.path.basename(path)
        dest = os.path.join(FILES_DIR, base)
        counter = 1
        name, ext = os.path.splitext(base)
        while os.path.exists(dest):
            base = f"{name}_{counter}{ext}"
            dest = os.path.join(FILES_DIR, base)
            counter += 1
        shutil.copy2(path, dest)
        self.filename_edit.setText(base)
        size_bytes = os.path.getsize(dest)
        self.size_edit.setText(format_file_size(size_bytes))

    def get_data(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "显示名称不能为空")
            return None
        fn = self.filename_edit.text().strip()
        if not fn:
            QMessageBox.warning(self, "警告", "请选择文件")
            return None
        return {
            "filename": fn,
            "name": name,
            "size": self.size_edit.text().strip() or "未知",
            "description": self.desc_edit.toPlainText().strip(),
            "icon": self.icon_edit.text().strip() or "fa-file"
        }


# ---------- 设置页面 ----------
class SettingsWidget(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 主题选择
        theme_group = QGroupBox("主题设置")
        theme_layout = QFormLayout(theme_group)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "custom"])
        self.theme_combo.currentTextChanged.connect(self.parent_window.on_theme_changed)
        theme_layout.addRow("主题:", self.theme_combo)

        # 自定义颜色组
        self.custom_group = QGroupBox("自定义颜色")
        custom_layout = QGridLayout(self.custom_group)
        self.color_buttons = {}
        colors_def = [
            ("background", "背景色"),
            ("text", "文字色"),
            ("accent", "强调色"),
            ("border", "边框色"),
            ("group_bg", "组背景"),
            ("input_bg", "输入框背景"),
            ("button_bg", "按钮背景"),
            ("button_hover", "按钮悬停")
        ]
        for i, (key, label) in enumerate(colors_def):
            btn = QPushButton()
            btn.setFixedSize(60, 30)
            btn.clicked.connect(lambda _, k=key: self.parent_window.choose_custom_color(k))
            self.color_buttons[key] = btn
            custom_layout.addWidget(QLabel(label), i, 0)
            custom_layout.addWidget(btn, i, 1)
        self.apply_custom_btn = QPushButton("应用自定义颜色")
        self.apply_custom_btn.clicked.connect(self.parent_window.apply_custom_theme)
        custom_layout.addWidget(self.apply_custom_btn, len(colors_def), 0, 1, 2)

        theme_layout.addRow(self.custom_group)

        # 其他设置
        other_group = QGroupBox("其他设置")
        other_layout = QVBoxLayout(other_group)
        self.auto_scroll_cb = QCheckBox("自动滚动输出到底部")
        self.auto_scroll_cb.setChecked(True)
        other_layout.addWidget(self.auto_scroll_cb)

        save_btn = QPushButton("💾 保存所有设置")
        save_btn.clicked.connect(self.parent_window.save_all_settings)

        layout.addWidget(theme_group)
        layout.addWidget(other_group)
        layout.addWidget(save_btn)
        layout.addStretch()

    def load_config(self, config):
        self.theme_combo.setCurrentText(config.get("theme", "dark"))
        self.auto_scroll_cb.setChecked(config.get("auto_scroll", True))
        # 更新颜色按钮显示
        custom_colors = config.get("custom_colors", {})
        for key, btn in self.color_buttons.items():
            color = custom_colors.get(key, "#2b2b2b")
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid #888;")
        # 显示/隐藏自定义组
        self.custom_group.setVisible(config.get("theme") == "custom")

    def get_config(self):
        return {
            "theme": self.theme_combo.currentText(),
            "auto_scroll": self.auto_scroll_cb.isChecked()
        }


# ---------- 主窗口 ----------
class CyberMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.theme_manager = ThemeManager()
        self.custom_colors = self.config.get("custom_colors", {
            "background": "#2b2b2b",
            "text": "#ffffff",
            "accent": "#4CAF50",
            "border": "#555555",
            "group_bg": "#363636",
            "input_bg": "#404040",
            "button_bg": "#4CAF50",
            "button_hover": "#45a049"
        })
        self.theme_manager.set_custom_colors(self.custom_colors)
        self.init_ui()
        self.apply_theme(self.config.get("theme", "dark"))

    def load_config(self):
        default = {
            "theme": "dark",
            "auto_scroll": True,
            "window_width": 1100,
            "window_height": 800,
            "custom_colors": {
                "background": "#2b2b2b",
                "text": "#ffffff",
                "accent": "#4CAF50",
                "border": "#555555",
                "group_bg": "#363636",
                "input_bg": "#404040",
                "button_bg": "#4CAF50",
                "button_hover": "#45a049"
            }
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    for k, v in default.items():
                        if k not in loaded:
                            loaded[k] = v
                    return loaded
            except:
                return default
        return default

    def save_config(self):
        config = {
            "theme": self.config.get("theme", "dark"),
            "auto_scroll": self.config.get("auto_scroll", True),
            "window_width": self.width(),
            "window_height": self.height(),
            "custom_colors": self.custom_colors
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def save_all_settings(self):
        if hasattr(self, 'settings_widget'):
            self.config["theme"] = self.settings_widget.theme_combo.currentText()
            self.config["auto_scroll"] = self.settings_widget.auto_scroll_cb.isChecked()
        self.config["custom_colors"] = self.custom_colors
        self.save_config()
        self.apply_theme(self.config["theme"])
        QMessageBox.information(self, "成功", "设置已保存并应用")

    def init_ui(self):
        self.setWindowTitle("赛博内容管理工具 · 主题定制版")
        self.setGeometry(100, 100, self.config["window_width"], self.config["window_height"])
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("⚡ 赛博枢纽管理终端 ⚡")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        self.tab_widget = QTabWidget()
        self.article_tab = ArticleManager()
        self.download_tab = DownloadManager()
        self.settings_widget = SettingsWidget(self)
        self.tab_widget.addTab(self.article_tab, "📚 文章管理")
        self.tab_widget.addTab(self.download_tab, "📦 下载管理")
        self.tab_widget.addTab(self.settings_widget, "⚙️ 设置")
        layout.addWidget(self.tab_widget)

        self.settings_widget.load_config(self.config)

        self.status_label = QLabel("就绪")
        self.statusBar().addWidget(self.status_label)

    def apply_theme(self, theme_name):
        style = self.theme_manager.get_theme(theme_name)
        self.setStyleSheet(style)
        if hasattr(self, 'settings_widget'):
            self.settings_widget.custom_group.setVisible(theme_name == "custom")
        if hasattr(self, 'status_label'):
            self.status_label.setStyleSheet("color: #aaa;")

    def on_theme_changed(self, theme_name):
        if theme_name == "custom":
            self.apply_custom_theme()
        else:
            self.apply_theme(theme_name)
        self.config["theme"] = theme_name

    def choose_custom_color(self, color_key):
        current = QColor(self.custom_colors.get(color_key, "#2b2b2b"))
        color = QColorDialog.getColor(current, self, f"选择 {color_key}")
        if color.isValid():
            self.custom_colors[color_key] = color.name()
            if hasattr(self, 'settings_widget'):
                btn = self.settings_widget.color_buttons.get(color_key)
                if btn:
                    btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888;")

    def apply_custom_theme(self):
        self.theme_manager.set_custom_colors(self.custom_colors)
        self.apply_theme("custom")
        self.config["theme"] = "custom"
        if hasattr(self, 'settings_widget'):
            self.settings_widget.theme_combo.setCurrentText("custom")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = CyberMainWindow()
    window.show()
    sys.exit(app.exec_())