import os


def __resize_stellarium_window_x11(width : int, height : int):
    from Xlib import X, display
    from Xlib.ext.xtest import fake_input
    import Xlib.XK
    import re
    from ewmh import EWMH

    ewmh = EWMH()
    windows = ewmh.getClientList()
    for win in windows:
        title = ewmh.getWmName(win)
        if isinstance(title, bytes):
            title = title.decode('utf-8', 'replace')#
        pattern = r'^Stellarium \d+\.\d+\.\d+$'
        if bool(re.match(pattern, title)):
            ewmh.setWmState(win, 0, '_NET_WM_STATE_FULLSCREEN')

            # setting width/size her is pointless. The window manager will clip it to the screen dimensions.
            # This window will not have the proper size when the size is larger than the screen.
            ewmh.setMoveResizeWindow(win, x=0, y=0, w=width, h=height, gravity=0)            
            ewmh.display.flush() 

            # Send Alt+F8 to the window
            d = display.Display()
            fake_input(d, X.KeyPress, d.keysym_to_keycode(Xlib.XK.string_to_keysym("Alt_L")))
            fake_input(d, X.KeyPress, d.keysym_to_keycode(Xlib.XK.string_to_keysym("F8")))
            fake_input(d, X.KeyRelease, d.keysym_to_keycode(Xlib.XK.string_to_keysym("F8")))
            fake_input(d, X.KeyRelease, d.keysym_to_keycode(Xlib.XK.string_to_keysym("Alt_L")))

            # Send four "Cursor Up" key presses
            for _ in range(4):
                fake_input(d, X.KeyPress, d.keysym_to_keycode(Xlib.XK.string_to_keysym("Up")))
                fake_input(d, X.KeyRelease, d.keysym_to_keycode(Xlib.XK.string_to_keysym("Up")))

            # Send "Enter" key press
            fake_input(d, X.KeyPress, d.keysym_to_keycode(Xlib.XK.string_to_keysym("Return")))        
            fake_input(d, X.KeyRelease, d.keysym_to_keycode(Xlib.XK.string_to_keysym("Return")))
            d.sync()

            # now move the window up so that its upper left corner is outside the screen. 
            ewmh.setMoveResizeWindow(win, x=0, y=0, w=width, h=height, gravity=0)            
            ewmh.display.flush()  # Apply changes

        print(title)


def resize_stellarium_window(width, height):
    if os.name == 'linux':
        __resize_stellarium_window_x11(width, height)
    else:
        raise NotImplementedError("This OS is not supported")
