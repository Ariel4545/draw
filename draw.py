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
        self.main_mods = 'draw', 'erase', 'hover'
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
        self.shapes_list = 'circle', 'square', 'arc', 'tringle', 'chord', 'pieslice', 'rectangle', 'pentagon', 'right triangle', 'hexagon', 'octagon'
        self.shape_var.set(self.shapes_list[0])
        self.last_smode = 'circle'

        # New features variables
        self.magnet_var = tk.BooleanVar()
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

        self.buttons_frame = tk.Frame(self)
        self.canvas_frame = tk.Frame(self)
        bottom_frame = tk.Frame(self)
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

        self.draw_size_box = ttk.Combobox(sizes_frame, width=5, textvariable=self.output_size, state='normal')
        self.erase_size_box = ttk.Combobox(sizes_frame, width=5, textvariable=self.eraser_size, state='normal')

        color_button = tk.Button(color_frame, text='Color', command=self.color_select, borderwidth=1)
        second_color = tk.Button(color_frame, text='Secondary color',
                                      command=lambda: self.color_select('second'), borderwidth=1)
        deafult_bg = tk.Button(color_frame, text='Canvas color', command=self.canvas_color, bd=1)
        self.change_colorb = tk.Button(color_frame, text='Edit color', command=self.change_color, borderwidth=1)

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

        im = Image.open('settings.png')
        ph = ImageTk.PhotoImage(im, master=self)
        options_button = tk.Button(self.buttons_frame, image=ph, command=self.options, relief='flat')
        options_button.image = ph
        self.cords_label = tk.Label(bottom_frame, text='', bd=1, relief='ridge')
        self.closest_item = tk.Label(bottom_frame, text='', bd=1, relief='ridge')

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
        self.buttons_frame.pack()
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)
        bottom_frame.pack()

        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.cords_label.grid(row=0, column=1)

        # groups of widgets
        self.sheet_shapes = {'line': pencil, 'square': square_draw, 'round': round_draw}
        self.sheet_tools = {'erase': eraser, 'draw': draw, 'hover': self.hover_button}
        self.placing_modes = {'drag': hold_move, 'straight': straight, 'centered': from_same}
        self.buttons_list = (draw, eraser, pencil, square_draw, round_draw, color_button, second_color, deafult_bg,
                             save_image, upload_image, erase_canvas, self.add_text, options_button, self.hover_button,
                             undo, self.redo_button, hold_move, straight, from_same, self.magnet_button, self.change_colorb,
                             self.bit_button, self.usage_button, self.github_button)
        self.text_list = draw_erase_title, lines_title, shapes_title, color_title, file_title, self.cords_label, sizes_title, write_title, edit_title, ashape_title, dash_title, dash_shape_title, dash_line_title, self.closest_item, self.bit_title
        self.fgbg_list = self.buttons_list + self.text_list
        self.frames = self.buttons_frame, self.canvas_frame, bottom_frame, width_size_frame, dash_shape_frame, dash_line_frame, self.bit_frame, self.bonus_frame


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

        self.cords_label.grid_forget()
        self.closest_item.grid_forget()
        self.cords_label.grid(row=0, column=1)

        if mode == 'draw':
            self.canvas.configure(cursor='pencil')
            self.color.set(self.paint_color.get())
        else:
            self.canvas.configure(cursor=tk.DOTBOX)
            self.color.set(self.eraser_color)

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

    def redo(self):
        if self.last_items:
            item = self.last_items[-1]


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
                elif self.pen_type.get() == 'square' or self.pen_type.get() == 'round':

                    if self.pen_type.get() == 'square':
                        self.line = self.canvas.create_polygon(self.p_x, self.p_y, self.p_x, self.y, self.x, self.sq_y,
                                                               fill=s_color,
                                                               outline=self.color.get())
                    else:
                        self.line = self.canvas.create_oval(self.p_x, self.p_y, self.sq_x, self.sq_y, fill=s_color,
                                                            outline=self.color.get())

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
            '''+ optional - make the borders more clear \ detect them better'''
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

    def color_select(self, mode='main'):
        color = colorchooser.askcolor(title='Select a color')

        if color[1]:
            if mode == 'main':
                self.paint_color.set(color[1])
            else:
                self.paint_second_color.set(color[1])
            if self.current_mode == 'draw':
                self.draw_erase()

    def cords(self, event):
        # some dynamic x,y capture and calculations
        self.x, self.y = event.x, event.y
        self.cords_label.configure(text=f'X coordinates:{self.x} | Y coordinates:{self.y}')

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
                if self.text_once.get():
                    self.deactivate(mode=mode)

        elif mode == 'shape':
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
            elif self.shape_var.get() in ('tringle', 'pentagon', 'right triangle', 'hexagon', 'octagon'):
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
            print(tranc)
            self.attributes('-alpha', tranc)

        def change_reliefs():
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
        op_font = 'arial 10 bold'

        titles = 'Change transparency', 'App colors', 'UI mode', 'Change reliefs', 'Others', 'Dots options', 'Scroll bars', 'Move paint', 'Special save', 'Lines', 'Bitmap'
        transparency_title, colors_title, ui_mode, relief_title, others_title, dotted_line_title, scroll_bars_title, mp_title, sp_title, ln_title, bm_title = [
            tk.Label(option_root, text=t, font=op_font) for t in titles]
        # UI's transparency
        transparency_bar = ttk.Scale(option_root, from_=10, to=100, orient='horizontal', command=change_transparency,
                                     value=100)
        # UI colors
        app_bg = tk.Button(option_root, text='general background', command=colors, bd=1)
        app_fg = tk.Button(option_root, text='general foreground', command=lambda: colors('foreground'), bd=1)
        eraser_based_bg = tk.Checkbutton(option_root, variable=self.eraser_bg, text='Eraser same as bg')
        # UI modes
        uim_frame = tk.Frame(option_root)
        buttons_uim = tk.Radiobutton(uim_frame, variable=self.plc_mode, text='Buttons', value='buttons', command=self.place_ui)
        menus_uim = tk.Radiobutton(uim_frame, variable=self.plc_mode, text='Menus (limited)', value='menus', command=self.place_ui)
        # relief options for the canvas and buttons
        relief_frame = tk.Frame(option_root)
        relief_tc = tk.Label(relief_frame, text='Canvas reliefs', font='arial 8')
        relief_combo_c = ttk.Combobox(relief_frame, textvariable=self.relief_var_canvas, values=self.relief_values)
        relief_tb = tk.Label(relief_frame, text='Buttons reliefs', font='arial 8')
        relief_combo_v = ttk.Combobox(relief_frame, textvariable=self.relief_var_buttons, values=self.relief_values)
        # lines drawing options
        lines_frame = tk.Frame(option_root)
        line_endstr_combo = tk.Checkbutton(lines_frame, variable=self.connect_fl, text='Connected end\start')
        # con_lines_combo = tk.Checkbutton(lines_frame, variable=self.connected_lines, text='Connected lines',
        #                                  command=self.update_cl)
        smooth_line_b = tk.Checkbutton(lines_frame, variable=self.smooth_line, text='Smooth line')
        # canvas' scroll bars
        scroll_bars_frame = tk.Frame(option_root)
        hrz_bar_box = tk.Checkbutton(scroll_bars_frame, variable=self.hrz_s_var, text='Horizontal', command=scroll_bars)
        vrt_bar_box = tk.Checkbutton(scroll_bars_frame, variable=self.vrt_s_var, text='Vertical',
                                     command=lambda: scroll_bars('vrt'))
        # scroll bars inc options
        inc_title = tk.Label(option_root, text='increment', font='arial 10 underline')
        scroll_bars_frame2 = tk.Frame(option_root)
        self.inc_hrz = tk.Entry(scroll_bars_frame2, width=8, bd=1)
        self.inc_vrt = tk.Entry(scroll_bars_frame2, width=8, bd=1)
        self.inc_hrz.insert(tk.END, 0), self.inc_vrt.insert(tk.END, 0)
        # move paint - with ratios and methods
        enable_title = tk.Label(option_root, text='Enable', font='arial 8 underline')
        enable_frame = tk.Frame(option_root)
        enable_mouse = tk.Checkbutton(enable_frame, variable=self.mp_mouse, text='Mouse', command=self.update_mp)
        enable_keys = tk.Checkbutton(enable_frame, variable=self.mp_keys, text='Keys', command=self.update_mp)

        single_all_title = tk.Label(option_root, text='Move single/all item(s)', font='arial 8 underline')
        single_all_frame = tk.Frame(option_root)
        mouse_sva_title = tk.Label(single_all_frame, text='Mouse', font='arial 8')
        keys_sva_title = tk.Label(single_all_frame, text='Keys', font='arial 8')
        mouse_sva_check = tk.Checkbutton(single_all_frame, text='All', variable=self.move_single_ms)
        keys_sva_check = tk.Checkbutton(single_all_frame, text='All', variable=self.move_single_ar)

        mouse_ratio_title = tk.Label(option_root, text='Mouse move ratio', font='arial 8 underline')
        mouse_ratio_scale = ttk.Scale(option_root, from_=1, to=3, variable=self.mp_mr, value=1)
        keys_pixel_title = tk.Label(option_root, text='Keys move distance', font='arial 8 underline')
        keys_pixel_amount = ttk.Combobox(option_root, textvariable=self.move_px, values=tuple(range(10, 100, 10)),
                                         width=10)
        # post-script save methods
        ps_frame = tk.Frame(option_root)
        ps_radio = tk.Radiobutton(ps_frame, variable=self.ps_mode, value='ps', text='Postscript',
                                  command=self.update_sp_button)
        pdf_radio = tk.Radiobutton(ps_frame, variable=self.ps_mode, value='pdf', text='PDF',
                                   command=self.update_sp_button)
        # other options
        singular_frame = tk.Frame(option_root)
        text_once_combo = tk.Checkbutton(singular_frame, variable=self.text_once, text='Singular text')
        shape_once_combo = tk.Checkbutton(singular_frame, variable=self.shape_once, text='Singular shape')
        last_frame = tk.Frame(option_root)
        skip_clear_w = tk.Checkbutton(last_frame, variable=self.erase_skipw, text='Erase canvas warning')
        
        bitmap_frame = tk.Frame(option_root)
        add_bitmap_check = tk.Checkbutton(bitmap_frame, variable=self.bitmap_active, text='Enable',
                                          command=self.bitmap_mode)
        singular_bit = tk.Checkbutton(bitmap_frame, variable=self.bit_once, text='One at a time')


        # confine

        transparency_title.grid(row=0, column=1, padx=10), transparency_bar.grid(row=1, column=1)
        colors_title.grid(row=2, column=1, pady=3), app_bg.grid(row=3, column=1, pady=1), app_fg.grid(row=4, column=1,pady=1)
        eraser_based_bg.grid(row=5, column=1)
        ui_mode.grid(row=6, column=1), uim_frame.grid(row=7, column=1)
        buttons_uim.grid(row=0, column=0), menus_uim.grid(row=0, column=2)

        relief_title.grid(row=8, column=1)
        relief_frame.grid(row=9, column=1, pady=3), relief_tc.grid(row=0, column=0)
        relief_combo_c.grid(row=1, column=0, padx=8), relief_tb.grid(row=0, column=2), relief_combo_v.grid(row=1,column=2,pady=3,padx=8)
        ln_title.grid(row=10, column=1), lines_frame.grid(row=11, column=1), smooth_line_b.grid(row=0,column=0), line_endstr_combo.grid(row=0, column=2)
        scroll_bars_title.grid(row=13, column=1), scroll_bars_frame.grid(row=14, column=1), hrz_bar_box.grid(row=0,column=0), vrt_bar_box.grid(row=0, column=2)
        inc_title.grid(row=15, column=1), scroll_bars_frame2.grid(row=16, column=1), self.inc_hrz.grid(row=0, column=0,padx=5), self.inc_vrt.grid(row=0, column=2, padx=5)

        mp_title.grid(row=17, column=1)
        enable_title.grid(row=18, column=1)
        enable_frame.grid(row=19, column=1)
        enable_mouse.grid(row=0, column=0), enable_keys.grid(row=0, column=2)
        single_all_title.grid(row=20, column=1), single_all_frame.grid(row=21, column=1)
        mouse_sva_title.grid(row=0, column=0), keys_sva_title.grid(row=0, column=2)
        mouse_sva_check.grid(row=1, column=0), keys_sva_check.grid(row=1, column=2)


        mouse_ratio_title.grid(row=22, column=1)
        mouse_ratio_scale.grid(row=23, column=1)
        keys_pixel_title.grid(row=24, column=1)
        keys_pixel_amount.grid(row=25, column=1)

        sp_title.grid(row=27, column=1)
        ps_frame.grid(row=28, column=1)
        ps_radio.grid(row=0, column=0)
        pdf_radio.grid(row=0, column=2)
        
        bm_title.grid(row=29, column=1)
        bitmap_frame.grid(row=30, column=1)
        add_bitmap_check.grid(row=0, column=0)
        singular_bit.grid(row=0, column=2)


        others_title.grid(row=31, column=1)
        singular_frame.grid(row=32, column=1), text_once_combo.grid(row=0, column=0), shape_once_combo.grid(row=0,column=2)
        last_frame.grid(row=33, column=1)
        skip_clear_w.grid(row=0, column=0)

        relief_combo_c.bind('<<ComboboxSelected>>', lambda event: change_reliefs())
        relief_combo_v.bind('<<ComboboxSelected>>', lambda event: change_reliefs())
        self.inc_hrz.bind('<KeyRelease>', self.update_inc), self.inc_vrt.bind('<KeyRelease>', self.update_inc)

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

            self.cords_label.grid_forget()
            self.cords_label.grid(row=0, column=0, padx=25)
            self.closest_item.grid(row=0, column=2, padx=25)

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

    def update_inc(self):
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
        (draw, eraser, pencil, square_draw, round_draw, color_button, second_color, deafult_bg,
                             save_image, upload_image, erase_canvas, self.add_text, options_button, self.hover_button,
                             undo, self.redo_button, hold_move, straight, from_same, self.magnet_button, self.change_colorb,
                             self.bit_button, self.usage_button, self.github_button) = self.buttons_list
        self.buttons_frame, self.canvas_frame, bottom_frame, width_size_frame, dash_shape_frame, dash_line_frame, self.bit_frame, self.bonus_frame = self.frames


        self.buttons_frame.pack_forget()
        self.canvas_frame.pack_forget()
        bottom_frame.pack_forget()
        self.config(menu='')

        if self.plc_mode.get() == 'buttons':
            self.buttons_frame.pack(side='top')
            self.canvas_frame.pack(expand=True, fill=tk.BOTH)
            bottom_frame.pack()

            draw_erase_title.grid(row=0, column=0)
            draw_erase_frame.grid(row=1, column=0, padx=2)
            draw.pack(pady=1)
            eraser.pack(pady=1)
            self.hover_button.pack(pady=1)

            lines_title.grid(row=0, column=1)
            lines_frame.grid(row=1, column=1, padx=2)
            hold_move.pack(pady=1)
            straight.pack(pady=1)
            from_same.pack(pady=1)

            sizes_title.grid(row=0, column=2)
            sizes_frame.grid(row=1, column=2, padx=2)
            self.draw_size_box.pack(pady=3)
            self.erase_size_box.pack(pady=3)
            self.font_size.pack(pady=1)

            shapes_title.grid(row=0, column=3)
            shapes_frame.grid(row=1, column=3, padx=2)
            pencil.pack(pady=1)
            round_draw.pack(pady=1)
            square_draw.pack(pady=1)

            color_title.grid(row=0, column=4)
            color_frame.grid(row=1, column=4, padx=2)
            color_button.pack(pady=1)
            second_color.pack(pady=1)
            deafult_bg.pack(pady=1)
            self.change_colorb.pack(pady=1)

            file_title.grid(row=0, column=5)
            file_frame.grid(row=1, column=5, padx=2)
            save_image.pack(pady=1)
            upload_image.pack(pady=1)
            self.save_script.pack(pady=1)

            write_title.grid(row=0, column=6)
            write_frame.grid(row=1, column=6, padx=3)
            self.add_text.pack()
            self.font_combo.pack(pady=1)
            self.typefaces.pack(pady=1)
            self.text_angle.pack()

            edit_title.grid(row=0, column=7)
            edit_frame.grid(row=1, column=7, padx=3)
            erase_canvas.pack(pady=1)
            undo.pack(pady=1)
            self.redo_button.pack(pady=1)
            self.magnet_button.pack(pady=1)

            ashape_title.grid(row=0, column=8)
            ashape_frame.grid(row=1, column=8, padx=3)
            self.shape_button.pack(pady=1)
            self.shapes_combo.pack(pady=1)
            width_size_frame.pack()
            self.shapes_size.grid(row=0, column=0, padx=3)
            self.shapes_width.grid(row=0, column=2, padx=3)

            dash_title.grid(row=0, column=9)
            dash_frame.grid(row=1, column=9)
            dash_shape_title.pack(), dash_shape_frame.pack()
            self.shape_dz.grid(row=0, column=0, padx=1), self.shape_dp.grid(row=0, column=2, padx=1)
            dash_line_title.pack(), dash_line_frame.pack()
            self.line_dz.grid(row=0, column=0, padx=1), self.line_dp.grid(row=0, column=2, padx=1)
            
            self.bit_button.pack(pady=8)
            self.bit_combo.pack(pady=8)

            options_button.grid(row=1, column=11, padx=3)
            
            self.bonus_frame.grid(row=1, column=12)
            self.usage_button.grid(row=0, column=0, padx=3, pady=5)
            self.github_button.grid(row=1, column=0, padx=3, pady=5)

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
            with open(os.path.join(dir_name, f'{now.strftime("%Y-%m-%d_%H-%M-%S")}.txt'), 'w') as f:
                    for line in text_list:
                        f.write(line + '\n')

        def close_us():
            self.us_active = False
            usage_root.destroy()

        usage_root = tk.Toplevel()
        usage_root.title('Usage stats')
        usage_root.resizable(False, False)
        usage_root.protocol('WM_DELETE_WINDOW', close_us)
        self.us_active = True

        title = tk.Label(usage_root, text='Usage statistics', font='Arial 12 bold')


        most_used_tool = max(self.time_dict.items(), key=operator.itemgetter(1))


        # way to include also the deleted ones
        lines_drawn = len(self.line_groups)
        # add a list of placed shapes like you have for lines
        # shapes_placed = len(self.shapes_group) # shapes_group not implemented in github version yet, skipping
        # text_placed = len(self.text_group) # text_group not implemented

        color_list = []
        for i in self.canvas.find_all():
            if not(self.canvas.type(i) == 'bitmap'):
                color_list.append(self.canvas.itemcget(i, 'fill'))
        if color_list:
            most_used_color = max(set(color_list), key=color_list.count)
        else:
            most_used_color = 'None'

        # text saved as variables to ease the saving process (if needed)
        mut_text = f'Most used tool {most_used_tool[0]}, estimated time {most_used_tool[1]}'
        muc_text = f'Most used color {most_used_color}'
        ld_text = f'Lines drawn {lines_drawn}'
        # sp_text = f'Shapes placed {shapes_placed}'
        # te_text = f'Text placed {text_placed}'
        text_list = [mut_text, ld_text]

        most_used_frame = tk.Frame(usage_root, bd=1, relief='ridge')
        itemp_frame = tk.Frame(usage_root, bd=1, relief='ridge')

        self.usage_time = tk.Label(usage_root)
        most_used_title = tk.Label(usage_root, text='Most used', font='Arial 11 underline')
        self.mut_label = tk.Label(most_used_frame, text=mut_text)
        muc_label = tk.Label(most_used_frame, text=muc_text)
        item_placed_title = tk.Label(usage_root, text='Placed Items', font='Arial 11 underline')
        ld_label = tk.Label(itemp_frame, text=ld_text)
        save_button = tk.Button(usage_root, text='Save', command=save_file)


        title.pack()

        most_used_title.pack()
        most_used_frame.pack(pady=3, padx=5)
        self.mut_label.pack()
        muc_label.pack()

        item_placed_title.pack()
        itemp_frame.pack(pady=3, padx=5)
        ld_label.pack()

        self.usage_time.pack()
        save_button.pack(pady=3, padx=5)

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
        self.usage_time.configure(text=f'Usage time: {self.ut}')
        most_used_tool = max(self.time_dict.items(), key=operator.itemgetter(1))
        try:
            self.mut_label.configure(text=f'Most used tool {most_used_tool[0]}, estimated time {most_used_tool[1]}')
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
