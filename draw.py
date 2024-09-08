import tkinter
from tkinter import ttk, colorchooser, filedialog, font, PhotoImage
from PIL import ImageGrab, Image, ImageTk, UnidentifiedImageError
from io import BytesIO



class Window(tkinter.Tk):
    def __init__(self):
        super().__init__()

        # drawing variables
        self.current_mode = 'draw'
        # self.brush_color = tkinter.StringVar()
        # self.brush_color.set('black')
        self.output_size, self.eraser_size, self.tool_width = tkinter.IntVar(), tkinter.IntVar(), tkinter.IntVar()
        self.output_size.set(3)
        self.eraser_size.set(5)
        self.output_predefined_sizes, self.eraser_predefined_sizes = (2, 3, 5, 7), (3, 5, 6, 9)
        self.predefined_sizes_dict = {'draw': (self.output_predefined_sizes, self.output_size),
                                      'erase': (self.eraser_predefined_sizes, self.eraser_size)}
        self.previous_point = [0, 0]
        self.move_dict = {'right': [10, 0], 'left': [-10, 0], 'up': [0, -10], 'down': [0, 10]}
        self.pen_types = 'line', 'round', 'square', 'arrow', 'diamond'
        self.pen_type = tkinter.StringVar()
        self.pen_type.set(self.pen_types[0])
        self.color, self.paint_color, self.paint_second_color = tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar()
        self.color.set('black'), self.paint_color.set('black'), self.paint_second_color.set('black')
        self.lines_list, self.images_list = [], []
        self.eraser_current, self.draw_current = 1, 1
        self.eraser_color = 'white'
        self.eraser_bg = tkinter.BooleanVar()
        self.eraser_bg.set(True)
        self.relief_var_canvas, self.relief_var_buttons = tkinter.StringVar(), tkinter.StringVar()
        self.relief_var_canvas.set('flat'), self.relief_var_buttons.set('ridge')
        self.relief_values = 'ridge', 'sunken', 'flat', 'groove'
        self.font_var, self.size_var, fonts = tkinter.StringVar(), tkinter.IntVar(), font.families()
        self.font_var.set('Arial'), self.size_var.set(16)
        self.last_items = []
        self.smooth_line = tkinter.BooleanVar()
        self.smooth_line.set(True)
        self.add_mode = False
        self.text_once = tkinter.BooleanVar()
        self.text_once.set(True)
        self.connected_lines = tkinter.BooleanVar()
        self.px2, self.py2 = 0, 0
        self.dotted_line_var = tkinter.BooleanVar()
        self.typeface_var = tkinter.StringVar()
        self.tp_values = '', 'underline', 'bold'
        self.fs_var = False
        self.dot_size, self.dot_space = '', ''


        # window size & cords
        self.width = 1250
        self.height = 830
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        placement_x = round((screen_width / 2) - (self.width / 2))
        placement_y = round((screen_height / 2) - (self.height / 2))
        self.geometry(f'{self.width}x{self.height}+{placement_x}+{placement_y}')

        # window design
        self.title('Ariel\'s / Egon Draw')
        self.style = ttk.Style()
        self.style.theme_use('vista')

        # window widgets
        frame_font = 'arial 8 underline'

        self.buttons_frame = tkinter.Frame(self)
        self.canvas_frame = tkinter.Frame(self)
        bottom_frame = tkinter.Frame(self)
        self.canvas = tkinter.Canvas(self.canvas_frame, cursor='pencil', bd=1, bg='white')

        title_list = 'Select mode', 'Select shape', 'Select colors', 'File management', 'Select sizes', 'Write', 'Edit'
        draw_erase_title, shapes_title, color_title, file_title, sizes_title, write_title, edit_title \
            = [tkinter.Label(self.buttons_frame, text=text, font=frame_font) for text in title_list]
        draw_erase_frame, shapes_frame, color_frame, file_frame, sizes_frame, write_frame, edit_frame \
            = [tkinter.Frame(self.buttons_frame, bd=1, bg='light grey') for x in range(7)]

        draw = tkinter.Button(draw_erase_frame, text='Draw', command=self.draw_erase, borderwidth=1, bg='grey')
        eraser = tkinter.Button(draw_erase_frame, text='Eraser', command=lambda: self.draw_erase('erase'),
                                borderwidth=1)
        self.hover_button = tkinter.Button(draw_erase_frame, text='Hover', command=self.hover_mouse, borderwidth=1)

        pencil = tkinter.Button(shapes_frame, text='Pencil', command=self.draw_tool, borderwidth=1)
        square_draw = tkinter.Button(shapes_frame, text='Marker', command=lambda: self.draw_tool('square'),
                                     borderwidth=1)
        round_draw = tkinter.Button(shapes_frame, text='Pen', command=lambda: self.draw_tool('round'), borderwidth=1)

        self.draw_size_box = ttk.Combobox(sizes_frame, width=5, textvariable=self.output_size, state='normal')
        self.erase_size_box = ttk.Combobox(sizes_frame, width=5, textvariable=self.eraser_size, state='normal')

        color_button = tkinter.Button(color_frame, text='Color', command=self.color_select, borderwidth=1)
        second_color = tkinter.Button(color_frame, text='Secondary color',
                                      command=lambda: self.color_select('second'), borderwidth=1)
        deafult_bg = tkinter.Button(color_frame, text='Canvas color', command=self.canvas_color, bd=1)

        self.add_text = tkinter.Button(write_frame, text='Add text', command=self.add_special, borderwidth=1)
        self.font_combo = ttk.Combobox(write_frame, width=15, textvariable=self.font_var, state='readonly',
                                       values=fonts)
        self.font_size = ttk.Combobox(write_frame, width=5, textvariable=self.size_var, state='readonly',
                                      style='TCombobox', values=tuple(range(8, 80, 2)))
        self.typefaces = ttk.Combobox(write_frame, width=5, values=self.tp_values, state='readonly',
                                      style='TCombobox', textvariable=self.typeface_var)

        save_image = tkinter.Button(file_frame, text='Save as image', command=self.save, borderwidth=1)
        upload_image = tkinter.Button(file_frame, text='Upload image', command=self.upload, borderwidth=1)
        save_script = tkinter.Button(file_frame, text='Save PostScript', command=self.upload, borderwidth=1,
                                     state=tkinter.DISABLED)

        erase_canvas = tkinter.Button(edit_frame, text='Erase canvas', command=lambda: self.canvas.delete('all'),
                                      borderwidth=1)
        undo = tkinter.Button(edit_frame, text='Undo', command=self.undo, borderwidth=1)
        redo = tkinter.Button(edit_frame, text='Redo', command=self.redo, borderwidth=1, state=tkinter.DISABLED)

        im = Image.open('settings.png')
        ph = ImageTk.PhotoImage(im, master=self)
        options_button = tkinter.Button(self.buttons_frame, image=ph, command=self.options, relief='flat')
        options_button.image = ph
        self.cords_label = tkinter.Label(bottom_frame, text='')

        # placing widgets
        self.buttons_frame.pack()
        self.canvas_frame.pack(expand=True, fill=tkinter.BOTH)
        bottom_frame.pack()

        draw_erase_title.grid(row=0, column=0)
        draw_erase_frame.grid(row=1, column=0, padx=2)
        draw.pack(pady=1)
        eraser.pack(pady=1)
        self.hover_button.pack(pady=1)

        sizes_title.grid(row=0, column=1)
        sizes_frame.grid(row=1, column=1)
        self.draw_size_box.pack(pady=3)
        self.erase_size_box.pack(pady=3)

        shapes_title.grid(row=0, column=2)
        shapes_frame.grid(row=1, column=2, padx=2)
        pencil.pack(pady=1)
        round_draw.pack(pady=1)
        square_draw.pack(pady=1)

        color_title.grid(row=0, column=3)
        color_frame.grid(row=1, column=3, padx=2)
        color_button.pack(pady=1)
        second_color.pack(pady=1)
        deafult_bg.pack(pady=1)

        file_title.grid(row=0, column=4)
        file_frame.grid(row=1, column=4, padx=2)
        save_image.pack(pady=1)
        upload_image.pack(pady=1)

        write_title.grid(row=0, column=5)
        write_frame.grid(row=1, column=5, padx=3)
        self.add_text.pack()
        self.font_combo.pack(pady=1)
        self.font_size.pack(pady=1)
        self.typefaces.pack(pady=1)

        edit_title.grid(row=0, column=6)
        edit_frame.grid(row=1, column=6, padx=3)
        erase_canvas.pack(pady=1)
        undo.pack(pady=1)
        redo.pack(pady=1)

        options_button.grid(row=1, column=9, padx=3)

        self.canvas.pack(fill=tkinter.BOTH, expand=True)
        self.cords_label.pack()

        # groups of widgets
        self.sheet_shapes = {'line': pencil, 'square': square_draw, 'round': round_draw}
        self.sheet_tools = {'erase': eraser, 'draw': draw, 'hover': self.hover_button}
        self.buttons_list = (draw, eraser, pencil, square_draw, round_draw, color_button, second_color, deafult_bg,
                             save_image, upload_image, erase_canvas, self.add_text, options_button, self.hover_button,
                             undo, redo)
        self.text_list = draw_erase_title, shapes_title, color_title, file_title, self.cords_label, sizes_title, write_title, edit_title
        self.fgbg_list = self.buttons_list + self.text_list
        self.frames = self.buttons_frame, self.canvas_frame, bottom_frame

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
        self.bind('<F11>', self.fullscreen)

        # function calling
        self.set_width()
        self.draw_erase()
        self.draw_tool()

    def set_width(self):
        if self.current_mode == 'draw':
            self.tool_width.set(self.output_size.get())
        elif self.current_mode == 'erase':
            self.tool_width.set(self.eraser_size.get())

    def button_mannagment(self, tool):
        if tool in self.pen_types:
            mode_dict = self.sheet_shapes
        else:
            mode_dict = self.sheet_tools

        for widget in mode_dict.values():
            widget.configure(bg='SystemButtonFace')
        mode_dict[tool].configure(bg='grey')

    def draw_tool(self, tool='line'):
        self.pen_type.set(tool)
        self.button_mannagment(tool)

    def draw_erase(self, mode='draw'):
        if self.add_mode:
            self.deactivate(mode=self.add_mode)
        self.hover_mouse(False)
        self.canvas.bind('<B1-Motion>', self.paint)
        if mode == 'draw':
            self.canvas.configure(cursor='pencil')
            self.color.set(self.paint_color.get())
        else:
            self.canvas.configure(cursor=tkinter.DOTBOX)
            self.color.set(self.eraser_color)

        self.button_mannagment(mode)
        self.current_mode = mode
        self.set_width()

    def save(self):
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

    def upload(self):
        global img_array, image, image_tk
        # load image into the canvas
        self.convert_image = filedialog.askopenfilename()
        if self.convert_image:
            image = Image.open(self.convert_image)
            image_tk = PhotoImage(file=self.convert_image)
            image_x = (self.canvas.winfo_width() // 2) - (image.width // 2)
            image_y = (self.canvas.winfo_height() // 2) - (image.height // 2)
            canvas_image = self.canvas.create_image(image_x, image_y, image=image_tk, anchor=tkinter.NW)
            self.images_list.append(canvas_image)


    def undo(self, event=None):
        items = self.canvas.find_all()
        if items:
            self.last_items.append(items[-1])
            self.canvas.delete(items[-1])

    def redo(self):
        if self.last_items:
            item = self.last_items[-1]

    def paint(self, event=None):
        if not self.current_mode == 'hover':

            self.last_items.clear()

            s_color = self.paint_second_color.get()
            if self.current_mode == 'erase':
                s_color = self.eraser_color

            if self.previous_point != [0, 0]:
                if self.pen_type.get() == 'line':
                    d_tuple = ()
                    if self.dot_size and self.dot_space:
                        if self.dot_size.get() and self.dot_space.get() and self.dotted_line_var.get(): d_tuple = (self.dot_size.get(), self.dot_space.get())
                    line = self.canvas.create_line(self.previous_point[0], self.previous_point[1], self.x,
                                                       self.y, dash=d_tuple,
                                                       fill=self.color.get(), width=self.tool_width.get(),
                                                       smooth=self.smooth_line.get())
                elif self.pen_type.get() == 'square' or self.pen_type.get() == 'round':

                    if self.pen_type.get() == 'square':
                        line = self.canvas.create_polygon(self.p_x, self.p_y, self.p_x, self.y, self.x, self.sq_y,
                                                          fill=s_color,
                                                          outline=self.color.get())
                    else:
                        line = self.canvas.create_oval(self.p_x, self.p_y, self.sq_x, self.sq_y, fill=s_color,
                                                       outline=self.color.get())

                self.lines_list.append(line)
        self.previous_point = [self.x, self.y]
        if event.type == '5':
            self.previous_point = [0, 0]

    def move_paint(self, key):
        if isinstance(key, str):
            move_x, move_y = self.move_dict[key]
        for l in self.lines_list:
            self.canvas.move(l, move_x, move_y)
        for img in self.images_list:
            self.canvas.move(img, move_x, move_y)

    def change_size(self):
        if self.current_mode == 'draw':
            size = self.output_size.get()
            drawt_list = list(map(int, list(self.draw_size_box['values'])))
            self.draw_current = drawt_list.index(size)
            self.draw_size_box.current(drawt_list.index(size))
            print(self.output_size.get())
        elif self.current_mode == 'erase':

            size = self.eraser_size.get()
            eraser_list = list(map(int, list(self.erase_size_box['values'])))

            self.eraser_current = eraser_list.index(size)
            self.erase_size_box.current(eraser_list.index(size))
            print(self.eraser_size.get())

        self.tool_width.set(size)

    def change_size_sc(self, event):
        if isinstance(event, int):
            value = event
        else:
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
        self.x, self.y = event.x, event.y
        self.cords_label.configure(text=f'X coordinates:{self.x} | Y coordinates:{self.y}')

        self.p_x, self.p_y = self.x - self.tool_width.get(), self.y - self.tool_width.get()
        self.sq_x, self.sq_y = self.x + self.tool_width.get(), self.y + self.tool_width.get()

    def add_special(self, mode='text'):
        def active(event=None, mode='text'):
            if mode == 'text':
                self.canvas.create_text(self.x, self.y, text=text,
                                        font=(self.font_var.get(), self.size_var.get(), self.typeface_var.get()),
                                        fill=self.paint_color.get())
                if self.text_once.get():
                    self.deactivate(mode=mode)


        proceed = False
        if mode == 'text':
            text = tkinter.simpledialog.askstring('Egon draw', 'Enter the text')
            if text:
                self.add_mode = 'text'
                self.add_text.configure(bg='grey', text='Edit text')
                proceed = True

        if proceed:
            self.last_mode = self.current_mode
            self.current_mode = 'hover'
            self.canvas.configure(cursor='center_ptr')
            self.button_mannagment('hover')
            self.canvas.bind('<ButtonRelease-1>', lambda e: active(mode=mode))
            self.canvas.unbind('<B1-Motion>')
            self.bind('<Escape>', self.deactivate)

    def deactivate(self, event=None, mode='text'):
        self.add_mode = False
        if mode == 'text':
            self.add_text.configure(bg='SystemButtonFace', text='Add text')
        self.current_mode = self.last_mode
        self.canvas.unbind('<ButtonRelease-1>')
        self.canvas.bind('<ButtonRelease-1>', self.paint)
        self.unbind('<Escape>')

        if 'draw' == self.current_mode or 'erase' == self.current_mode:
            self.draw_erase(mode=self.current_mode)
        else:
            self.hover_mouse()

    def canvas_color(self):
        color = colorchooser.askcolor(title='Select bg color')[1]
        self.canvas.configure(bg=color)
        if self.eraser_bg.get():
            self.eraser_color = color

    def options(self):
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


        option_root = tkinter.Toplevel()
        option_root.title('Egon draw - Options')
        option_root.resizable(False, False)
        op_font = 'arial 10 bold'

        transparency_title = tkinter.Label(option_root, text='Change transparency', font=op_font)
        transparency_bar = ttk.Scale(option_root, from_=10, to=100, orient='horizontal', command=change_transparency,
                                     value=100)

        colors_title = tkinter.Label(option_root, text='App colors', font=op_font)
        eraser_based_bg = tkinter.Checkbutton(option_root, variable=self.eraser_bg, text='Eraser same as bg')

        app_bg = tkinter.Button(option_root, text='general background', command=colors, bd=1)
        app_fg = tkinter.Button(option_root, text='general foreground', command=lambda: colors('foreground'), bd=1)
        #
        relief_title = tkinter.Label(option_root, text='Change reliefs', font=op_font)
        relief_tc = tkinter.Label(option_root, text='Canvas reliefs', font='arial 8')
        relief_combo_c = ttk.Combobox(option_root, textvariable=self.relief_var_canvas, values=self.relief_values)
        relief_tb = tkinter.Label(option_root, text='Buttons reliefs', font='arial 8')
        relief_combo_v = ttk.Combobox(option_root, textvariable=self.relief_var_buttons, values=self.relief_values)
        #
        # confine
        others_title = tkinter.Label(option_root, text='Others', font=op_font)
        smooth_line_b = tkinter.Checkbutton(option_root, variable=self.smooth_line, text='Smooth line')
        text_once_combo = tkinter.Checkbutton(option_root, variable=self.text_once, text='Singular text')

        con_lines_combo = tkinter.Checkbutton(option_root, variable=self.connected_lines, text='Connected lines',
                                              command=self.update_cl)

        dotted_line_title = tkinter.Label(option_root, text='Dots options', font=op_font)
        dotted_line_check = tkinter.Checkbutton(option_root, text='Dotted line', variable=self.dotted_line_var)
        dot_values_frame = tkinter.Frame(option_root)
        self.dot_size = tkinter.Entry(dot_values_frame, width=5, bd=1)
        self.dot_space = tkinter.Entry(dot_values_frame, width=5, bd=1)
        self.dot_size.insert(tkinter.END, 1), self.dot_space.insert(tkinter.END, 1)

        transparency_title.pack(padx=10), transparency_bar.pack()
        colors_title.pack(pady=3), app_bg.pack(), app_fg.pack(), eraser_based_bg.pack()
        relief_title.pack(), relief_tc.pack(), relief_combo_c.pack(pady=3), relief_tb.pack(), relief_combo_v.pack(
            pady=3)
        dotted_line_title.pack(), dotted_line_check.pack(), dot_values_frame.pack(), self.dot_size.grid(row=0, column=0,
                                                                                                        padx=3), self.dot_space.grid(
            row=0, column=2, padx=3)
        others_title.pack()
        smooth_line_b.pack(pady=3)
        text_once_combo.pack()
        con_lines_combo.pack()

        relief_combo_c.bind('<<ComboboxSelected>>', lambda event: change_reliefs())
        relief_combo_v.bind('<<ComboboxSelected>>', lambda event: change_reliefs())

    def hover_mouse(self, activate=True):
        if activate:
            self.canvas.unbind('<B1-Motion>')
            self.canvas.configure(cursor='arrow')
            self.button_mannagment('hover')
            self.current_mode = 'hover'

    def update_cl(self):
        if self.connected_lines.get():
            self.canvas.unbind('<ButtonRelease-1>')
        else:
            self.canvas.bind('<ButtonRelease-1>', self.paint)

    def fullscreen(self, event):
        self.fs_var = not(self.fs_var)
        self.attributes('-fullscreen', self.fs_var)


if __name__ == '__main__':
    app = Window()
    app.mainloop()
