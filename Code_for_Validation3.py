from lxml import etree
#import tkinter.filedialog
import os
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog

def open_file_dialog():
    app = QApplication(sys.argv)

    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFiles)
    dialog.setViewMode(QFileDialog.Detail)  # User can sort by column (e.g., date)
    dialog.setOption(QFileDialog.DontUseNativeDialog, False)
    dialog.setNameFilter("Tcx Files (*.tcx)")

    selected_files = []
    if dialog.exec_():
        selected_files = dialog.selectedFiles()

    return selected_files

# Load the schema and the XML file
schema_path = "TrainingCenterDatabasev2.xsd"  # Replace with the path to the Garmin TCX schema


# Open file dialog to select multiple files
file_paths = open_file_dialog()

#file_paths = tkinter.filedialog.askopenfilenames(title="Select tcxfiles",
#                                         filetypes=[("tcxfiles", "*.tcx")])
# Process each file
for file_path in file_paths:
    print(f"Processing: {file_path}")
#    with open(file_path, 'r', encoding='utf-8') as file:
#        content = file.read()
#        print(content[:100])  # Print the first 100 characters as an example


#input_file = tkinter.filedialog.askopenfilename(filetypes=[("tcxfile", "*.tcx")])
    basename_without_ext = os.path.splitext(os.path.basename(file_path))[0]
    print(basename_without_ext)
    dirname = os.path.dirname(file_path)
    output_file2 = dirname+"/"+basename_without_ext+".tcx"
    xml_path = output_file2

    try:
        # Parse the schema
        with open(schema_path, 'rb') as schema_file:
            schema_root = etree.XML(schema_file.read())
            schema = etree.XMLSchema(schema_root)

        # Parse and validate the XML file
        with open(xml_path, 'rb') as xml_file:
            xml_doc = etree.parse(xml_file)

        # Validate and capture errors
        is_valid = schema.validate(xml_doc)
        if is_valid:
            print("The TCX file is valid!")
        else:
            # Retrieve detailed error log
            for error in schema.error_log:
                print(f"Line {error.line}, Column {error.column}: {error.message}")

    except etree.XMLSchemaParseError as e:
        print(f"Schema parsing error: {e}")
    except etree.XMLSyntaxError as e:
        print(f"XML syntax error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")