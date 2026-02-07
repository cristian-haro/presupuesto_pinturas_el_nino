from fpdf import FPDF
from datetime import datetime
import os
from utils import get_resource_path, get_app_path

class QuotePDF(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path
        # Add Unicode fonts
        # Check for Windows Arial
        if os.path.exists("c:/windows/fonts/arial.ttf"):
            self.add_font("Arial", "", "c:/windows/fonts/arial.ttf", uni=True)
            self.add_font("Arial", "B", "c:/windows/fonts/arialbd.ttf", uni=True)
            self.add_font("Arial", "I", "c:/windows/fonts/ariali.ttf", uni=True)
        # Check for Linux Liberation Sans (Docker)
        elif os.path.exists("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
            self.add_font("Arial", "", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", uni=True)
            self.add_font("Arial", "B", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", uni=True)
            self.add_font("Arial", "I", "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", uni=True)
        else:
            # Fallback to standard core fonts (might lack some unicode chars but won't crash)
            pass

    def header(self):
        # Company Info
        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, 'PINTURAS EL NIÑO', new_x="LMARGIN", new_y="NEXT", align='L')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Samuel Martín Alcántara', new_x="LMARGIN", new_y="NEXT", align='L')
        self.cell(0, 5, '74744540Z', new_x="LMARGIN", new_y="NEXT", align='L')
        self.cell(0, 5, 'info@pinturaselnino.com', new_x="LMARGIN", new_y="NEXT", align='L')
        self.cell(0, 5, '654749368', new_x="LMARGIN", new_y="NEXT", align='L')
        self.cell(0, 5, 'C/ Viento 4, Salobreña', new_x="LMARGIN", new_y="NEXT", align='L')
        
        # Logo handling
        # Assuming logo is approx 40x40mm. Position at Top Right: x=160, y=10
        logo_drawn = False
        
        if self.logo_path and os.path.exists(self.logo_path):
             try:
                 self.image(self.logo_path, 160, 10, 35)
                 logo_drawn = True
             except:
                 pass # Fallback if image is invalid
        
        if not logo_drawn:
            # Check default locations using resource path
            default_logo = get_resource_path('logo.png')
            if os.path.exists(default_logo):
                self.image(default_logo, 160, 10, 35)
            elif os.path.exists('logo.jpg'):
                self.image('logo.jpg', 160, 10, 35)
            else:
                # Draw a placeholder box if no logo
                self.set_draw_color(200, 200, 200)
                self.rect(160, 10, 35, 35)
                self.set_xy(160, 25)
                self.set_font('Arial', 'I', 8)
                self.cell(35, 5, '(Logo)', align='C')

        self.ln(40) # Space after header

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

def generate_pdf(services, description, price, detailed_price_text=None, logo_path=None, client_name=None, validity="3 meses"):
    pdf = QuotePDF(logo_path=logo_path)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Body
    pdf.set_font('Arial', '', 12)
    
    # Intro
    pdf.cell(0, 10, 'Este presupuesto incluye las siguientes partes:', new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.ln(2)
    
    # Services List
    for service in services:
        pdf.cell(10) # Indent
        pdf.cell(5, 5, '\u2022', align='C') # Bullet point
        pdf.multi_cell(0, 5, service)
        pdf.ln(1)
        
    pdf.ln(5)
    
    # Description Paragraph
    pdf.multi_cell(0, 6, description, markdown=True)
    pdf.ln(5)
    
    # Price Paragraph
    # "Yo me comprometo a la aportación de todo el material y/o herramienta necesaria..."
    if detailed_price_text:
        price_text = detailed_price_text
    else:
        price_text = (
            f"Yo me comprometo a la aportación de todo el material y/o herramienta necesaria para la "
            f"realización de dicho trabajo, teniendo este un coste total de {price}."
        )
    
    pdf.multi_cell(0, 6, price_text)
    pdf.ln(5)
    
    # Payment Terms
    payment_terms = (
        "Para la realización de este, habrá que abonar el 30% del coste total al empezar el trabajo. "
        "La no respuesta a este anulará el mismo y se dará por cancelado el trabajo. "
        f"Este presupuesto tendrá una validez de {validity}."
    )
    pdf.multi_cell(0, 6, payment_terms)
    
    pdf.ln(30)
    
    # Date and Signature
    current_date = datetime.now()
    # Spanish date format: "2 de febrero de 2026"
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
              "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    date_str = f"{current_date.day} de {months[current_date.month - 1]} de {current_date.year}"
    
    pdf.set_x(100) # Move to right side
    pdf.cell(0, 10, f"Atentamente, Pinturas El Niño a {date_str}.", align='R')
    
    # Output file
    # Optimize filename with client name if available
    date_part = current_date.strftime('%Y%m%d_%H%M%S')
    if client_name:
        # Sanitize client name (remove forbidden chars)
        safe_name = "".join([c for c in client_name if c.isalnum() or c in (' ', '_', '-')]).strip().replace(' ', '_')
        filename = f"Presupuesto_{safe_name}_{date_part}.pdf"
    else:
        filename = f"Presupuesto_{date_part}.pdf"
        
    output_path = os.path.join(get_app_path(), filename)
    pdf.output(output_path)
    return output_path



def main():
    print("--- Generador de Presupuestos - Pinturas El Niño ---\n")
    
    print("Introduce los servicios a realizar (escribe 'fin' para terminar):")
    services = []
    while True:
        line = input("> ")
        if line.lower() == 'fin':
            if not services:
                print("Debes añadir al menos un servicio.")
                continue
            break
        if line.strip():
            services.append(line.strip())
            
    print("\nIntroduce la descripción del trabajo (puede ser largo):")
    description = input("> ")
    
    print("\nIntroduce el precio total (ej: 2100€ IVA incluido):")
    price = input("> ")
    
    # Construct the full price paragraph with the input price
    price_paragraph = (
        f"Yo me comprometo a la aportación de todo el material y/o herramienta necesaria para la "
        f"realización de dicho trabajo, teniendo este un coste total de {price}."
    )
    
    generate_pdf(services, description, price, detailed_price_text=price_paragraph)
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
