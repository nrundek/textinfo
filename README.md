# TextInfo

**TextInfo** is a global NVDA add-on that provides quick access to text information in the application where reading or writing is taking place.  
The information is available in **English**, **Croatian**, and **Serbian**, depending on NVDA language settings.

---

## Features and Keyboard Shortcuts

- **Alt+1** – Reports text cards (1 card = 1800 characters including spaces) and the number of characters missing to the next full card.  
- **Alt+2** – Reports the number of characters including spaces.  
- **Alt+3** – Reports the number of characters excluding spaces.  
- **Alt+4** – Reports the number of words in the document.  
- **Alt+5** – Caret position: reports the column number of the caret relative to the total number of columns in the current line.  
- **Alt+6** – Reports the number of written (non-empty) lines.  
- **Alt+7** – Reports the number of empty lines (only spaces or completely blank).  
- **Alt+8** – Reports the estimated number of pages (calculated by 1800 characters per page).  

---

## Tested Applications

1. MS Word  
2. Notepad  
3. WordPad  
4. LibreOffice  
5. Biblouis  

---

## Technical Notes

- The add-on uses the **TextInfo API**, clipboard fallback methods, and custom algorithms when standard approaches are not available.  
- Page estimation is based on the ratio `1800 characters = 1 page`, which corresponds to a typical text format.  

---

## Localization

The add-on supports translation via `.po` files.  
Currently available languages:  
- English (en)  
- Croatian (hr)  
- Serbian (sr)  
