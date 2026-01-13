# Egon Draw (Ariel's Draw) 🎨

## Overview
Egon Draw is a feature-rich Python drawing application built using Tkinter. It extends the capabilities of the standard canvas to provide a versatile environment for freehand drawing, geometric shape creation, text manipulation, and image management.

## Features

### 🖌️ Drawing Tools
*   **Pencil**: Creates standard lines.
*   **Marker**: Creates lines with square tips.
*   **Pen**: Creates lines with round tips.
*   **Eraser**: Removes content by painting over it (can automatically match canvas background).

### 📏 Line Placing Modes
Control how your input translates to lines on the canvas:
*   **Drag**: Standard freehand drawing.
*   **Straight Lines**: Click to set a start point, drag, and release to create a straight line.
*   **Centered**: Define a center point; subsequent clicks create lines radiating from that center.

### 🔺 Shapes Library
Insert customizable geometric shapes:
*   **Shapes**: Circle, Square, Rectangle, Arc, Chord, Pieslice, Triangle, Right Triangle, Pentagon, Hexagon, Octagon.
*   **Customization**:
    *   **Size & Width**: Adjust the scale and border thickness.
    *   **Dash Patterns**: Define custom dash sizes and spacing for borders.
    *   **Advanced Attributes**: Adjust XY ratios for rectangles, start/extent angles for arcs, and pointing direction for polygons.

### ✍️ Text Engine
Add and style text directly on the canvas:
*   **Typography**: Select from all system-installed fonts.
*   **Styling**: Adjust size, toggle Bold/Underline.
*   **Orientation**: Rotate text to any angle (0-360°).

### 🎨 Color & Appearance
*   **Primary & Secondary Colors**: distinct selection for fill and outline colors.
*   **Canvas Background**: Change the working area's background color.
*   **UI Themes**: The application attempts to adapt to the OS theme (Vista theme on Windows, specific frame colors for macOS).

### 🛠️ Advanced Settings
Access the **Options** menu (gear icon) for deep customization:
*   **Visuals**: Adjust window transparency, UI colors, and button relief styles.
*   **Interface Mode**: Switch between the standard Button Layout and a compact Menu Bar Layout.
*   **Canvas Control**: Enable horizontal/vertical scrollbars and set scroll increments.
*   **Movement**: Configure how items are moved (via Mouse or Keyboard) and adjust sensitivity/ratios.
*   **Line Options**: Toggle line smoothing and connection behaviors.

### 📂 File Management
*   **Save Image**: Export your work as PNG, JPG, or JPEG.
*   **Save PostScript**: Export as `.ps` (supports PDF conversion if `ps2pdf` is available).
*   **Upload Image**: Import existing images onto the canvas for editing or tracing.

## Controls & Shortcuts ⌨️

| Action | Input | Description |
| :--- | :--- | :--- |
| **Draw** | `Left Click` | Draw lines or place shapes/text. |
| **Move Item** | `Right Click` | Drag to move items (if enabled in settings). |
| **Move Canvas** | `Arrow Keys` | Move the entire drawing or selected items. |
| **Change Size** | `Scroll Wheel` | Increase/Decrease tool size. |
| **Undo** | `Ctrl + Z` | Undo the last action. |
| **Fullscreen** | `F11` | Toggle fullscreen mode. |
| **Move Left** | `Left Arrow` | Move paint left. |
| **Move Right** | `Right Arrow` | Move paint right. |
| **Move Up** | `Up Arrow` | Move paint up. |
| **Move Down** | `Down Arrow` | Move paint down. |

## Installation & Running 🚀

1.  **Prerequisites**: Ensure Python is installed.
2.  **Dependencies**: Install the Pillow library for image handling.
    ```bash
    pip install Pillow
    ```
3.  **Launch**:
    Run the live version file:
    ```bash
    python "draw/draw.py"
    ```

## Development Roadmap & History 📅

### Soft-Launch Strategy ⌛
The program is currently in a "soft-launch" phase. This approach is designed to relieve development pressure, ensuring that features are not rushed and that additions are fully fleshed out before major releases.

### Update History

#### Update 1 - Initial Release
*   **Core Canvas**: Freehand line drawing with basic options (size, color, eraser, neutral mode).
*   **File Management**: Capabilities to upload and save images.
*   **Text System**: Basic text addition with font, size, and tone controls.
*   **Customization**: Initial set of settings and shortcut functionalities.

#### Update 2 - Shapes, Text, Cords, and much more
*   **Shapes & Text**: Enhanced shape insertion and text functionalities with extensive customization.
*   **Drawing Modes**: Introduction of special coordinate placement modes (Straight & Centered lines).
*   **Interaction**: Added "Move Paint" functionality using the mouse button, with configurable options.
*   **UI Enhancements**: Added subsidiary UI elements and configuration options.
*   **Save Methods**: Introduction of new saving formats and methods.
*   **Technical Improvements**: Improved line detection algorithms and expanded settings.

#### Update 3 - Magnet, Bitmaps, and Usage Stats
*   **Magnet Tool**: A new tool to move items closer to a reference point, allowing for precise adjustments.
*   **Bitmap Support**: Added the ability to insert system bitmaps (icons) onto the canvas.
*   **Usage Statistics**: A new feature to track and display usage statistics such as time spent drawing, most used tools, and item counts.
*   **Color Editing**: Added a dedicated "Edit Color" button to change the color of existing items on the canvas.
*   **UI Refinements**: Reorganized the UI layout to accommodate new features, including a new "Bonus" frame for usage stats and GitHub link.
*   **Performance**: Optimized window resizing and initial placement logic.
*   **Stability**: Implemented thread-safe UI updates, robust error handling for file operations, and safer tool state management.

### Future Updates
#### Update 4 - The Facelift
*   **UI Overhaul**: Introduced a Ribbon interface, Professional Status Bar, and Modern Options menu.
*   **New Tools**: Added Magnet, Grid System, Eyedropper, and Diamond Brush.
*   **Content**: Added Bitmaps (icons) and new shapes (Heart, Star).
*   **Features**: Implemented Usage Statistics and "Edit Color" functionality.
*   **Polish**: Professional neutral theme, improved tool hints, and stability fixes.

### Future Updates
*   **Update 5**: ???

---
*Project maintained by Ariel.*
