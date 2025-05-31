from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
from core.constants import DAYS, HOURS
from tqdm import tqdm
from collections import defaultdict
from datetime import datetime
import pickle
with open("data/heuristic_allocation.pkl", "rb") as f:
        data, encoded_df, section_data, subject_map, staff_map = pickle.load(f)

def build_staff_timetable_map(gene):
    # Map from staff_name -> [ [ [entry], ..., H ] for D ]
    staff_tt_map = defaultdict(lambda: [[None for _ in range(HOURS)] for _ in range(DAYS)])

    for section in gene:
        for day in range(DAYS):
            for hour in range(HOURS):
                entry = gene[section][day][hour]
                if entry:
                    id_, subjects = entry
                    subject = subjects[0] if isinstance(subjects, list) else subjects
                    for item in data:
                        if item["id"] == id_:
                            for staff in item["staffs"]:
                                if staff == "nan":
                                    continue
                                staff_tt_map[staff][day][hour] = (section, subject, id_)
                            break
    return staff_tt_map

def create_staff_table(staff_name, staff_tt, styles, normal_style):
    elements = []

    table_data = []
    header_row = [""] + [f"Period {i+1}" for i in range(HOURS)]
    table_data.append(header_row)

    for day in range(DAYS):
        row = [f"Day {day+1}"]
        for hour in range(HOURS):
            entry = staff_tt[day][hour]
            if entry:
                section, subject, id_ = entry
                text = f"{subject} ({id_})\n{section}"
                row.append(Paragraph(text, normal_style))
            else:
                row.append("")
        table_data.append(row)

    total_width = 720
    day_col_width = 80
    period_col_width = (total_width - day_col_width) / HOURS
    col_widths = [day_col_width] + [period_col_width] * HOURS

    tt_table = Table(table_data, colWidths=col_widths)
    tt_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(Paragraph(f"Timetable for {staff_name}", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(KeepTogether([tt_table]))

    return elements

def plot_timetables_for_all_staff(gene, filename="staff_timetables.pdf"):
    staff_tt_map = build_staff_timetable_map(gene)

    filename = "generated_timetables/staff/" + "t" + datetime.now().strftime("%d_%H_%M_%S_%f") + filename 
    document = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
        title="Staff Timetables",
        author="SASTRA Scheduler",
        subject="Staff-wise Timetable",
    )

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        name="NormalWrapped",
        parent=styles["Normal"],
        wordWrap='CJK',
        fontSize=9,
        leading=10
    )

    all_elements = []
    for staff_name in sorted(staff_tt_map):
        staff_elements = create_staff_table(staff_name, staff_tt_map[staff_name], styles, normal_style)
        all_elements.extend(staff_elements)
        all_elements.append(PageBreak())

    document.build(all_elements)
    #print(f"All staff timetables saved to '{filename}'")

if __name__ == "__main__":
    plot_timetables_for_all_staff()
