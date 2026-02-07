import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext
import sys
import os
import json
from utils import get_app_path, get_resource_path

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quote_generator import generate_pdf

EXTERNAL_CONFIG = os.path.join(get_app_path(), "config.json")
BUNDLED_CONFIG = get_resource_path("config.json")

class QuoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Presupuestos - Pinturas El Niño")
        
        # Load Config
        self.config = self.load_config()
        
        # Center the window
        window_width = 1000
        window_height = 1000
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Main container with padding
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Presupuesto Pinturas El Niño", font=("Helvetica", 18, "bold"), bootstyle="primary")
        title_label.pack(pady=(0, 20))

        # --- Client Data Section ---
        client_frame = ttk.Labelframe(main_frame, text="Datos del Cliente", padding="10")
        client_frame.pack(fill=X, pady=5)
        
        ttk.Label(client_frame, text="Nombre del Cliente (Para guardar el archivo):").pack(side=LEFT, padx=(0, 5))
        self.client_name_entry = ttk.Entry(client_frame)
        self.client_name_entry.pack(side=LEFT, fill=X, expand=True)

        # --- Logo Section ---
        logo_frame = ttk.Labelframe(main_frame, text="Logotipo (Opcional)", padding="10")
        logo_frame.pack(fill=X, pady=5)
        
        self.logo_path_var = tk.StringVar(value=self.config.get("logo_path", ""))
        
        logo_inner = ttk.Frame(logo_frame)
        logo_inner.pack(fill=X)
        
        self.logo_entry = ttk.Entry(logo_inner, textvariable=self.logo_path_var, state='readonly')
        self.logo_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        logo_btn = ttk.Button(logo_inner, text="📂 Seleccionar", command=self.select_logo, bootstyle="secondary-outline")
        logo_btn.pack(side=LEFT)

        # --- Services Section ---
        services_frame = ttk.Labelframe(main_frame, text="Servicios", padding="10")
        services_frame.pack(fill=BOTH, expand=True, pady=10)

        # Input area
        input_frame = ttk.Frame(services_frame)
        input_frame.pack(fill=X, pady=(0, 5))
        
        self.service_entry = ttk.Entry(input_frame)
        self.service_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.service_entry.bind("<Return>", self.add_service)
        
        add_btn = ttk.Button(input_frame, text="Añadir", command=self.add_service, bootstyle="success")
        add_btn.pack(side=LEFT, padx=5)

        # Favorites
        favorites = self.config.get("favorites", [])
        self.fav_combo = ttk.Combobox(input_frame, values=favorites, state="readonly", width=30)
        self.fav_combo.set("Seleccionar Favorito...")
        self.fav_combo.pack(side=LEFT, padx=5)
        self.fav_combo.bind("<<ComboboxSelected>>", self.add_favorite)

        # List area
        self.services_listbox = tk.Listbox(services_frame, height=5, selectmode=tk.SINGLE, borderwidth=1, relief="solid")
        self.services_listbox.pack(fill=BOTH, expand=True, pady=5)
        
        del_btn = ttk.Button(services_frame, text="Eliminar Seleccionado", command=self.remove_service, bootstyle="danger-outline")
        del_btn.pack(anchor=E)

        # --- Description Section ---
        desc_frame = ttk.Labelframe(main_frame, text="Descripción del Trabajo", padding="10")
        desc_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Toolbar
        toolbar_frame = ttk.Frame(desc_frame)
        toolbar_frame.pack(fill=X, pady=(0, 5))
        
        ttk.Label(toolbar_frame, text="Formato: ", font=("Arial", 9, "bold")).pack(side=LEFT)
        
        # Bold Button
        btn_bold = ttk.Button(toolbar_frame, text="Negrita", width=8, bootstyle="secondary-outline", command=self.apply_bold)
        btn_bold.pack(side=LEFT, padx=2)
        
        # Italic Button
        btn_italic = ttk.Button(toolbar_frame, text="Cursiva", width=8, bootstyle="secondary-outline", command=self.apply_italic)
        btn_italic.pack(side=LEFT, padx=2)
        
        ttk.Label(toolbar_frame, text="(Selecciona texto y pulsa)", font=("Arial", 8, "italic"), bootstyle="secondary").pack(side=LEFT, padx=10)

        self.desc_text = scrolledtext.ScrolledText(desc_frame, height=6, wrap=tk.WORD, font=("Arial", 10))
        self.desc_text.pack(fill=BOTH, expand=True)
        
        default_desc = (
            "Se sanearán las grietas y desconchones. Se aplicará una mano de fijador de cal y agua "
            "a las partes donde se haya quitado la pintura en mal estado o esté la pared virgen. "
            "Se terminará con dos manos de pintura de primera calidad."
        )
        self.desc_text.insert(tk.END, default_desc)

        # --- Price Section ---
        price_frame = ttk.Labelframe(main_frame, text="Precio Final", padding="10")
        price_frame.pack(fill=X, pady=10)
        
        price_inner_frame = ttk.Frame(price_frame)
        price_inner_frame.pack(fill=X)

        ttk.Label(price_inner_frame, text="Importe Total:").pack(side=LEFT)
        self.price_entry = ttk.Entry(price_inner_frame, width=15)
        self.price_entry.pack(side=LEFT, padx=5)
        
        ttk.Label(price_inner_frame, text="€").pack(side=LEFT)
        
        ttk.Label(price_inner_frame, text="IVA:").pack(side=LEFT, padx=(20, 5))
        self.iva_combo = ttk.Combobox(price_inner_frame, values=["IVA incluido", "+ IVA", "Sin IVA", "(Personalizado)"], state="readonly", width=15)
        self.iva_combo.pack(side=LEFT)
        self.iva_combo.set(self.config.get("default_iva", "IVA incluido"))
        
        # Validity
        ttk.Label(price_inner_frame, text="Validez:").pack(side=LEFT, padx=(20, 5))
        self.validity_entry = ttk.Entry(price_inner_frame, width=15)
        self.validity_entry.pack(side=LEFT)
        self.validity_entry.insert(0, self.config.get("default_validity", "3 meses"))
        
        # --- Action Buttons ---
        btn_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        btn_frame.pack(fill=X, pady=10)

        generate_btn = ttk.Button(btn_frame, text="GENERAR PDF", command=self.generate_pdf_action, bootstyle="primary", width=20)
        generate_btn.pack(side=RIGHT)
        
        exit_btn = ttk.Button(btn_frame, text="Salir", command=self.on_close, bootstyle="secondary", width=10)
        exit_btn.pack(side=LEFT)

    def load_config(self):
        # 1. Try EXTERNAL (User preferences)
        if os.path.exists(EXTERNAL_CONFIG):
            try:
                with open(EXTERNAL_CONFIG, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        
        # 2. Try BUNDLED (Defaults inside EXE)
        if os.path.exists(BUNDLED_CONFIG):
            try:
                with open(BUNDLED_CONFIG, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
                
        # 3. Fallback
        return {}

    def save_config(self):
        # Update config with current values
        self.config["logo_path"] = self.logo_path_var.get()
        self.config["default_validity"] = self.validity_entry.get()
        self.config["default_iva"] = self.iva_combo.get()
        # Theme is read-only for now unless we add a selector, so keep existing or default
        if "theme" not in self.config:
            self.config["theme"] = "flatly"
            
        try:
            # ALWAYS save to external config so settings persist
            with open(EXTERNAL_CONFIG, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def on_close(self):
        self.save_config()
        self.root.destroy()

    def apply_bold(self):
        self._wrap_selection("**")

    def apply_italic(self):
        self._wrap_selection("__") 

    def _wrap_selection(self, wrapper):
        try:
            sel_start = self.desc_text.index("sel.first")
            sel_end = self.desc_text.index("sel.last")
            
            selected_text = self.desc_text.get(sel_start, sel_end)
            if not selected_text: return
            
            new_text = f"{wrapper}{selected_text}{wrapper}"
            
            self.desc_text.delete(sel_start, sel_end)
            self.desc_text.insert(sel_start, new_text)
        except tk.TclError:
            pass 

    def add_service(self, event=None):
        service = self.service_entry.get().strip()
        if service:
            self.services_listbox.insert(tk.END, service)
            self.service_entry.delete(0, tk.END)

    def add_favorite(self, event=None):
        selected = self.fav_combo.get()
        if selected and selected != "Seleccionar Favorito...":
            self.services_listbox.insert(tk.END, selected)
            self.fav_combo.set("Seleccionar Favorito...") # Reset

    def remove_service(self):
        selection = self.services_listbox.curselection()
        if selection:
            self.services_listbox.delete(selection[0])

    def select_logo(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar Logo",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.logo_path_var.set(file_path)

    def generate_pdf_action(self):
        self.save_config() # Save preferences on generate

        # Gather Data
        services = list(self.services_listbox.get(0, tk.END))
        if not services:
            messagebox.showwarning("Faltan datos", "Por favor, añade al menos un servicio.")
            return

        description = self.desc_text.get("1.0", tk.END).strip()
        if not description:
            messagebox.showwarning("Faltan datos", "Por favor, añade una descripción.")
            return

        amount = self.price_entry.get().strip()
        iva_option = self.iva_combo.get()
        logo_path = self.logo_path_var.get()
        client_name = self.client_name_entry.get().strip()
        validity = self.validity_entry.get().strip()
        
        if not validity:
            validity = "3 meses" 
        
        if not amount:
            messagebox.showwarning("Faltan datos", "Por favor, indica un precio.")
            return

        # Construct Price String
        if iva_option == "(Personalizado)":
             full_price_str = f"{amount}€"
        else:
             full_price_str = f"{amount}€ {iva_option}"

        price_paragraph = (
            f"Yo me comprometo a la aportación de todo el material y/o herramienta necesaria para la "
            f"realización de dicho trabajo, teniendo este un coste total de {full_price_str}."
        )

        try:
            output_path = generate_pdf(
                services, 
                description, 
                full_price_str, 
                detailed_price_text=price_paragraph, 
                logo_path=logo_path,
                client_name=client_name,
                validity=validity
            )
            
            msg = f"PDF Generado exitosamente:\n{output_path}\n\n¿Quieres abrirlo ahora?"
            if messagebox.askyesno("Éxito", msg):
                os.startfile(output_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el PDF:\n{str(e)}")

def main():
    # Helper to load config for theme
    theme = "flatly"
    
    # Check External
    if os.path.exists(EXTERNAL_CONFIG):
        try:
            with open(EXTERNAL_CONFIG, "r", encoding="utf-8") as f:
                c = json.load(f)
                theme = c.get("theme", "flatly")
        except:
             pass
    # Check Bundled
    elif os.path.exists(BUNDLED_CONFIG):
         try:
            with open(BUNDLED_CONFIG, "r", encoding="utf-8") as f:
                c = json.load(f)
                theme = c.get("theme", "flatly")
         except:
             pass

    root = ttk.Window(themename=theme) 
    app = QuoteApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
