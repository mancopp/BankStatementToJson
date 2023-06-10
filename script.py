import re
import json
import os
from PyPDF2 import PdfReader

current_directory = os.getcwd()

folder_name = 'pdf_files'
folder_path = os.path.join(current_directory, folder_name)

transactions = []

for filename in os.listdir(folder_path):
    if filename.endswith('.pdf'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            lines = text.split('\n')
            date_regex = r'\d{4}\.\d{2}\.\d{2}'
            amount_regex = r'-?\d{1,3}(?: \d{3})*(?:,\d{2})'

            i = 0
            first_date_line_encountered = ''
            while i < len(lines):
                line = lines[i].strip()
                if re.match(date_regex, line):
                    if first_date_line_encountered != '':
                        transaction = {'date': first_date_line_encountered, 'description': '', 'amount': ''}
                        first_date_line_encountered = ''
                        i += 1
                        while i < len(lines) and not re.match(date_regex, lines[i]) and not re.match(amount_regex, lines[i]):
                            transaction['description'] += lines[i].strip() + ' '
                            i += 1
                        if i < len(lines) and re.match(amount_regex, lines[i]):
                            amount = re.search(amount_regex, lines[i]).group().replace(' ', '').replace(',', '.')
                            transaction['amount'] = float(amount)
                        if transaction['description'] and transaction['amount']:
                            transactions.append(transaction)
                    else:
                        first_date_line_encountered = line
                else:
                    i += 1

sorted_transactions = sorted(transactions, key=lambda t: t['date'])

data = {'transactions': sorted_transactions}

json_data = json.dumps(data, indent=4)

output_file = 'bank_statement.json'
with open(output_file, 'w') as json_file:
    json_file.write(json_data)

print(f"JSON file '{output_file}' exported successfully.")
