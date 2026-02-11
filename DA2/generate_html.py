import markdown
import os

# Define styles for printing - OPTIMIZED FOR DENSE, ACADEMIC PDF
CSS = """
<style>
    body {
        font-family: 'Times New Roman', Times, serif; /* Academic standard */
        line-height: 1.35; /* Denser line height */
        font-size: 11pt;   /* Smaller, standard academic size */
        max-width: 800px;  /* Standard A4 width approx */
        margin: 0 auto;
        padding: 30px;
        color: #000;       /* Pure black for print */
        text-align: justify; /* Academic justification */
    }
    h1 {
        font-family: 'Arial', sans-serif;
        font-size: 20pt;
        font-weight: bold;
        border-bottom: 2px solid #000;
        padding-bottom: 5px;
        margin-top: 0;
        margin-bottom: 20px;
        text-align: center;
        text-transform: uppercase;
    }
    h2 {
        font-family: 'Arial', sans-serif;
        font-size: 14pt;
        color: #000;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 1px solid #ccc;
        padding-bottom: 3px;
        font-weight: bold;
    }
    h3 {
        font-family: 'Arial', sans-serif;
        font-size: 12pt;
        color: #333;
        margin-top: 15px;
        margin-bottom: 8px;
        font-weight: bold;
        font-style: italic;
    }
    h4 {
         font-size: 11pt;
         font-weight: bold;
         margin-bottom: 5px;
    }
    p {
        margin-bottom: 10px;
    }
    ul, ol {
        margin-bottom: 10px;
        margin-top: 5px;
        padding-left: 25px;
    }
    li {
        margin-bottom: 2px;
    }
    code {
        font-family: 'Courier New', Courier, monospace;
        font-size: 10pt;
        background-color: #f0f0f0;
        padding: 1px 3px;
    }
    pre {
        background-color: #f5f5f5;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 9pt;
        overflow-x: auto;
        white-space: pre-wrap;
    }
    .diagram {
        font-family: 'Courier New', Courier, monospace;
        white-space: pre;
        font-size: 9pt;
        line-height: 1;
        background: #fff;
        border: 1px solid #000;
        padding: 10px;
        margin: 15px 0;
        display: block;
        width: 100%;
    }
    hr {
        margin: 20px 0;
        border: 0;
        border-top: 1px solid #000;
    }
    /* Citation style */
    blockquote {
        border-left: 3px solid #ccc;
        margin: 10px 0;
        padding-left: 10px;
        font-style: italic;
        color: #555;
    }
    
    @media print {
        body {
            max-width: 100%;
            padding: 0;
            margin: 1.5cm; /* Standard print margins */
        }
        @page {
            margin: 1.5cm;
            size: A4;
        }
    }
</style>
"""

def convert_md_to_html(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Enable extras for definition lists, tables, etc.
    html_content = markdown.markdown(text, extensions=['extra', 'codehilite', 'tables'])
    
    # formatting tweaks
    html_content = html_content.replace('<pre><code>', '<pre class="diagram">') # Try to catch diagrams
    
    final_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{filename.replace('.md', '').replace('_', ' ')}</title>
        {CSS}
    </head>
    <body>
        <div style="text-align: right; font-size: 9pt; margin-bottom: 20px;">
            <strong>Course:</strong> Blockchain & Distributed Ledger Technology<br>
            <strong>Submission:</strong> DA-2<br>
            <strong>Date:</strong> February 2026
        </div>
        {html_content}
        <div style="text-align: center; font-size: 9pt; margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px;">
            <em>Generated for Academic Submission</em>
        </div>
    </body>
    </html>
    """
    
    html_filename = filename.replace('.md', '.html')
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Created {html_filename}")

# Convert the files
files = ['Literature_Review.md', 'Proposed_Work_and_Architecture.md']
for file in files:
    if os.path.exists(file):
        convert_md_to_html(file)
    else:
        print(f"File {file} not found!")
