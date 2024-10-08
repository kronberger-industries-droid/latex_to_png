# LaTeX Equation Processor

The LaTeX Equation Processor is a Python tool designed to convert equations from a CSV file into standalone PNG images with consistent font size and visual height. This tool is particularly useful for generating high-quality equation images for use in documentation, presentations, and educational materials.

## Dependencies

This tool relies on several external applications and Python libraries. Ensure you have the following installed:

### External Applications:
- **TeX Live** or **MikTeX**: LaTeX distribution that includes `xelatex`.
   - **When on Arch Linux**:
     ```bash
      sudo pacman -S texlive-xetex texlive-pictures texlive-latexrecommended texlive-latexextra texlive-latex texlive-fontsrecommended texlive-fontsextra texlive-bin texlive-basic
      ```
- **ImageMagick**: Tool for image conversion, specifically used here to convert PDFs to PNGs.

### Python Libraries:
- `argparse` - For parsing command-line options.
- `os` - For OS-dependent functionality.
- `re` - For regular expression matching.
- `subprocess` - For running external commands.
- `csv` - For reading CSV files.
- `shutil` - For file and directory management.
- `logging` - For outputting logs.
- `tabulate` - For formatting tables in the terminal.

## Installation

1. **Install LaTeX Distribution:**
   - For **Windows**: Download and install from [MikTeX](https://miktex.org) or [TeX Live](http://tug.org/texlive/).

2. **Install ImageMagick:**
   - For **Windows**: Download and install from [ImageMagick Download](https://imagemagick.org/script/download.php).
   
3. **Install GhostScript:**
   - For **Windows**: Download and install from [GhostScript Download](https://ghostscript.com/releases/gsdnld.html)

4. **Install Python Dependencies:**
   - If python is not installed yet. Go to [Python](https://www.python.org/) and install the latest version for your system. (Tested on Python 3.13.3)

## Usage

To use the LaTeX Equation Processor, prepare a CSV file with the following format:
- Use a header
- The first column should indicate validity of the equation with '1' (where '1' means valid).
- The second column should contain the LaTeX equation text.
- The third column should contain the desired filename for the output image.

### Command Line Syntax:
First make sure you are in the directory where you installed the Application.

```bash
python equation_processor.py --file_path PATH_TO_CSV --output_path OUTPUT_DIRECTORY [--resolution 300] [--color #2b363a]
```

- `--file_path`: Path to the CSV file containing the equations.
- `--output_path`: Directory where output PNG images will be saved (default: `output`).
- `--resolution`: Resolution of the output PNG images, in DPI (default: 300).
- `--color`: Color of the equation text in hex format (default: `#2b363a`).

### Example:

```bash
python equation_processor.py --file_path equations.csv --output_path images
```

This will process each equation in `equations.csv` and save the resulting PNG images in the `images` directory.

## Troubleshooting

If you encounter issues with LaTeX compilation or ImageMagick conversion, check the following:
- Ensure all LaTeX packages required in the script are installed.
- Confirm that ImageMagick permissions are set to allow PDF to PNG conversions, especially on macOS and Windows.

For further assistance, consult the application logs or adjust the logging level in the script.
