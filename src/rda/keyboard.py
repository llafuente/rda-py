import logging
from typing import List, Optional
import platform

from .automation import Automation
from .base import Base

class VirtualKey:
    """
    Virtual key
    """

    #: string - Virtual key, example: {vk41}
    vk = ""

    #: boolean - shift pressed?
    shift = False

    #: boolean - ctrl pressed?
    ctrl = False

    #: boolean - alt pressed?
    alt = False

    def __init__(self, vk: str, shift: bool, ctrl: bool, alt: bool):
        """
          Creates a virtual key
        """
        self.vk = vk
        self.shift = shift
        self.ctrl = ctrl
        self.alt = alt

    def __str__(self):
        """
          Retrieves the virtual key to be used with sendKeys
        """
        output = ""

        if self.shift:
            output += "{LShift Down}"
        if self.ctrl:
            output += "{LControl Down}"
        if self.alt:
            output += "{LAlt Down}"

        output += self.vk

        if self.shift:
            output += "{LShift Up}"
        if self.ctrl:
            output += "{LControl Up}"
        if self.alt:
            output += "{LAlt Up}"

        return output

class Keyboard(Base):
    """
    Keyboard handling at OS level.

    Remarks:
      type use Raw Mode
    """

    def __init__(self, automation: Automation):
        # Assert automation is not null
        self.automation = automation

    def _type(self, text: str, hwnd: Optional[int] = 0, backgroundControl: str = "") -> 'Keyboard':
        if self.automation.input_mode == "interactive":
            # TODO REVIEW blocking: bool = True
            self.automation.ahk.send(text, raw = True, key_delay = self.automation.key_delay, key_press_duration = self.automation.press_duration, send_mode = self.automation.send_mode)
        else:
            if not hwnd:
                raise ValueError('hwnd is required when input mode is background')
            raw_text = "{Raw}" + text
            self.automation.ahk.control_send(raw_text, backgroundControl, title=f"ahk_id {hwnd}", detect_hidden_windows = True)

        return self

    def type(self, text: str, hwnd: Optional[int] = 0, backgroundControl: str = "") -> 'Keyboard':
        """
        Sends given text (literally) as keystrokes

        :remarks:
          This method can disclosure information, use <Keyboard.send_password>

        :remarks:
          use Raw mode: https://www.autohotkey.com/docs/v1/lib/Send.htm#Raw

        :param text: text.
        :param hwnd: Window handle.
        :param backgroundControl: Control parameter from ControlSend.

        :raises ValueError: hwnd is required when input mode is background

        :return: Keyboard for chaining
        """
        logging.debug(f'Keyboard.type {({"text": text, "hwnd": hwnd, "backgroundControl": backgroundControl, "automation": repr(self.automation)})}')

        return self._type(text, hwnd, backgroundControl)


    def type_password(self, password: str, hwnd: Optional[int] = 0, backgroundControl: str = "") -> 'Keyboard':
        """
        Sends given password (literally) as keystrokes

        :remarks:
          This method can disclosure information, use <Keyboard.send_password>

        :remarks:
          use Raw mode: https://www.autohotkey.com/docs/v1/lib/Send.htm#Raw

        :param password: password.
        :param hwnd: Window handle.
        :param backgroundControl: Control parameter from ControlSend.

        :raises ValueError: hwnd is required when input mode is background

        :return: Keyboard for chaining
        """

        logging.debug(f'Keyboard.type_password {({"password": len(password), "hwnd": hwnd, "backgroundControl": backgroundControl, "automation": repr(self.automation)})}')

        return self._type(password, hwnd, backgroundControl)

    def _send_keys(self, keys: str, hwnd: Optional[int] = 0, backgroundControl: str = "") -> 'Keyboard':
        if self.automation.input_mode == "interactive":
            # TODO REVIEW blocking: bool = True
            self.automation.ahk.send(keys, raw = False, key_delay = self.automation.key_delay, key_press_duration = self.automation.press_duration, send_mode = self.automation.send_mode)
        else:
            if not hwnd:
                raise ValueError('hwnd is required when input mode is background')

            self.automation.ahk.control_send(keys, control = backgroundControl, title=f"ahk_id {hwnd}", detect_hidden_windows = True)

        return self

    def send_keys(self, keys: str, hwnd: Optional[int] = 0, backgroundControl: str = "") -> 'Keyboard':
        """
        Sends simulated keystrokes

        :remarks:
          This method can disclosure information, use <Keyboard.send_password>

        :param keys: keys.
        :param hwnd: Window handle.
        :param backgroundControl: Control parameter from ControlSend.

        :raises ValueError: hwnd is required when input mode is background

        :return: Keyboard for chaining
        """
        logging.debug(f'Keyboard.send_keys {({"keys": keys, "hwnd": hwnd, "backgroundControl": backgroundControl, "automation": repr(self.automation)})}')

        return self._send_keys(keys, hwnd, backgroundControl)

    def send_password(self, password: str, hwnd: Optional[int] = 0, backgroundControl: str = "") -> 'Keyboard':
        """
        It's an alias of <Keyboard.sendKeys> but just log the length

        :remarks:
          This method can disclosure information, use <Keyboard.send_password>

        :param password: password.
        :param hwnd: Window handle.
        :param backgroundControl: Control parameter from ControlSend.

        :raises ValueError: hwnd is required when input mode is background

        :return: Keyboard for chaining
        """
        logging.debug(f'Keyboard.send_keys {({"password": len(password), "hwnd": hwnd, "backgroundControl": backgroundControl, "automation": repr(self.automation)})}')

        self._send_keys(password, hwnd, backgroundControl)

        return self


    def get_keyboard_layouts(self) -> List[int]:
        """
        Retrieves selectable (by user) keyboard layouts
        """
        import ctypes

        hkl_num = 20
        hHkls = (ctypes.c_void_p * hkl_num)()

        # Get number of keyboard layouts
        num = ctypes.windll.user32.GetKeyboardLayoutList(hkl_num, hHkls)

        # Convert to list of integers
        list = []
        for i in range(num):
            list.append(int(hHkls[i]))

        logging.debug(f"Keyboard.get_keyboard_layouts() <-- {list}")

        return list

    def get_letter_to_virtualkey(self, letter: str, hkl: int) -> VirtualKey:
        """
        Translates a character to the corresponding virtual-key code and shift state. The function translates the character using the input language and physical keyboard layout identified by the input locale identifier.

        :param letter: one letter string
        :param hkl: keyboard layout, see: <Window.get_keyboardlayout>

        :raise: VkKeyScanExW call failed

        :return: virtual key
        """
        import ctypes

        logging.debug(f"get_letter_to_virtualkey()")

        # Get Unicode character code
        ch = ord(letter)
        retVK = None
        if (int(platform.architecture()[0][:2], 10) == 64): # pragma no cover
            # Call VkKeyScanExW
            retVK = ctypes.windll.User32.VkKeyScanExW(
                ctypes.c_ushort(ch),
                ctypes.c_uint(hkl)
            )

            if retVK == -1:
                raise Exception("VkKeyScanExW call failed")
        else:
            retVK = ctypes.windll.User32.VkKeyScanExA(
                ctypes.c_char(ch),
                ctypes.c_uint(hkl)
            )

            if retVK == -1:
                raise Exception("VkKeyScanExA call failed") # pragma no cover
        print(retVK)
        vk_int = retVK & 0xFF
        print(vk_int)
        vk_hex = hex(vk_int)[2:].zfill(2).upper()
        vk = f"{{vk{vk_hex}}}"
        """
        keyboard_state = vk_int >> 8
        shift = bool(keyboard_state & 0x01)
        ctrl = bool(keyboard_state & 0x02)
        alt = bool(keyboard_state & 0x04)
        """
        shift = bool(retVK & 0x100)
        ctrl = bool(retVK & 0x200)
        alt = bool(retVK & 0x400)
        #hanankey = bool(retVK & 0x800)

        return VirtualKey(vk, shift, ctrl, alt)

    def get_text_to_virtualkeys(self, text: str, hkl: int) -> List[VirtualKey]:
        """
        Translates given text to the corresponding virtual-key code and shift state. The function translates the character using the input language and physical keyboard layout identified by the input locale identifier.

        :param text: text
        :param hkl: keyboard layout, see: <Window.get_keyboardlayout>

        :raise: VkKeyScanExW call failed

        :return: virtual key list
        """
        logging.debug(f"textToVirtualKeys()")

        result = []
        for ch in text:
            result.append(self.get_letter_to_virtualkey(ch, hkl))

        return result

    def get_text_to_sendkeys(self, text: str, hkl: int) -> str:
        """
        Translates text_to_virtualkeys so it can be used in send_keys

        :param text: text
        :param hkl: keyboard layout, see: <Window.get_keyboardlayout>

        :raise: VkKeyScanExW call failed

        :return: virtual key list as string that can be used in sendKeys
        """

        keys = self.get_text_to_virtualkeys(text, hkl)

        output = ""
        shift = False
        ctrl = False
        alt = False

        for k in keys:
            # Start-stop modifiers
            if shift and not k.shift:
                output += "{LShift Up}"
                shift = False
            if ctrl and not k.ctrl:
                output += "{LControl Up}"
                ctrl = False
            if alt and not k.alt:
                output += "{LAlt Up}"
                alt = False

            if not shift and k.shift:
                output += "{LShift Down}"
                shift = True
            if not ctrl and k.ctrl:
                output += "{LControl Down}"
                ctrl = True
            if not alt and k.alt:
                output += "{LAlt Down}"
                alt = True

            output += k.vk

        # Close modifiers
        if shift:
            output += "{LShift Up}"
        if ctrl:
            output += "{LControl Up}"
        if alt:
            output += "{LAlt Up}"

        return output
