from fitz import open
from typing import Dict

data_upper = {
    "Last Name": "DELA CRUZ",
    "First Name": "JUAN",
    "Middle Name": "SANTOS",
    "No. & Street/Sitio": "123 MAIN ST",
    "Barangay": "SAN ISIDRO",
    "Municipality": "CEBU CITY",
    "Province": "CEBU",
    "Cell phone Number": "09123456789",
}

data_side = {
    "Age_Applicant": "30",  # Age 1
    "Bank Name": "LandBank of the Philippines",
    "Bank Account No.": "1234567890",
    "Bank Branch / Address": "Cebu City",
    "Spouse": "Genetta Cruz",
    "Beneficiaries": "Maria Cruz",
    "Age_Beneficiary": "40",  # Age 2
    "Relationship": "Sister",
}

class RegFormStamper:
    def __init__(self, form_path: str):
        self.form_path = form_path
        self.doc = open(form_path)
        
    def text_search(self, fontsize, stamp_op, form_data: Dict[str, str], output_path: str):
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            
            for field_name, value in form_data.items():
                if '_' in field_name and field_name.split('_')[0] == "Age":
                    actual_field_name = field_name.split('_')[0]
                    text_instances = page.search_for(actual_field_name)

                    if text_instances:
                        if '_Applicant' in field_name: # Age Applicant
                            instance_index = 2
                        elif '_Beneficiary' in field_name: # Age Beneficiary
                            instance_index = 3
                        else:
                            instance_index = 0
                        
                        if instance_index < len(text_instances):
                            label_rect = text_instances[instance_index]
                            page.draw_rect(label_rect, color=(1, 0, 0), width=0.5)
                            
                            # if stamp_op == 1:
                            self.insert_upper(page, label_rect, fontsize, value)
                            # else:
                                # self.insert_side(page, label_rect, fontsize, value)
                else:
                    # Regular field without suffix - search for the full field name
                    text_instances = page.search_for(field_name)
                    
                    if text_instances:
                        # For regular fields, just use the first instance
                        label_rect = text_instances[0]
                        page.draw_rect(label_rect, color=(1, 0, 0), width=0.5)
                        
                        # if form_data == data_upper:
                        self.insert_upper(page, label_rect, fontsize, value)
                        # else:
                            # self.insert_side(page, label_rect, fontsize, value)

        self.doc.save(output_path)

    # Insert text above label
    def insert_upper(self, page, label_rect, fontsize, value):
        page.insert_text(
            (label_rect.x0, label_rect.y0 - fontsize),
            value,
            fontsize=fontsize,
            color=(0, 0, 0)
        )

    # Insert text side of label
    def insert_side(self, page, label_rect, fontsize, value):
        page.insert_text(
            (label_rect.x1 + fontsize, label_rect.y1 - label_rect.height / 2),
            value,
            fontsize=fontsize,
            color=(0, 0, 0)
        )
    
    def box_search(self, form_data: Dict[str, str], output_path: str):
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
        
        for field_name, value in form_data.items():
            text_instances = page.search_for(field_name)

        if text_instances:
            label_rect = text_instances[0]
            page.draw_rect(label_rect, color=(1, 0, 0), width=0.5)
            
        self.doc.save(output_path)


    # Function to close document
    def close(self):
        """Close the PDF document"""
        if hasattr(self, 'doc'):
            self.doc.close()

# Usage example
def main():
    ...
    
if __name__ == "__main__":
    main()