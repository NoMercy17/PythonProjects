import os
from PyPDF2 import PdfReader, PdfWriter


source_directory = 'C:/Users/Antonio/PycharmProjects/PDF'
output_directory = 'C:/Users/Antonio/PycharmProjects/PDF/Output_project'

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.mkdir(output_directory)

# Collect all .pdf files in the source directory
pdf_files = [f for f in os.listdir(source_directory) if f.endswith('.pdf')]


pdf_reader_cover_path = os.path.join(source_directory, 'cover.pdf')


if not os.path.exists(pdf_reader_cover_path):
    print(f"Error: 'cover.pdf' not found in {source_directory}")
else:
    # Open the cover PDF and extract the first page
    pdf_reader_cover = PdfReader(pdf_reader_cover_path)
    page_cover = pdf_reader_cover.pages[0]  


    for file in pdf_files:
        if file == 'cover.pdf':
            continue  # Skip the cover itself

        pdf_path = os.path.join(source_directory, file)
        pdf_reader = PdfReader(pdf_path)
        pdf_writer = PdfWriter()

        # Add the cover page first
        pdf_writer.add_page(page_cover)

        # Add the pages from the current PDF
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

        # Save the new PDF to the output directory with "_with_cover" in the name
        output_file_path = os.path.join(output_directory, f"{os.path.splitext(file)[0]}_with_cover.pdf")

        # Write the new PDF with the added cover
        with open(output_file_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        print(f"Processed {file} and saved to {output_file_path}")

