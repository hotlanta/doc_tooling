import markdown
from markdown.extensions import tables

def add_sources_to_dita(dita_file):
    header_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE concept PUBLIC "-//OASIS//DTD DITA Concept//EN" "concept.dtd">
<concept id="OPENSOURCE">
  <title>Open Source Components</title>
  <conbody>
    <table frame="all" rowsep="1" colsep="1" id="table_h3w_3xn_cbc">
    <title>Open Source Components</title>
    <tgroup cols="4">
    <colspec colname="c1" colnum="1" colwidth="1*"/>
    <colspec colname="c2" colnum="2" colwidth="1*"/>
    <colspec colname="c3" colnum="3" colwidth="1*"/>
    <colspec colname="c4" colnum="4" colwidth="1*"/>
    <thead>
    </thead>
    <tbody>
"""

    end_content = """</tbody>
    </tgroup>
  </table>
  </conbody>
</concept>
"""

    # Read existing content from DITA file
    with open(dita_file, 'r', encoding='utf-8') as file:
        dita_content = file.read()

    # Combine source content with existing DITA content
    final_content = header_content + '\n' + dita_content + '\n' + end_content

    # Write the combined content back to the DITA file
    with open(dita_file, 'w', encoding='utf-8') as file:
        file.write(final_content)

def convert_markdown_to_dita(markdown_file, dita_file):
    # Read the Markdown file
    with open(markdown_file, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Parse Markdown content
    md = markdown.Markdown(extensions=['tables'])
    md_content = md.convert(markdown_content)

    # Convert Markdown tables to DITA tables
    dita_content = md_content.replace('<table>', '<table frame="all" rowsep="1" colsep="1">')
    dita_content = dita_content.replace('<thead>', '<tgroup cols="4">')
    dita_content = dita_content.replace('<tbody>', '')
    dita_content = dita_content.replace('</thead>', '')
    dita_content = dita_content.replace('</tbody>', '')

    # Keep the replacement lines from {lines2}
    dita_content = dita_content.replace('<tr>', '<row>')
    dita_content = dita_content.replace('</tr>', '</row>')
    dita_content = dita_content.replace('<th>', '<entry>')
    dita_content = dita_content.replace('</th>', '</entry>')
    dita_content = dita_content.replace('<td>', '<entry>')
    dita_content = dita_content.replace('</td>', '</entry>')

    # Write the converted content to DITA file
    with open(dita_file, 'w', encoding='utf-8') as file:
        file.write(dita_content)

# Convert Markdown file to DITA file
convert_markdown_to_dita('HPE_TAS_450_Opensources.md', 'converted.dita')

# Add source content to DITA file
add_sources_to_dita('converted.dita')
