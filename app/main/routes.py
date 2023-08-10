import os
import json
import time
import pandas as pd

from flask import render_template, request, send_file, after_this_request
from werkzeug.utils import secure_filename
from . import main

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    """Renders the tpose landing page

    Returns:
        str: HTML output
    """

    return render_template('index.html')

@main.route('/do', methods = ["GET", "POST"])
def do():
    """Converts the t-scan CSV to Excel (POST only)

    Returns:
        Response: Flask response which forces the browser to download the Excel file
    """

    if request.method != "POST":
        return "This endpoint only accepts POST requests."
    
    if "csv" not in request.files:
        return "Missing file."
    
    file = request.files["csv"]
    if file.filename == '':
        return "No selected file"
    
    cache_dir = os.path.abspath(os.environ["CACHE_DIR"])
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Save the file to cache
        file_path = os.path.join(cache_dir, filename)
        file.save(file_path)

    # Load into pandas
    df = pd.read_csv(file_path, sep=",", header=0, index_col=False)
    
    # Create Excel filename
    excel_path = f"{file_path}.xlsx"

    # Build the Excel Writer
    writer = pd.ExcelWriter(excel_path,
                        engine='xlsxwriter',
                        engine_kwargs={'options': {'strings_to_numbers': True}})
    sheet_name = "t_pose" # funny funny

    df.to_excel(writer, sheet_name=sheet_name, index=False)

    workbook  = writer.book
    worksheet = writer.sheets[sheet_name]   

    # Prepare float and int formats    
    float_format = workbook.add_format({'num_format': '0.000000'})
    int_format = workbook.add_format({'num_format': '0'})

    # Set the appropriate formats where needed
    for index, column in enumerate(df.dtypes):
        if column == "float64":
            worksheet.set_column(index, index, None, float_format)
        elif column == "int64":
            worksheet.set_column(index, index, None, int_format)

    # Close the Excel file
    writer.close()

    # After the Excel file has been downloaded, remove the Excel and CSV files
    @after_this_request
    def remove_file(response):
        try:
            os.remove(excel_path)
            os.remove(file_path)
        except Exception as error:
            return "Oops?"
        return response

    return send_file(excel_path, as_attachment=True)