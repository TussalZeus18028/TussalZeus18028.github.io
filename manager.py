import sys
import os
import json
import shutil
import re
import subprocess
import threading
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
    QLabel, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QSplitter, QGroupBox, QSpinBox, QCheckBox, QComboBox,
    QColorDialog, QScrollArea, QTextBrowser
)
from PyQt5.QtCore import Qt, QSize, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import QUrl

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False

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
                color: #4CAF50;
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
                background-color: #2d4a2d;
                padding: 6px;
                border: none;
                font-weight: bold;
                color: #4CAF50;
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

        # 预览区：优先使用 QWebEngineView（支持代码高亮/公式/Mermaid），否则用 QTextBrowser
        if WEBENGINE_AVAILABLE:
            self.preview = QWebEngineView()
            self._preview_mode = "webengine"
        elif MARKDOWN_AVAILABLE:
            self.preview = QTextBrowser()
            self.preview.setOpenExternalLinks(True)
            self._preview_mode = "textbrowser"
        else:
            self.preview = None
            self._preview_mode = "none"

        btn_bar = QHBoxLayout()
        btn_save = QPushButton("💾 保存")
        btn_save.clicked.connect(self.save_article)
        btn_delete = QPushButton("🗑️ 删除")
        btn_delete.clicked.connect(self.delete_article)
        btn_preview = QPushButton("👁️ 预览")
        if self.preview:
            btn_preview.clicked.connect(self.preview_markdown)
        else:
            btn_preview.clicked.connect(
                lambda: QMessageBox.warning(self, "缺少依赖", "请安装依赖库：\npip install markdown PyQtWebEngine")
            )
        btn_bar.addWidget(btn_save)
        btn_bar.addWidget(btn_delete)
        btn_bar.addWidget(btn_preview)
        btn_bar.addStretch()

        right_layout.addWidget(form)
        right_layout.addWidget(QLabel("📝 Markdown 内容:"))
        if self.preview:
            splitter = QSplitter(Qt.Vertical)
            splitter.addWidget(self.md_edit)
            splitter.addWidget(self.preview)
            splitter.setSizes([300, 300])
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
        if not md_text.strip():
            if self._preview_mode == "webengine":
                self.preview.setHtml(self._empty_preview_html(), QUrl())
            else:
                self.preview.clear()
            return

        if self._preview_mode == "webengine":
            # 使用 WebEngine 渲染：加载 CDN，支持代码高亮 + KaTeX 公式 + Mermaid + 代码增强
            import html as html_mod
            escaped_md = html_mod.escape(md_text)
            # </script> 关闭标签拼接，避免 Python 转义问题
            _sc = "</scr" + "ipt>"
            _sco = '<script src="'  # script open tag prefix

            full_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
{_sco}https://cdn.jsdelivr.net/npm/marked/marked.min.js">{_sc}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
{_sco}https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js">{_sc}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
{_sco}https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js">{_sc}
{_sco}https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js">{_sc}
{_sco}https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js">{_sc}
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0d1a0d; color: #c5e1a5; padding: 20px; font-size: 14px; }}
  h1,h2,h3 {{ color: #4CAF50; border-bottom: 1px solid #2e4a2e; padding-bottom: 0.4rem; margin-top: 1.5rem; }}
  p {{ margin: 1rem 0; line-height: 1.7; }}
  code {{ background: #1a2e1a; padding: 2px 6px; border-radius: 6px; color: #81c784; font-family: 'Consolas', monospace; font-size: 0.9em; }}
  pre {{ background: #111; padding: 14px; border-radius: 0 0 12px 12px; border: 1px solid #2e4a2e; border-top: none; overflow-x: auto; margin: 0; }}
  pre code {{ background: transparent; padding: 0; color: inherit; }}
  .code-block-wrapper {{ margin: 1rem 0; border-radius: 12px; overflow: hidden; border: 1px solid #2e4a2e; }}
  .code-toolbar {{ display:flex; justify-content:space-between; align-items:center; padding: 0.3rem 0.8rem; font-size: 0.8rem; background: #1a2e1a; }}
  .code-lang-label {{ font-family: 'Consolas', monospace; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7; color: #4CAF50; }}
  .code-copy-btn {{ background: transparent; border: 1px solid #2e4a2e; color: #4CAF50; cursor: pointer; padding: 0.15rem 0.5rem; border-radius: 5px; font-size: 0.75rem; }}
  .code-copy-btn:hover {{ background: #4CAF50; color: #000; }}
  blockquote {{ border-left: 4px solid #4CAF50; padding: 0.8rem 1.2rem; color: #a5d6a7; background: rgba(76,175,80,0.05); border-radius: 0 12px 12px 0; font-style: italic; margin: 1rem 0; }}
  a {{ color: #66bb6a; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; border-radius: 12px; overflow: hidden; }}
  th {{ background: #1a2e1a; color: #4CAF50; padding: 10px; text-align: left; border: 1px solid #2e4a2e; }}
  td {{ padding: 10px; border: 1px solid #2e4a2e; }}
  tr:hover td {{ background: rgba(76,175,80,0.08); }}
  ul li {{ list-style: none; margin: 0.3rem 0; }}
  ul li input[type="checkbox"] {{ margin-right: 0.5rem; accent-color: #4CAF50; }}
  del {{ opacity: 0.6; }}
  hr {{ border: none; height: 2px; background: linear-gradient(90deg, transparent, #4CAF50, transparent); margin: 2rem 0; }}
  .mermaid-wrapper {{ margin: 1rem 0; border-radius: 12px; overflow: hidden; border: 1px solid #2e4a2e; }}
  .mermaid-toolbar {{ display:flex; justify-content:space-between; align-items:center; padding: 0.3rem 0.8rem; font-size: 0.85rem; background: #1a2e1a; }}
  .mermaid-label {{ font-weight: 600; color: #4CAF50; }}
  .mermaid-toggle-btn {{ background: transparent; border: 1px solid #2e4a2e; color: #4CAF50; cursor: pointer; padding: 0.15rem 0.6rem; border-radius: 5px; font-size: 0.78rem; }}
  .mermaid-toggle-btn:hover {{ background: #4CAF50; color: #000; }}
  .mermaid-btn-group {{ display:flex; gap:4px; }}
  .mermaid-view-btn {{ background: transparent; border: 1px solid #2e4a2e; color: #4CAF50; cursor: pointer; padding: 0.15rem 0.6rem; border-radius: 5px; font-size: 0.78rem; }}
  .mermaid-view-btn:hover {{ background: #4CAF50; color: #000; }}
  .mermaid-view-btn.active {{ background: rgba(76,175,80,0.15); font-weight: 600; }}
  .mermaid-chart-view {{ background: rgba(76,175,80,0.06); padding: 1.2rem; text-align: center; overflow-x: auto; }}
  .mermaid-code-view {{ padding: 0; }}
  .mermaid-code-view pre {{ border-radius: 0; margin: 0; }}
  .mermaid {{ background: transparent !important; padding: 0 !important; margin: 0 !important; }}
  .katex-display {{ margin: 1rem 0; overflow-x: auto; overflow-y: hidden; }}
  img {{ max-width: 100%; border-radius: 12px; }}
</style>
</head><body>
<div id="content"></div>
<script id="md-source" type="text/markdown">{escaped_md}</script>
<script>
  // 预处理：保护 Mermaid 和公式不被 marked 破坏
  function preprocessMarkdown(md) {{
    const mermaidBlocks = [];
    const mathBlocks = [];
    let counter = 0;
    let processed = md.replace(/```mermaid\\n([\\s\\S]*?)```/g, (m, code) => {{
      const id = `%%MERMAID_${{counter}}%%`;
      mermaidBlocks.push({{ id, code: code.trim() }});
      counter++;
      return id;
    }});
    processed = processed.replace(/\\$\\$([\\s\\S]*?)\\$\\$/g, (m, formula) => {{
      const id = `%%MATH_${{counter}}%%`;
      mathBlocks.push({{ id, formula: formula.trim() }});
      counter++;
      return id;
    }});
    return {{ processed, mermaidBlocks, mathBlocks }};
  }}

  function restoreBlocks(html, mermaidBlocks, mathBlocks) {{
    for (const {{ id, formula }} of mathBlocks) {{
      try {{
        const rendered = katex.renderToString(formula, {{ displayMode: true, throwOnError: false }});
        html = html.replace(id, `<div class="katex-display">${{rendered}}</div>`);
      }} catch(e) {{
        html = html.replace(id, `<div class="katex-display"><code>${{formula}}</code></div>`);
      }}
    }}
    for (const {{ id, code }} of mermaidBlocks) {{
      const uid = 'mwrap_' + Math.random().toString(36).substr(2, 9);
      const esc = code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      html = html.replace(id, `
        <div class="mermaid-wrapper" id="${{uid}}">
          <div class="mermaid-toolbar">
            <span class="mermaid-label">Mermaid</span>
            <div class="mermaid-btn-group">
              <button class="mermaid-view-btn active" onclick="switchMermaidView(this,'chart')">Chart</button>
              <button class="mermaid-view-btn" onclick="switchMermaidView(this,'code')">Code</button>
            </div>
          </div>
          <div class="mermaid-chart-view"></div>
          <div class="mermaid-code-view" style="display:none;">
            <pre class="mermaid-source-pre"><code class="language-mermaid">${{esc}}</code></pre>
          </div>
          <textarea class="mermaid-src" style="display:none;">${{code}}</textarea>
        </div>
      `);
    }}
    return html;
  }}

  window.switchMermaidView = function(btn, view) {{
    const wrapper = btn.closest('.mermaid-wrapper');
    const chartView = wrapper.querySelector('.mermaid-chart-view');
    const codeView = wrapper.querySelector('.mermaid-code-view');
    const btns = wrapper.querySelectorAll('.mermaid-view-btn');
    if (view === 'chart') {{
      chartView.style.display = '';
      codeView.style.display = 'none';
      btns.forEach(b => b.classList.remove('active'));
      btns[0].classList.add('active');
    }} else {{
      chartView.style.display = 'none';
      codeView.style.display = '';
      btns.forEach(b => b.classList.remove('active'));
      btns[1].classList.add('active');
      codeView.querySelectorAll('pre code').forEach(b => {{
        if (!b.classList.contains('hljs')) hljs.highlightElement(b);
      }});
    }}
  }};

  // 渲染 Markdown → HTML
  const mdSrc = document.getElementById('md-source').textContent;
  const {{ processed, mermaidBlocks, mathBlocks }} = preprocessMarkdown(mdSrc);
  let html = marked.parse(processed);
  html = restoreBlocks(html, mermaidBlocks, mathBlocks);
  document.getElementById('content').innerHTML = html;

  // ⚠️ 执行顺序很重要！
  // 1) 先初始化 Mermaid
  mermaid.initialize({{ startOnLoad: false, theme: 'dark', securityLevel: 'loose' }});

  // 2) 渲染所有 Mermaid 图表（DOM API，串行 await，从 textarea 读取源码）
  (async function() {{
    const wrappers = document.querySelectorAll('.mermaid-wrapper');
    for (let i = 0; i < wrappers.length; i++) {{
      const wrapper = wrappers[i];
      const textarea = wrapper.querySelector('textarea.mermaid-src');
      const code = textarea ? textarea.value.trim() : '';
      if (!code) continue;
      const chartView = wrapper.querySelector('.mermaid-chart-view');
      const uid = 'm_' + Date.now() + '_' + i;
      try {{
        const {{ svg }} = await mermaid.render(uid, code);
        chartView.innerHTML = svg;
      }} catch(e) {{
        chartView.innerHTML = '<div style="color:#ff9285;padding:1rem;font-family:monospace;">Mermaid render failed: ' + e.message + '</div>';
      }}
      if (textarea) textarea.remove();
    }}

    // 3) 代码高亮（跳过 mermaid 容器内的代码）
    document.querySelectorAll('pre:not(.mermaid) code').forEach(block => hljs.highlightElement(block));

    // 4) 行内公式渲染（$...$）
    renderMathInElement(document.body, {{
      delimiters: [
        {{left: '$$', right: '$$', display: true}},
        {{left: '$', right: '$', display: false}}
      ],
      throwOnError: false
    }});

    // 5) 增强代码块：添加语言标签 + 复制按钮
    document.querySelectorAll('pre').forEach(pre => {{
      const code = pre.querySelector('code');
      if (!code || pre.closest('.mermaid-wrapper')) return;
      const langClass = [...code.classList].find(c => c.startsWith('language-'));
      const lang = langClass ? langClass.replace('language-', '') : '';
      if (pre.querySelector('.code-toolbar')) return;
      const wrapper = document.createElement('div');
      wrapper.className = 'code-block-wrapper';
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);
      const toolbar = document.createElement('div');
      toolbar.className = 'code-toolbar';
      if (lang) {{
        const label = document.createElement('span');
        label.className = 'code-lang-label';
        label.textContent = lang;
        toolbar.appendChild(label);
      }}
      const copyBtn = document.createElement('button');
      copyBtn.className = 'code-copy-btn';
      copyBtn.innerHTML = '<i class="fas fa-copy"></i> 复制';
      copyBtn.onclick = function() {{
        navigator.clipboard.writeText(code.textContent).then(() => {{
          copyBtn.innerHTML = '<i class="fas fa-check"></i> 已复制';
          setTimeout(() => {{ copyBtn.innerHTML = '<i class="fas fa-copy"></i> 复制'; }}, 2000);
        }});
      }};
      toolbar.appendChild(copyBtn);
      wrapper.insertBefore(toolbar, pre);
    }});
  }})();
{_sc}
</body></html>"""
            self.preview.setHtml(full_html, QUrl())

        elif self._preview_mode == "textbrowser" and MARKDOWN_AVAILABLE:
            # Fallback: 纯 Markdown 渲染（无公式/Mermaid 支持）
            html = markdown.markdown(md_text, extensions=['extra', 'codehilite', 'tables', 'fenced_code'])
            style = """
            <style>
                body { font-family: 'Segoe UI', monospace; background: #0d1a0d; color: #c5e1a5; padding: 20px; font-size: 14px; }
                h1,h2,h3 { color: #4CAF50; border-bottom: 1px solid #2e4a2e; }
                code { background: #1a2e1a; padding: 2px 6px; border-radius: 6px; color: #81c784; }
                pre { background: #111; padding: 14px; border-radius: 12px; border: 1px solid #2e4a2e; }
                a { color: #66bb6a; }
                table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
                th, td { border: 1px solid #2e4a2e; padding: 8px; }
                th { background: #1a2e1a; color: #4CAF50; }
                blockquote { border-left: 4px solid #4CAF50; padding-left: 1rem; color: #a5d6a7; }
            </style>
            """
            self.preview.setHtml(style + html)

    def _empty_preview_html(self):
        return """<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  body { font-family: 'Segoe UI', sans-serif; background: #0d1a0d; color: #2e4a2e;
         padding: 60px 20px; text-align: center; font-size: 16px; }
  .hint { color: #4CAF50; font-size: 48px; margin-bottom: 16px; }
</style></head><body>
  <div class="hint">📝</div>
  <div>在上方编辑 Markdown，点击「预览」查看效果</div>
  <div style="margin-top:12px;font-size:13px;color:#555;">
    代码高亮 · 数学公式 · Mermaid 图表 · 复制按钮 · 视图切换
  </div>
</body></html>"""


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


# ---------- Git 推送工作线程 ----------
class GitWorker(QThread):
    log_signal = pyqtSignal(str)
    done_signal = pyqtSignal(bool, str)

    def __init__(self, repo_dir, commit_msg, push_remote, push_branch):
        super().__init__()
        self.repo_dir = repo_dir
        self.commit_msg = commit_msg
        self.push_remote = push_remote
        self.push_branch = push_branch

    def _run_cmd(self, cmd):
        """执行命令，实时返回输出行"""
        self.log_signal.emit(f"<span style='color:#66bb6a'>$ {' '.join(cmd)}</span>")
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            )
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    self.log_signal.emit(line)
            proc.wait()
            return proc.returncode
        except FileNotFoundError:
            self.log_signal.emit("<span style='color:#ef9a9a'>错误: 未找到 git 命令，请确认 Git 已安装并加入 PATH</span>")
            return -1

    def run(self):
        self.log_signal.emit("<b>===== 开始 Git 推送流程 =====</b>")

        # git add .
        rc = self._run_cmd(["git", "add", "."])
        if rc != 0:
            self.done_signal.emit(False, "git add 失败")
            return

        # git status --short（展示将提交的内容）
        self._run_cmd(["git", "status", "--short"])

        # git commit
        rc = self._run_cmd(["git", "commit", "-m", self.commit_msg])
        if rc not in (0, 1):   # 1 = nothing to commit，视为正常
            self.done_signal.emit(False, "git commit 失败")
            return

        # git push
        push_cmd = ["git", "push", self.push_remote, self.push_branch]
        rc = self._run_cmd(push_cmd)
        if rc != 0:
            self.done_signal.emit(False, "git push 失败，请检查网络或远端配置")
            return

        self.done_signal.emit(True, "✅ 推送成功！")


# ---------- Git 推送页面 ----------
class GitPushWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 标题
        title = QLabel("🚀 Git 推送到 GitHub")
        title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 4px 0;")
        layout.addWidget(title)

        # 配置区
        config_group = QGroupBox("推送配置")
        config_form = QFormLayout(config_group)

        self.remote_edit = QLineEdit("origin")
        self.branch_edit = QLineEdit("main")
        self.commit_edit = QLineEdit()
        self.commit_edit.setPlaceholderText("更新内容描述，留空则使用自动时间戳")

        config_form.addRow("远端(remote):", self.remote_edit)
        config_form.addRow("分支(branch):", self.branch_edit)
        config_form.addRow("Commit 信息:", self.commit_edit)
        layout.addWidget(config_group)

        # 按钮行
        btn_row = QHBoxLayout()
        self.push_btn = QPushButton("🚀 一键推送")
        self.push_btn.setMinimumHeight(36)
        self.push_btn.clicked.connect(self.do_push)
        self.clear_btn = QPushButton("🧹 清空日志")
        self.clear_btn.clicked.connect(self.clear_log)
        btn_row.addWidget(self.push_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # 日志输出
        log_group = QGroupBox("执行日志")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextBrowser()
        self.log_output.setMinimumHeight(300)
        self.log_output.setStyleSheet(
            "font-family: 'Consolas','Courier New',monospace; font-size: 12px;"
            "background:#0d1a0d; color:#c5e1a5; border-radius:8px; padding:8px;"
        )
        self.log_output.setOpenExternalLinks(False)
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_group)

    def do_push(self):
        commit_msg = self.commit_edit.text().strip()
        if not commit_msg:
            commit_msg = f"update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        remote = self.remote_edit.text().strip() or "origin"
        branch = self.branch_edit.text().strip() or "main"

        self.push_btn.setEnabled(False)
        self.push_btn.setText("⏳ 推送中...")

        self.worker = GitWorker(BASE_DIR, commit_msg, remote, branch)
        self.worker.log_signal.connect(self.append_log)
        self.worker.done_signal.connect(self.on_done)
        self.worker.start()

    def append_log(self, text):
        self.log_output.append(text)
        # 滚动到底
        sb = self.log_output.verticalScrollBar()
        sb.setValue(sb.maximum())

    def on_done(self, success, msg):
        color = "#a5d6a7" if success else "#ef9a9a"
        self.append_log(f"<br><b><span style='color:{color}'>{msg}</span></b>")
        self.push_btn.setEnabled(True)
        self.push_btn.setText("🚀 一键推送")

    def clear_log(self):
        self.log_output.clear()


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
        self.git_tab = GitPushWidget()
        self.settings_widget = SettingsWidget(self)
        self.tab_widget.addTab(self.article_tab, "📚 文章管理")
        self.tab_widget.addTab(self.download_tab, "📦 下载管理")
        self.tab_widget.addTab(self.git_tab, "🚀 Git 推送")
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