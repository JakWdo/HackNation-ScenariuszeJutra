import PyPDF2
import re

def extract_data_from_pdf(filepath):
    pdfFileObj = open(filepath, 'rb') 

    pdfReader = PyPDF2.PdfReader(pdfFileObj) 

    pageObj = pdfReader.pages[3] # spis tresci
    extracted_text = pageObj.extract_text()
    pattern = r'\d+\s+\w.*'
    headings = list(re.findall(pattern, extracted_text))
    headings_cleaned = [x.replace('\xa0', ' ') for x in headings]
    metadata = [{int(re.findall(r'\d+', x)[0]): re.sub(r'\d+', '', x).strip() for x in headings_cleaned}][0]
    return pdfReader, metadata

def ingest_single_text(): 
    pass



if __name__ == '__main__': 
    filepath = './data/tone_styling/tone.pdf'

    pdfReader, metadata = extract_data_from_pdf(filepath)

    for i, (key, val) in enumerate(metadata.items()): 
        if i == 0: 
            continue
        else: 
            print(val)
            starting_page = i
            ending_page = list(metadata.keys())[i+1] if i != len(list(metadata.keys())) else list(metadata.keys())[i]

            starting_paragraph = val
            ending_paragraph = metadata[list(metadata.keys())[i+1]] if i != len(list(metadata.keys())) else metadata[list(metadata.keys())[i]]

            text = ""
            for page_num in range(starting_page, ending_page+1): 
                page_content = pdfReader.pages[page_num].extract_text()
                text += page_content

            start_index = text.find(starting_paragraph)
            end_index = text.find(ending_paragraph)

            if start_index != -1 and end_index != -1 and start_index < end_index:
                content_between = text[start_index:end_index].strip()
                # print(f"Content for '{val}':\n{content_between}\n---")



