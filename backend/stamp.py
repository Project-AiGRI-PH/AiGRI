from fitz import open
from typing import Dict

# assuming data fetched from RSBSA reg database 
data_upper = {
    "Last Name": "DELA CRUZ",
    "First Name": "JUAN",
    "Middle Name": "SANTOS",
}

# other data inputted on route: 
data_side = {
    "Bank Name": "LandBank of the Philippines",
    "Bank Account No.": "1234567890",
    "Bank Branch / Address": "Cebu City",
}

class RegFormStamper:
    def __init__(self, form_path: str):
        self.form_path = form_path
        self.doc = open(form_path)
    
    # ref
    def text_search(self, fontsize, stamp_op, form_data: Dict[str, str], output_path: str):
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]

            for field_name, value in form_data.items():
                if field_name.startswith("farm_"):
                    # Example: "farm_sitio_1" -> "Sitio"
                    label = field_name.split("_")[1].capitalize()
                    text_instances = page.search_for(label)

                    if text_instances:
                        # Use 2nd instance if available, else fallback
                        instance_index = 1 if len(text_instances) > 1 else 0
                        label_rect = text_instances[instance_index]

                        page.draw_rect(label_rect, color=(0, 0, 1), width=0.5)
                        self.insert_side(page, label_rect, fontsize, value)

                else:
                    # Regular fields → place above the label
                    text_instances = page.search_for(field_name)
                    if text_instances:
                        label_rect = text_instances[0]
                        page.draw_rect(label_rect, color=(1, 0, 0), width=0.5)
                        self.insert_upper(page, label_rect, fontsize, value)

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