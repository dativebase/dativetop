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
    "var focused = document.activeElement;\n"
    "var start = focused.selectionStart;\n"
    "var end = focused.selectionEnd;\n"
    "var val = focused.value;\n"
    "var new_val = val.slice(0, start) + val.slice(end, val.length);\n"
    "focused.value = new_val;\n"
    "focused.setSelectionRange(start, start);\n"
    "val.slice(start, end);"
)


# JavaScript/jQuery to select all text
SELECT_ALL_JS = (
    "var focused = document.activeElement;\n"
    "var val = focused.value;\n"
    "focused.setSelectionRange(0, val.length);"
)


def paste_js(clipboard):
    """Paste the string ``clipboard`` into the selected text of the focused
    element in the DOM using JavaScript/jQuery.
    """
    return (
        f"var focused = document.activeElement;\n"
        f"var start = focused.selectionStart;\n"
        f"var end = focused.selectionEnd;\n"
        f"var val = focused.value;\n"
        f"var new_val = val.slice(0, start) + `{clipboard}` + val.slice(end, val.length);\n"
        f"focused.value = new_val;\n"
        f"var cursorPos = start + `{clipboard}`.length;\n"
        f"focused.setSelectionRange(cursorPos, cursorPos);"
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
