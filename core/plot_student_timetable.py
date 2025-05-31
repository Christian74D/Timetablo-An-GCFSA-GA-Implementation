from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
from core.generate_individual import generate_gene
from core.constants import DAYS, HOURS, blocked_color, multisec_color, lunch_color
from tqdm import tqdm
import pickle
from datetime import datetime
with open("data/heuristic_allocation.pkl", "rb") as f:
        data, encoded_df, section_data, subject_map, staff_map = pickle.load(f)

def create_section_tables(gene, section_name, styles, normal_style, data, data_lookup):
    elements = []

    timetable = gene[section_name]
    table_data = []
    header_row = [""] + [f"Period {i+1}" for i in range(HOURS)]
    table_data.append(header_row)

    lunch_cells = []
    blocked_cells = []
    multisec_cells = []

    for day in range(DAYS):
        row = [f"Day {day+1}"]
        for hour in range(HOURS):
            entry = timetable[day][hour]
            if entry:
                subject_code = ",\n".join(entry[1]) if isinstance(entry[1], list) else entry[1]
                text = f"{subject_code} ({entry[0]})"
                cell_content = Paragraph(text, normal_style)
                if "nan" in data_lookup[entry[0]]["staffs"]:
                    lunch_cells.append((day, hour))
                elif len(data_lookup[entry[0]]["sections"]) > 1:
                    multisec_cells.append((day, hour))
                elif data_lookup[entry[0]]["block"]:
                    blocked_cells.append((day, hour))
                
            else:
                cell_content = ""
            row.append(cell_content)
        table_data.append(row)

    total_width = 720
    day_col_width = 80
    period_col_width = (total_width - day_col_width) / HOURS
    col_widths = [day_col_width] + [period_col_width] * HOURS

    timetable_table = Table(table_data, colWidths=col_widths)

    timetable_style = [
        ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    for day, hour in lunch_cells:
        timetable_style.append(('BACKGROUND', (hour+1, day+1), (hour+1, day+1), lunch_color))

    for day, hour in blocked_cells:
        timetable_style.append(('BACKGROUND', (hour+1, day+1), (hour+1, day+1), blocked_color))

    for day, hour in multisec_cells:
        timetable_style.append(('BACKGROUND', (hour+1, day+1), (hour+1, day+1), multisec_color))

    
    timetable_table.setStyle(TableStyle(timetable_style))

    staff_table_data = []
    staff_table_data.append(["ID", "Subject Codes", "Staff Names", "Theory", "Lab"])

    for item in data:
        if section_name in item["sections"] and item["theory"] + item["lab"] > 0:
            subject_codes = ", ".join(item["subjects"]) if item["subjects"] else "N/A"
            staff_names_str = ", ".join(item["staffs"]) if item["staffs"] else "N/A"
            theory_str = str(item["theory"]) if item["theory"] is not None else "N/A"
            lab_str = str(item["lab"]) if item["lab"] is not None else "N/A"
            staff_table_data.append([
                str(item["id"]),
                Paragraph(subject_codes, normal_style),
                Paragraph(staff_names_str, normal_style),
                theory_str,
                lab_str
            ])

    staff_table = Table(staff_table_data, colWidths=[60, 200, 250, 80, 80])
    staff_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(Paragraph(f"Timetable and Staff Details for {section_name}", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(KeepTogether([
        timetable_table,
        Spacer(1, 20),
        staff_table
    ]))

    return elements

def plot_timetables_for_all_sections(gene, filename):
    filename = "generated_timetables/student/" + "t" + datetime.now().strftime("%d_%H_%M_%S_%f") + filename 
    data_lookup = {item["id"]: item for item in data}
    document = SimpleDocTemplate(filename, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20, title="Timetablo")
    
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        name="NormalWrapped",
        parent=styles["Normal"],
        wordWrap='CJK',
        fontSize=9,
        leading=10
    )

    all_elements = []
    for section_name in section_data:
        section_elements = create_section_tables(gene, section_name, styles, normal_style, data, data_lookup)
        all_elements.extend(section_elements)
        all_elements.append(PageBreak())

    document.build(all_elements)
    print(f"All section timetables saved to '{filename}'")

