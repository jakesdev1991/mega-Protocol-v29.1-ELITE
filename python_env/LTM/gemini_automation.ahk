; AutoHotkey Script for Gemini Browser Automation
; Hotkey: Ctrl + J
; Use 'Window Spy' (right-click AHK icon in tray) to find your exact X, Y coords

^j:: ; Hotkey: Ctrl + J
{
    ; 1. Move and click the browser's text input area
    ; IMPORTANT: Use Window Spy to find the coordinates of the chat box.
    ; Replace the 500, 800 with your actual X, Y screen coordinates.
    Click, 500, 800 
    Sleep, 500 ; Brief wait to ensure focus
    
    ; 2. Paste the prompt currently in your clipboard
    ; Ensure your Python script (using pyperclip) has already copied the prompt.
    Send, ^v 
    Sleep, 300
    
    ; 3. Press Enter to submit to Gemini
    Send, {Enter}
}
return
