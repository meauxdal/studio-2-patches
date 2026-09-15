# Hagley archival transformations

This repository preserves canonical Hagley digital downloads and converts them into proper binary images.

Canonical input names preserve Hagley's archival labeling. Generated filenames
instead describe the program, variant, or fragment established by the research;
they are not generic page ranges or repetitions of an uncertain archive label.

## Build

The Python 3 build.py script will scan its own directory for Hagley extracted binaries.

It will also scan /hagley if it exists.

```text
python build.py
python build.py --check
```

Output files are placed in /derived in per-accession directories.

Input files are not modified.
