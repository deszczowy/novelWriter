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
import subprocess
import glob

from fpdf import FPDF

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import (
    QPainter, QPixmap, QPen, QPaintEvent, QResizeEvent, QColor,
    QBrush, QPolygon
)
from PyQt6.QtWidgets import (
    QDialogButtonBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QSpinBox,
    QButtonGroup, QRadioButton, QComboBox
)

from novelwriter import CONFIG
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.modified import NDialog
from novelwriter.types import QtDialogClose, QtDialogOk

logger = logging.getLogger(__name__)

class CustomPDFOptions:

    def __init__(self) -> None:
        self.IsPortrait = False
        self.RatioPercent = 50
        self.createDictionaries()
        self.LineSpacing = 0.8
        self.FontType = "S"
        self.FontSize = 9
        self.ParagraphSpacing = 0.8
        self.drawFileName()
        self.DocumentName = ""

    def drawFileName(self) -> None:
        self.FileName = f"{str(uuid.uuid4().hex)}.pdf"
        pdfPath = CONFIG.tempPath("custompdf")
        pdfPath.mkdir(exist_ok=True)
        self.FileName = os.path.join(pdfPath, self.FileName)

    def createDictionaries(self) -> None:
        self.values = {
            "ls" : {
                0 : ["0.5", 0.5, 0],
                1 : ["0.8", 0.8, 1],
                2 : ["1", 1.0, 0],
                3 : ["1.5", 1.5, 0],
                4 : ["2", 2.0, 0]
            },
            "ps" : {
                0 : ["0.5", 0.5, 0],
                1 : ["0.8", 0.8, 0],
                2 : ["1", 1.0, 1],
                3 : ["1.5", 1.5, 0],
                4 : ["2", 2.0, 0],
                5 : ["3", 3.0, 0],
                6 : ["4", 4.0, 0]
            },
            "fs" : {
                0 : ["6", 6.0, 1],
                1 : ["8", 8.0, 0],
                2 : ["9", 9.0, 0],
                3 : ["10", 10.0, 0],
                4 : ["11", 11.0, 0],
                5 : ["12", 12.0, 0],
                6 : ["14", 14.0, 0]
            },
            "ft" : {
                0 : ["Typewriter", "M", 0],
                1 : ["Sans", "S", 1],
                2 : ["Serif", "D", 0]
            }
        }


class GuiCustomPDF(NDialog):

    def __init__(self, parent: QWidget, dc: str, title: str) -> None:
        super().__init__(parent=parent)

        self.settings = CustomPDFOptions()
        self.settings.DocumentName = title
        self.content = dc

        logger.debug("Create: GuiCustomPDF")
        logger.debug(f"Document: {title}")
        self.setObjectName("GuiCustomPDF")

        self.setWindowTitle(self.tr("Custom PDF export"))
        self.resize(CONFIG.pxInt(700), CONFIG.pxInt(300))

        self.lblDialogTitle = NColourLabel(
            self.tr("Export document to PDF"),
            scale=1.6,
            bold=True,
            parent=parent
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
        self._clearTemp()
        pdf = PDFCreator(self.content, self.settings)
        close = False
        if pdf.completed():
            close = subprocess.call(["xdg-open", self.settings.FileName]) == 0

        if close:
            self.reject()
        else:
            print("PDF Error: something bad happened.")

    def _fillComboBox(self, combo, values):
        default = 0
        for i in values:
            v = values[i]
            if v[2] == 1:
                default = i
            combo.addItem(v[0], v)
        combo.setCurrentIndex(default)

    def _buildOptions(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        percentLabel = QLabel(self.tr("Page fill percent"), self)

        percentField = QSpinBox(self)

        percentField.setValue(self.settings.RatioPercent)
        percentField.setMinimum(40)
        percentField.setMaximum(85)
        percentField.valueChanged.connect(self._percentFieldChange)

        orientationLabel = QLabel(self.tr("Document orientation"), self)
        orientationGroup = QButtonGroup(self)
        orientationPortrait = QRadioButton("Portrait")
        orientationLandscape = QRadioButton("Landscape")
        orientationGroup.addButton(orientationPortrait, 1)
        orientationGroup.addButton(orientationLandscape, 2)
        orientationPortrait.setChecked(self.settings.IsPortrait is True)
        orientationLandscape.setChecked(self.settings.IsPortrait is False)
        orientationGroup.idClicked.connect(self._orientationChanged)

        fontTypeLabel = QLabel(self.tr("Font type"), self)
        self.fontTypeCombo = QComboBox(self)
        self.fontTypeCombo.currentIndexChanged.connect(
            self._fontTypeChange
        )
        self._fillComboBox(self.fontTypeCombo, self.settings.values["ft"])

        fontSizeLabel = QLabel(self.tr("Font size"), self)
        self.fontSizeCombo = QComboBox(self)
        self.fontSizeCombo.currentIndexChanged.connect(
            self._fontSizeChange
        )
        self._fillComboBox(self.fontSizeCombo, self.settings.values["fs"])

        lineSpacingLabel = QLabel(self.tr("Line spacing"), self)
        self.lineSpacingCombo = QComboBox(self)
        self.lineSpacingCombo.currentIndexChanged.connect(
            self._lineSpacingChange
        )
        self._fillComboBox(self.lineSpacingCombo, self.settings.values["ls"])

        paragraphSpacingLabel = QLabel(self.tr("Paragraph spacing"), self)
        self.paragraphSpacingCombo = QComboBox(self)
        self.paragraphSpacingCombo.currentIndexChanged.connect(
            self._paragraphSpacingChange
        )
        self._fillComboBox(self.paragraphSpacingCombo, self.settings.values["ps"])
        layout.addWidget(percentLabel)
        layout.addWidget(percentField)
        layout.addWidget(orientationLabel)
        layout.addWidget(orientationPortrait)
        layout.addWidget(orientationLandscape)
        layout.addWidget(fontTypeLabel)
        layout.addWidget(self.fontTypeCombo)
        layout.addWidget(fontSizeLabel)
        layout.addWidget(self.fontSizeCombo)
        layout.addWidget(lineSpacingLabel)
        layout.addWidget(self.lineSpacingCombo)
        layout.addWidget(paragraphSpacingLabel)
        layout.addWidget(self.paragraphSpacingCombo)
        layout.addStretch()

        return layout

    def _buildPreview(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        previewLabel = QLabel("Preview")
        self.preview = CustomPDFCLientPreview(
            self._getRatio(self.settings.RatioPercent),
            self.settings.IsPortrait
        )
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

    def _percentFieldChange(self, newValue: int) -> None:
        self.settings.RatioPercent = newValue
        self.preview.updateRatio(self._getRatio(newValue))

    def _orientationChanged(self, id: int) -> None:
        self.settings.IsPortrait = id == 1
        self.preview.updateOrientation(self.settings.IsPortrait)

    def _fontTypeChange(self, index: int) -> None:
        data = self.fontTypeCombo.itemData(index)        
        self.settings.FontType = data[1]

    def _fontSizeChange(self, index: int) -> None:
        data = self.fontSizeCombo.itemData(index)        
        self.settings.FontSize = data[1]

    def _lineSpacingChange(self, index: int) -> None:
        data = self.lineSpacingCombo.itemData(index)
        self.settings.LineSpacing = data[1]

    def _paragraphSpacingChange(self, index: int) -> None:
        data = self.paragraphSpacingCombo.itemData(index)
        self.settings.ParagraphSpacing = data[1]

    def _getRatio(self, value: float) -> float:
        return value / 100

    def _clearTemp(self) -> None:
        param = CONFIG.tempPath("custompdf")
        param = os.path.join(param, '*.pdf')
        try:
            files = glob.glob(param)
            for f in files:
                os.remove(f)
        except Exception as e:
            print("TEMP Clean: failed")
            print(e)


class CustomPDFCLientPreview(QWidget):
    page = []
    client = []
    fold = []
    cut = []

    def __init__(self, startingRatio: float, isPortrait: bool) -> None:
        super().__init__()
        self.ratio = startingRatio
        # A4 measures
        self.defaultWidth = 210
        self.defaultHeight = 297
        self._calculateSize(isPortrait)
        self.painter = QPainter()

    def _setPixmap(self) -> None:
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)
        self.calculate()
        self.repaint()

    def calculate(self) -> None:
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

    def repaint(self) -> None:

        brush = QBrush()
        brush.setColor(Qt.GlobalColor.white)
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        self.painter.begin(self.pixmap)
        self.painter.setBrush(brush)

        self.painter.setPen(self.getPen(Qt.GlobalColor.darkGray))
        self.painter.drawPolygon(self.page)

        self.painter.setPen(self.getPen(Qt.GlobalColor.gray))
        self.painter.drawPolygon(self.client)

        self.painter.setPen(self.getPen(Qt.GlobalColor.white))
        self.painter.drawPolygon(self.cut)

        self.painter.setPen(self.getPen(Qt.GlobalColor.darkGray))
        self.painter.drawPolygon(self.fold)

        self.painter.end()
        self.update()

    def getPen(self, color: QColor) -> None:
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(color)
        return pen

    def paintEvent(self, event: QPaintEvent) -> None:
        with QPainter(self) as painter:
            painter.drawPixmap(0, 0, self.pixmap)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._setPixmap()
        event.accept()

    def updateRatio(self, newRatio: float) -> None:
        self.ratio = newRatio
        self._setPixmap()

    def _calculateSize(self, isPortrait: bool) -> None:
        if isPortrait is True:
            self.currentWidth = self.defaultWidth
            self.currentHeight = self.defaultHeight
        else:
            self.currentWidth = self.defaultHeight
            self.currentHeight = self.defaultWidth

    def updateOrientation(self, isPortrait: bool) -> None:
        self._calculateSize(isPortrait)
        self._setPixmap()

#######
class LocalFont:
    def __init__(self, fname, fstyle, fileName):
        self.family = fname
        self.style = fstyle
        self.path = fileName

class FontCollection:
    def __init__(self):
        path = CONFIG.assetPath("fonts")
        self.collection = {
            "M": {
                "N": LocalFont("typewriter", "", path / "CourierNormal.ttf"),
                "B": LocalFont("typewriter", "b", path / "CourierBold.ttf"),
                "I": LocalFont("typewriter", "i", path / "CourierItalic.ttf")
            },
            "D": {
                "N": LocalFont("notable", "", path / "NotoNormal.ttf"),
                "B": LocalFont("notable", "b", path / "NotoBold.ttf"),
                "I": LocalFont("notable", "i", path / "NotoItalic.ttf")
            },
            "S": {
                "N": LocalFont("lato", "", path / "LatoNormal.ttf"),
                "B": LocalFont("lato", "b", path / "LatoBold.ttf"),
                "I": LocalFont("lato", "i", path / "LatoItalic.ttf")
            },
        }
    
    def font(self, ftype, style) -> LocalFont:
        return self.collection[ftype][style]

#######
class PDFCreator(FPDF):

    def __init__(self, text: str, settings: CustomPDFOptions) -> None:
        super().__init__()

        self._storeFonts()
        self.done = False
        self._setDefaults()
        self._calculate(settings)
        self._processText(text)
        self._startup()
        self._printout()
        self._save(settings.FileName)
    
    def _storeFonts(self):
        self.localFonts = FontCollection()
        for mainKey, family in self.localFonts.collection.items():
            for styleKey, font in family.items():
                self.add_font(font.family, style=font.style, fname=font.path)


    def _setDefaults(self) -> None:
        self.margin = 10  # mm
        self.orientation = "P"
        self.columnWidth = 210  # a4
        self.chapterCounter = 0
        self.contents = []
        self.mainFontSize = 10
        self.headerFontSize = 12
        self.lineHeight = 6

    def _calculate(self, settings: CustomPDFOptions) -> None:
        if settings.IsPortrait is False:
            self.columnWidth = 297
            self.orientation = "L"

        self.columnWidth -= self.margin * 2
        self.columnWidth = (self.columnWidth * settings.RatioPercent) / 100

        self.mainFontSize = settings.FontSize
        self.headerFontSize = int(self.mainFontSize * 1.20)

        self.lineHeight = self.mainFontSize * settings.LineSpacing
        self.paragraphSpacing = settings.ParagraphSpacing
        self.fontType = settings.FontType

    def _startup(self) -> None:
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

    def _set_local_font(self, style, size):
        font = self.localFonts.font(self.fontType, style)
        self.set_font(font.family, font.style, size)
    
    def _extractName(self, name: str) -> str:
        i = 0
        n = len(name)
        regular = True

        if n == 0:
            return [ name, False ]
        
        while True:
            c = name[i]
            if c != "#":
                if c == "!":
                    regular = False
                    i += 1
                return [ name[i:].strip(), regular ]
            i += 1

            if i >= n:
                break
        return [ name, True ]

    def _processText(self, text: str) -> None:
        currentName = ""
        currentContent = ""

        for paragragraph in text.splitlines():
            line = paragragraph.strip()
            if line.startswith("#"):
                data = self._extractName(currentName)
                self._addContents(data[0], currentContent, data[1])
                currentName = line
                currentContent = ""
            else:
                if len(line) > 0:
                    currentContent += "\n" + line

        if len(currentName) > 0 or len(currentContent) > 0:
            data = self._extractName(currentName)
            self._addContents(data[0], currentContent, data[1])

    def _addContents(self, label: str, content: str, isRegular: bool) -> None:
        entryLabel = label.strip()
        entryContent = content.strip()

        if len(entryLabel) == 0 and len(entryContent) == 0:
            return

        entry = [entryLabel, entryContent, isRegular]
        self.contents.append(entry)

    def _printout(self) -> None:
        for entry in self.contents:
            self._printChapter(entry[0], entry[1], entry[2])

    def _printChapterTitle(self, label: str, isRegular: bool) -> None:
        caption = f"Chapter {self.chapterCounter}" if isRegular else ""
        if len(label) > 0:
            caption += f": {label}" if isRegular else label

        self.set_title(label)

        self._set_local_font("B", self.headerFontSize)
        self.multi_cell(
            self.columnWidth,
            self.lineHeight,
            caption,
            new_x="LMARGIN",
            new_y="NEXT",
            align="R",
            fill=False,
        )
        self.ln(4)

    def _printChapterBody(self, text: str) -> None:
        paragraphs = text.splitlines()
        self._set_local_font("N", self.mainFontSize)
        for p in paragraphs:
            self.multi_cell(self.columnWidth, self.lineHeight, p)
            step = self.font_size * self.paragraphSpacing
            self.ln(step)

    def _printChapter(self, title: str, text: str, isRegular: bool) -> None:
        if len(text) > 0:
            if isRegular:
                self.chapterCounter += 1
            self._printChapterTitle(title, isRegular)
            self._printChapterBody(text)

    # override
    def header(self) -> None:
        self._set_local_font("B", 9)
        width = self.get_string_width(self.title) + 11
        self.set_line_width(0.1)
        self._set_local_font("I", 8)
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
    def footer(self) -> None:
        self.set_y(-15)  # mm
        self._set_local_font("I", 8)
        self.set_text_color(128)
        self.cell(self.columnWidth, 10, f"Page {self.page_no()}", align="L")

    def _save(self, filePath: str) -> None:
        self.output(filePath)
        self.done = os.path.exists(filePath)

    def completed(self) -> None:
        return self.done
