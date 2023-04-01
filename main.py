import PyPDF2 
import re


# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        contract_text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            contract_text += page_text
    # print(json.dumps(contract_text))
    return contract_text

# Extract attributes from text
def extract_attributes(contract_text):

    # Define regular expression for Contract Number
    contract_number_regex = r"CONTRACT \( Proc\. Inst\. Ident \) NO\.\s+([\w-]+)"

    # Define regular expression for effective date extraction
    effective_date_regex = r"EFFECTIVE DATE\s+(\d{1,2}\s+\w{3}\s+\d{4})"

    # Define regular expression for Rating
    rating_regex = r'RATING\s+([\w:]+\s*\w+)'

    # Define regular expression for Request Project Number
    request_project_regex = r" REQUISITION/PURCHASE REQUEST PROJECT NO.\s+([\w\s]+)\n"

    # Define regular expression for Contract Officer
    contract_officer_regex = r'NAME OF CONTRACTING OFFICER\s+([\w\s]+\n)'

    # Define regular expression for Date Signed
    date_signed_regex = r'DATE SIGNED\s+(\d{1,2}[A-Z]{3}\d{4})'

    # Extract Contract Number
    contract_number_match = re.search(contract_number_regex, contract_text)

    # Extract Rating
    rating_match = re.search(rating_regex, contract_text)

    # Extract Effective Date
    effective_date_math = re.search(effective_date_regex, contract_text)

    # Extract Request Project Number
    request_project_match = re.search(request_project_regex, contract_text)

    # Extract Contract Officer
    contract_officer_match = re.search(contract_officer_regex, contract_text)

    # Extract Date Signed
    date_signed_match = re.search(date_signed_regex, contract_text)

    return {
        'Contract Number': contract_number_match.group(1) if contract_number_match else None,
        'Rating': rating_match.group(1) if rating_match else None,
        'Effective Date': effective_date_math.group(1) if effective_date_math else None,
        'Request Project': request_project_match.group(1) if request_project_match else None,
        'Contract Officer': contract_officer_match.group(1) if contract_officer_match else None,
        'Date Signed': date_signed_match.group(1) if date_signed_match else None
        
    }

# Extract line items from text
def extract_line_items(contract_text):
    line_items = []
    number_pattern = re.compile(r'Item No\.\s+(\d+)')
    items_pattern = re.compile(r'Quantity U/I[^\n]+')
    number_matches = number_pattern.finditer(contract_text)
    items_matches = items_pattern.findall(contract_text)

    for num_match, item_match in zip(number_matches, items_matches):
        item_no = num_match.group(1)
        elements = item_match.split()
        items = combine_elements(elements)
        index = contract_text.find(item_match)
        end_of_quantity_line = index + len(item_match)+1
        value_line = contract_text[end_of_quantity_line:].split('\n', 1)[0].strip() 
        values = value_line.split()       
        line_items.append({
            'Item No': item_no,
            'items': ",".join(items),
            'values': ",".join(values)
        }) 

    return line_items

 
# Extract clauses from text
def extract_clauses(text):
    # Find the CONTRACT CLAUSES section
    contract_clauses_section = re.search(r'SECTION I\nCONTRACT CLAUSES(.+?)(?=PART III|\Z)', text, flags=re.DOTALL)
    if contract_clauses_section:
        clauses_text = contract_clauses_section.group(1)
    else:
        return {}

    clauses_list = re.split(r'\n\s*\n', clauses_text.strip())
    return clauses_list


KEYWORDS_MAP = {
    "Estimated": ["Unit Cost", "Unit Cost", "Total Price", "Total Cost"],
    "Unit": ["Price", "Cost"],
    "Total": ["Estimated Cost","Price", "Cost"],
    "Fee": ["Percentage"],
}

# Combine the elements in the list based on the keywords map
def combine_elements(elements):
    combined = []
    skip_next = False
    i = 0
    while(i<len(elements)):
        if elements[i] not in KEYWORDS_MAP:
            combined.append(elements[i])
            i+=1
        else:
            combine_word = elements[i]
            key = elements[i]
            i+=1
            for value in KEYWORDS_MAP[key]:
                value_len = len(value.split())
                if " ".join(elements[i:i + value_len]) == value:
                    combine_word = combine_word + " " + value
                    i+=value_len
            combined.append(combine_word)
    return combined


def main(pdf_path):
    contract_text = extract_text_from_pdf(pdf_path)
    attributes = extract_attributes(contract_text)
    line_items = extract_line_items(contract_text)
    clauses = extract_clauses(contract_text)

    with open('output.txt', 'w') as f:
        f.write("======Attributes===============:\n")
        for key, value in attributes.items():
            f.write(f"{key}: {value}\n")

        f.write("======Line Items===============:\n")
        for i, item in enumerate(line_items):
            f.write(f"{i+1}. {item}\n")

        f.write("======Clauses=================:\n")
        for clause in clauses:
            f.write(f"{clause}\n\n")

    print("Output saved to output.txt. successefully!")


if __name__ == '__main__':
    pdf_path = 'contract.pdf'
    main(pdf_path)


  









# clauses_heading_regex = r'^CONTRACT CLAUSES\s*(.*)$'
# clauses_start = re.search(clauses_heading_regex, contract_text, re.MULTILINE)
# Define the regular expression pattern to match the "CONTRACT CLAUSES" section and extract the clauses

# clauses_regex = r'SECTION I\s+CONTRACT CLAUSES\s+([\d\.\-\s]+)\n'

# # Search for the pattern in the contract text and extract the clauses
# clauses_start = re.search(clauses_regex, contract_text)
# if clauses_start:
#     clauses_text = clauses_start.group(1)
# else:
#     clauses_text = ""
# print(clauses_text)

# # Split the text into individual clauses
# clauses_list = re.findall(r'([\d\.\-]+)\s+([^\n]+)\n', clauses_text)

# # Format the clauses as a list of dictionaries with clause number and text
# clauses = [{"number": number.strip(), "text": text.strip()} for number, text in clauses_list]

# # Print the clauses
# for clause in clauses:
#     print(f"{clause['number']}:\n{clause['text']}\n")


# Print the clauses in the desired format
# for match in clause_matches:
#     clause_number = match[0]
#     clause_title = match[1]
#     clause_date = match[2]
#     clause_text = match[3].strip()
#     print(f"Clause {clause_number} ({clause_date}): {clause_title}\n{clause_text}")

# nlp = spacy.load('en_core_web_sm')

# def extract_clauses(text):
#     doc = nlp(text)
#     clauses = []
#     for ent in doc.ents:
#         if ent.label_ == 'CLAUSE':
#             clauses.append(ent.text)
#     return clauses

# clauses = extract_clauses(contract_text)

# Output extracted information
# print(f'Contract Number: {contract_number}')
# # print(f'Solicitation Number: {solicitation_number}')
# print(f'Rating: {rating}')
# print('Effective Date:', effective_date)
# etc.

# for i in range(len(unit_price_matches)):
#     print(f'Line Item {i+1}: Unit Price={unit_price_matches[i]}, Quantity={quantity_matches[i]}, Amount={amount_matches[i]}')
    
# for clause in clauses:
#     print(f'Clause: {clause}')



