"""CherryScript - A dynamic scripting language for data science and automation"""
__version__ = "1.0.0"
__author__ = "Cherry Computer Ltd."

from .runtime.interpreter import Runtime
from .cli import main

__all__ = ["Runtime", "main"]
