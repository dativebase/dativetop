"""DativeTop JavaScript functionality and snippets

Contains strings of JavaScript for doing certain things in the Dative
CoffeeScript SPA that DativeTop serves locally.

"""


# JavaScript to copy any selected text
COPY_SELECTION_JS = (
    'if (window.getSelection) {\n'
    '  window.getSelection().toString();\n'
    '} else if (document.selection && document.selection.type != "Control") {\n'
    '  document.selection.createRange().text;\n'
    '}')


# JavaScript/jQuery to cut (copy and remove) any selected text
CUT_SELECTION_JS = (
    "var focused = $(':focus');\n"
    "var focused_ntv = focused[0];\n"
    "var start = focused_ntv.selectionStart;\n"
    "var end = focused_ntv.selectionEnd;\n"
    "var focused_val = focused.val();\n"
    "var new_focused_val = focused_val.slice(0, start) + "
    "focused_val.slice(end, focused_val.length);\n"
    "focused.val(new_focused_val);\n"
    "focused_ntv.setSelectionRange(start, start);\n"
    "focused_val.slice(start, end);"
)


# JavaScript/jQuery to select all text
SELECT_ALL_JS = (
    "$(':focus').select();"
)


def paste_js(clipboard):
    """Paste the string ``clipboard`` into the selected text of the focused
    element in the DOM using JavaScript/jQuery.
    """
    return (
        f"var focused = $(':focus');\n"
        f"var focused_ntv = focused[0];\n"
        f"var start = focused_ntv.selectionStart;\n"
        f"var end = focused_ntv.selectionEnd;\n"
        f"var focused_val = focused.val();\n"
        f"focused.val(focused_val.slice(0, start) + "
        f"`{clipboard}` + focused_val.slice(end, focused_val.length));\n"
        f"var cursorPos = start + `{clipboard}`.length;\n"
        f"focused_ntv.setSelectionRange(cursorPos, cursorPos);"
    )


DESTROY_DATIVE_APP_SETTINGS = (
    "localStorage.removeItem('dativeApplicationSettings');"
)


GET_DATIVE_APP_SETTINGS = (
    "var x = localStorage.getItem('dativeApplicationSettings');\n"
    "x;"
)


SET_DATIVE_APP_SETTINGS = (
    "localStorage.setItem('dativeApplicationSettings', '{dative_app_settings}');\n"
)
