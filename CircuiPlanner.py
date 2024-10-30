import os
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageColor


# Configuration
COL_NUM = 80
ROW_NUM = 40
PIXEL_SIZE = 20  # Size of each square in pixels

class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CircuiPlanner")
        self.color = "#000000"  # Default color (black)
        self.action = "Point"

        """Create the toolbar."""
        # Create toolbar on the left
        self.toolbar = tk.Frame(root, width=60, bg="lightgray")
        self.toolbar.pack(side="left", fill="y")

        # Load or create icons for toolbar
        self.load_icons()
        
        # Move button
        self.move_button = tk.Button(self.toolbar, image=self.move_icon, command=self.move_mode, bg="lightgray", relief="flat")
        self.move_button.pack(padx=4, pady=10)
        
        # Point button
        self.point_button = tk.Button(self.toolbar, image=self.point_icon, command=self.point_mode, bg="lightgray", relief="flat")
        self.point_button.pack(padx=4, pady=10)
        
        # Add button
        self.add_button = tk.Button(self.toolbar, image=self.add_icon, command=self.add_mode, bg="lightgray", relief="flat")
        self.add_button.pack(padx=4, pady=10)
        
        # Line button
        self.line_button = tk.Button(self.toolbar, image=self.line_icon, command=self.line_mode, bg="lightgray", relief="flat")
        self.line_button.pack(padx=4, pady=10)
        
        # Erase button
        self.erase_button = tk.Button(self.toolbar, image=self.erase_icon, command=self.erase_mode, bg="lightgray", relief="flat")
        self.erase_button.pack(padx=4, pady=10)
        
        # Color selection button
        self.color_button = tk.Button(self.toolbar, image=self.color_icon, command=self.choose_color, bg="lightgray", relief="flat")
        self.color_button.pack(padx=4, pady=10)
        
        # Colorpick button
        self.colorpick_button = tk.Button(self.toolbar, image=self.colorpick_icon, command=self.colorpick_mode, bg="lightgray", relief="flat")
        self.colorpick_button.pack(padx=4, pady=10)
        
        # Bucket button
        self.bucket_button = tk.Button(self.toolbar, image=self.bucket_icon, command=self.bucket_mode, bg="lightgray", relief="flat")
        self.bucket_button.pack(padx=4, pady=10)
        
        # Text button
        self.text_button = tk.Button(self.toolbar, image=self.text_icon, command=self.text_mode, bg="lightgray", relief="flat")
        self.text_button.pack(padx=4, pady=10)
        
        # Save button
        self.save_button = tk.Button(self.toolbar, image=self.save_icon, command=self.save_image, bg="lightgray", relief="flat")
        self.save_button.pack(padx=4, pady=10)
        
        # Download button
        self.download_button = tk.Button(self.toolbar, image=self.download_icon, command=self.download_image, bg="lightgray", relief="flat")
        self.download_button.pack(padx=4, pady=10)
        
        # Open button
        self.open_button = tk.Button(self.toolbar, image=self.open_icon, command=self.open_file, bg="lightgray", relief="flat")
        self.open_button.pack(padx=4, pady=10)
        
        

        # Canvas for drawing
        self.canvas = tk.Canvas(root, width=COL_NUM * PIXEL_SIZE, height=ROW_NUM * PIXEL_SIZE)
        self.canvas.pack(side="right")
        
        # Draw checkered background
        self.draw_background()
        
        # Event bindings for canvas
        self.canvas.bind("<Button-1>", self.left_mouse_click)
        self.canvas.bind("<Button-2>", self.mid_mouse_click)
        self.canvas.bind("<Button-3>", self.right_mouse_click) 
        self.canvas.bind("<Button-4>", self.scroll_up) 
        self.canvas.bind("<Button-5>", self.scroll_down) 
        self.canvas.bind("<B1-Motion>", self.left_mouse_hold)
        self.canvas.bind("<B2-Motion>", self.mid_mouse_hold)
        self.canvas.bind("<B3-Motion>", self.right_mouse_hold)
        
        # Initialize a grid to keep track of pixel colors
        self.pixel_colors = [[None for _ in range(COL_NUM)] for _ in range(ROW_NUM)]
        
    def load_icons(self):
        """Load the icons for the toolbar."""
        # Load color icon from the specified file path
        self.move_icon = ImageTk.PhotoImage(Image.open("Icons/arrows.png"))
        self.save_icon = ImageTk.PhotoImage(Image.open("Icons/disk.png"))
        self.download_icon = ImageTk.PhotoImage(Image.open("Icons/download.png"))
        self.erase_icon = ImageTk.PhotoImage(Image.open("Icons/eraser.png"))
        self.colorpick_icon = ImageTk.PhotoImage(Image.open("Icons/eye-dropper.png"))
        self.bucket_icon = ImageTk.PhotoImage(Image.open("Icons/fill.png"))
        self.color_icon = ImageTk.PhotoImage(Image.open("Icons/palette.png"))
        self.line_icon = ImageTk.PhotoImage(Image.open("Icons/plug-connection.png"))
        self.point_icon = ImageTk.PhotoImage(Image.open("Icons/pen-clip.png"))
        self.add_icon = ImageTk.PhotoImage(Image.open("Icons/plus-hexagon.png"))
        self.open_icon = ImageTk.PhotoImage(Image.open("Icons/subfolder.png"))
        self.text_icon = ImageTk.PhotoImage(Image.open("Icons/text.png"))


    def draw_background(self):
        """Draw a checkered background on the canvas."""
        for y in range(ROW_NUM):
            for x in range(COL_NUM):
                color = "#D3D3D3" if (x + y) % 2 == 0 else "#FFFFFF"  # Alternate between light gray and white
                self.canvas.create_rectangle(
                    x * PIXEL_SIZE, y * PIXEL_SIZE,
                    (x + 1) * PIXEL_SIZE, (y + 1) * PIXEL_SIZE,
                    fill=color, outline=color
                )

    
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
    
    
    def move_mode(self):
        self.move_icon = self.paint_icon("Icons/arrows.png", '#646464')
        self.move_button.config(image=self.move_icon, relief="groove")
        pass
    
    def point_mode(self):
        self.action = "Point"
        self.point_icon = self.paint_icon("Icons/pen-clip.png", '#646464')
        self.point_button.config(image=self.point_icon, relief="groove")
        pass
    
    def erase_mode(self):
        self.action = "Erase"
        self.erase_icon = self.paint_icon("Icons/eraser.png", '#646464')
        self.erase_button.config(image=self.erase_icon, relief="groove")
        pass
    
    def colorpick_mode(self):
        pass
    
    def bucket_mode(self):
        pass
    
    def line_mode(self):
        pass
    
    def add_mode(self):
        pass
    
    def open_file(self):
        pass
    
    def text_mode(self):
        pass
    
    def choose_color(self):
        """Open color chooser dialog to select color."""
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color
            self.color_icon = self.paint_icon("Icons/palette.png", color)#242424
            self.color_button.config(image=self.color_icon)


    def paint_pixel(self, event):
        if 0 < event.x < COL_NUM * PIXEL_SIZE and 0 < event.y < ROW_NUM * PIXEL_SIZE:
            """Paint a pixel on the canvas and store its color in the grid."""
            x, y = event.x // PIXEL_SIZE, event.y // PIXEL_SIZE
            self.canvas.create_rectangle(
                x * PIXEL_SIZE, y * PIXEL_SIZE,
                (x + 1) * PIXEL_SIZE, (y + 1) * PIXEL_SIZE,
                fill=self.color, outline=self.color
            )
            self.pixel_colors[y][x] = self.color

    def erase_pixel(self, event):
        self.erase_icon = self.paint_icon("Icons/eraser.png", '#646464')
        self.erase_button.config(image=self.erase_icon, relief="groove")
        if 0 < event.x < COL_NUM * PIXEL_SIZE and 0 < event.y < ROW_NUM * PIXEL_SIZE:
            """Erase a pixel from the canvas by setting it to transparent."""
            x, y = event.x // PIXEL_SIZE, event.y // PIXEL_SIZE
            # Draw over the pixel with the background color
            bg_color = "#D3D3D3" if (x + y) % 2 == 0 else "#FFFFFF"
            self.canvas.create_rectangle(
                x * PIXEL_SIZE, y * PIXEL_SIZE,
                (x + 1) * PIXEL_SIZE, (y + 1) * PIXEL_SIZE,
                fill=bg_color, outline=bg_color
            )
            # Set pixel to transparent in the data grid
            self.pixel_colors[y][x] = None

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
        pass
    
    
    
    
    
    def left_mouse_click(self, event):
        action = self.action
        if action == "Point":
            self.paint_pixel(event)
        elif action == "Erase":
            self.erase_pixel(event)
    
    
    def mid_mouse_click(self, event):
        pass
    
    
    def right_mouse_click(self, event):
        pass
    
    
    def scroll_up(self, event):
        pass
    
    
    def scroll_down(self, event):
        pass
    
    
    def left_mouse_hold(self, event):
        action = self.action
        if action == "Point":
            self.paint_pixel(event)
        elif action == "Erase":
            self.erase_pixel(event)
    
    
    def mid_mouse_hold(self, event):
        pass
    
    
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
