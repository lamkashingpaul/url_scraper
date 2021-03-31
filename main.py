from tkinter import ttk
from bs4 import BeautifulSoup
from threading import Thread
from urllib.parse import urljoin
from urllib.parse import unquote
from datetime import datetime
# import concurrent.futures

import tkinter as tk
import os
import re
import requests
import mimetypes
# from requests.auth import HTTPBasicAuth


WIDTH = 600
HEIGHT = 480
URL_PATH = ''
DEFAULT_COURSE = 'https://course.ie.cuhk.edu.hk/~ierg4998/21-22/SupervisorList.htm'

username = 'math2010'  # Not Implemented Yet
password = 'calculus'  # Not Implemented Yet

current_dir = os.path.dirname(__file__)


# GUI Interface
class Application(tk.Frame):
    def __init__(self, master):
        # Initialization of GUI
        tk.Frame.__init__(self, master)
        tk.Frame.pack(self)

        # Top URL Frame
        self.url_frame = tk.LabelFrame(root, text='URL', padx=5, pady=5, borderwidth=5)
        self.url_frame.pack(side='top', fill='x')

        self.url_label = tk.Label(self.url_frame, text=URL_PATH)
        self.url_entry = EntryWithPlaceholder(self.url_frame, placeholder=DEFAULT_COURSE)
        self.url_entry.bind('<Return>', lambda _: self.browser_threaded(self.url_entry.get()))
        self.url_button = tk.Button(self.url_frame, text='Go', command=lambda: self.browser_threaded(self.url_entry.get()))

        self.url_label.grid(row=1, column=1)
        self.url_entry.grid(row=1, column=2)
        self.url_button.grid(row=1, column=3)
        # self.url_label_load.grid(row=1, column=4)

        self.url_frame.grid_rowconfigure((0, 2), weight=1)
        self.url_frame.grid_columnconfigure((0, 4), weight=1)

        # Authorizing Frame
        # Adding bottom and entry

        # Middle List Frame
        self.list_frame = DoubleScrollbarFrame(root, relief='sunken')
        self.scroll_frame_inside = ttk.Frame(self.list_frame.get_frame())

        self.scroll_frame_inside.pack(padx=5, pady=5, side='top', fill='both', expand=True)
        self.list_frame.pack(padx=5, pady=5, side='top', fill='both', expand=True)

        # Data list
        self.course = ''
        self.data = []

        # Bottom Action Frame
        self.action_frame = tk.LabelFrame(root, text='Action', padx=5, pady=5, borderwidth=5)
        self.action_frame.pack(side='bottom', fill='x')

        # Search Function
        # Not Fully Implemented

        # self.action_label_field = tk.Label(self.action_frame, text='Search from Field: ')
        # self.action_combobox = ttk.Combobox(self.action_frame, state='readonly', values=('All', 'Filename', 'URL'), width=8)
        # self.action_entry = EntryWithPlaceholder(self.action_frame, 'Keywords')
        # self.action_regex_toggle = tk.IntVar()
        # self.action_regex_checkbutton = tk.Checkbutton(self.action_frame, text='RegEx', variable=self.action_regex_toggle)
        # self.action_button_search = tk.Button(self.action_frame, text='Search')
        # self.action_label_field.grid(row=1, column=1)
        # self.action_combobox.set('All')
        # self.action_combobox.grid(row=1, column=2)
        # self.action_entry.grid(row=1, column=3)
        # self.action_regex_checkbutton.grid(row=1, column=4)
        # self.action_button_search.grid(row=1, column=5)

        self.action_button_deselect_all = tk.Button(self.action_frame, text='Deselect All', command=lambda: self.deselect_all())
        self.action_button_select_all = tk.Button(self.action_frame, text='Select All', command=lambda: self.select_all())
        self.action_button_inverse_select = tk.Button(self.action_frame, text='Inverse Select', command=lambda: self.inverse_select())
        self.action_button_download_selected = tk.Button(self.action_frame, text='Download Selected', command=lambda: self.download_selected_threaded())

        self.action_button_deselect_all.grid(row=1, column=6)
        self.action_button_select_all.grid(row=1, column=7)
        self.action_button_inverse_select.grid(row=1, column=8)
        self.action_button_download_selected.grid(row=1, column=9)

        self.action_frame.grid_rowconfigure((0, 2), weight=1)
        self.action_frame.grid_columnconfigure((0, 10), weight=1)
        for i in range(6, 10):
            self.action_frame.grid_columnconfigure(i, pad=50)

    # Requesting the html Page
    def browser(self, course):
        self.master.title('Loading...')
        self.s = requests.session()
        self.r = self.s.get(course)
        self.soup = BeautifulSoup(self.r.text, 'html.parser')

        if self.soup.title:
            self.master.title('[' + self.soup.title.string + ']')
        else:
            self.master.title('[' + course + ']')

        self.course = course

        # Reset the list frame
        self.scroll_frame_inside.pack_forget()
        self.list_frame.pack_forget()

        self.list_frame = DoubleScrollbarFrame(root, relief='sunken')
        self.scroll_frame_inside = ttk.Frame(self.list_frame.get_frame())

        self.scroll_frame_inside.pack(padx=5, pady=5, side='top', fill='both', expand=True)
        self.list_frame.pack(padx=5, pady=5, side='top', fill='both', expand=True)

        # Update list

        self.write_data_links()
        self.update_list_frame()

    def browser_threaded(self, course):
        thread = Thread(target=self.browser, args=(course, ))
        thread.start()

    # Constructing 2D List Data
    # Index | Data
    #   0   | Description
    #   1   | URL
    #   2   | Checkbox_Buttom
    #   3   | Checkbox_Value
    #   4   | State
    def write_data_links(self):
        self.data = [[self.flatstr(a.text), urljoin(self.course, a['href']), tk.Checkbutton(), tk.IntVar(), tk.StringVar()] for a in self.soup.find_all('a', href=re.compile('(?i)\\.[^./]+$')) if a.text]
        for data in self.data:
            data[0] = tk.StringVar(value=data[0])
            data[2] = tk.Checkbutton(self.scroll_frame_inside, variable=data[3])
            pass

    # Packing Widget to Frame
    def update_list_frame(self):
        # Write list to the frame
        if self.data:
            self.list_frame_texts = tk.Label(self.scroll_frame_inside, text='Name')
            self.list_frame_links = tk.Label(self.scroll_frame_inside, text='URL')
            self.list_frame_filenames = tk.Label(self.scroll_frame_inside, text='Filename')
            self.list_frame_checkboxs = tk.Label(self.scroll_frame_inside, text='Checkbox')
            self.list_frame_states = tk.Label(self.scroll_frame_inside, text='State')

            self.list_frame_texts.grid(row=1, column=1)
            self.list_frame_links.grid(row=1, column=2)
            self.list_frame_filenames.grid(row=1, column=3)
            self.list_frame_checkboxs.grid(row=1, column=4)
            self.list_frame_states.grid(row=1, column=5)

            for i in range(len(self.data)):
                self.list_frame_texts = tk.Label(self.scroll_frame_inside, textvariable=self.data[i][0])
                self.list_frame_links = tk.Label(self.scroll_frame_inside, text=self.data[i][1])
                self.list_frame_filenames = tk.Entry(self.scroll_frame_inside, textvariable=self.data[i][0])
                self.list_frame_states = tk.Label(self.scroll_frame_inside, textvariable=self.data[i][4])

                self.list_frame_texts.grid(row=i + 2, column=1)
                self.list_frame_links.grid(row=i + 2, column=2)
                self.list_frame_filenames.grid(row=i + 2, column=3)
                self.data[i][2].grid(row=i + 2, column=4)
                self.list_frame_states.grid(row=i + 2, column=5)
                pass

            self.scroll_frame_inside.grid_columnconfigure((0, 5), weight=1)

        self.scroll_frame_inside.pack(padx=5, pady=5, side='top', fill='both', expand=True)
        self.list_frame.pack(padx=5, pady=5, side='top', fill='both', expand=True)

    def flatstr(self, value):
        for c in '\\/:*?"<>|':
            value = value.replace(c, '-')
        return value.lstrip()

    def deselect_all(self):
        for checkbutton in self.data:
            checkbutton[3].set(0)

    def select_all(self):
        for checkbutton in self.data:
            checkbutton[3].set(1)

    def inverse_select(self):
        for checkbutton in self.data:
            if checkbutton[3].get() == 1:
                checkbutton[3].set(0)
            else:
                checkbutton[3].set(1)

    def download_selected(self):
        self.action_button_download_selected['state'] = 'disable'
        self.action_button_download_selected['text'] = 'Download In Progress'

        # Initialize State and Parameters
        for data in self.data:
            data[4].set('')
        total_number_of_downloads = sum([(i[3].get()) for i in self.data])

        s = requests.session()

        i = 0
        for data in self.data:
            self.list_frame.pack(padx=5, pady=5, side='top', fill='both', expand=True)
            if data[3].get() == 1:
                try:
                    # Print Message to user
                    data[4].set(f'{i}/{total_number_of_downloads} Completed. Downloading...')

                    # Create Folder for Domain
                    target_dir = os.path.join(current_dir, self.flatstr(self.course))
                    os.makedirs(target_dir, exist_ok=True)

                    # Define the filename and file path
                    r = s.get(data[1], auth=(username, password))
                    content_type = r.headers['content-type']
                    remote_size = int(r.headers['content-length'])
                    extension = mimetypes.guess_extension(content_type)

                    if extension is None:
                        extension = '.' + data[1].split('/')[-1].split('.')[-1]
                        if extension is None:
                            extension = ''

                    filename = unquote(data[1].split('/')[-1].split('.')[-2]) + ' - ' + data[0].get() + extension
                    filepath = os.path.join(target_dir, filename)

                    # Check if file already exists
                    if os.path.isfile(filepath):
                        # Compare local and remote file length
                        local_size = os.path.getsize(filepath)
                        if local_size == remote_size:
                            print(f'File already exists: {filename}')
                            data[4].set(f'{i + 1}/{total_number_of_downloads} Completed. File Already UpToDate')
                            i += 1
                            continue
                        else:
                            # Rename the local file
                            print(f'Remote file is different from local: {filename}')

                            newfilename = os.path.splitext(filename)[0] + ' - ' + datetime.today().strftime('%Y%m%d-%H%M%S') + extension + '.BAK'
                            newfilepath = os.path.join(target_dir, newfilename)
                            os.rename(filepath, newfilepath)

                            print(f'Local file is backed up as: {newfilename}')

                    # Write to disk
                    with open(filepath, 'wb') as f:
                        f.write(r.content)
                        data[4].set(f'{i + 1}/{total_number_of_downloads} Completed. Downloaded Successfully.')

                except Exception as e:
                    print('Failed to do something: ' + str(e))
                    data[4].set(f'{i + 1}/{total_number_of_downloads} Completed. Failed to do something: + {str(e)}')

                i += 1

        self.action_button_download_selected['state'] = 'normal'
        self.action_button_download_selected['text'] = 'Download Selected'

    def download_selected_threaded(self):
        thread = Thread(target=self.download_selected, daemon=True)
        thread.start()


# Class for Creating Entry with Placeholder
class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master, placeholder='PLACEHOLDER', color='grey', **kwargs):
        super().__init__(master, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind('PLACEHOLDER', self.foc_in)
        self.bind('<FocusOut>', self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


# Class for Creating Frame with Vertical and Horizontal Scrollbars
class DoubleScrollbarFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        '''
            Initialization. The DoubleScrollbarFrame consist of :
                - an horizontal scrollbar
                - a  vertical   scrollbar
                - a canvas in which the user can place sub-elements
        '''
        ttk.Frame.__init__(self, master, **kwargs)

        # Canvas creation with double scrollbar
        self.hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.sizegrip = ttk.Sizegrip(self)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                                yscrollcommand=self.vscrollbar.set,
                                xscrollcommand=self.hscrollbar.set)
        self.canvas.bind('<Enter>', self.bound_to_mousewheel)
        self.canvas.bind('<Leave>', self.unbound_to_mousewheel)
        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)

        self.insdie_frame = ttk.Frame(self.canvas)

    def pack(self, **kwargs):
        '''
            Pack the scrollbar and canvas correctly in order to recreate the same look as MFC's windows.
        '''
        self.hscrollbar.pack(side=tk.BOTTOM, fill=tk.X, expand=tk.FALSE)
        self.vscrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=tk.FALSE)
        self.sizegrip.pack(in_=self.hscrollbar, side=tk.BOTTOM, anchor='se')
        self.canvas.pack(side=tk.LEFT, padx=5, pady=5,
                         fill=tk.BOTH, expand=tk.TRUE)

        self.canvas.create_window(0, 0, window=self.insdie_frame, anchor='nw')
        root.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox('all'))
        # self.canvas.xview_moveto(0)
        # self.canvas.yview_moveto(0)
        ttk.Frame.pack(self, **kwargs)

    def bound_to_mousewheel(self, event):
        self.bind_all('<MouseWheel>', self.on_mousewheel)

    def unbound_to_mousewheel(self, event):
        self.unbind_all('<MouseWheel>')

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def get_frame(self):
        '''
            Return the frame useful to place inner controls.
        '''
        return self.insdie_frame


# Start of the Script
if __name__ == '__main__':
    root = tk.Tk()
    root.minsize(WIDTH, HEIGHT)
    app = Application(master=root)
    root.mainloop()
