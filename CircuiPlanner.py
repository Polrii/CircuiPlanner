import os
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageColor


# Configuration
COL_NUM = 180
ROW_NUM = 140
PIXEL_SIZE = 10  # Size of each square in pixels
MIN_PIXEL_SIZE = 2   # Minimum pixel size for zoom-out limit
MAX_PIXEL_SIZE = 20  # Maximum pixel size for zoom-in limit
CANVAS_X = 0
CANVAS_Y = 0


class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CircuiPlanner")
        self.root.state('zoomed')
        
        self.color = "#000000"  # Default color (black)
        self.action = "Point"
        
        self.previous_pos = None

        """Create the toolbar."""
        # Create toolbar on the left
        self.toolbar = tk.Frame(root, width=60, bg="lightgray")
        self.toolbar.pack(side="left", fill="y")

        # Load or create icons for toolbar
        self.load_icons()
        
        # Move button
        self.move_button = tk.Button(self.toolbar, image=self.icons['move'][1], command=self.move_mode, bg="lightgray", relief="flat")
        self.move_button.pack(padx=4, pady=10)
        
        # Point button
        self.point_button = tk.Button(self.toolbar, image=self.icons['point'][2], command=self.point_mode, bg="lightgray", relief="groove")
        self.point_button.pack(padx=4, pady=10)
        
        # Add button
        self.add_button = tk.Button(self.toolbar, image=self.icons['add'][1], command=self.add_mode, bg="lightgray", relief="flat")
        self.add_button.pack(padx=4, pady=10)
        
        # Line button
        self.line_button = tk.Button(self.toolbar, image=self.icons['line'][1], command=self.line_mode, bg="lightgray", relief="flat")
        self.line_button.pack(padx=4, pady=10)
        
        # Erase button
        self.erase_button = tk.Button(self.toolbar, image=self.icons['erase'][1], command=self.erase_mode, bg="lightgray", relief="flat")
        self.erase_button.pack(padx=4, pady=10)
        
        # Color selection button
        self.color_button = tk.Button(self.toolbar, image=self.icons['color'][1], command=self.choose_color, bg="lightgray", relief="flat")
        self.color_button.pack(padx=4, pady=10)
        
        # Colorpick button
        self.colorpick_button = tk.Button(self.toolbar, image=self.icons['colorpick'][1], command=self.colorpick_mode, bg="lightgray", relief="flat")
        self.colorpick_button.pack(padx=4, pady=10)
        
        # Bucket button
        self.bucket_button = tk.Button(self.toolbar, image=self.icons['bucket'][1], command=self.bucket_mode, bg="lightgray", relief="flat")
        self.bucket_button.pack(padx=4, pady=10)
        
        # Text button
        self.text_button = tk.Button(self.toolbar, image=self.icons['text'][1], command=self.text_mode, bg="lightgray", relief="flat")
        self.text_button.pack(padx=4, pady=10)
        
        # Save button
        self.save_button = tk.Button(self.toolbar, image=self.icons['save'][1], command=self.save_image, bg="lightgray", relief="flat")
        self.save_button.pack(padx=4, pady=10)
        
        # Download button
        self.download_button = tk.Button(self.toolbar, image=self.icons['download'][1], command=self.download_image, bg="lightgray", relief="flat")
        self.download_button.pack(padx=4, pady=10)
        
        # Open button
        self.open_button = tk.Button(self.toolbar, image=self.icons['open'][1], command=self.open_file, bg="lightgray", relief="flat")
        self.open_button.pack(padx=4, pady=10)
        
        

        # Canvas for drawing
        self.canvas = tk.Canvas(root, width=COL_NUM * PIXEL_SIZE, height=ROW_NUM * PIXEL_SIZE)
        self.canvas.pack(side="right")
        
        # Draw checkered background
        self.draw_background()
        
        # Event bindings for canvas
        self.canvas.bind("<Button-1>", self.left_mouse_click)
        self.canvas.bind("<Button-2>", self.mid_mouse_click)
        self.canvas.bind("<ButtonRelease-2>", self.mid_mouse_release)
        self.canvas.bind("<Button-3>", self.right_mouse_click) 
        self.canvas.bind("<MouseWheel>", self.scroll_action)
        self.canvas.bind("<Motion>", self.mouse_move) 
        self.canvas.bind("<B1-Motion>", self.left_mouse_hold)
        self.canvas.bind("<B2-Motion>", self.mid_mouse_hold)
        self.canvas.bind("<B3-Motion>", self.right_mouse_hold)
        
        # Initialize a grid to keep track of pixel colors
        self.pixel_colors = [[None for _ in range(COL_NUM)] for _ in range(ROW_NUM)]
        
    def load_icons(self):
        """Load the icons for the toolbar."""
        self.icons = {'move': ["arrows"], 'save': ["disk"], 'download': ["download"], 'erase': ["eraser"], 'colorpick': ["eye-dropper"], 
                      'bucket': ["fill"], 'color': ["palette"], 'line': ["plug-connection"], 'point': ["pen-clip"], 'add': ["plus-hexagon"], 
                      'open': ["subfolder"], 'text': ["text"], }
        
        for icon in self.icons:
            self.icons[icon].append(ImageTk.PhotoImage(Image.open(f"Icons/{self.icons[icon][0]}.png")))
            self.icons[icon].append(self.paint_icon(f"Icons/{self.icons[icon][0]}.png", '#646464'))
    
    
    def make_background(self, width, height):
        bgs_list = os.listdir("Backgrounds")
        if f"{width}x{height}.png" not in bgs_list:
            image = Image.new("RGB", (width, height), (255, 255, 255))
            for y in range(height):
                for x in range(width):
                    color = (211, 211, 211) if (x + y) % 2 == 0 else (255, 255, 255)
                    image.putpixel((x, y), color)
                    
            image.save(f"Backgrounds/{width}x{height}.png")


    def draw_background(self):
        self.make_background(COL_NUM, ROW_NUM)
        image = Image.open(f"Backgrounds/{COL_NUM}x{ROW_NUM}.png")
        resized_image = image.resize((COL_NUM * PIXEL_SIZE, ROW_NUM * PIXEL_SIZE), Image.NEAREST)
        self.bg_image = ImageTk.PhotoImage(resized_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(CANVAS_X, CANVAS_Y, anchor="nw", image=self.bg_image)
    
    
    def update_canvas(self):
        # Resize the canvas according to the new PIXEL_SIZE
        self.canvas.config(width=COL_NUM * PIXEL_SIZE, height=ROW_NUM * PIXEL_SIZE)
        self.draw_background()
        for y in range(ROW_NUM):
            for x in range(COL_NUM):
                color = self.pixel_colors[y][x]
                if color:
                    self.paint_pixel((x * PIXEL_SIZE, y * PIXEL_SIZE), color)
                    
    
    def move_background(self, pos):
        global CANVAS_X
        global CANVAS_Y
        
        if self.previous_pos is not None:
            CANVAS_X += (pos[0]-self.previous_pos[0])
            CANVAS_Y += (pos[1]-self.previous_pos[1])
            self.update_canvas()
            self.previous_pos = pos
        else:
            self.previous_pos = pos
        
        
        
        """
        try:
            CANVAS_X += (pos[0]-self.previous_pos[0])
            CANVAS_Y += (pos[1]-self.previous_pos[1])
            self.draw_background()
            self.previous_pos = pos
        except AttributeError or TypeError:
            self.previous_pos = pos"""

    
    def paint_icon(self, path, color):
        """Open the icon and change its color."""
        # Load the original icon image
        img = Image.open(path).convert("RGBA")
        
        # Process each pixel to replace black with the selected color
        data = img.getdata()
        new_data = []
        for pixel in data:
            # Check if pixel is black
            if pixel[:3] == (0, 0, 0):  # Black in RGB
                new_data.append((*ImageColor.getrgb(color), pixel[3]))  # Replace with chosen color and original alpha
            else:
                new_data.append(pixel)  # Keep other colors unchanged

        img.putdata(new_data)

        # Return the new icon
        return ImageTk.PhotoImage(img)
    
    
    def update_toolbar(self):
        self.move_button.config(image=self.icons['move'][1], relief="flat")
        self.point_button.config(image=self.icons['point'][1], relief="flat")
        self.add_button.config(image=self.icons['add'][1], relief="flat")
        self.line_button.config(image=self.icons['line'][1], relief="flat")
        self.erase_button.config(image=self.icons['erase'][1], relief="flat")
        self.colorpick_button.config(image=self.icons['colorpick'][1], relief="flat")
        self.bucket_button.config(image=self.icons['bucket'][1], relief="flat")
        self.text_button.config(image=self.icons['text'][1], relief="flat")
        self.save_button.config(image=self.icons['save'][1], relief="flat")
        self.download_button.config(image=self.icons['download'][1], relief="flat")
        self.open_button.config(image=self.icons['open'][1], relief="flat")
        

    def paint_pixel(self, pos, color=None):
        if not color:
            color = self.color
        if 0 < pos[0] < COL_NUM * PIXEL_SIZE and 0 < pos[1] < ROW_NUM * PIXEL_SIZE:
            """Paint a pixel on the canvas and store its color in the grid."""
            x, y = pos[0] // PIXEL_SIZE, pos[1] // PIXEL_SIZE
            self.canvas.create_rectangle(
                x * PIXEL_SIZE, y * PIXEL_SIZE,
                (x + 1) * PIXEL_SIZE, (y + 1) * PIXEL_SIZE,
                fill=color, outline=color
            )
            self.pixel_colors[y][x] = color


    def erase_pixel(self, pos):
        if 0 < pos[0] < COL_NUM * PIXEL_SIZE and 0 < pos[1] < ROW_NUM * PIXEL_SIZE:
            """Erase a pixel from the canvas by setting it to transparent."""
            x, y = pos[0] // PIXEL_SIZE, pos[1] // PIXEL_SIZE
            # Draw over the pixel with the background color
            bg_color = "#D3D3D3" if (x + y) % 2 == 0 else "#FFFFFF"
            self.canvas.create_rectangle(
                x * PIXEL_SIZE, y * PIXEL_SIZE,
                (x + 1) * PIXEL_SIZE, (y + 1) * PIXEL_SIZE,
                fill=bg_color, outline=bg_color
            )
            # Set pixel to transparent in the data grid
            self.pixel_colors[y][x] = None
    
    
    def preview_line(self, pos):
        if 0 < pos[0] < COL_NUM * PIXEL_SIZE and 0 < pos[1] < ROW_NUM * PIXEL_SIZE:
            """Erase the previous line"""
            if self.previous_line != []:
                for pixel in self.previous_line:
                    if not pixel[2]:
                        self.erase_pixel((pixel[0], pixel[1]))
                    else:
                        self.paint_pixel((pixel[0], pixel[1]), pixel[2])
            self.previous_line = []
            
            """Draw a temporary line"""
            if (abs(self.line_start[0] - pos[0]) < abs(self.line_start[1] - pos[1]) and 
                abs(self.line_start[0] - pos[0]) < abs(abs(self.line_start[0] - pos[0]) - abs(self.line_start[1] - pos[1])) ): # Vertical line
                if self.line_start[1] < pos[1]:
                    a, b = self.line_start[1]-PIXEL_SIZE, pos[1]
                else:
                    a, b = pos[1]-PIXEL_SIZE, self.line_start[1]
                    
                for posy in range(a, b):
                    if posy % PIXEL_SIZE == 0:
                        self.previous_line.append([self.line_start[0], posy, self.pixel_colors[posy // PIXEL_SIZE][self.line_start[0] // PIXEL_SIZE]])
                        self.paint_pixel((self.line_start[0], posy))
                        
                        
            elif (abs(self.line_start[1] - pos[1]) < abs(self.line_start[0] - pos[0]) and 
                  abs(self.line_start[1] - pos[1]) < abs(abs(self.line_start[0] - pos[0]) - abs(self.line_start[1] - pos[1])) ): # Horizontal line
                if self.line_start[0] < pos[0]:
                    a, b = self.line_start[0]-PIXEL_SIZE, pos[0]
                else:
                    a, b = pos[0]-PIXEL_SIZE, self.line_start[0]
                    
                for posx in range(a, b):
                    if posx % PIXEL_SIZE == 0:
                        self.previous_line.append([posx, self.line_start[1], self.pixel_colors[self.line_start[1] // PIXEL_SIZE][posx // PIXEL_SIZE]])
                        self.paint_pixel((posx, self.line_start[1]))
            
            else: # Diagonal line
                relative_pos = (pos[0]-self.line_start[0], pos[1]-self.line_start[1])
                try:
                    multx, multy = relative_pos[0]/abs(relative_pos[0]), relative_pos[1]/abs(relative_pos[1])
                except ZeroDivisionError:
                    multx, multy = 1, 1
                deviation = (abs(relative_pos[0]) + abs(relative_pos[1]))/2
                current_deviation = 0
                while current_deviation <= deviation:
                    pointx, pointy = int(self.line_start[0]+(current_deviation*multx)), int(self.line_start[1]+(current_deviation*multy))
                    self.previous_line.append([pointx, pointy, self.pixel_colors[pointy // PIXEL_SIZE][pointx // PIXEL_SIZE]])
                    self.paint_pixel((pointx, pointy))
                    current_deviation += PIXEL_SIZE
                
    
    def draw_line(self, pos):
        if 0 < pos[0] < COL_NUM * PIXEL_SIZE and 0 < pos[1] < ROW_NUM * PIXEL_SIZE:
            
            if (abs(self.line_start[0] - pos[0]) < abs(self.line_start[1] - pos[1]) and 
                abs(self.line_start[0] - pos[0]) < abs(abs(self.line_start[0] - pos[0]) - abs(self.line_start[1] - pos[1])) ): # Vertical line
                if self.line_start[1] < pos[1]:
                    a, b = self.line_start[1]-PIXEL_SIZE, pos[1]
                else:
                    a, b = pos[1]-PIXEL_SIZE, self.line_start[1]
                    
                for posy in range(a, b):
                    if posy % PIXEL_SIZE == 0:
                        self.paint_pixel((self.line_start[0], posy))          
                        
            elif (abs(self.line_start[1] - pos[1]) < abs(self.line_start[0] - pos[0]) and 
                  abs(self.line_start[1] - pos[1]) < abs(abs(self.line_start[0] - pos[0]) - abs(self.line_start[1] - pos[1])) ): # Horizontal line
                if self.line_start[0] < pos[0]:
                    a, b = self.line_start[0]-PIXEL_SIZE, pos[0]
                else:
                    a, b = pos[0]-PIXEL_SIZE, self.line_start[0]
                    
                for posx in range(a, b):
                    if posx % PIXEL_SIZE == 0:
                        self.paint_pixel((posx, self.line_start[1]))
            
            else: # Diagonal line
                relative_pos = (pos[0]-self.line_start[0], pos[1]-self.line_start[1])
                try:
                    multx, multy = relative_pos[0]/abs(relative_pos[0]), relative_pos[1]/abs(relative_pos[1])
                except ZeroDivisionError:
                    multx, multy = 1, 1
                deviation = (abs(relative_pos[0]) + abs(relative_pos[1]))/2
                current_deviation = 0
                while current_deviation <= deviation:
                    pointx, pointy = int(self.line_start[0]+(current_deviation*multx)), int(self.line_start[1]+(current_deviation*multy))
                    self.paint_pixel((pointx, pointy))
                    current_deviation += PIXEL_SIZE
            
            self.line_start = None

    
    def move_mode(self):
        self.action = "Move"
        self.update_toolbar()
        self.move_button.config(image=self.icons['move'][2], relief="groove")
        pass
    
    def point_mode(self):
        self.action = "Point"
        self.update_toolbar()
        self.point_button.config(image=self.icons['point'][2], relief="groove")
        pass
    
    def erase_mode(self):
        self.action = "Erase"
        self.update_toolbar()
        self.erase_button.config(image=self.icons['erase'][2], relief="groove")
        pass
    
    def colorpick_mode(self):
        self.action = "Colorpick"
        self.update_toolbar()
        self.colorpick_button.config(image=self.icons['colorpick'][2], relief="groove")
        pass
    
    def bucket_mode(self):
        self.action = "Bucket"
        self.update_toolbar()
        self.bucket_button.config(image=self.icons['bucket'][2], relief="groove")
        pass
    
    def line_mode(self):
        self.action = "Line"
        self.update_toolbar()
        self.line_button.config(image=self.icons['line'][2], relief="groove")
        self.line_start = None
    
    def add_mode(self):
        self.action = "Add"
        self.update_toolbar()
        self.add_button.config(image=self.icons['add'][2], relief="groove")
        pass
    
    def open_file(self):
        self.action = "Open"
        self.update_toolbar()
        self.open_button.config(image=self.icons['open'][2], relief="groove")
        pass
    
    def text_mode(self):
        self.action = "Text"
        self.update_toolbar()
        self.text_button.config(image=self.icons['text'][2], relief="groove")
        pass
    
    def choose_color(self):
        """Open color chooser dialog to select color."""
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color
            self.color_icon = self.paint_icon("Icons/palette.png", color)
            self.color_button.config(image=self.color_icon)


    def save_image(self):
        """Save the current pixel art as a PNG file."""
        image = Image.new("RGBA", (COL_NUM, ROW_NUM), (255, 255, 255, 0))  # RGBA with transparent background
        
        for y in range(ROW_NUM):
            for x in range(COL_NUM):
                color = self.pixel_colors[y][x]
                if color is not None:  # Only draw non-transparent pixels
                    image.putpixel((x, y), self.hex_to_rgba(color))
        
        image = image.resize((COL_NUM * PIXEL_SIZE, ROW_NUM * PIXEL_SIZE), Image.NEAREST)
        image.save("pixel_art.png")
        print("Image saved as pixel_art.png")
        
    def download_image(self):
        self.action = "Download"
        self.update_toolbar()
        self.download_button.config(image=self.icons['download'][2], relief="groove")
        pass
    
    
    
    def left_mouse_click(self, event):
        action = self.action
        if action == "Point":
            self.paint_pixel((event.x, event.y))
        elif action == "Erase":
            self.erase_pixel((event.x, event.y))
        elif action == "Line":
            if not self.line_start:
                self.previous_line = []
                self.line_start = event.x, event.y
                self.preview_line((event.x, event.y))
            else:
                self.draw_line((event.x, event.y))
                self.previous_line = []
    
    
    def mid_mouse_click(self, event):
        pass
    
    
    def mid_mouse_release(self, event):
        self.previous_pos = None
    
    
    def right_mouse_click(self, event):
        pass
    
    
    def scroll_action(self, event):
        global PIXEL_SIZE
        if event.delta > 0 and PIXEL_SIZE < MAX_PIXEL_SIZE:  # Scroll up (zoom in)
            PIXEL_SIZE += 2  # Adjust zoom increment as needed
            self.update_canvas()
        elif event.delta < 0 and PIXEL_SIZE > MIN_PIXEL_SIZE:  # Scroll down (zoom out)
            PIXEL_SIZE -= 2  # Adjust zoom increment as needed
            self.update_canvas()
    
    
    def mouse_move(self, event):
        action = self.action
        if action == "Line":
            if self.line_start:
                self.preview_line((event.x, event.y))
    
    
    def left_mouse_hold(self, event):
        action = self.action
        if action == "Point":
            self.paint_pixel((event.x, event.y))
        elif action == "Erase":
            self.erase_pixel((event.x, event.y))
    
    
    def mid_mouse_hold(self, event):
        self.move_background((event.x, event.y))
    
    
    def right_mouse_hold(self, event):
        pass
    
    

    @staticmethod
    def hex_to_rgba(hex_color):
        """Convert hex color (#RRGGBB) to RGBA tuple with full opacity."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return rgb + (255,)
    
    

# Run the application
root = tk.Tk()
app = PixelArtApp(root)
root.mainloop()
