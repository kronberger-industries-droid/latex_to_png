import argparse
import os
import re
import subprocess
import csv
import logging
from tabulate import tabulate

# Set up logging configuration to capture detailed debug information
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class EquationProcessor:
    def __init__(self, file_path, output_path, resolution, color):
        """
        Initialize the EquationProcessor with necessary parameters.

        Args:
            file_path (str): Path to the CSV file containing equations.
            output_path (str): Directory where the output PNG images will be saved.
            resolution (int): Resolution for the output PNG images.
            color (str): Hex color code for the equations in the output images.
        """
        self.file_path = file_path
        self.output_path = os.path.join(os.getcwd(), output_path)
        self.resolution = resolution
        self.color = color

    def read_equation_list(self):
        """Reads equations from the provided CSV file, skipping the header."""
        equations = []
        with open(self.file_path, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            for row in reader:
                if (
                    row[0] == "1"
                ):  # Filtering valid rows assuming '1' indicates a valid entry
                    equations.append((row[1].strip(), row[2].strip()))
        return equations

    def clean_filename(self, filename):
        """Cleans a filename to remove unwanted characters, allowing only alphanumeric, underscore, and dot."""
        return re.sub(r"[^a-zA-Z0-9_.]", "", filename)

    def wrap_equation_in_latex(self, equation, color):
        """Wraps the provided equation in a LaTeX document template with consistent font size and controlled height."""
        color_code = color.lstrip("#")
        return f"""
        \\documentclass[border=1pt]{{standalone}}
        \\usepackage{{amsmath}}
        \\usepackage{{xfrac}}
        \\usepackage{{gfsneohellenicot}}
        \\usepackage{{xcolor}}
        \\definecolor{{equationcolor}}{{HTML}}{{{color_code}}}
        \\begin{{document}}
        \\setbox0\\hbox{{\\Large \\textcolor{{equationcolor}}{{${equation}$}}}}
        \\dimen0=12mm
        \\ifdim\\ht0<\\dimen0
        \\ht0=\\dimen0
        \\fi
        \\ifdim\\dp0<5mm
        \\dp0=5mm
        \\fi
        \\box0
        \\end{{document}}"""

    def check_create_folder(self):
        """Ensures the output folder exists, creating it if necessary."""
        os.makedirs(self.output_path, exist_ok=True)
        logging.info(f'Ensured folder "{self.output_path}" exists.\n\n')

    def compile_latex_file(self, tex_file):
        """Compiles a LaTeX file into a PDF and logs the compiler output with verbose real-time output."""
        try:
            output_dir = os.path.abspath(self.output_path).replace("\\", "/")
            tex_file_unix = tex_file.replace("\\", "/")

            process = subprocess.Popen(
                ["xelatex", f"-output-directory={output_dir}", tex_file_unix],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Print and log output in real-time
            full_output = []
            for line in process.stdout:
                print(line, end="")  # Print to console in real-time
                full_output.append(line)
                logging.debug(line.strip())  # Log each line

            process.wait()

            if process.returncode != 0:
                logging.error(f"LaTeX Compiler Errors:\n{''.join(full_output)}")
            else:
                logging.info(
                    f"Compiled LaTeX file successfully: {os.path.basename(tex_file)}"
                )
                logging.debug(f"LaTeX Compiler Output:\n{''.join(full_output)}")

        except Exception as e:
            logging.error(
                f"LaTeX compilation failed for {os.path.basename(tex_file)}: {str(e)}"
            )

    def convert_pdf_to_png(self, pdf_file, png_file):
        """Converts a PDF file to PNG format using ImageMagick's `convert` command."""
        try:
            pdf_file_unix = pdf_file.replace("\\", "/")
            png_file_unix = png_file.replace("\\", "/")
            subprocess.run(
                [
                    "magick",
                    "convert",
                    "-density",
                    str(self.resolution),
                    "-quality",
                    "100",
                    pdf_file_unix,
                    png_file_unix,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            logging.info(f"Converted PDF to PNG: {os.path.basename(pdf_file)}\n")
        except subprocess.CalledProcessError as e:
            logging.error(
                f"PDF to PNG conversion failed for {os.path.basename(pdf_file)}: {e}"
            )

    def cleanup_files(self):
        """Cleans up intermediate files generated during the processing."""
        file_extensions = [".log", ".aux", ".tex", ".pdf"]
        deleted_files = 0
        for root, dirs, files in os.walk(self.output_path):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    os.remove(os.path.join(root, file))
                    deleted_files += 1
        logging.info(
            f"\nDeleted {deleted_files} intermediate files and build directories."
        )

    def process_equations(self):
        """Main processing function for equations from a CSV file to PNG images."""
        self.check_create_folder()
        equations = self.read_equation_list()
        print("Loaded Equations:")
        headers = ["Index", "Equation", "Filename"]
        table = [[i, eq[0], eq[1]] for i, eq in enumerate(equations, start=1)]
        print(tabulate(table, headers=headers, tablefmt="grid"))
        confirmation = (
            input("\n\nDo you want to proceed with these equations? (y/n): ")
            .strip()
            .lower()
        )
        if confirmation != "y":
            print("Operation cancelled by user.")
            return
        for i, (equation, filename) in enumerate(equations, start=1):
            latex_content = self.wrap_equation_in_latex(equation, self.color)
            base_filename = self.clean_filename(
                filename if filename else f"equation_{i}"
            )
            tex_filename = base_filename + ".tex"
            increment = 1
            while os.path.exists(os.path.join(self.output_path, tex_filename)):
                tex_filename = f"{base_filename}_{increment}.tex"
                increment += 1
            tex_file_path = os.path.join(self.output_path, tex_filename)
            with open(tex_file_path, "w") as tex_file:
                tex_file.write(latex_content)
            print("test 1")
            self.compile_latex_file(tex_file_path)
            print("test 2")
            pdf_file_path = tex_file_path.replace(".tex", ".pdf")
            png_file_path = tex_file_path.replace(".tex", ".png")
            self.convert_pdf_to_png(pdf_file_path, png_file_path)
        self.cleanup_files()


def main():
    parser = argparse.ArgumentParser(
        description="Process equations from a CSV file into PNG images."
    )
    parser.add_argument("--file_path", default=None, help="Path to the CSV file.")
    parser.add_argument("--output_path", default="output", help="Output directory.")
    parser.add_argument("--resolution", type=int, default=600, help="Image resolution.")
    parser.add_argument(
        "--color",
        default="#2B363A",
        help="Equation color in hex format. (standard gray: #2b363a, black: #000000, red: #ff0000, blue: #0000ff, green: #00ff00, etc.)",
    )
    args = parser.parse_args()
    if not args.file_path:
        args.file_path = input("Enter the path to the CSV file: ").strip()
    processor = EquationProcessor(
        args.file_path, args.output_path, args.resolution, args.color
    )
    processor.process_equations()


if __name__ == "__main__":
    main()
