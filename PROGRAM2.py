import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import json
import time
from PIL import Image, ImageTk
from xai_sdk import Client
from xai_sdk.chat import system, user, assistant, image
import os
import base64
import re

API_KEY = "xai-190haggHSufNOBu1YOmy9WHhJIKG4XsU9S9VHQlPXvki6QrUm98qXmGBNEiifwxEgLwShjVP8qvviiYM"
