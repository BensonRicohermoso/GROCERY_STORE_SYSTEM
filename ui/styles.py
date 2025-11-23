import tkinter as tk
from tkinter import ttk
import config


class AppStyles:
    """Application styling constants"""
    
    # Colors
    PRIMARY = config.COLORS['primary']
    SECONDARY = config.COLORS['secondary']
    SUCCESS = config.COLORS['success']
    DANGER = config.COLORS['danger']
    WARNING = config.COLORS['warning']
    INFO = config.COLORS['info']
    LIGHT = config.COLORS['light']
    DARK = config.COLORS['dark']
    WHITE = config.COLORS['white']
    BACKGROUND = config.COLORS['background']
    TEXT = config.COLORS['text']
    TEXT_LIGHT = config.COLORS['text_light']
    
    # Fonts
    FONT_FAMILY = config.FONTS['family']
    FONT_SMALL = (FONT_FAMILY, config.FONTS['size_small'])
    FONT_NORMAL = (FONT_FAMILY, config.FONTS['size_normal'])
    FONT_MEDIUM = (FONT_FAMILY, config.FONTS['size_medium'])
    FONT_LARGE = (FONT_FAMILY, config.FONTS['size_large'])
    FONT_TITLE = (FONT_FAMILY, config.FONTS['size_title'], 'bold')
    FONT_HEADER = (FONT_FAMILY, config.FONTS['size_header'], 'bold')
    
    @staticmethod
    def configure_ttk_styles():
        """Configure ttk styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Button styles
        style.configure('Primary.TButton',
                       background=AppStyles.PRIMARY,
                       foreground=AppStyles.WHITE,
                       borderwidth=0,
                       focuscolor='none',
                       font=AppStyles.FONT_MEDIUM)
        style.map('Primary.TButton',
                 background=[('active', AppStyles.SECONDARY)])
        
        style.configure('Success.TButton',
                       background=AppStyles.SUCCESS,
                       foreground=AppStyles.WHITE,
                       borderwidth=0,
                       font=AppStyles.FONT_MEDIUM)
        style.map('Success.TButton',
                 background=[('active', '#229954')])
        
        style.configure('Danger.TButton',
                       background=AppStyles.DANGER,
                       foreground=AppStyles.WHITE,
                       borderwidth=0,
                       font=AppStyles.FONT_MEDIUM)
        style.map('Danger.TButton',
                 background=[('active', '#c0392b')])
        
        # Frame styles
        style.configure('Card.TFrame',
                       background=AppStyles.WHITE,
                       relief='flat',
                       borderwidth=1)
        
        # Label styles
        style.configure('Title.TLabel',
                       background=AppStyles.WHITE,
                       foreground=AppStyles.PRIMARY,
                       font=AppStyles.FONT_TITLE)
        
        style.configure('Header.TLabel',
                       background=AppStyles.WHITE,
                       foreground=AppStyles.TEXT,
                       font=AppStyles.FONT_HEADER)
        
        # Entry styles
        style.configure('TEntry',
                       fieldbackground=AppStyles.WHITE,
                       borderwidth=1,
                       relief='solid')
        
        # Treeview styles
        style.configure('Treeview',
                       background=AppStyles.WHITE,
                       foreground=AppStyles.TEXT,
                       fieldbackground=AppStyles.WHITE,
                       font=AppStyles.FONT_NORMAL)
        style.configure('Treeview.Heading',
                       background=AppStyles.PRIMARY,
                       foreground=AppStyles.WHITE,
                       font=AppStyles.FONT_MEDIUM)
        style.map('Treeview.Heading',
                 background=[('active', AppStyles.SECONDARY)])
    
    @staticmethod
    def create_card_frame(parent, **kwargs):
        """Create a styled card frame"""
        frame = tk.Frame(parent, bg=AppStyles.WHITE, relief='solid', 
                        borderwidth=1, **kwargs)
        return frame
    
    @staticmethod
    def create_title_label(parent, text, **kwargs):
        """Create a styled title label"""
        label = tk.Label(parent, text=text, bg=AppStyles.WHITE,
                        fg=AppStyles.PRIMARY, font=AppStyles.FONT_TITLE,
                        **kwargs)
        return label
    
    @staticmethod
    def create_header_label(parent, text, **kwargs):
        """Create a styled header label"""
        label = tk.Label(parent, text=text, bg=AppStyles.WHITE,
                        fg=AppStyles.TEXT, font=AppStyles.FONT_HEADER,
                        **kwargs)
        return label
    
    @staticmethod
    def create_button(parent, text, command, style='Primary.TButton', **kwargs):
        """Create a styled button"""
        button = ttk.Button(parent, text=text, command=command,
                          style=style, **kwargs)
        return button