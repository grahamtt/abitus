"""Compatibility helpers for Flet API changes."""

import flet as ft


# Icon constants for Flet 0.28.3 compatibility
class icons:
    """Icon constants compatible with Flet 0.28.3."""
    # Navigation
    HOME = "home"
    HOME_OUTLINED = "home_outlined"
    BOOK = "book"
    BOOK_OUTLINED = "book_outlined"
    ASSIGNMENT = "assignment"
    ASSIGNMENT_OUTLINED = "assignment_outlined"
    PERSON = "person"
    PERSON_OUTLINED = "person_outlined"
    SETTINGS = "settings"
    SETTINGS_OUTLINED = "settings_outlined"
    
    # Actions
    ARROW_BACK = "arrow_back"
    ARROW_FORWARD = "arrow_forward"
    CHECK = "check"
    CHECK_CIRCLE = "check_circle"
    CHECK_BOX = "check_box"
    CHECK_BOX_OUTLINE_BLANK = "check_box_outline_blank"
    CLOSE = "close"
    ADD = "add"
    ADD_CIRCLE_OUTLINE = "add_circle_outline"
    EDIT = "edit"
    EDIT_OUTLINED = "edit_outlined"
    EDIT_NOTE = "edit_note"
    DELETE_OUTLINE = "delete_outline"
    DELETE_FOREVER = "delete_forever"
    PLAY_ARROW = "play_arrow"
    
    # Symbols
    STAR = "star"
    TIMER = "timer"
    REPEAT = "repeat"
    LIGHTBULB = "lightbulb"
    LIGHTBULB_OUTLINE = "lightbulb_outline"
    ROCKET_LAUNCH = "rocket_launch"
    AUTO_AWESOME = "auto_awesome"
    CHEVRON_RIGHT = "chevron_right"
    CIRCLE_OUTLINED = "circle_outlined"
    RADIO_BUTTON_CHECKED = "radio_button_checked"
    RADIO_BUTTON_UNCHECKED = "radio_button_unchecked"


# Color constants for Flet 0.28.3 compatibility
class colors:
    """Color constants compatible with Flet 0.28.3."""
    # Basic colors
    WHITE = "white"
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    TRANSPARENT = "transparent"
    
    # Material colors
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ERROR = "error"
    SURFACE = "surface"
    ON_SURFACE = "onsurface"
    ON_PRIMARY = "onprimary"
    ON_PRIMARY_CONTAINER = "onprimarycontainer"
    PRIMARY_CONTAINER = "primarycontainer"
    SURFACE_CONTAINER_HIGHEST = "surfacecontainerhighest"
    SURFACE_CONTAINER_HIGH = "surfacecontainerhigh"
    INVERSE_SURFACE = "inversesurface"
    ON_INVERSE_SURFACE = "oninversesurface"
    
    # Shade colors
    AMBER = "amber"
    AMBER_700 = "amber700"
    ORANGE_700 = "orange700"
    BLUE_700 = "blue700"
    GREEN_700 = "green700"
    GREEN_800 = "green800"
    RED_700 = "red700"
    GREY_800 = "grey800"
    GREY_700 = "grey700"
    GREY_600 = "grey600"
    
    @staticmethod
    def with_opacity(opacity: float, color: str) -> str:
        """Apply opacity to a color. Returns color with opacity suffix or hex with alpha."""
        # For hex colors, prepend alpha
        if color.startswith("#"):
            # Convert opacity to hex alpha (00-FF)
            alpha = int(opacity * 255)
            alpha_hex = f"{alpha:02x}"
            # Insert alpha after # for #AARRGGBB format
            return f"#{alpha_hex}{color[1:]}"
        
        # For named colors, use opacity suffix (e.g., "white70" for 70% opacity)
        opacity_percent = int(opacity * 100)
        # Map common percentages to Material naming
        opacity_map = {
            10: "12",
            15: "12", 
            20: "24",
            30: "26",
            40: "38",
            50: "54",
            60: "54",
            70: "70",
            80: "87",
            90: "87",
        }
        suffix = opacity_map.get(opacity_percent, str(opacity_percent))
        return f"{color}{suffix}"


def padding_all(value: float) -> ft.Padding:
    """Create padding with same value on all sides."""
    return ft.Padding(value, value, value, value)


def padding_symmetric(horizontal: float = 0, vertical: float = 0) -> ft.Padding:
    """Create padding with symmetric horizontal and vertical values."""
    return ft.Padding(left=horizontal, right=horizontal, top=vertical, bottom=vertical)


def padding_only(
    left: float = 0, 
    right: float = 0, 
    top: float = 0, 
    bottom: float = 0
) -> ft.Padding:
    """Create padding with specific side values."""
    return ft.Padding(left=left, right=right, top=top, bottom=bottom)

