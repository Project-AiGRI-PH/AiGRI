from fitz import open
from typing import Dict

# assuming data fetched from RSBSA reg database 
class RegFormStamper:
    def __init__(self, form_path: str):
        self.form_path = form_path
        self.doc = open(form_path)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self):
        """Context manager exit - ensures document is closed"""
        self.close()
        return False
    
    # ref
    def text_search(self, fontsize, form_data: Dict[str, str], output_path: str):
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]

            for field_name, value in form_data.items():
                if field_name.startswith("farm_"):

                    # Example: "farm_sitio_1" -> "Sitio"
                    label = field_name.split("_")[1].capitalize()
                    text_instances = page.search_for(label) # returns integer count of matches

                    if text_instances:
                        # Use 2nd instance if available, else fallback
                        instance_index = 1 if len(text_instances) > 1 else 0
                        label_rect = text_instances[instance_index]

                        page.draw_rect(label_rect, color=(0, 0, 1), width=0.5)
                        self.insert_side2(page, label_rect, fontsize, value)
                
                # First instance for farmer fields for draft stamper
                elif field_name.startswith("farmer_"):
                    # Example: "farmer_last" -> "Last"
                    label = field_name.split("_")[1].capitalize()
                    # print(label)
                    text_instances = page.search_for(label)
                    
                    label_rect = text_instances[0]    
                    page.draw_rect(label_rect, color=(1, 0, 0), width=0.5)

                    if label == "Bank name" or label == "Bank account no." or label == "Bank branch / address":
                        self.insert_side1(page, label_rect, fontsize, value)
                    else:
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

    # Insert text side of label first
    def insert_side1(self, page, label_rect, fontsize, value):
        page.insert_text(
            (label_rect.x1 + fontsize, label_rect.y1 - label_rect.height / 2),
            value,
            fontsize=fontsize,
            color=(0, 0, 0)
        )
    
    # Insert text side of label
    def insert_side2(self, page, label_rect, fontsize, value):
        input_field_x = 145

        page.insert_text(
            (input_field_x, label_rect.y1),
            value,
            fontsize=fontsize,
            color=(0, 0, 0)
        )

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