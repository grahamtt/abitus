"""Compatibility helpers for Flet API changes."""

import flet as ft


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

