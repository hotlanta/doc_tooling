Oxygen Author's logs don't usually indicate on which page an overlapped margin  or individual table cell overflow might be. Here's a script to help locate pages where these overflows occur: \Mondi-Tech\Everyone - BSS\HPE MPC Common\Tools\Scripts\pdf_analyzer.py

Example usage when the python script is run in Command Prompt:
python pdf_analyzer.py "d:\Mondi-Tech\Everyone - BSS\HPE DEG\DEG 5.8\05_drafts\HCLTech_DEG_5_8_Baremetal_User_Guide.pdf" --top 22 --bottom 5 --left 36 --right 37 --cell-tolerance 5 --output overflow_report.txt

If you run pdf_analyzer.py in a different folder than where it is located, use the script as follows: python "D:\Mondi-Tech\Everyone - BSS\HPE MPC Common\Tools\Scripts\pdf_analyzer.py" "D:\Mondi-Tech\Everyone - BSS\HPE DEG\DEG 5.6.13\HCLTech_DEG_5_6_13_ReadMe.pdf"

Everything after "...pdf" is optional. Default values for the margins are top 22pt, bottom 19pt, left 36pt, and right 30pt. Default value for overflow of individual table cells is 3pt (if --no-cells is used instead of --cell-tolerance <x>, then only page margins are checked). Note that in the actual command "pt" is not used.

overflow_report.txt is the file name where the results of the script will be saved if you need such a file. Name can be changed to whatever you want. Default is to only show results in Command Prompt window.

software requirements:
install python (https://www.python.org/downloads/) and install required libraries by using either of the following commands (2nd option worked for me): pip install pypdf pdfplumber or python -m pip install pypdf pdfplumber