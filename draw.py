import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, font, PhotoImage, messagebox, simpledialog
from PIL import ImageGrab, Image, ImageTk, UnidentifiedImageError
from io import BytesIO
from platform import system
import subprocess
import os
import time
from datetime import datetime, timedelta
import operator
from threading import Thread
import webbrowser
import math

class Window(tk.Tk):
    def __init__(self):
        super().__init__()

        # apps logo
        try:
            LOGO = PhotoImage(file='logo.png')
            self.iconphoto(False, LOGO)
        except Exception:
            pass

        # drawing variables
        self.current_mode = 'draw'
        self.last_mode = 'draw'
        # output (draw/erase) sizes
        self.output_size, self.eraser_size, self.tool_width = tk.IntVar(), tk.IntVar(), tk.IntVar()
        self.output_size.set(3)
        self.eraser_size.set(5)
        self.eraser_current, self.draw_current = 1, 1
        self.output_predefined_sizes, self.eraser_predefined_sizes = (2, 3, 5, 7), (3, 5, 6, 9)
        self.predefined_sizes_dict = {'draw': (self.output_predefined_sizes, self.output_size),
                                      'erase': (self.eraser_predefined_sizes, self.eraser_size)}
        self.previous_point = [0, 0]

        self.mp_mouse, self.mp_keys = tk.BooleanVar(), tk.BooleanVar()
        self.mp_mouse.set(True), self.mp_keys.set(True)
        self.mp_mr = tk.DoubleVar()
        self.mp_mr.set(1)
        self.move_px = tk.StringVar()
        self.move_px.set(10)
        self.move_single_ar, self.move_single_ms = tk.BooleanVar(), tk.BooleanVar()
        self.move_single_ar.set(True)

        # draw/erase options
        self.pen_types = 'line', 'round', 'square', 'arrow', 'diamond'
        self.pen_type, self.shape_var = tk.StringVar(), tk.StringVar()
        self.pen_type.set(self.pen_types[0])
        self.eraser_color = 'white'
        self.eraser_bg = tk.BooleanVar()
        self.eraser_bg.set(True)
        # text variables
        self.font_var, self.size_var, fonts = tk.StringVar(), tk.IntVar(), font.families()
        self.typeface_var = tk.StringVar()
        self.text_once, self.shape_once = tk.BooleanVar(), tk.BooleanVar()
        self.tp_values = '', 'underline', 'bold'
        self.font_var.set('Arial'), self.size_var.set(16)
        self.add_mode = False
        self.text_angle_var = tk.IntVar()
        # lines mannagement and options
        self.last_items = []
        self.smooth_line = tk.BooleanVar()
        self.smooth_line.set(True)
        self.text_once.set(True)
        self.connected_lines = tk.BooleanVar()
        self.px2, self.py2 = 0, 0
        self.dotted_line_var = tk.BooleanVar()
        self.dot_size, self.dot_space = '', ''
        self.points_mode = tk.StringVar()
        self.points_mode.set('drag')
        self.main_mods = 'draw', 'erase', 'hover', 'eyedropper'
        self.line_group, self.line_groups = [], []
        self.connect_fl = tk.BooleanVar()
        # general / otheres
        self.color, self.paint_color, self.paint_second_color = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.color.set('black'), self.paint_color.set('black'), self.paint_second_color.set('black')
        self.fs_var = False
        self.all_lines_list, self.images_list = [], []
        self.relief_var_canvas, self.relief_var_buttons = tk.StringVar(), tk.StringVar()
        self.relief_var_canvas.set('flat'), self.relief_var_buttons.set('ridge')
        self.relief_values = 'ridge', 'sunken', 'flat', 'groove'
        self.move_dict = {'right': [10, 0], 'left': [-10, 0], 'up': [0, -10], 'down': [0, 10]}
        self.predefined_bg = 'SystemButtonFace'
        self.hrz_s_var, self.vrt_s_var = tk.BooleanVar(), tk.BooleanVar()
        self.erase_skipw = tk.BooleanVar()
        self.ps_mode = tk.StringVar()
        self.ps_mode.set('ps')
        # shapes variables
        self.xy_var = tk.DoubleVar()
        self.xy_var.set(0.75)
        self.direction_var = tk.StringVar()
        self.direction_var.set('Top')
        self.shapes_list = 'circle', 'square', 'arc', 'tringle', 'chord', 'pieslice', 'rectangle', 'pentagon', 'right triangle', 'hexagon', 'octagon', 'star', 'heart'
        self.shape_var.set(self.shapes_list[0])
        self.last_smode = 'circle'

        # New features variables
        self.magnet_var = tk.BooleanVar()
        self.grid_active = tk.BooleanVar()
        self.snap_to_grid = tk.BooleanVar()
        self.grid_spacing = 50
        self.bitmaps = ['error', 'gray75', 'gray50', 'gray25', 'gray12', 'hourglass', 'info', 'questhead', 'question', 'warning']
        self.selected_bm = tk.StringVar()
        self.selected_bm.set(self.bitmaps[0])
        self.bitmap_active, self.bit_once = tk.BooleanVar(), tk.BooleanVar()
        self.draw_time, self.erase_time, self.hover_time = 0, 0, 0
        self.time_dict = {'draw': self.draw_time, 'erase': self.erase_time, 'hover': self.hover_time}
        self.us_active = False
        self.last_active = ''
        self.deactivate_color = tk.BooleanVar()
        self.mp_x, self.mp_y = 0, 0
        self.undo_count, self.redo_count, self.clear_count = 0, 0, 0

        # menus varibales
        self.output_mode_var = tk.StringVar()
        self.output_cords_var = tk.StringVar()
        self.output_shape_var = tk.StringVar()

        # window design
        self.title('Ariel\'s / Egon Draw')
        self.style = ttk.Style()
        self.style.theme_use('vista')

        frame_c = '#d9d9d9'
        if system().lower() == 'macos':
            frame_c = '#ffffff'

        # window widgets
        frame_font = 'arial 8 underline'
        
        # Initialize Hints Dictionary
        self.tool_hints = {
            'line': 'Click and drag to draw freehand lines.',
            'erase': 'Click and drag to erase objects.',
            'square': 'Click and drag to draw a rectangle.',
            'round': 'Click and drag to draw an oval.',
            'diamond': 'Click and drag to draw a polygon.',
            'hover': 'Hover over objects to see properties. Click to select.',
            'drag': 'Click and drag to move the view.',
            'straight': 'Click start and end points for straight lines.',
            'centered': 'Click center point, then drag out.',
            'text': 'Click anywhere to add text.',
            'bit': 'Click to place the bitmap.',
            'shape': 'Click and drag to place the shape.'
        }

        self.buttons_frame = tk.Frame(self)
        self.canvas_frame = tk.Frame(self)
        self.status_bar = ttk.Frame(self, relief='sunken')
        self.canvas = tk.Canvas(self.canvas_frame, cursor='pencil', bd=1, bg='white')

        title_list = 'Select mode', 'Lines output', 'Select shape', 'Select colors', 'File management', 'Select sizes', 'Write', 'Edit', 'Add shape', 'Dash Size/Space'
        draw_erase_title, lines_title, shapes_title, color_title, file_title, sizes_title, write_title, edit_title, ashape_title, dash_title  \
            = [tk.Label(self.buttons_frame, text=text, font=frame_font, bg=frame_c) for text in title_list]
        self.topframes = [tk.Frame(self.buttons_frame, bd=1, bg='light grey') for x in range(10)]
        draw_erase_frame, shapes_frame, color_frame, file_frame, sizes_frame, write_frame, edit_frame, ashape_frame, lines_frame, dash_frame = self.topframes
        
        # New frames
        self.bit_frame = tk.Frame(self.buttons_frame)
        self.bonus_frame = tk.Frame(self.buttons_frame)

        draw = tk.Button(draw_erase_frame, text='Draw', command=self.draw_erase, borderwidth=1, bg='grey')
        eraser = tk.Button(draw_erase_frame, text='Eraser', command=lambda: self.draw_erase('erase'),
                                borderwidth=1)
        self.hover_button = tk.Button(draw_erase_frame, text='Hover', command=self.hover_mouse, borderwidth=1)

        hold_move = tk.Button(lines_frame, command=self.line_placing, text='Drag', bd=1)
        straight = tk.Button(lines_frame, command=lambda: self.line_placing('straight'), text='Straight lines', bd=1)
        from_same = tk.Button(lines_frame, command=lambda: self.line_placing('centered'), text='Centered from point',
                              bd=1)

        pencil = tk.Button(shapes_frame, text='Pencil', command=self.draw_tool, borderwidth=1)
        square_draw = tk.Button(shapes_frame, text='Marker', command=lambda: self.draw_tool('square'),
                                     borderwidth=1)
        round_draw = tk.Button(shapes_frame, text='Pen', command=lambda: self.draw_tool('round'), borderwidth=1)
        diamond_draw = tk.Button(shapes_frame, text='Brush', command=lambda: self.draw_tool('diamond'), borderwidth=1)

        self.draw_size_box = ttk.Combobox(sizes_frame, width=5, textvariable=self.output_size, state='normal')
        self.erase_size_box = ttk.Combobox(sizes_frame, width=5, textvariable=self.eraser_size, state='normal')

        color_button = tk.Button(color_frame, text='Color', command=self.color_select, borderwidth=1)
        second_color = tk.Button(color_frame, text='Secondary color',
                                      command=lambda: self.color_select('second'), borderwidth=1)
        deafult_bg = tk.Button(color_frame, text='Canvas color', command=self.canvas_color, bd=1)
        self.change_colorb = tk.Button(color_frame, text='Edit color', command=self.change_color, borderwidth=1)
        self.eyedropper_button = tk.Button(color_frame, text='Pick Color', command=self.toggle_eyedropper, borderwidth=1)

        self.add_text = tk.Button(write_frame, text='Add text', command=self.add_special, borderwidth=1)
        self.font_combo = ttk.Combobox(write_frame, width=15, textvariable=self.font_var, state='readonly',
                                       values=fonts)
        self.font_size = ttk.Combobox(write_frame, width=5, textvariable=self.size_var, state='readonly',
                                      style='TCombobox', values=tuple(range(8, 80, 2)))
        self.typefaces = ttk.Combobox(write_frame, width=5, values=self.tp_values, state='readonly',
                                      style='TCombobox', textvariable=self.typeface_var)
        self.text_angle = ttk.Scale(write_frame, from_=0, to=360, variable=self.text_angle_var)

        save_image = tk.Button(file_frame, text='Save as image', command=self.save, borderwidth=1)
        upload_image = tk.Button(file_frame, text='Upload image', command=self.upload, borderwidth=1)
        self.save_script = tk.Button(file_frame, text='Save PostScript', command=self.save_ps, borderwidth=1)

        erase_canvas = tk.Button(edit_frame, text='Erase canvas', command=lambda: self.erase_all,
                                      borderwidth=1)
        undo = tk.Button(edit_frame, text='Undo', command=self.undo, borderwidth=1)
        self.redo_button = tk.Button(edit_frame, text='Redo', command=self.redo, borderwidth=1, state=tk.DISABLED)
        self.magnet_button = tk.Button(edit_frame, text='Magnet', command=self.magnet, bd=1)
        self.grid_button = tk.Button(edit_frame, text='Grid', command=self.toggle_grid, bd=1)

        im = Image.open('settings.png')
        ph = ImageTk.PhotoImage(im, master=self)
        options_button = tk.Button(self.buttons_frame, image=ph, command=self.options, relief='flat')
        options_button.image = ph
        
        # --- Professional Status Bar ---
        # Styles
        self.style.configure('StatusBar.TFrame', background='#f0f0f0')
        self.style.configure('StatusBar.TLabel', background='#f0f0f0', foreground='black', font=('Segoe UI', 9))
        
        self.status_bar = ttk.Frame(self, style='StatusBar.TFrame')
        
        # 1. System Status (Left)
        self.status_label = ttk.Label(self.status_bar, text="Ready", style='StatusBar.TLabel', padding=(10, 2))
        self.status_label.pack(side='left')
        
        # Separator
        tk.Label(self.status_bar, text="|", bg='#f0f0f0', fg='#a0a0a0', font=('Arial', 12)).pack(side='left', padx=2)

        # 2. Current Tool (Left)
        self.tool_status = ttk.Label(self.status_bar, text="Tool: Pencil", style='StatusBar.TLabel', padding=(5, 2))
        self.tool_status.pack(side='left')

        # 3. Size Indicator (Left)
        self.size_status = ttk.Label(self.status_bar, text="Size: 5px", style='StatusBar.TLabel', padding=(5, 2))
        self.size_status.pack(side='left')

        # 4. Context Hints (Center - Expands)
        self.hint_label = ttk.Label(self.status_bar, text="Click and drag to start drawing.", style='StatusBar.TLabel', anchor='center')
        self.hint_label.pack(side='left', fill='x', expand=True, padx=10)

        # 5. Canvas Info (Right)
        self.canvas_info = ttk.Label(self.status_bar, text="Size: -- x --", style='StatusBar.TLabel', padding=(5, 2))
        self.canvas_info.pack(side='right', padx=10)

        # Separator
        tk.Label(self.status_bar, text="|", bg='#f0f0f0', fg='#a0a0a0', font=('Arial', 12)).pack(side='right', padx=2)

        # 6. Coordinates (Right)
        self.cords_label = ttk.Label(self.status_bar, text='Ln 1, Col 1', style='StatusBar.TLabel', width=15, anchor='e', padding=(5, 2))
        self.cords_label.pack(side='right', padx=5)

        # Cleanups
        self.closest_item = self.hint_label # Reuse hint label for item details if needed, or keep separate.


        self.shape_button = tk.Button(ashape_frame, text='Add shape', command=lambda: self.add_special('shape'), bd=1)
        self.shapes_combo = ttk.Combobox(ashape_frame, width=10, textvariable=self.shape_var, state='readonly',
                                    values=self.shapes_list)
        width_size_frame = tk.Frame(ashape_frame)
        self.shapes_size = tk.Entry(width_size_frame, bd=1, width=4)
        self.shapes_width = tk.Entry(width_size_frame, bd=1, width=4)
        self.shapes_width.insert(tk.END, 2), self.shapes_size.insert(tk.END, 10)

        dash_shape_title = tk.Label(dash_frame, text='For shapes', font='arial 8', bg=frame_c)
        dash_shape_frame = tk.Frame(dash_frame)
        self.shape_dz, self.shape_dp = tk.Entry(dash_shape_frame, width=4), tk.Entry(dash_shape_frame, width=4)
        dash_line_title = tk.Label(dash_frame, text='For line', font='arial 8', bg=frame_c)
        dash_line_frame = tk.Frame(dash_frame)
        self.line_dz, self.line_dp = tk.Entry(dash_line_frame, width=4), tk.Entry(dash_line_frame, width=4)

        self.bit_title = tk.Label(self.buttons_frame, text='Add bitmap', font=frame_font, bg=frame_c)
        self.bit_button = tk.Button(self.bit_frame, text='Add BitMap', command=lambda: self.add_special('bit'), bd=1)
        self.bit_combo = ttk.Combobox(self.bit_frame, width=10, textvariable=self.selected_bm, state='readonly',
                                      values=self.bitmaps)

        self.usage_button = tk.Button(self.bonus_frame, text='Usage stats', command=self.usage_stats, bd=1)
        self.github_button = tk.Button(self.bonus_frame, text='Github', command=lambda : webbrowser.open('https://github.com/Ariel4545/draw'), bd=1)

        im = Image.open('settings.png')
        ph = ImageTk.PhotoImage(im, master=self)
        self.options_button = tk.Button(self.buttons_frame, image=ph, command=self.options, relief='flat')
        self.options_button.image = ph

        # placing widgets
        # placing widgets
        self.buttons_frame.pack(side='top', fill='x')
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)
        self.status_bar.pack(side='bottom', fill='x')

        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # groups of widgets
        self.sheet_shapes = {'line': pencil, 'square': square_draw, 'round': round_draw, 'diamond': diamond_draw}
        self.sheet_tools = {'erase': eraser, 'draw': draw, 'hover': self.hover_button, 'eyedropper': self.eyedropper_button}
        self.placing_modes = {'drag': hold_move, 'straight': straight, 'centered': from_same}
        self.buttons_list = (draw, eraser, pencil, square_draw, round_draw, diamond_draw, color_button, second_color, deafult_bg,
                             save_image, upload_image, erase_canvas, self.add_text, options_button, self.hover_button,
                             undo, self.redo_button, hold_move, straight, from_same, self.magnet_button, self.grid_button, self.change_colorb,
                             self.eyedropper_button, self.bit_button, self.usage_button, self.github_button)
        self.text_list = draw_erase_title, lines_title, shapes_title, color_title, file_title, self.cords_label, sizes_title, write_title, edit_title, ashape_title, dash_title, dash_shape_title, dash_line_title, self.closest_item, self.bit_title
        self.fgbg_list = self.buttons_list + self.text_list
        self.frames = self.buttons_frame, self.canvas_frame, self.status_bar, width_size_frame, dash_shape_frame, dash_line_frame, self.bit_frame, self.bonus_frame


        # activate UI

        self.app_menu = tk.Menu(self)
        self.modes_menu, self.lines_menu, self.sizes_menu, self.shapes_menu, self.color_menu, self.file_menu, self.write_menu, \
            self.edit_menu, self.ashape_menu, self.dash_menu = [
            tk.Menu(self.app_menu, tearoff=False) for x in range(10)]

        self.plc_mode = tk.StringVar()
        self.plc_mode.set('buttons')
        self.place_ui()


        # configuration related to UI
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<Configure>', self.update_canvas_info) 
        # release to update the last point of drawing variable to not make connected lines
        self.canvas.bind('<ButtonRelease-1>', self.paint)
        self.canvas.bind('<MouseWheel>', self.change_size_sc)
        self.draw_size_box['values'] = self.output_predefined_sizes
        self.erase_size_box['values'] = self.eraser_predefined_sizes
        self.bind('<Left>', lambda e: self.move_paint(key='left'))
        self.bind('<Right>', lambda e: self.move_paint(key='right'))
        self.bind('<Up>', lambda e: self.move_paint(key='up'))
        self.bind('<Down>', lambda e: self.move_paint(key='down'))
        self.bind('<Control-Key-z>', self.undo)
        self.bind('<Motion>', self.cords)
        self.draw_size_box.bind('<<ComboboxSelected>>', lambda event: self.change_size())
        self.erase_size_box.bind('<<ComboboxSelected>>', lambda event: self.change_size())
        self.draw_size_box.current(1), self.erase_size_box.current(1)
        self.font_combo.current(fonts.index('Arial'))
        self.shapes_combo.bind('<<ComboboxSelected>>', self.update_shape_ui)
        self.bind('<F11>', self.fullscreen)
        
        self.add_special_buttons = {'text': self.add_text, 'bit': self.bit_button, 'shape': self.shape_button,
                                    'magnet': self.magnet_button}

        # function calling
        self.effective_size()
        self.set_width()
        self.draw_erase()
        self.draw_tool()
        self.line_placing(self.points_mode.get())
        self.update_mp()
        Thread(target=self.stopwatch, daemon=True).start()

        # aditional
        self.scroll = ttk.Scrollbar(self.canvas_frame, orient='horizontal')
        self.scroll2 = ttk.Scrollbar(self.canvas_frame, orient='vertical')
        self.xy_ratio_sc = ttk.Scale(ashape_frame, from_=0.1, to=0.9, variable=self.xy_var, value=0.75)
        self.arc_frame = tk.Frame(ashape_frame)
        self.start_degree_box, self.arc_extent = tk.Entry(self.arc_frame, width=5), tk.Entry(self.arc_frame, width=5)
        self.start_degree_box.insert(tk.END, 0), self.arc_extent.insert(tk.END, 90)
        self.custom_title = tk.Label(ashape_frame, font='arial 8')
        self.shape_direction = ttk.Combobox(ashape_frame, values=('Top', 'Bottom'), textvariable=self.direction_var,
                                            width=10)


        # Drop-down menu's tabs initial creation (without placing)
        self.app_menu.add_cascade(label='Output mode', menu=self.modes_menu)
        self.app_menu.add_cascade(label='Line types', menu=self.lines_menu)
        # self.app_menu.add_cascade(label='Tools sizes', menu=self.sizes_menu)
        self.app_menu.add_cascade(label='Tool shapes', menu=self.shapes_menu)
        self.app_menu.add_cascade(label='Tools colors', menu=self.color_menu)
        self.app_menu.add_cascade(label='Files', menu=self.file_menu)
        # self.app_menu.add_cascade(label='label output', menu=self.write_menu)
        self.app_menu.add_cascade(label='Others', menu=self.edit_menu)
        # self.app_menu.add_cascade(label='Shape output', menu=self.ashape_menu)
        # self.app_menu.add_cascade(label='Dash options', menu=self.dash_menu)
        self.app_menu.add_cascade(label='Settings', command=self.options)

        # menus foundation
        # modes_menu, lines_menu, sizes_menu, shapes_menu, color_menu, file_menu, write_menu, edit_menu, ashape_menu, dash_menu = [
        #     tk.Menu(self.app_menu) for x in range(10)]

        # modes menu items
        self.modes_menu.add_checkbutton(label='draw', command=self.draw_erase, variable=self.output_mode_var,
                                        onvalue='draw')
        self.modes_menu.add_checkbutton(label='erase', command=lambda: self.draw_erase('erase'),
                                        variable=self.output_mode_var, onvalue='erase')
        self.modes_menu.add_checkbutton(label='hover', command=self.hover_mouse, variable=self.output_mode_var,
                                        onvalue='hover')
        # lines menu items
        self.lines_menu.add_checkbutton(label='Drag', command=self.line_placing, variable=self.output_cords_var,
                                        onvalue='drag')
        self.lines_menu.add_checkbutton(label='Straight', command=lambda: self.line_placing('straight'),
                                        variable=self.output_cords_var, onvalue='straight')
        self.lines_menu.add_checkbutton(label='Centered', command=lambda: self.line_placing('centered'),
                                        variable=self.output_cords_var, onvalue='centered')
        # sizes items
        # tool shapes items
        self.shapes_menu.add_checkbutton(label='Pencil', command=self.draw_tool, variable=self.output_shape_var,
                                         onvalue='line')
        self.shapes_menu.add_checkbutton(label='Marker', command=lambda: self.draw_tool('square'),
                                         variable=self.output_shape_var, onvalue='square')
        self.shapes_menu.add_checkbutton(label='Pencil', command=lambda: self.draw_tool('round'),
                                         variable=self.output_shape_var, onvalue='round')
        # color buttons
        self.color_menu.add_cascade(label='Main color', command=self.color_select)
        self.color_menu.add_cascade(label='Secondary color', command=lambda: self.color_select('second'))
        self.color_menu.add_cascade(label='Canvas color', command=self.canvas_color)
        # files buttons
        self.file_menu.add_cascade(label='Save as image', command=self.save)
        self.file_menu.add_cascade(label='Upload image', command=self.upload)
        self.file_menu.add_cascade(label='Save PostScript', command=self.save_ps)
        # edit buttons
        self.edit_menu.add_cascade(label='Erase canvas', command=lambda: self.erase_all)
        self.edit_menu.add_cascade(label='Undo', command=self.undo)
        self.edit_menu.add_cascade(label='Redo', command=self.redo, state=tk.DISABLED)
        self.edit_menu.add_cascade(label='Magnet', command=self.magnet)

    def set_width(self):
        if self.current_mode == 'draw':
            self.tool_width.set(self.output_size.get())
        elif self.current_mode == 'erase':
            self.tool_width.set(self.eraser_size.get())
        
        if hasattr(self, 'size_status'):
            self.size_status.configure(text=f"Size: {self.tool_width.get()}px")

    def change_size(self):
        self.set_width() # Call set_width to update tool_width and size_status

    def update_canvas_info(self, event=None):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas_info.configure(text=f"Size: {width} x {height}")
        if hasattr(self, 'size_status'):
            self.size_status.configure(text=f"Size: {self.tool_width.get()}px")

    def button_mannagment(self, tool):
        if tool in self.pen_types:
            mode_dict = self.sheet_shapes
        elif tool in self.main_mods:
            mode_dict = self.sheet_tools
        else:
            mode_dict = self.placing_modes

        for widget in mode_dict.values():
            widget.configure(bg=self.predefined_bg)
        mode_dict[tool].configure(bg='grey')

    def draw_tool(self, tool='line'):
        self.output_shape_var.set(tool)
        self.pen_type.set(tool)
        self.button_mannagment(tool)
        if self.last_mode in ('draw', 'erase') and (self.add_mode or self.magnet_var.get()) and self.last_active:
            self.deactivate(self.last_active)

    def draw_erase(self, mode='draw'):
        self.output_mode_var.set(mode)
        if self.add_mode:
            self.deactivate(mode=self.add_mode)
        if self.magnet_var.get():
            self.deactivate(mode='magnet')
        self.hover_mouse(False)
        self.unbind('<ButtonRelease-1>')
        self.line_placing(self.points_mode.get())


        if mode == 'draw':
            self.canvas.configure(cursor='pencil')
            self.color.set(self.paint_color.get())
            self.tool_width.set(self.output_size.get())
        else:
            self.canvas.configure(cursor=tk.DOTBOX)
            self.color.set(self.eraser_color)
            self.tool_width.set(self.eraser_size.get())
            
        if hasattr(self, 'size_status'):
             self.size_status.configure(text=f"Size: {self.tool_width.get()}px")

        self.button_mannagment(mode)
        self.current_mode = mode
        self.set_width()

    def save(self):
        # save image by screenshoting
        image_name = filedialog.asksaveasfilename(
            filetypes=(('PNG', '*.png'), ('JPG', '*.jpg'), ('JPEG Files', '*.jpeg')),
            defaultextension='.jpg')
        self.attributes('-topmost', True)
        sp_x = 0
        x = self.winfo_rootx() + self.canvas.winfo_x() + sp_x
        y = self.winfo_rooty() + self.canvas.winfo_y() + self.buttons_frame.winfo_height()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        image = ImageGrab.grab().crop((x, y, x1, y1))
        image.save(image_name)
        self.attributes('-topmost', False)

    def save_ps(self):
        file_name = filedialog.asksaveasfilename(defaultextension='.ps')
        if file_name:
            self.canvas.postscript(file=file_name, colormode='color')
            if self.ps_mode.get() == 'pdf':
                try:
                    process = subprocess.Popen(['ps2pdf', 'tmp.ps', 'result.pdf'], shell=True)
                    process.wait()
                    os.remove(file_name)
                except FileNotFoundError:
                    messagebox.showerror('Error', 'ps2pdf not found. Please install it to save as PDF.')

    def upload(self):
        global img_array, image, image_tk
        # load image into the canvas
        self.convert_image = filedialog.askopenfilename()
        if self.convert_image:
            try:
                image = Image.open(self.convert_image)
                image_tk = PhotoImage(file=self.convert_image)
                image_x = (self.canvas.winfo_width() // 2) - (image.width // 2)
                image_y = (self.canvas.winfo_height() // 2) - (image.height // 2)
                canvas_image = self.canvas.create_image(image_x, image_y, image=image_tk, anchor=tk.NW)
                self.images_list.append(canvas_image)
            except (UnidentifiedImageError, OSError):
                messagebox.showerror('Error', 'Could not open image file.')


    def undo(self, event=None, custom_index=-1):
        items = self.canvas.find_all()
        if items:
            last_group = []
            if self.points_mode.get() == 'drag':
                if self.line_groups:
                    line_group = self.line_groups[-1]
                    loop_range = len(line_group) + 1
                    for line in range(1, loop_range):
                        ind = line * -1
                        last_group.append(items[ind])
                        self.canvas.delete(items[ind])
                    del self.line_groups[-1]
                    self.last_items.append(last_group)
            else:
                try:
                    self.canvas.delete(items[custom_index])
                    last_group.append(items[custom_index])
                except IndexError:
                    pass
            self.redo_button.configure(state=tk.ACTIVE)
            self.undo_count += 1
            if self.us_active: self.update_usage_ui()

    def redo(self):
        if self.last_items:
            item = self.last_items[-1]
            self.redo_count += 1
            if self.us_active: self.update_usage_ui()


    def line_placing(self, mode='drag'):
        self.output_cords_var.set(mode)
        self.initial_point = True
        self.points_mode.set(mode)
        self.button_mannagment(mode)

        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

        if mode == 'drag':
            self.canvas.bind('<B1-Motion>', self.paint)
            if not(self.connected_lines.get()):
                self.canvas.bind('<ButtonRelease-1>', self.paint)
            # variable and binds to make an updated "prevoius point"
        elif mode == 'straight':
            self.canvas.bind('<ButtonRelease-1>', self.special_paint_cords)
            # on click take starting pos and on the seoond makes the line

        # seperated to make some values/variables default after they're changed for 'centered' mode
        if mode == 'centered':
            # starting pos change rarely
            cursor = self.canvas['cursor']
            self.canvas.bind('<ButtonRelease-1>', lambda e: self.special_paint_cords(cursor=cursor))
            self.canvas.configure(cursor='crosshair')
        else:
            # self.canvas.configure(cursor='pen')
            pass

    def paint(self, event=None):
        # paint in 3 shapes and many other options
        if not self.current_mode == 'hover' or self.line and self.points_mode.get() == 'straight':

            self.last_items.clear()

            # eraser usage through the paint function
            s_color = self.paint_second_color.get()
            if self.current_mode == 'erase':
                s_color = self.eraser_color

            if self.previous_point != [0, 0]:
                # pen shapes conditions
                if self.pen_type.get() == 'line':
                    dl_size, sl_space, dl_tup = self.line_dz.get(), self.line_dp.get(), ()
                    if isinstance(dl_size, str) and dl_size.isdigit(): dl_size = int(dl_size)
                    if isinstance(sl_space, str) and sl_space.isdigit(): sl_space = int(sl_space)
                    if isinstance(dl_size, int) and isinstance(sl_space, int): dl_tup = (dl_size, sl_space)

                    self.line = self.canvas.create_line(self.previous_point[0], self.previous_point[1], self.x,
                                                        self.y, dash=dl_size,
                                                        fill=self.color.get(), width=self.tool_width.get(),
                                                        smooth=self.smooth_line.get())
                elif self.pen_type.get() == 'square' or self.pen_type.get() == 'round' or self.pen_type.get() == 'diamond':

                    if self.pen_type.get() == 'square':
                        self.line = self.canvas.create_polygon(self.p_x, self.p_y, self.p_x, self.y, self.x, self.sq_y,
                                                               fill=s_color,
                                                               outline=self.color.get())
                    elif self.pen_type.get() == 'round':
                        self.line = self.canvas.create_oval(self.p_x, self.p_y, self.sq_x, self.sq_y, fill=s_color,
                                                            outline=self.color.get())
                    elif self.pen_type.get() == 'diamond':
                        r = self.tool_width.get()
                        self.line = self.canvas.create_polygon(self.x, self.y - r, self.x + r, self.y, self.x, self.y + r, self.x - r, self.y, fill=s_color, outline=self.color.get())

                self.all_lines_list.append(self.line)
                self.line_group.append(self.line)
                if event.type == tk.EventType.ButtonRelease:
                    self.line_groups.append(self.line_group)
        if (self.points_mode.get() == 'drag') and not self.connected_lines.get():
            self.previous_point = [self.x, self.y]
            self.line = ''

            if event.type == tk.EventType.ButtonRelease:
                if self.connect_fl.get():
                    # connection between the first and the last line
                    initial_x, initial_y, x1, y1 = self.canvas.bbox((self.line_group[0]))
                    self.canvas.coords(self.line_group[0], initial_x, initial_y, self.x, self.y)
                self.line_group = []
                if self.us_active: self.update_usage_ui()

        elif self.points_mode.get() == 'straight':
            if event.type == tk.EventType.ButtonRelease:
                self.canvas.bind('<ButtonRelease-1>', self.special_paint_cords)
            elif event.type == tk.EventType.Motion:
                # gets the work sone by updating original (bit harder)
                item = self.canvas.find_all()[-1]
                inx, iny, x, y = self.canvas.bbox(item)
                self.canvas.coords(item, inx, iny, self.x, self.y)
                # gets the work done by deleting the last one but can cause some inconviniences
                # self.undo(-2)
                '''+ needs to choose method and make that after a usage the function will be called back'''

        if event.type == '5' and self.points_mode.get() != 'centered':
            self.previous_point = [0, 0]
            '''+ need to update prev point after you done with centered mode'''

    def move_paint(self, key):
        # move paint a bit depending on the arrow keys
        item = ''
        self.movep_x, self.movep_y = None, None
        # indicator for keys method
        if isinstance(key, str):
            move_all = self.move_single_ar.get()
            self.movep_x, self.movep_y = self.move_dict[key]
            if self.move_px.get().isdigit():
                try:
                    # formula for moving the drawing using arrow keys
                    self.movep_x, self.movep_y = self.movep_x * int(self.move_px.get()) // 10, self.movep_y * int(self.move_px.get()) // 10
                    print(self.movep_x, self.movep_y)
                except TypeError:
                    pass
        else:
            move_all = self.move_single_ms.get()
            if key.type == tk.EventType.ButtonPress:
                # for another function with the same bind
                self.mp_x, self.mp_y = key.x, key.y
            else:
                # formula for moving the drawing relative to the mouse pos (at the start and at the end)
                self.movep_x, self.movep_y = int((self.x - self.mp_x) // self.mp_mr.get()), int((
                            self.y - self.mp_y) // self.mp_mr.get())


        if move_all:
            for l in self.all_lines_list:
                self.canvas.move(l, self.movep_x, self.movep_y)
            for img in self.images_list:
                self.canvas.move(img, self.movep_x, self.movep_y)
        else:
            '''+ optional - make the borders more clear \\ detect them better'''
            item = self.canvas.find_closest(self.x, self.y)
            if item:
                for group in self.line_groups:
                    if item[0] in group:
                        item = group

                if isinstance(item, (list, tuple)) and len(item) > 1:
                    for line in item:
                        self.canvas.move(line, self.movep_x, self.movep_y)
                else:
                    self.canvas.move(item[0], self.movep_x, self.movep_y)


    def change_size(self):
        # change general size (for the variable that mannages the draw/erase size)
        if self.current_mode == 'draw':
            size = self.output_size.get()
            drawt_list = list(map(int, list(self.draw_size_box['values'])))
            try:
                self.draw_current = drawt_list.index(size)
                self.draw_size_box.current(drawt_list.index(size))
            except ValueError:
                pass
        elif self.current_mode == 'erase':

            size = self.eraser_size.get()
            eraser_list = list(map(int, list(self.erase_size_box['values'])))
            try:
                self.eraser_current = eraser_list.index(size)
                self.erase_size_box.current(eraser_list.index(size))
            except ValueError:
                pass

        # global size var for both erase and draw, bnecause erase it's hust a draw with different color and variables
        self.tool_width.set(size)

    def change_size_sc(self, event):
        if isinstance(event, int):
            value = event
        else:
            # mouse wheel events
            if (event.num == 5 or event.delta == -120):
                value = -1
            else:
                value = 1

        try:
            if self.current_mode == 'draw':
                self.draw_size_box.current(self.draw_current + value)
                self.draw_current += value

            elif self.current_mode == 'erase':
                self.erase_size_box.current(self.eraser_current + value)
                self.eraser_current += value
            self.change_size()
        except Exception as e:
            print(e)

    def button_mannagment(self, tool):
        # configure the button that is preseed to be sunken and the others to raise
        for i in self.sheet_tools:
            if i != tool:
                self.sheet_tools[i].configure(relief='raise', bg='SystemButtonFace')
            else:
                self.sheet_tools[i].configure(relief='sunken', bg='grey')
                if hasattr(self, 'tool_status'):
                    self.tool_status.configure(text=f"Tool: {tool.capitalize()}")
                if hasattr(self, 'hint_label') and hasattr(self, 'tool_hints'):
                    hint = self.tool_hints.get(tool, "")
                    self.hint_label.configure(text=hint)

    def color_select(self, mode='main'):
        color = colorchooser.askcolor(title='Select a color')

        if color[1]:
            if mode == 'main':
                self.paint_color.set(color[1])
            else:
                self.paint_second_color.set(color[1])
            if self.current_mode == 'draw':
                self.draw_erase()

    def update_canvas_info(self, event=None):
        if hasattr(self, 'canvas_info'):
            self.canvas_info.configure(text=f"Size: {self.canvas.winfo_width()} x {self.canvas.winfo_height()}")

    def cords(self, event):
        # some dynamic x,y capture and calculations
        self.x, self.y = event.x, event.y
        self.cords_label.configure(text=f'X: {self.x}, Y: {self.y}')

        self.p_x, self.p_y = self.x - self.tool_width.get(), self.y - self.tool_width.get()
        self.sq_x, self.sq_y = self.x + self.tool_width.get(), self.y + self.tool_width.get()

    def special_paint_cords(self, event=None, cursor=False):
        if (self.points_mode.get() == 'straight') and event.type == tk.EventType.ButtonRelease or self.initial_point:
            self.previous_point, self.initial_point = (self.x, self.y), False

        if cursor:
            self.canvas.configure(cursor=cursor)

        self.canvas.unbind('<ButtonRelease-1>')
        self.canvas.bind('<ButtonRelease-1>', self.paint)

    def erase_all(self):
        d = False
        if not (self.erase_skipw.get()):
            if messagebox.askyesno('Draw', 'are you sure that you want to erase the canvas?'):
                d = True
        else:
            d = True
        if d:
            self.canvas.delete('all')
            self.clear_count += 1
            self.line_groups.clear()
            if self.us_active: self.update_usage_ui()

    def add_special(self, mode='text'):
        self.last_active, self.text_msg = mode, ''
        proceed = False
        if mode == 'text':
            self.text_msg = tk.simpledialog.askstring('Egon draw', 'Enter the text')
            if self.text_msg:
                self.add_mode = 'text'
                self.add_text.configure(bg='grey', text='Edit text')
                proceed = True
        elif mode == 'bit':
            proceed = True
            self.bit_button.configure(bg='grey')
            self.add_mode = 'bit'
        else:
            if self.shape_var.get():
                self.add_mode = 'shape'
                proceed = True
                self.shape_button.configure(bg='grey')

        if proceed:
            self.last_mode = self.current_mode
            self.current_mode = 'hover'
            self.canvas.configure(cursor='center_ptr')
            self.button_mannagment('hover')
            self.canvas.bind('<ButtonRelease-1>', lambda e: self.active_add(mode=mode))
            self.canvas.unbind('<B1-Motion>')
            self.bind('<Escape>', lambda e: self.deactivate(mode=mode))

    def active_add(self, event=None, mode='text'):
        if mode == 'text':
            if self.text_msg:
                self.canvas.create_text(self.x, self.y, text=self.text_msg,
                                        font=(self.font_var.get(), self.size_var.get(), self.typeface_var.get()),
                                        fill=self.paint_color.get(), angle=self.text_angle_var.get())
                if self.us_active: self.update_usage_ui()
                if self.text_once.get():
                    self.deactivate(mode=mode)

        elif mode == 'shape':
            if self.us_active: self.update_usage_ui()
            d_size, d_space, d_tup = (self.shape_dz.get()), (self.shape_dp.get()), ()
            if isinstance(d_size, str) and d_size.isdigit(): d_size = int(d_size)
            if isinstance(d_space, str) and d_space.isdigit(): d_space = int(d_space)
            if isinstance(d_space, int) and isinstance(d_size, int): d_tup = (d_size, d_space)

            width = int(self.shapes_width.get())
            size = (self.shapes_size.get())
            if size:
                if size.isdigit():
                    size = int(size)
                    p_x, p_y, sq_x, sq_y = self.p_x - size // 2,  self.p_y - size // 2, self.sq_x + size // 2, self.sq_y + size // 2
                    if self.shape_var.get() == 'rectangle':
                        # ratio between x and y (in favor of x)
                        ratio = float(self.xy_var.get())
                        xr, yr = ratio, 1 - ratio
                        p_x, p_y, sq_x, sq_y = self.p_x - size // (4*xr), self.p_y - size // (4*yr), self.sq_x + size // (4*xr), self.sq_y + size // (4*yr)


            if self.shape_var.get() == 'circle':
                self.canvas.create_oval(p_x, p_y, sq_x, sq_y, fill=self.paint_color.get(), outline=self.paint_second_color.get(), width=width, dash=d_tup)
            elif self.shape_var.get() in ('rectangle', 'square'):
                self.canvas.create_rectangle(p_x, p_y, sq_x, sq_y, fill=self.paint_color.get(),
                                             outline=self.paint_second_color.get(), width=width, dash=d_tup)
            elif self.shape_var.get() in ('arc', 'chord', 'pieslice'):
                sdegree, sextend = 0, 90
                if self.start_degree_box.get():
                    if self.start_degree_box.get().isdigit():
                        sdegree = self.start_degree_box.get()
                if self.arc_extent.get():
                    if self.arc_extent.get().isdigit():
                        sextend = self.arc_extent.get()

                self.canvas.create_arc(p_x, p_y, sq_x, sq_y, fill=self.paint_color.get(), start=sdegree, dash=d_tup,
                                       outline=self.paint_second_color.get(), width=width, style=self.shape_var.get(), extent=sextend)
            elif self.shape_var.get() in ('tringle', 'pentagon', 'right triangle', 'hexagon', 'octagon', 'star', 'heart'):
                x_mid = (p_x + sq_x) // 2  # base mid
                x_dis = (sq_x - p_x)  # base len

                half_s = x_mid - p_x
                shape_s = half_s * 2
                if self.shape_var.get() == 'tringle':
                    tringle_x = (p_x+sq_x) // 2
                    if self.direction_var.get() == 'Bottom':
                        dir_tuple = p_x, p_y, sq_x , p_y, tringle_x, sq_y
                    else:
                        dir_tuple = p_x, sq_y, sq_x, sq_y, tringle_x, p_y
                elif self.shape_var.get() == 'pentagon':
                    if self.direction_var.get() == 'Top':
                        dir_tuple =  (sq_x - (shape_s * 0.75), sq_y, p_x + (shape_s * 0.75), sq_y
                                     , sq_x, (sq_y + p_y) // 2,

                            (p_x + sq_x) // 2, p_y, p_x, (sq_y + p_y) // 2)
                    else:
                        dir_tuple = (sq_x - (shape_s * 0.75), p_y, p_x + (shape_s * 0.75), p_y
                                     , sq_x, (sq_y + p_y) // 2,

                                     (p_x + sq_x) // 2, sq_y, p_x, (sq_y + p_y) // 2)

                    #                         dir_tuple = ((p_x + sq_x) // 1.25, sq_y, (sq_x + p_x) // 1.75, sq_y

                elif self.shape_var.get() == 'hexagon':
                    dir_tuple = (sq_x - (shape_s * 0.8), sq_y, p_x + (shape_s * 0.8), sq_y
                                 , sq_x, (sq_y + p_y) // 2, p_x + (shape_s * 0.8), p_y, sq_x - (shape_s * 0.8),
                                 p_y,

                                   p_x, (sq_y + p_y) // 2)

                elif self.shape_var.get() == 'octagon':
                    mid_y_t = sq_y - (shape_s * 0.7)
                    mid_y_b = sq_y - (shape_s * 0.3)
                    left_base, right_base = sq_x - (shape_s * 0.7), p_x + (shape_s * 0.7),
                    dir_tuple = (left_base, sq_y, right_base, sq_y #  bottom base
                    , sq_x, mid_y_b, sq_x, mid_y_t  # right side
                     ,right_base ,p_y, left_base, p_y # top base
                    , p_x, p_y + (shape_s * 0.3), p_x, mid_y_b,  # left side
                     left_base, sq_y) # connection

                elif self.shape_var.get() == 'right triangle':
                    if self.direction_var.get() == 'Right top':
                        dir_tuple = (p_x, sq_y, sq_x, sq_y
                                                   , sq_x , p_y)
                    elif self.direction_var.get() == 'Right bottom':
                        dir_tuple = (p_x, p_y, sq_x, p_y, sq_x, sq_y)
                    elif self.direction_var.get() == 'Left bottom':
                        dir_tuple = (sq_x, p_y, p_x, p_y
                                     , p_x, sq_y)
                    elif self.direction_var.get() == 'Left top':
                        dir_tuple = (sq_x, sq_y, p_x, sq_y, p_x, p_y)

                elif self.shape_var.get() == 'star':
                    cx, cy = (p_x + sq_x) // 2, (p_y + sq_y) // 2
                    rx, ry = (sq_x - p_x) // 2, (sq_y - p_y) // 2
                    points = []
                    for i in range(10):
                        angle = -math.pi / 2 + i * math.pi / 5
                        r_factor = 1 if i % 2 == 0 else 0.4
                        x = cx + rx * r_factor * math.cos(angle)
                        y = cy + ry * r_factor * math.sin(angle)
                        points.extend([x, y])
                    dir_tuple = tuple(points)

                elif self.shape_var.get() == 'heart':
                    cx, cy = (p_x + sq_x) // 2, (p_y + sq_y) // 2
                    w = (sq_x - p_x)
                    h = (sq_y - p_y)
                    points = []
                    steps = 40
                    for i in range(steps):
                        t = (2 * math.pi * i) / steps
                        x_val = 16 * math.sin(t)**3
                        y_val = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
                        px = cx + x_val * (w / 35)
                        py = cy - y_val * (h / 35)
                        points.extend([px, py])
                    dir_tuple = tuple(points)

                else:
                    dir_tuple = self.poly_points
                    self.poly_points = []
                    self.regular_shapes()

                self.canvas.create_polygon(dir_tuple, fill=self.paint_color.get(),
                                           outline=self.paint_second_color.get(), width=width)



            if self.shape_once.get():
                self.deactivate(mode=mode)
        
        elif mode == 'bit':
            mid_x, mid_y = (self.sq_x + self.p_x) // 2, (self.sq_y + self.p_y) // 2
            self.canvas.create_bitmap(mid_x, mid_y, bitmap=self.selected_bm.get())
            if self.bit_once.get():
                self.deactivate(mode=mode)

    def deactivate(self, event=None, mode='text', regular=True):
        # deacrivate special addition mode (text for now)
        self.add_mode, self.last_active = False, ''
        if mode == 'text':
            self.add_text.configure(bg='SystemButtonFace', text='Add text')
        elif mode == 'bit':
            self.bit_button.configure(bg=self.predefined_bg)
        elif mode == 'magnet':
            self.unbind('<Left>'), self.unbind('<Right>'), self.unbind('<Up>'), self.unbind('<Down>')
            self.bind('<Left>', lambda e: self.move_paint(key='left'))
            self.bind('<Right>', lambda e: self.move_paint(key='right'))
            self.bind('<Up>', lambda e: self.move_paint(key='up'))
            self.bind('<Down>', lambda e: self.move_paint(key='down'))

            self.unbind('<B1-Motion>')
            self.canvas.bind('<B1-Motion>', self.paint)

            self.magnet_var.set(False)
            self.magnet_button.configure(bg=self.predefined_bg)
        elif mode == 'eyedropper':
            self.canvas.unbind('<Button-1>')
            self.eyedropper_button.configure(bg=self.predefined_bg)
        else:
            self.shape_button.configure(bg=self.predefined_bg)
        self.current_mode = self.last_mode
        self.canvas.unbind('<ButtonRelease-1>')
        self.canvas.bind('<ButtonRelease-1>', self.paint)
        self.unbind('<Escape>')

        if regular:
            if 'draw' == self.current_mode or 'erase' == self.current_mode:
                self.draw_erase(mode=self.current_mode)
            else:
                self.hover_mouse()

    def canvas_color(self):
        color = colorchooser.askcolor(title='Select bg color')[1]
        self.canvas.configure(bg=color)
        if self.eraser_bg.get():
            self.eraser_color = color

    def update_mp(self):
        if self.mp_keys.get():
            self.bind('<Left>', lambda e: self.move_paint(key='left'))
            self.bind('<Right>', lambda e: self.move_paint(key='right'))
            self.bind('<Up>', lambda e: self.move_paint(key='up'))
            self.bind('<Down>', lambda e: self.move_paint(key='down'))
        else:
            self.unbind('<Left>'), self.unbind('<Right>')
            self.unbind('<Up>'), self.unbind('<Down>')

        if self.mp_mouse.get():
            self.canvas.bind('<ButtonPress-3>', self.move_paint)
            self.canvas.bind('<ButtonRelease-3>', self.move_paint)
        else:
            self.canvas.unbind('<ButtonPress-3>')
            self.canvas.unbind('<ButtonRelease-3>')

    def options(self):
        # many customizations options
        def change_transparency(size):
            tranc = float(size) / 100
            # print(tranc)
            self.attributes('-alpha', tranc)

        def change_reliefs(event=None):
            self.canvas.configure(relief=self.relief_var_canvas.get())
            for button in self.buttons_list:
                button.configure(relief=self.relief_var_buttons.get())

        def colors(mode='background'):
            color = color = colorchooser.askcolor(title=f'Select {mode} color')[1]
            if color:
                for button in self.fgbg_list:
                    button[mode] = color
                if mode == 'background':
                    for frame in self.frames:
                        frame[mode] = color
                        self[mode] = color
        def scroll_bars(mode='hrz'):
            if 'hrz' in mode:
                if self.hrz_s_var.get():
                    self.scroll.pack(side='bottom', fill=tk.X)
                    self.canvas.config(xscrollcommand=self.scroll.set)
                    self.scroll.config(command=self.canvas.xview)
                else:
                    self.scroll.pack_forget()
                    self.canvas.config(xscrollcommand=tk.NONE)
            if 'vrt' in mode:
                if self.vrt_s_var.get():
                    self.canvas.pack_forget()
                    self.scroll2.pack(side='right', fill=tk.Y)
                    self.canvas.pack(fill=tk.BOTH, expand=True)
                    self.canvas.config(yscrollcommand=self.scroll2.set)
                    self.scroll2.config(command=self.canvas.yview)
                else:
                    self.scroll2.pack_forget()
                    self.canvas.config(yscrollcommand=tk.NONE)


        option_root = tk.Toplevel()
        option_root.title('Egon draw - Options')
        option_root.resizable(False, False)
        # Apply standard theme background if possible, or let ttk handle it
        
        # Create Notebook (Tabs)
        notebook = ttk.Notebook(option_root)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Tab 1: Appearance
        tab_appearance = ttk.Frame(notebook)
        notebook.add(tab_appearance, text='Appearance')

        # Tab 2: Tools & Behavior
        tab_tools = ttk.Frame(notebook)
        notebook.add(tab_tools, text='Tools & Behavior')

        # Tab 3: General
        tab_general = ttk.Frame(notebook)
        notebook.add(tab_general, text='General')

        # --- Tab 1: Appearance Content ---
        
        # Transparency Group
        trans_group = ttk.LabelFrame(tab_appearance, text="Window Transparency", padding=10)
        trans_group.pack(fill='x', padx=10, pady=5)
        ttk.Scale(trans_group, from_=10, to=100, orient='horizontal', command=change_transparency, value=self.attributes('-alpha')*100).pack(fill='x')

        # Colors Group
        color_group = ttk.LabelFrame(tab_appearance, text="Application Colors", padding=10)
        color_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(color_group, text='Change Background Color', command=colors).pack(fill='x', pady=2)
        ttk.Button(color_group, text='Change Foreground Color', command=lambda: colors('foreground')).pack(fill='x', pady=2)
        ttk.Checkbutton(color_group, variable=self.eraser_bg, text='Sync Eraser with Background').pack(pady=5, anchor='w')

        # Reliefs Group
        relief_group = ttk.LabelFrame(tab_appearance, text="Interface Reliefs", padding=10)
        relief_group.pack(fill='x', padx=10, pady=5)
        
        r_frame = ttk.Frame(relief_group)
        r_frame.pack(fill='x')
        
        ttk.Label(r_frame, text='Canvas Border:').grid(row=0, column=0, padx=5, sticky='w')
        relief_combo_c = ttk.Combobox(r_frame, textvariable=self.relief_var_canvas, values=self.relief_values, width=10, state='readonly')
        relief_combo_c.grid(row=0, column=1, padx=5)
        
        ttk.Label(r_frame, text='Buttons:').grid(row=1, column=0, padx=5, sticky='w')
        relief_combo_v = ttk.Combobox(r_frame, textvariable=self.relief_var_buttons, values=self.relief_values, width=10, state='readonly')
        relief_combo_v.grid(row=1, column=1, padx=5)

        relief_combo_c.bind('<<ComboboxSelected>>', change_reliefs)
        relief_combo_v.bind('<<ComboboxSelected>>', change_reliefs)


        # --- Tab 2: Tools & Behavior Content ---

        # Lines Group
        lines_group = ttk.LabelFrame(tab_tools, text="Line Settings", padding=10)
        lines_group.pack(fill='x', padx=10, pady=5)
        ttk.Checkbutton(lines_group, variable=self.smooth_line, text='Smooth line drawing').pack(anchor='w')
        ttk.Checkbutton(lines_group, variable=self.connect_fl, text='Connect lines (continuous)').pack(anchor='w')

        # Scroll Bars Group
        scroll_group = ttk.LabelFrame(tab_tools, text="Scroll Bars", padding=10)
        scroll_group.pack(fill='x', padx=10, pady=5)
        
        s_check_frame = ttk.Frame(scroll_group)
        s_check_frame.pack(fill='x')
        ttk.Checkbutton(s_check_frame, variable=self.hrz_s_var, text='Horizontal', command=scroll_bars).pack(side='left', padx=5)
        ttk.Checkbutton(s_check_frame, variable=self.vrt_s_var, text='Vertical', command=lambda: scroll_bars('vrt')).pack(side='left', padx=15)
        
        ttk.Separator(scroll_group, orient='horizontal').pack(fill='x', pady=5)
        
        s_inc_frame = ttk.Frame(scroll_group)
        s_inc_frame.pack(fill='x', pady=2)
        ttk.Label(s_inc_frame, text="Scroll Increment (px):").pack(side='left', padx=5)
        
        self.inc_hrz = ttk.Spinbox(s_inc_frame, from_=0, to=100, width=5)
        self.inc_vrt = ttk.Spinbox(s_inc_frame, from_=0, to=100, width=5)
        self.inc_hrz.set(0) # Default
        self.inc_vrt.set(0) # Default
        
        # Note: Keeping original logic where Entry text was used. Spinbox works similarly.
        # But we need to check if self.update_inc expects an event.
        self.inc_hrz.pack(side='left', padx=2)
        ttk.Label(s_inc_frame, text="H").pack(side='left')
        
        self.inc_vrt.pack(side='left', padx=2)
        ttk.Label(s_inc_frame, text="V").pack(side='left')

        self.inc_hrz.bind('<KeyRelease>', self.update_inc)
        self.inc_vrt.bind('<KeyRelease>', self.update_inc)
        self.inc_hrz.bind('<<Increment>>', self.update_inc)
        self.inc_vrt.bind('<<Decrement>>', self.update_inc)
        self.inc_hrz.bind('<<Increment>>', self.update_inc) # Bind spinbox arrows
        self.inc_vrt.bind('<<Decrement>>', self.update_inc)


        # Move Paint Group
        mp_group = ttk.LabelFrame(tab_tools, text="Move & Paint Control", padding=10)
        mp_group.pack(fill='x', padx=10, pady=5)
        
        mp_en_frame = ttk.Frame(mp_group)
        mp_en_frame.pack(fill='x')
        ttk.Label(mp_en_frame, text="Enable Move by:").pack(side='left')
        ttk.Checkbutton(mp_en_frame, variable=self.mp_mouse, text='Mouse', command=self.update_mp).pack(side='left', padx=5)
        ttk.Checkbutton(mp_en_frame, variable=self.mp_keys, text='Keys', command=self.update_mp).pack(side='left', padx=5)

        ttk.Separator(mp_group, orient='horizontal').pack(fill='x', pady=5)
        
        mp_mode_frame = ttk.Frame(mp_group)
        mp_mode_frame.pack(fill='x')
        ttk.Label(mp_mode_frame, text="Move 'All' Items:").pack(side='left')
        ttk.Checkbutton(mp_mode_frame, text='Mouse Drag', variable=self.move_single_ms).pack(side='left', padx=10)
        ttk.Checkbutton(mp_mode_frame, text='Keys', variable=self.move_single_ar).pack(side='left', padx=10)

        # Scales
        ttk.Label(mp_group, text='Mouse Sensitivity:').pack(anchor='w', pady=(5,0))
        ttk.Scale(mp_group, from_=1, to=3, variable=self.mp_mr, value=1).pack(fill='x')
        
        ttk.Label(mp_group, text='Key Step Distance:').pack(anchor='w', pady=(5,0))
        ttk.Combobox(mp_group, textvariable=self.move_px, values=tuple(range(10, 100, 10)), width=10, state='readonly').pack(fill='x')


        # --- Tab 3: General Content ---

        # UI Mode Group
        ui_group = ttk.LabelFrame(tab_general, text="Interface Mode", padding=10)
        ui_group.pack(fill='x', padx=10, pady=5)
        ttk.Radiobutton(ui_group, variable=self.plc_mode, text='Standard Buttons', value='buttons', command=self.place_ui).pack(anchor='w')
        ttk.Radiobutton(ui_group, variable=self.plc_mode, text='Minimalist Menus', value='menus', command=self.place_ui).pack(anchor='w')

        # Export Group
        save_group = ttk.LabelFrame(tab_general, text="Export Options", padding=10)
        save_group.pack(fill='x', padx=10, pady=5)
        ttk.Radiobutton(save_group, variable=self.ps_mode, value='ps', text='Postscript (.ps)', command=self.update_sp_button).pack(side='left', padx=5)
        ttk.Radiobutton(save_group, variable=self.ps_mode, value='pdf', text='PDF Document (.pdf)', command=self.update_sp_button).pack(side='left', padx=5)

        # Bitmap Group
        bm_group = ttk.LabelFrame(tab_general, text="Bitmap Settings", padding=10)
        bm_group.pack(fill='x', padx=10, pady=5)
        ttk.Checkbutton(bm_group, variable=self.bitmap_active, text='Enable Bitmaps', command=self.bitmap_mode).pack(side='left', padx=5)
        ttk.Checkbutton(bm_group, variable=self.bit_once, text='Place One at a time').pack(side='left', padx=15)

        # Misc Group
        misc_group = ttk.LabelFrame(tab_general, text="Miscellaneous", padding=10)
        misc_group.pack(fill='x', padx=10, pady=5)
        ttk.Checkbutton(misc_group, variable=self.text_once, text='Reset tool after adding Text').pack(anchor='w')
        ttk.Checkbutton(misc_group, variable=self.shape_once, text='Reset tool after adding Shape').pack(anchor='w')
        ttk.Checkbutton(misc_group, variable=self.erase_skipw, text='Show warning before "Erase All"').pack(anchor='w')

    def hover_mouse(self, activate=True, slm=False):

        if self.add_mode:
            self.deactivate(mode=self.add_mode, regular=False)
        
        if slm:
            self.last_mode = self.current_mode

        # neutral that doesn't do anything, and lets you use your mouse in the canvas without worries
        if activate:
            self.output_mode_var.set('hover')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.configure(cursor='arrow')
            self.button_mannagment('hover')
            self.current_mode = 'hover'

            self.closest_item.configure(text="Hover over an item to see details")

            self.canvas.bind('<ButtonRelease-1>', self.identify_item)


    def identify_item(self, event=None):
        cords_msg, color_msg, group_ = '', '', ''
        self.close_item = self.canvas.find_closest(self.x, self.y)
        if self.close_item:
            self.item_type = self.canvas.type(self.close_item)
            color = self.canvas.itemcget(self.close_item, 'fill')
            color_msg = f' | {self.item_type}\'s color:{color}'
            if self.item_type  == 'line':
                for group in self.line_groups:
                    if self.close_item[0] in group:
                        group_ = group
                    if group_:
                        start, end = self.canvas.coords(group_[0]), self.canvas.coords(group_[-1])
                        cords_msg = f' | Starting pos:{start}, Ending pos:{end}'
            else:
                if self.item_type != 'text':
                    secondary_color = self.canvas.itemcget(self.close_item, 'outline')
                    if secondary_color != color:
                        color_msg = f' | {self.item_type}\'s fill color:{color}, {self.item_type}\'s outline color:{secondary_color}'
            self.closest_item.configure(text=f'Closest item: {self.item_type}{color_msg}{cords_msg}')

    def update_shape_ui(self, event):
        # with mode we adding widget that certain shapes need, and with the last mode we remove those who aren't necessary anymore
        mode = self.shape_var.get()

        if self.last_smode in ('rectangle', 'arc', 'chord', 'pieslice', 'pentagon', 'tringle', 'right triangle'):
            self.custom_title.pack_forget()
            if self.last_smode == 'rectangle':
                self.xy_ratio_sc.pack_forget()
            elif self.last_smode in ('arc', 'chord', 'pieslice'):
                self.arc_frame.pack_forget()
            elif self.last_smode in ('pentagon', 'tringle', 'right triangle'):
                if self.last_smode == 'right triangle':
                    self.shape_direction.configure(values=('Top', 'Bottom'))
                self.shape_direction.pack_forget()

        if mode in ('rectangle', 'arc', 'chord', 'pieslice', 'pentagon', 'tringle', 'right triangle'):
            self.custom_title.pack()
            if mode == 'rectangle':
                self.xy_ratio_sc.pack()
                self.custom_title['text'] = 'XY ratio'
            elif mode in ('arc', 'chord', 'pieslice'):
                self.arc_frame.pack()
                self.start_degree_box.grid(row=0, column=0)
                self.arc_extent.grid(row=0, column=2)
                self.custom_title['text'] = 'Starting degree | Extend'
            elif mode in ('pentagon', 'tringle', 'right triangle'):
                if mode == 'right triangle':
                    self.shape_direction.configure(values=('Right top', 'Right bottom', 'Left top', 'Left bottom'))
                    self.direction_var.set('Right top')
                self.shape_direction.pack()
                self.custom_title['text'] = 'Pointy direction'

        self.last_smode = mode


    def update_sp_button(self):
        self.save_script.configure(text=f'Save {self.ps_mode.get().upper()}')

    def regular_shapes(self):
        self.shape_button.configure(text='Add shape', bg=self.predefined_bg, command=lambda: self.add_special('shape'))
        self.canvas.unbind('<ButtonPress>')
        self.deactivate(mode='shape')


    def update_cl(self):
        # update connected lines option
        if self.connected_lines.get():
            self.canvas.unbind('<ButtonRelease-1>')
        else:
            self.canvas.bind('<ButtonRelease-1>', self.paint)

    def update_inc(self, event=None):
        self.canvas.configure(xscrollincrement=int(self.inc_hrz.get()), yscrollincrement=int(self.inc_vrt.get()))

    def fullscreen(self, event):
        self.fs_var = not(self.fs_var)
        self.attributes('-fullscreen', self.fs_var)

    def place_ui(self):
        # unpacking the widget for the class' tuples
        (draw_erase_frame, shapes_frame, color_frame, file_frame, sizes_frame, write_frame, edit_frame, ashape_frame,
         lines_frame, dash_frame) = self.topframes
        (draw_erase_title, lines_title, shapes_title, color_title, file_title, self.cords_label, sizes_title, write_title, edit_title,
         ashape_title, dash_title, dash_shape_title, dash_line_title, self.closest_item, self.bit_title) = self.text_list
        (draw, eraser, pencil, square_draw, round_draw, diamond_draw, color_button, second_color, deafult_bg,
                             save_image, upload_image, erase_canvas, self.add_text, options_button, self.hover_button,
                             undo, self.redo_button, hold_move, straight, from_same, self.magnet_button, self.grid_button, self.change_colorb,
                             self.eyedropper_button, self.bit_button, self.usage_button, self.github_button) = self.buttons_list
        self.buttons_frame, self.canvas_frame, bottom_frame, width_size_frame, dash_shape_frame, dash_line_frame, self.bit_frame, self.bonus_frame = self.frames


        self.buttons_frame.pack_forget()
        self.canvas_frame.pack_forget()
        bottom_frame.pack_forget()
        self.config(menu='')

        if self.plc_mode.get() == 'buttons':
            self.buttons_frame.pack(side='top', fill='x')
            self.canvas_frame.pack(expand=True, fill=tk.BOTH)
            self.status_bar.pack(side='bottom', fill='x')

            # Create Ribbon (Notebook)
            if hasattr(self, 'ribbon'):
                self.ribbon.destroy()
            self.ribbon = ttk.Notebook(self.buttons_frame)
            self.ribbon.pack(fill='both', expand=True, padx=2, pady=2)

            # --- Tab 1: Home (Tools, Colors, Sizes) ---
            tab_home = ttk.Frame(self.ribbon)
            self.ribbon.add(tab_home, text='Home')

            # Tools Group
            draw_erase_frame.lift()
            draw_erase_frame.pack(in_=tab_home, side='left', padx=5, pady=5, fill='y')
            draw.pack(side='left', padx=2)
            eraser.pack(side='left', padx=2)
            self.hover_button.pack(side='left', padx=2)
            self.eyedropper_button.pack(side='left', padx=2)

            ttk.Separator(tab_home, orient='vertical').pack(side='left', fill='y', padx=5)

            # Colors Group
            color_frame.lift()
            color_frame.pack(in_=tab_home, side='left', padx=5, pady=5, fill='y')
            color_button.pack(side='left', padx=2)
            second_color.pack(side='left', padx=2)
            deafult_bg.pack(side='left', padx=2)
            self.change_colorb.pack(side='left', padx=2)

            ttk.Separator(tab_home, orient='vertical').pack(side='left', fill='y', padx=5)

            # Sizes Group
            sizes_frame.lift()
            sizes_frame.pack(in_=tab_home, side='left', padx=5, pady=5, fill='y')
            tk.Label(sizes_frame, text="Size:", font=('Arial', 8)).pack(side='left')
            self.draw_size_box.pack(side='left', padx=2)
            tk.Label(sizes_frame, text="Eraser:", font=('Arial', 8)).pack(side='left')
            self.erase_size_box.pack(side='left', padx=2)
            
            # --- Tab 2: Insert (Shapes, Lines, Text) ---
            tab_insert = ttk.Frame(self.ribbon)
            self.ribbon.add(tab_insert, text='Insert')

            # Basic Shapes
            shapes_frame.lift()
            shapes_frame.pack(in_=tab_insert, side='left', padx=5, pady=5, fill='y')
            pencil.pack(side='left', padx=2)
            round_draw.pack(side='left', padx=2)
            square_draw.pack(side='left', padx=2)
            diamond_draw.pack(side='left', padx=2)

            ttk.Separator(tab_insert, orient='vertical').pack(side='left', fill='y', padx=5)

            # Lines
            lines_frame.lift()
            lines_frame.pack(in_=tab_insert, side='left', padx=5, pady=5, fill='y')
            hold_move.pack(side='left', padx=2)
            straight.pack(side='left', padx=2)
            from_same.pack(side='left', padx=2)

            ttk.Separator(tab_insert, orient='vertical').pack(side='left', fill='y', padx=5)

            # Custom Shapes
            ashape_frame.lift()
            ashape_frame.pack(in_=tab_insert, side='left', padx=5, pady=5, fill='y')
            self.shape_button.pack(side='left', padx=2)
            self.shapes_combo.pack(side='left', padx=2)
            width_size_frame.lift()
            width_size_frame.pack(in_=ashape_frame, side='left', padx=2)
            self.shapes_size.pack(side='left')
            self.shapes_width.pack(side='left')

            ttk.Separator(tab_insert, orient='vertical').pack(side='left', fill='y', padx=5)

            # Text
            write_frame.lift()
            write_frame.pack(in_=tab_insert, side='left', padx=5, pady=5, fill='y')
            self.add_text.pack(side='left', padx=2)
            self.font_combo.pack(side='left', padx=2)
            self.font_size.pack(side='left', padx=2)
            self.typefaces.pack(side='left', padx=2)
            self.text_angle.pack(side='left', padx=2)

            # Bitmaps
            self.bit_button.pack(in_=self.bit_frame, side='left')
            self.bit_combo.pack(in_=self.bit_frame, side='left', padx=2)
            self.bit_frame.lift()
            self.bit_frame.pack(in_=tab_insert, side='left', padx=5, pady=5)

            ttk.Separator(tab_insert, orient='vertical').pack(side='left', fill='y', padx=5)

            # Dash Settings
            dash_frame.lift()
            dash_frame.pack(in_=tab_insert, side='left', padx=5, pady=5, fill='y')
            # Dash Shape Row
            dash_shape_frame.lift()
            dash_shape_frame.pack(in_=dash_frame, fill='x', pady=1)
            tk.Label(dash_shape_frame, text="Dash Shape:", font=('Arial', 8)).pack(side='left')
            self.shape_dz.pack(in_=dash_shape_frame, side='left', padx=1)
            self.shape_dp.pack(in_=dash_shape_frame, side='left', padx=1)
            
            # Dash Line Row
            dash_line_frame.lift()
            dash_line_frame.pack(in_=dash_frame, fill='x', pady=1)
            tk.Label(dash_line_frame, text="Dash Line:", font=('Arial', 8)).pack(side='left')
            self.line_dz.pack(in_=dash_line_frame, side='left', padx=1)
            self.line_dp.pack(in_=dash_line_frame, side='left', padx=1)

            # --- Tab 3: Actions (Edit, View) ---
            tab_actions = ttk.Frame(self.ribbon)
            self.ribbon.add(tab_actions, text='Actions')

            edit_frame.lift()
            edit_frame.pack(in_=tab_actions, side='left', padx=5, pady=5, fill='y')
            undo.pack(side='left', padx=2)
            self.redo_button.pack(side='left', padx=2)
            erase_canvas.pack(side='left', padx=2)
            
            ttk.Separator(tab_actions, orient='vertical').pack(side='left', fill='y', padx=5)

            self.magnet_button.pack(in_=edit_frame, side='left', padx=2)
            self.grid_button.pack(in_=edit_frame, side='left', padx=2)
            
            # --- Tab 4: File (Save, Stats) ---
            tab_file = ttk.Frame(self.ribbon)
            self.ribbon.add(tab_file, text='File')
            
            file_frame.lift()
            file_frame.pack(in_=tab_file, side='left', padx=5, pady=5, fill='y')
            save_image.pack(side='left', padx=2)
            upload_image.pack(side='left', padx=2)
            self.save_script.pack(side='left', padx=2)

            ttk.Separator(tab_file, orient='vertical').pack(side='left', fill='y', padx=5)

            self.bonus_frame.lift()
            self.bonus_frame.pack(in_=tab_file, side='left', padx=5, pady=5)
            self.usage_button.pack(in_=self.bonus_frame, side='left', padx=2)
            self.github_button.pack(in_=self.bonus_frame, side='left', padx=2)
            
            options_button.lift()
            options_button.pack(in_=tab_file, side='right', padx=10)

        elif self.plc_mode.get() == 'menus':
            self.canvas_frame.pack(expand=True, fill=tk.BOTH)
            bottom_frame.pack()
            self.config(menu=self.app_menu)

    def magnet(self):
        if not(self.magnet_var.get()):
            self.hover_mouse()
            self.canvas.configure(cursor='fleur')
            self.unbind('<B1-Motion>')
            self.bind('<B1-Motion>', self.move_magnet)
            self.unbind('<Left>'), self.unbind('<Right>'), self.unbind('<Up>'), self.unbind('<Down>')
            self.bind('<Left>', lambda e: self.move_magnet(event='left'))
            self.bind('<Right>', lambda e: self.move_magnet(event='right'))
            self.bind('<Up>', lambda e: self.move_magnet(event='up'))
            self.bind('<Down>', lambda e: self.move_magnet(event='down'))
            self.magnet_button.configure(bg='light grey')
            self.last_active = 'magnet'

        else:
            self.deactivate(mode='magnet')

        self.magnet_var.set(not (self.magnet_var.get()))

    def toggle_grid(self):
        if self.grid_active.get():
            self.canvas.delete('grid_line')
            self.grid_button.configure(bg=self.predefined_bg)
            self.grid_active.set(False)
        else:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            step = 50
            for i in range(0, w, step):
                self.canvas.create_line(i, 0, i, h, tag='grid_line', fill='#e1e1e1')
            for i in range(0, h, step):
                self.canvas.create_line(0, i, w, i, tag='grid_line', fill='#e1e1e1')
            self.canvas.tag_lower('grid_line')
            self.grid_button.configure(bg='grey')
            self.grid_active.set(True)

    def move_magnet(self, event=None):
        closest_item = self.canvas.find_closest(self.x, self.y)
        if isinstance(event, str):
            self.magnet_x, self.magnet_y = self.move_dict[event]
        else:
            # if event.type == tk.EventType.ButtonPress:
            self.refrence_point = event.x, event.y
            x1, y1, x2, y2 = self.canvas.coords(closest_item)
            # conidition to check which is closer
            # item_x, item_y = [x if x1 - self.refrence_point[0] < x2 - self.refrence_point[0] ]
            item_x, item_y = (x1 + x2) // 2, (y1 + y2) // 2
            self.magnet_x, self.magnet_y = self.refrence_point[0] - item_x, self.refrence_point[1] - item_y
        self.canvas.move(closest_item, self.magnet_x, self.magnet_y)

    def change_color(self):

        def activation(event):
            closest_item = self.canvas.find_closest(event.x, event.y)
            group = (closest_item,)
            print(group)
            if self.canvas.type(closest_item) == 'line':
                for line_group in self.line_groups:
                    if group[0][0] in line_group:
                        group = line_group
                        break

            selected_color = colorchooser.askcolor(title='Select a color')
            if selected_color:
                for item in group:
                    self.canvas.itemconfig(item, fill=selected_color[1])

            if self.deactivate_color.get():
                deactivation()

        def deactivation():
            self.change_colorb['bg'] = 'SystemButtonFace'
            self.unbind('<B1-Motion>')
            if not self.last_mode == 'hover':
                self.draw_erase(self.last_mode)

        self.hover_mouse(slm=True)
        self.canvas['cursor'] = 'spraycan'
        self.change_colorb['bg'] = 'light grey'
        self.bind('<ButtonRelease-1>', activation)

    def toggle_eyedropper(self):
        if self.current_mode != 'eyedropper':
            self.last_mode = self.current_mode
            self.current_mode = 'eyedropper'
            self.canvas.configure(cursor='crosshair')
            self.button_mannagment('eyedropper')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.canvas.bind('<Button-1>', self.pick_color)
        else:
            self.deactivate(mode='eyedropper')

    def pick_color(self, event):
        items = self.canvas.find_closest(event.x, event.y)
        if items:
            item = items[0]
            color = self.canvas.itemcget(item, 'fill')
            if color:
                self.paint_color.set(color)
        self.deactivate(mode='eyedropper')

    def bitmap_mode(self):
        if self.bitmap_active.get():
            self.bit_title.grid(row=0, column=10)
            self.bit_frame.grid(row=1, column=10)
        else:
            self.bit_title.grid_forget()
            self.bit_frame.grid_forget()

    def usage_stats(self):

        def save_file():
            dir_name = 'Draw_usage_report'
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            now = datetime.now()
            
            # Recalculate stats
            lines_drawn = len(self.line_groups)
            
            color_list = []
            for i in self.canvas.find_all():
                if self.canvas.type(i) != 'bitmap':
                    try:
                        color_list.append(self.canvas.itemcget(i, 'fill'))
                    except Exception:
                        pass
            
            if color_list:
                most_used_color = max(set(color_list), key=color_list.count)
                unique_colors = len(set(color_list))
            else:
                most_used_color = 'None'
                unique_colors = 0
            
            most_used_tool = max(self.time_dict.items(), key=operator.itemgetter(1))
            mut_text = f'Most used tool: {most_used_tool[0]} ({timedelta(seconds=int(most_used_tool[1]))})'
            
            current_duration = getattr(self, 'ut', timedelta(0))

            text_list = [
                f"Session Date: {getattr(self, 'start_date', 'Unknown')}",
                f"Total Duration: {current_duration}",
                mut_text,
                f"Lines drawn: {lines_drawn}",
                f"Undos: {self.undo_count}",
                f"Redos: {self.redo_count}",
                f"Clears: {self.clear_count}",
                f"Most used color: {most_used_color}",
                f"Unique colors used: {unique_colors}",
                "--- Tool Breakdown ---"
            ]
            for tool, duration in self.time_dict.items():
                text_list.append(f'{tool.capitalize()}: {timedelta(seconds=int(duration))}')

            with open(os.path.join(dir_name, f'{now.strftime("%Y-%m-%d_%H-%M-%S")}.txt'), 'w') as f:
                    for line in text_list:
                        f.write(line + '\n')
            
            messagebox.showinfo('Success', f'Report saved to {dir_name}')

        def close_us():
            self.us_active = False
            usage_root.destroy()

        usage_root = tk.Toplevel()
        usage_root.title('Usage Dashboard')
        usage_root.geometry('400x500')
        usage_root.resizable(False, False)
        usage_root.protocol('WM_DELETE_WINDOW', close_us)
        
        style = ttk.Style()
        style.configure('Big.TLabel', font=('Helvetica', 20, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))

        notebook = ttk.Notebook(usage_root)
        notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # === Tab 1: Dashboard ===
        tab_overview = ttk.Frame(notebook)
        notebook.add(tab_overview, text='Dashboard')

        # Session Time Frame
        time_frame = ttk.LabelFrame(tab_overview, text="Session Duration")
        time_frame.pack(fill='x', padx=10, pady=5)
        
        self.usage_time = ttk.Label(time_frame, text='0:00:00', style='Big.TLabel', anchor='center')
        self.usage_time.pack(pady=5, fill='x')

        # Key Stats Grid
        stats_frame = ttk.LabelFrame(tab_overview, text="Key Statistics")
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Grid layout for stats
        # Row 0
        ttk.Label(stats_frame, text="Lines:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.ld_label = ttk.Label(stats_frame, text="0", font=('Arial', 9, 'bold'))
        self.ld_label.grid(row=0, column=1, padx=5, pady=2, sticky='e')
        
        ttk.Label(stats_frame, text="Colors:").grid(row=0, column=2, padx=5, pady=2, sticky='w')
        self.uc_label = ttk.Label(stats_frame, text="0", font=('Arial', 9, 'bold'))
        self.uc_label.grid(row=0, column=3, padx=5, pady=2, sticky='e')

        # Row 1
        ttk.Label(stats_frame, text="Undos:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.undo_label = ttk.Label(stats_frame, text="0", font=('Arial', 9, 'bold'))
        self.undo_label.grid(row=1, column=1, padx=5, pady=2, sticky='e')
        
        ttk.Label(stats_frame, text="Redos:").grid(row=1, column=2, padx=5, pady=2, sticky='w')
        self.redo_label = ttk.Label(stats_frame, text="0", font=('Arial', 9, 'bold'))
        self.redo_label.grid(row=1, column=3, padx=5, pady=2, sticky='e')

        # Row 2
        ttk.Label(stats_frame, text="Clears:").grid(row=2, column=0, padx=5, pady=2, sticky='w')
        self.clear_label = ttk.Label(stats_frame, text="0", font=('Arial', 9, 'bold'))
        self.clear_label.grid(row=2, column=1, padx=5, pady=2, sticky='e')

        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        # Most Used Tool Section
        top_tool_frame = ttk.LabelFrame(tab_overview, text="Top Tool")
        top_tool_frame.pack(fill='x', padx=10, pady=5)
        
        self.mut_label = ttk.Label(top_tool_frame, text='...', font=('Arial', 10))
        self.mut_label.pack(pady=5)

        # Most Used Color Section
        color_frame = ttk.LabelFrame(tab_overview, text="Dominant Color")
        color_frame.pack(fill='x', padx=10, pady=5)
        
        color_inner = tk.Frame(color_frame)
        color_inner.pack(pady=5)
        
        self.muc_display = tk.Canvas(color_inner, width=30, height=30, bg='SystemButtonFace', highlightthickness=1, relief='sunken')
        self.muc_display.pack(side='left', padx=10)
        self.muc_label = ttk.Label(color_inner, text='None')
        self.muc_label.pack(side='left')

        save_button = ttk.Button(tab_overview, text='Save Report', command=save_file)
        save_button.pack(pady=10, fill='x', padx=20)


        # === Tab 2: Analysis ===
        tab_details = ttk.Frame(notebook)
        notebook.add(tab_details, text='Analysis')
        
        scroll = ttk.Scrollbar(tab_details)
        scroll.pack(side='right', fill='y')
        
        details_canvas = tk.Canvas(tab_details, yscrollcommand=scroll.set)
        details_canvas.pack(side='left', fill='both', expand=True)
        scroll.config(command=details_canvas.yview)
        
        details_inner = ttk.Frame(details_canvas)
        details_canvas.create_window((0,0), window=details_inner, anchor="nw")
        
        details_inner.bind("<Configure>", lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all")))

        ttk.Label(details_inner, text='Tool Usage Breakdown', style='Header.TLabel').pack(pady=10, anchor='w', padx=10)
        
        self.tool_bars = {}
        for tool in self.time_dict:
            frame = ttk.Frame(details_inner)
            frame.pack(fill='x', padx=10, pady=2)
            
            # Label row
            lbl_frame = ttk.Frame(frame)
            lbl_frame.pack(fill='x')
            ttk.Label(lbl_frame, text=tool.capitalize()).pack(side='left')
            time_lbl = ttk.Label(lbl_frame, text="0s")
            time_lbl.pack(side='right')
            
            # Progress bar
            bar = ttk.Progressbar(frame, orient='horizontal', length=200, mode='determinate')
            bar.pack(fill='x', pady=(0, 5))
            
            self.tool_bars[tool] = {'bar': bar, 'label': time_lbl}

        self.us_active = True
        self.update_usage_ui()

    def stopwatch(self):
        self.start_time = time.time()
        self.start_date = datetime.now().strftime('%Y-%m-%d')
        self.stt = timedelta(seconds=int(time.time() - self.start_time))
        while True:
            time.sleep(0.5)
            self.ut = timedelta(seconds=int(time.time() - self.start_time))
            self.time_dict[self.current_mode] += 0.5
            if self.us_active:
                self.after(0, self.update_usage_ui)

    def update_usage_ui(self):
        try:
            # Update Time
            if hasattr(self, 'ut'):
                self.usage_time.configure(text=f'{self.ut}')
            
            # Get max duration for progress bars
            total_seconds = max(1, sum(self.time_dict.values()))
            
            # Update Most Used Tool
            most_used_tool = max(self.time_dict.items(), key=operator.itemgetter(1))
            self.mut_label.configure(text=f'{most_used_tool[0].capitalize()} ({timedelta(seconds=int(most_used_tool[1]))})')
            
            # Update Tool Breakdown (Bars)
            if hasattr(self, 'tool_bars'):
                for tool, duration in self.time_dict.items():
                    if tool in self.tool_bars:
                        # Update bar value
                        percent = (duration / total_seconds) * 100
                        self.tool_bars[tool]['bar']['value'] = percent
                        self.tool_bars[tool]['label'].configure(text=f"{timedelta(seconds=int(duration))}")
            
            # Update Lines Drawn
            if hasattr(self, 'ld_label'):
                self.ld_label.configure(text=f'{len(self.line_groups)}')

            # Update Undos/Redos/Clears
            if hasattr(self, 'undo_label'): self.undo_label.configure(text=f'{self.undo_count}')
            if hasattr(self, 'redo_label'): self.redo_label.configure(text=f'{self.redo_count}')
            if hasattr(self, 'clear_label'): self.clear_label.configure(text=f'{self.clear_count}')
            
            # Update Colors
            if hasattr(self, 'muc_label') and hasattr(self, 'uc_label'):
                color_list = []
                for i in self.canvas.find_all():
                    if self.canvas.type(i) != 'bitmap':
                        try:
                            # Filter out system colors or None if needed, but 'fill' usually returns something
                            c = self.canvas.itemcget(i, 'fill')
                            if c: color_list.append(c)
                        except Exception:
                            pass
                
                if color_list:
                    most_used_color = max(set(color_list), key=color_list.count)
                    unique_colors = len(set(color_list))
                    
                    # Update Color Preview
                    self.muc_display.configure(bg=most_used_color)
                    self.muc_label.configure(text=most_used_color)
                else:
                    unique_colors = 0
                    self.muc_display.configure(bg='SystemButtonFace')
                    self.muc_label.configure(text='No Data')
                
                self.uc_label.configure(text=f'{unique_colors}')

        except tk.TclError:
            pass

    def effective_size(self):
        self.update_idletasks()
        # window size & cords
        str_width = 1250
        str_height = 830
        min_width = self.buttons_frame.winfo_width()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.width = round(str_width * (screen_width / 1920))
        self.height = round(str_height * (screen_height / 1080))

        if min_width > self.width:
            self.width = min_width

        placement_x = round((screen_width / 2) - (self.width / 2))
        placement_y = round((screen_height / 2) - (self.height / 2))
        self.geometry(f'{self.width}x{self.height}+{placement_x}+{placement_y}')

if __name__ == '__main__':
    app = Window()
    app.mainloop()
