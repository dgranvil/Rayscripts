
import sys
import os

# Retrieve the path to RayStation.exe.
# This will only work if the script is run from within RayStation.
path = os.path.normpath(os.path.join(sys.argv[0], '../..'))
#path=r"C:\Program Files\RaySearch Laboratories\RayStation 9 Alpha 1"
sys.path.append(path)

# Add references to libraries for PDF creation.
import clr
clr.AddReference("MigraDoc.DocumentObjectModel-WPF.dll")
clr.AddReference("MigraDoc.Rendering-WPF.dll")
clr.AddReference("PdfSharp-WPF.dll")

# Import objects for PDF creation.
from MigraDoc.DocumentObjectModel import Document
from MigraDoc.Rendering import PdfDocumentRenderer
from PdfSharp import Pdf

# Import object to open the created PDF document.
from System.Diagnostics import Process

# Create a PDF document.
doc = Document()

# Add a section to the document.
sec = doc.AddSection()

# Add a paragraph with the text "Hello world".
sec.AddParagraph('Hello world')

# Render the document.
renderer = PdfDocumentRenderer(True, Pdf.PdfFontEmbedding.Always)
renderer.Document = doc
renderer.RenderDocument()

# Save the file.
filename = os.path.join(os.environ['TEMP'], 'Test.pdf')
renderer.PdfDocument.Save(filename)

# Display the PDF file.
process = Process()
process.StartInfo.FileName = filename
process.Start()


