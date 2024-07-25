"""
novelWriter – GUI Custom Print Box
===========================

File History:
Created: 2024-06-19 [0.5.2] GuiCustomPDF

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import logging
import uuid
import os

from fpdf import FPDF

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPixmap, QPen, QPaintEvent, QBrush, QPolygon
from PyQt5.QtWidgets import (
    QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QSpinBox, QButtonGroup,
    QRadioButton, QComboBox
)

from novelwriter import CONFIG
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.modified import NDialog
from novelwriter.types import QtDialogClose, QtDialogOk

logger = logging.getLogger(__name__)

# slownik na spacingi
# rodzaj fontu szeryf, bezszeryf, mono
# czy otworzyc, czy zapisac do pliku


class CustomPDFOptions:

    def __init__(self):
        self.IsPortrait = False
        self.RatioPercent = 50
        self.LineSpacing = 0.8
        self.ParagraphSpacing = 0.8
        self.drawFileName()

    def drawFileName(self) -> None:
        self.FileName = f"{str(uuid.uuid4().hex)}.pdf"
        pdfPath = CONFIG.tempPath("custompdf")
        pdfPath.mkdir(exist_ok=True)
        self.FileName = os.path.join(pdfPath, self.FileName)

class GuiCustomPDF(NDialog):

    def __init__(self, parent: QWidget, documentContent: str) -> None:
        super().__init__(parent=parent)

        self.settings = CustomPDFOptions()
        self.content = documentContent

        logger.debug("Create: GuiCustomPDF")
        self.setObjectName("GuiCustomPDF")

        self.setWindowTitle(self.tr("Custom PDF export"))
        self.resize(CONFIG.pxInt(700), CONFIG.pxInt(300))

        self.lblDialogTitle = NColourLabel(
            self.tr("Export document to PDF"), scale=1.6, bold=True, parent=parent
        )

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()

        # settings and preview
        self.innerBox.addLayout(self._buildOptions())
        self.innerBox.addLayout(self._buildPreview())

        # buttons
        self.btnBox = QDialogButtonBox(QtDialogOk | QtDialogClose, self)
        self.btnBox.rejected.connect(self.reject)
        self.btnBox.accepted.connect(self._accept)

        # main view compose
        self.outerBox.addWidget(self.lblDialogTitle)
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addLayout(self._buildDocumentPath())
        self.outerBox.addWidget(self.btnBox)

        # main view settings
        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        # self.setStyleSheet(f"QWidget {{border: 1px solid red;}} ")

        logger.debug("Ready: GuiAbout")
        return

    def _accept(self) -> None:
        pdf = PDFCreator(self.content, self.settings)
        if pdf.completed():
            self.reject()
        else:
            print("PDF Error: something bad happened.")

    def _buildOptions(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        percentLabel = QLabel("Page fill percent")
        percentField = QSpinBox(self)
        percentField.setValue(self.settings.RatioPercent)
        percentField.setMinimum(40)
        percentField.setMaximum(85)
        percentField.valueChanged.connect(self._percentFieldChange)

        orientationLabel = QLabel("Document orientation")
        orientationGroup = QButtonGroup(self)
        orientationPortrait = QRadioButton("Portrait")
        orientationLandscape = QRadioButton("Landscape")
        orientationGroup.addButton(orientationPortrait, 1)
        orientationGroup.addButton(orientationLandscape, 2)
        orientationPortrait.setChecked(self.settings.IsPortrait is True)
        orientationLandscape.setChecked(self.settings.IsPortrait is False)
        orientationGroup.idClicked.connect(self._orientationChanged)

        lineSpacingLabel = QLabel("Line spacing")
        lineSpacingCombo = QComboBox(self)
        lineSpacingCombo.addItem("0.8")
        lineSpacingCombo.addItem("1")
        lineSpacingCombo.addItem("1.5")
        lineSpacingCombo.addItem("2")
        lineSpacingCombo.activated[str].connect(self._lineSpacingChange)

        paragraphSpacingLabel = QLabel("Paragraph spacing")
        paragraphSpacingCombo = QComboBox(self)
        paragraphSpacingCombo.addItem("0.8")
        paragraphSpacingCombo.addItem("1")
        paragraphSpacingCombo.addItem("1.5")
        paragraphSpacingCombo.addItem("2")
        paragraphSpacingCombo.activated[str].connect(self._paragraphSpacingChange)

        layout.addWidget(percentLabel)
        layout.addWidget(percentField)
        layout.addWidget(orientationLabel)
        layout.addWidget(orientationPortrait)
        layout.addWidget(orientationLandscape)
        layout.addWidget(lineSpacingLabel)
        layout.addWidget(lineSpacingCombo)
        layout.addWidget(paragraphSpacingLabel)
        layout.addWidget(paragraphSpacingCombo)
        layout.addStretch()

        return layout

    def _buildPreview(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        previewLabel = QLabel("Preview")
        self.preview = CustomPDFCLientPreview(self._getRatio(self.settings.RatioPercent), self.settings.IsPortrait)
        self.preview.setMinimumHeight(350)

        layout.addWidget(previewLabel)
        layout.addWidget(self.preview)
        layout.addStretch()

        return layout

    def _buildDocumentPath(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        pathLabel = QLabel(f"PDF document path: {self.settings.FileName}")
        layout.addWidget(pathLabel)

        return layout

    def _percentFieldChange(self, newValue):
        self.settings.RatioPercent = newValue
        self.preview.updateRatio(self._getRatio(newValue))

    def _orientationChanged(self, id):
        self.settings.IsPortrait = id == 1
        self.preview.updateOrientation(self.settings.IsPortrait)

    def _lineSpacingChange(self, value):
        self.settings.LineSpacing = float(value)

    def _paragraphSpacingChange(self, value):
        self.settings.ParagraphSpacing = float(value)

    def _getRatio(self, value):
        return value / 100


class CustomPDFCLientPreview(QWidget):
    page = []
    client = []
    fold = []
    cut = []

    def __init__(self, startingRatio, isPortrait):
        super().__init__()
        self.ratio = startingRatio
        # A4 measures
        self.defaultWidth = 210
        self.defaultHeight = 297
        self._calculateSize(isPortrait)
        self.painter = QPainter()

    def _setPixmap(self):
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.white)
        self.calculate()
        self.repaint()

    def calculate(self):
        folding = int(0.20 * self.currentWidth)
        pad = 5
        clientWidth = int(self.currentWidth * self.ratio) - pad

        """
        P0 +---------------------------- P1 +       + P2
           |  P7 +---------------+ P8       | \\
           |     |               |          |   \\
           |     |               |          |     \\
           |     |               |       P3 +-------+ P4
           |     |               |                  |
           |     |               |                  |
           |     |               |                  |
           |  P9 +---------------+ P10              |
        P5 +----------------------------------------+ P6
        """
        x0 = int((self.width() - self.currentWidth) / 2)
        y0 = int((self.height() - self.currentHeight) / 2)

        P0 = QPoint(x0, y0)
        P1 = QPoint(P0.x() + self.currentWidth - folding, P0.y())
        P2 = QPoint(P0.x() + self.currentWidth, P0.y())
        P3 = QPoint(P1.x(), P1.y() + folding)
        P4 = QPoint(P2.x(), P3.y())
        P5 = QPoint(P0.x(), P0.y() + self.currentHeight)
        P6 = QPoint(P2.x(), P5.y())
        P7 = QPoint(P0.x() + pad, P0.y() + pad)
        P8 = QPoint(P7.x() + clientWidth, P7.y())
        P9 = QPoint(P7.x(), P5.y() - pad)
        P10 = QPoint(P8.x(), P9.y())

        self.page = QPolygon([
            P0, P1, P4, P6, P5
        ])

        self.fold = QPolygon([
            P1, P3, P4
        ])

        self.client = QPolygon([
            P7, P8, P10, P9
        ])

        self.cut = QPolygon([
            P1, P2, P4
        ])

    def repaint(self):

        brush = QBrush()
        brush.setColor(Qt.white)
        brush.setStyle(Qt.SolidPattern)

        self.painter.begin(self.pixmap)
        self.painter.setBrush(brush)

        self.painter.setPen(self.getPen(Qt.darkGray))
        self.painter.drawPolygon(self.page)

        self.painter.setPen(self.getPen(Qt.gray))
        self.painter.drawPolygon(self.client)

        self.painter.setPen(self.getPen(Qt.white))
        self.painter.drawPolygon(self.cut)

        self.painter.setPen(self.getPen(Qt.darkGray))
        self.painter.drawPolygon(self.fold)

        self.painter.end()
        self.update()

    def getPen(self, color):
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(color)
        return pen

    def paintEvent(self, event: QPaintEvent):
        with QPainter(self) as painter:
            painter.drawPixmap(0, 0, self.pixmap)

    def resizeEvent(self, event):
        self._setPixmap()
        event.accept()

    def updateRatio(self, newRatio):
        self.ratio = newRatio
        self._setPixmap()

    def _calculateSize(self, isPortrait):
        if isPortrait is True:
            self.currentWidth = self.defaultWidth
            self.currentHeight = self.defaultHeight
        else:
            self.currentWidth = self.defaultHeight
            self.currentHeight = self.defaultWidth

    def updateOrientation(self, isPortrait):
        self._calculateSize(isPortrait)
        self._setPixmap()

#######


class PDFCreator(FPDF):

    # sekcje
    # sekcje widoczne i niewidoczne (#!)
    def __init__(self, text, settings):
        super().__init__()

        nn = CONFIG.assetPath("fonts") / "NotoNormal.ttf"
        nb = CONFIG.assetPath("fonts") / "NotoBold.ttf"
        ni = CONFIG.assetPath("fonts") / "NotoItalic.ttf"

        self.add_font("notable-font", style="", fname=nn)
        self.add_font("notable-font", style="b", fname=nb)
        self.add_font("notable-font", style="i", fname=ni)

        self.done = False
        self._setDefaults()
        self._calculate(settings)
        self._processText(text)
        self._startup()
        self._printout()
        self._save(settings.FileName)

    def _setDefaults(self):
        self.margin = 10  # mm
        self.orientation = "P"
        self.columnWidth = 210  # a4
        self.chapterCounter = 0
        self.contents = []

    def _calculate(self, settings):
        if settings.IsPortrait is False:
            self.columnWidth = 297
            self.orientation = "L"

        self.columnWidth -= self.margin * 2
        self.columnWidth = (self.columnWidth * settings.RatioPercent) / 100

    def _startup(self):
        self.set_title("")
        if len(self.contents) > 0:
            self.set_title(self.contents[0][0])
        if len(self.title) == 0:
            self.set_title("untitled")

        self.add_page(
            orientation=self.orientation,
            format="A4",
            same=False
        )

    def _processText(self, text):
        currentName = ""
        currentContent = ""

        for paragragraph in text.splitlines():
            line = paragragraph.strip()
            if line.startswith("#"):
                self._addContents(currentName, currentContent)
                currentName = line
                currentContent = ""
            else:
                if len(line) > 0:
                    currentContent += "\n" + line

        if len(currentName) > 0 or len(currentContent) > 0:
            self._addContents(currentName, currentContent)

    def _addContents(self, label, content):
        entryLabel = label.strip()
        entryContent = content.strip()

        if len(entryLabel) == 0 and len(entryContent) == 0:
            return

        entry = [entryLabel, entryContent]
        self.contents.append(entry)

    def _printout(self):
        for entry in self.contents:
            self._printChapter(entry[0], entry[1])

    def _printChapterTitle(self, label):
        print(self.columnWidth)
        caption = f"Chapter {self.chapterCounter}"
        if len(label) > 0:
            caption += f": {label}"

        self.set_title(label)

        self.set_font("notable-font", "B", 12)
        self.multi_cell(
            self.columnWidth,
            6,
            caption,
            new_x="LMARGIN",
            new_y="NEXT",
            align="R",
            fill=False,
        )
        self.ln(4)

    def _printChapterBody(self, text):
        self.set_font("notable-font", "", size=10)
        self.multi_cell(self.columnWidth, 6, text)
        self.ln()

    def _printChapter(self, title, text):
        if len(text) > 0:
            self.chapterCounter += 1
            self._printChapterTitle(title)
            self._printChapterBody(text)

    # override
    def header(self):
        self.set_font("notable-font", "B", 9)
        width = self.get_string_width(self.title) + 11
        self.set_line_width(0.1)
        self.set_font("notable-font", "I", 8)
        self.set_text_color(128)
        self.set_draw_color(128)

        self.cell(
            width,
            5,
            self.title,
            border="B",
            new_x="LMARGIN",
            new_y="NEXT",
            align="L",
            fill=False,
        )
        self.ln(10)

    # override
    def footer(self):
        self.set_y(-15)  # mm
        self.set_font("notable-font", "I", 8)
        self.set_text_color(128)
        self.cell(self.columnWidth, 10, f"Page {self.page_no()}", align="L")

    def _save(self, filePath):
        self.output(filePath)
        self.done = os.path.exists(filePath)

    def completed(self):
        return self.done
