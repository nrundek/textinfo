
# -*- coding: UTF-8 -*-
# NVDA appModule providing TextInfo-like commands for this application.
# This file is auto-generated.

import math
import time

import addonHandler
addonHandler.initTranslation()

import api
import ui
from logHandler import log
import appModuleHandler
import textInfos
from keyboardHandler import KeyboardInputGesture

# Clipboard handlers (text only)
try:
    from clipboardHandler import getClipboardText, setClipboardText
except Exception:
    def getClipboardText():
        raise RuntimeError("Clipboard not available")
    def setClipboardText(text):
        pass

CARD_SIZE = 1800
EST_CHARS_PER_PAGE = 4500 

class AppModule(appModuleHandler.AppModule):
    __gestures = {
        "kb:alt+1": "reportCardsOnly",
        "kb(laptop):alt+1": "reportCardsOnly",
        "kb:alt+2": "reportCharCountWithSpaces",
        "kb(laptop):alt+2": "reportCharCountWithSpaces",
        "kb:alt+3": "reportCharCountNoSpaces",
        "kb(laptop):alt+3": "reportCharCountNoSpaces",
        "kb:alt+4": "reportWordCount",
        "kb(laptop):alt+4": "reportWordCount",
        "kb:alt+5": "reportCaretColumnRelative",
        "kb(laptop):alt+5": "reportCaretColumnRelative",
        "kb:alt+6": "reportWrittenLineCount",
        "kb(laptop):alt+6": "reportWrittenLineCount",
        "kb:alt+7": "reportEmptyLineCount",
        "kb(laptop):alt+7": "reportEmptyLineCount",
        "kb:alt+8": "reportEstimatedPages",
        "kb(laptop):alt+8": "reportEstimatedPages",
    }

    # ---------- Utils ----------
    def _sendKeys(self, sequence):
        try:
            KeyboardInputGesture.fromName(sequence).send()
        except Exception as e:
            log.debugWarning("Sending keys '%s' failed: %s" % (sequence, e))

    def _get_all_text(self):
        obj = api.getFocusObject()
        try:
            ti = obj.makeTextInfo(textInfos.POSITION_ALL)
            text = ti.text
            if text and text.strip():
                return text
        except Exception as e:
            log.debugWarning("TextInfo POSITION_ALL failed: %s" % e)
        return self._get_text_via_clipboard()

    def _get_text_via_clipboard(self):
        backup = None
        try:
            try:
                backup = getClipboardText()
            except Exception:
                backup = None

            text = None
            for _ in range(2):
                self._sendKeys("control+a")
                time.sleep(0.35)
                self._sendKeys("control+c")
                time.sleep(0.45)
                try:
                    t = getClipboardText()
                except Exception:
                    t = None
                if t:
                    text = t
                    break

            if backup is not None:
                try:
                    setClipboardText(backup)
                except Exception:
                    pass
            return text
        except Exception as e:
            log.debugWarning("Clipboard fallback failed: %s" % e)
            try:
                if backup is not None:
                    setClipboardText(backup)
            except Exception:
                pass
            return None

    def _count_words(self, text):
        return len(text.split())

    def _count_chars_with_spaces(self, text):
        return len(text)

    def _count_chars_no_spaces(self, text):
        return sum(1 for ch in text if not ch.isspace())

    def _count_written_lines_from_text(self, text):
        if not text:
            return 0
        return sum(1 for ln in text.splitlines() if ln.strip() != "")

    def _count_written_lines_from_TI(self, obj):
        try:
            allTi = obj.makeTextInfo(textInfos.POSITION_ALL)
            cur = allTi.copy()
            cur.collapse(start=True)
            count = 0
            seg = cur.copy()
            seg.expand(textInfos.UNIT_LINE)
            if (seg.text or "").strip() != "":
                count += 1
            while cur.move(textInfos.UNIT_LINE, 1):
                seg = cur.copy()
                seg.expand(textInfos.UNIT_LINE)
                if (seg.text or "").strip() != "":
                    count += 1
            return count
        except Exception as e:
            log.debugWarning("Written-line count via TextInfo failed: %s" % e)
            return 0

    def _count_empty_lines_from_text(self, text):
        if not text:
            return 0
        return sum(1 for ln in text.splitlines() if ln.strip() == "")

    def _count_empty_lines_from_TI(self, obj):
        try:
            allTi = obj.makeTextInfo(textInfos.POSITION_ALL)
            cur = allTi.copy()
            cur.collapse(start=True)
            count = 0
            seg = cur.copy()
            seg.expand(textInfos.UNIT_LINE)
            if (seg.text or "").strip() == "":
                count += 1
            while cur.move(textInfos.UNIT_LINE, 1):
                seg = cur.copy()
                seg.expand(textInfos.UNIT_LINE)
                if (seg.text or "").strip() == "":
                    count += 1
            return count
        except Exception as e:
            log.debugWarning("Empty-line count via TextInfo failed: %s" % e)
            return 0

    def _estimated_pages(self, text):
        if not text:
            return None
        totalChars = self._count_chars_with_spaces(text)
        if totalChars <= 0:
            return 0
        return int(math.ceil(totalChars / float(EST_CHARS_PER_PAGE)))

    # ---------- Caret/Column detection ----------
    def _get_line_and_caret_column_TextInfo(self):
        try:
            obj = api.getFocusObject()
            caretTi = obj.makeTextInfo(textInfos.POSITION_CARET)
            lineTi = caretTi.copy()
            lineTi.expand(textInfos.UNIT_LINE)

            lineText = (lineTi.text or "").replace("\r", "").replace("\n", "")
            totalCols = len(lineText)

            startToCaret = lineTi.copy()
            startToCaret.collapse(start=True)
            startToCaret.setEndPoint(caretTi, "endToStart")
            leftText = (startToCaret.text or "").replace("\r", "").replace("\n", "")
            caretCol = len(leftText) + 1

            if totalCols > 0:
                if caretCol < 1:
                    caretCol = 1
                if caretCol > totalCols:
                    caretCol = totalCols
            return (caretCol, totalCols)
        except Exception as e:
            log.debugWarning("_get_line_and_caret_column_TextInfo failed: %s" % e)
            return None

    def _get_line_and_caret_column_keyboard(self):
        backup = None
        try:
            try:
                backup = getClipboardText()
            except Exception:
                backup = None

            # 1) caret->start
            self._sendKeys("shift+home")
            time.sleep(0.25)
            self._sendKeys("control+c")
            time.sleep(0.45)
            try:
                leftText = getClipboardText() or ""
            except Exception:
                leftText = ""
            leftLen = len(leftText.replace("\r", "").replace("\n", ""))

            # 2) extend to end (whole line)
            self._sendKeys("shift+end")
            time.sleep(0.25)
            self._sendKeys("control+c")
            time.sleep(0.45)
            try:
                fullLine = getClipboardText() or ""
            except Exception:
                fullLine = ""
            fullLine = fullLine.replace("\r", "").replace("\n", "")
            totalCols = len(fullLine)

            # 3) restore caret
            self._sendKeys("home")
            time.sleep(0.10)
            for _ in range(max(0, leftLen)):
                self._sendKeys("rightArrow")
                time.sleep(0.003)

            if backup is not None:
                try:
                    setClipboardText(backup)
                except Exception:
                    pass

            caretCol = min(leftLen + 1, max(1, totalCols if totalCols > 0 else 1))
            return (caretCol, totalCols)
        except Exception as e:
            log.debugWarning("_get_line_and_caret_column_keyboard failed: %s" % e)
            try:
                if backup is not None:
                    setClipboardText(backup)
            except Exception:
                pass
            return None

    def _get_line_and_caret_column_docClipboard(self):
        backup = None
        try:
            try:
                backup = getClipboardText()
            except Exception:
                backup = None

            # part to caret
            self._sendKeys("control+shift+home")
            time.sleep(0.35)
            self._sendKeys("control+c")
            time.sleep(0.55)
            try:
                leftDoc = getClipboardText() or ""
            except Exception:
                leftDoc = ""
            leftDoc = leftDoc.replace("\r\n", "\n").replace("\r", "\n")
            leftLenDoc = len(leftDoc)

            # full doc
            self._sendKeys("control+a")
            time.sleep(0.35)
            self._sendKeys("control+c")
            time.sleep(0.55)
            try:
                fullText = getClipboardText() or ""
            except Exception:
                fullText = ""
            fullText = fullText.replace("\r\n", "\n").replace("\r", "\n")
            fullLen = len(fullText)
            if fullLen == 0:
                if backup is not None:
                    try:
                        setClipboardText(backup)
                    except Exception:
                        pass
                return None

            caretAbs = max(0, fullLen - leftLenDoc)
            if caretAbs > fullLen:
                caretAbs = fullLen

            before = fullText[:caretAbs]
            after = fullText[caretAbs:]
            lastNL = before.rfind("\n")
            lineStart = 0 if lastNL == -1 else lastNL + 1
            nextNL = after.find("\n")
            lineEnd = fullLen if nextNL == -1 else caretAbs + nextNL

            lineText = fullText[lineStart:lineEnd].replace("\r", "")
            totalCols = len(lineText)
            caretCol = (caretAbs - lineStart) + 1

            # restore caret approximately
            self._sendKeys("control+home")
            time.sleep(0.10)
            for _ in range(max(0, caretAbs)):
                self._sendKeys("rightArrow")
                time.sleep(0.0015)

            if backup is not None:
                try:
                    setClipboardText(backup)
                except Exception:
                    pass

            return (caretCol, totalCols)
        except Exception as e:
            log.debugWarning("_get_line_and_caret_column_docClipboard failed: %s" % e)
            try:
                if backup is not None:
                    setClipboardText(backup)
            except Exception:
                pass
            return None

    def _get_line_and_caret_column_walk(self):
        try:
            obj = api.getFocusObject()
            caretTi = obj.makeTextInfo(textInfos.POSITION_CARET)

            cur = caretTi.copy()
            leftLen = 0
            while True:
                prev = cur.copy()
                if not prev.move(textInfos.UNIT_CHARACTER, -1):
                    break
                chTi = prev.copy()
                chTi.expand(textInfos.UNIT_CHARACTER)
                ch = chTi.text or ""
                if ch in ("\r", "\n"):
                    break
                leftLen += 1
                cur = prev

            lineStartTi = cur.copy()

            totalCols = 0
            scan = lineStartTi.copy()
            while True:
                chTi2 = scan.copy()
                chTi2.expand(textInfos.UNIT_CHARACTER)
                ch2 = chTi2.text or ""
                if not ch2:
                    moved = scan.move(textInfos.UNIT_CHARACTER, 1)
                    if not moved:
                        break
                    chTi2 = scan.copy()
                    chTi2.expand(textInfos.UNIT_CHARACTER)
                    ch2 = chTi2.text or ""
                if ch2 in ("\r", "\n"):
                    break
                if ch2 == "":
                    if not scan.move(textInfos.UNIT_CHARACTER, 1):
                        break
                    continue
                totalCols += 1
                if not scan.move(textInfos.UNIT_CHARACTER, 1):
                    break

            caretCol = min(leftLen + 1, max(1, totalCols if totalCols > 0 else 1))
            return (caretCol, totalCols)
        except Exception as e:
            log.debugWarning("_get_line_and_caret_column_walk failed: %s" % e)
            return None

    def _get_line_and_caret_column(self):
        cols = self._get_line_and_caret_column_TextInfo()
        if cols:
            caretCol, totalCols = cols
            if totalCols == 0:
                walkCols = self._get_line_and_caret_column_walk()
                if walkCols:
                    return walkCols
                kbCols = self._get_line_and_caret_column_keyboard()
                if kbCols:
                    return kbCols
            return cols
        walkCols = self._get_line_and_caret_column_walk()
        if walkCols:
            return walkCols
        cols = self._get_line_and_caret_column_keyboard()
        if cols:
            return cols
        return self._get_line_and_caret_column_docClipboard()

    # ---------- Scripts ----------
    def script_reportCardsOnly(self, gesture):
        text = self._get_all_text()
        if not text:
            ui.message(_("Unable to fetch text"))
            return
        chars = self._count_chars_with_spaces(text)
        cards_float = chars / float(CARD_SIZE)
        cards_one_decimal = round(cards_float + 1e-12, 1)
        remainder = chars % CARD_SIZE
        missing = 0 if remainder == 0 else (CARD_SIZE - remainder)
        ui.message(_("Cards: {cards:.1f}. {missing} characters to the next card").format(
            cards=cards_one_decimal, missing=missing))

    def script_reportWordCount(self, gesture):
        text = self._get_all_text()
        if not text:
            ui.message(_("Unable to fetch text"))
            return
        words = self._count_words(text)
        ui.message(_("Words: {words}").format(words=words))

    def script_reportCharCountWithSpaces(self, gesture):
        text = self._get_all_text()
        if not text:
            ui.message(_("Unable to fetch text"))
            return
        chars = self._count_chars_with_spaces(text)
        ui.message(_("Characters with spaces: {chars}").format(chars=chars))

    def script_reportCharCountNoSpaces(self, gesture):
        text = self._get_all_text()
        if not text:
            ui.message(_("Unable to fetch text"))
            return
        chars = self._count_chars_no_spaces(text)
        ui.message(_("Characters without spaces: {chars}").format(chars=chars))

    def script_reportCaretColumnRelative(self, gesture):
        cols = self._get_line_and_caret_column()
        if not cols:
            ui.message(_("Unable to determine column"))
            return
        caretCol, totalCols = cols
        ui.message(_("Column {col} of {total}").format(col=caretCol, total=totalCols))

    def script_reportWrittenLineCount(self, gesture):
        obj = api.getFocusObject()
        text = self._get_all_text()
        if text:
            lines = self._count_written_lines_from_text(text)
        else:
            lines = self._count_written_lines_from_TI(obj)
        ui.message(_("Written lines: {lines}").format(lines=lines))

    def script_reportEmptyLineCount(self, gesture):
        obj = api.getFocusObject()
        text = self._get_all_text()
        if text:
            lines = self._count_empty_lines_from_text(text)
        else:
            lines = self._count_empty_lines_from_TI(obj)
        ui.message(_("Empty lines: {lines}").format(lines=lines))

    def script_reportEstimatedPages(self, gesture):
        text = self._get_all_text()
        pages = self._estimated_pages(text)
        if pages is None:
            ui.message(_("Estimated total pages: 0 (by {cpp} chars/page)").format(cpp=EST_CHARS_PER_PAGE))
        else:
            ui.message(_("Estimated total pages: {pages} (by {cpp} chars/page)").format(
                pages=pages, cpp=EST_CHARS_PER_PAGE))

# Input help strings
AppModule.script_reportCardsOnly.__doc__ = _("Alt+1: Reports 'text cards' (1 card = 1800 characters including spaces) and characters missing to the next full card.")
AppModule.script_reportCharCountWithSpaces.__doc__ = _("Alt+2: Reports the total number of characters (including spaces).")
AppModule.script_reportCharCountNoSpaces.__doc__ = _("Alt+3: Reports the total number of characters (excluding whitespace).")
AppModule.script_reportWordCount.__doc__ = _("Alt+4: Reports the number of words in the document.")
AppModule.script_reportCaretColumnRelative.__doc__ = _("Alt+5: Reports the caret column relative to the total number of columns in the current line (e.g., 'Column 12 of 80').")
AppModule.script_reportWrittenLineCount.__doc__ = _("Alt+6: Reports the number of written (non-empty) lines.")
AppModule.script_reportEmptyLineCount.__doc__ = _("Alt+7: Reports the number of empty (blank/whitespace-only) lines.")
AppModule.script_reportEstimatedPages.__doc__ = _("Alt+8: Reports estimated total pages by 4500 chars/page.")
