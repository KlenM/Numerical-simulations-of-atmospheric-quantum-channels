import subprocess
from pathlib import Path


def convert(path='plots'):
    for plot in Path(path).glob('*.pdf'):
        print(f"Converting {plot.name}")
        command = (f"gs -sOutputFile={plot.parent}/monochrome/{plot.name} "
                "-sDEVICE=pdfwrite -sColorConversionStrategy=Gray "
                "-dProcessColorModel=/DeviceGray -dCompatibilityLevel=1.4 "
                f"-dNOPAUSE -dBATCH {plot}")
        subprocess.run(command, shell=True, check=True)

if __name__ == "__main__":
    convert()
