from fpdf import FPDF

def gerar_pdf_relatorio(active_drivers, df_passengers, selected_day):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False) 
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    titulo = f"Relatório de Caronas - {selected_day}"
    pdf.cell(0, 10, titulo.encode('latin-1', 'replace').decode('latin-1'), 0, 1, "C")
    pdf.ln(5)
    
    col = 0
    y_start = pdf.get_y()
    max_y = y_start
    col_width = 60
    margin_x = 10  
    gap = 5     
    
    for idx, driver in active_drivers:
        driver_name = driver['Nome']
        try:
            total_vagas = int(driver['Vagas'])
        except:
            total_vagas = 4
        
        current_passengers = df_passengers[df_passengers[selected_day] == driver_name]
        ocupados = len(current_passengers)
        
        if col == 0 and y_start > 250:
            pdf.add_page()
            y_start = pdf.get_y()
            max_y = y_start
        
        x = margin_x + col * (col_width + gap)
        pdf.set_xy(x, y_start)
        
        pdf.set_font("Arial", "B", 10)
        txt_mot = f"{driver_name} ({ocupados}/{total_vagas})"
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(col_width, 7, txt_mot.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=2, align="C", fill=True)
        
        pdf.set_font("Arial", "", 9)
        if ocupados == 0:
            pdf.cell(col_width, 6, "Vazio".encode('latin-1', 'replace').decode('latin-1'), border=1, ln=2, align="C")
        else:
            for _, p in current_passengers.iterrows():
                p_name = p['Nome'][:25]
                pdf.cell(col_width, 6, f" {p_name}".encode('latin-1', 'replace').decode('latin-1'), border=1, ln=2, align="L")
        
        current_y = pdf.get_y()
        if current_y > max_y:
            max_y = current_y
        
        col += 1
        if col == 3:
            col = 0
            y_start = max_y + 5

    try:
        return bytes(pdf.output())
    except:
        return pdf.output(dest="S").encode("latin-1")