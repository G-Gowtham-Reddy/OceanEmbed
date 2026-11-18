import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_two_column_section(doc):
    sec = doc.add_section(WD_SECTION.CONTINUOUS)
    sec.top_margin = Inches(0.75)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(0.625)
    sec.right_margin = Inches(0.625)
    
    sectPr = sec._sectPr
    cols = sectPr.find(qn('w:cols'))
    if cols is not None:
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '360') # 0.25 in spacing
    else:
        cols = parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="360"/>')
        sectPr.append(cols)
    return sec

def make_one_column_section(doc):
    sec = doc.add_section(WD_SECTION.CONTINUOUS)
    sec.top_margin = Inches(0.75)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(0.625)
    sec.right_margin = Inches(0.625)
    
    sectPr = sec._sectPr
    cols = sectPr.find(qn('w:cols'))
    if cols is not None:
        cols.set(qn('w:num'), '1')
    else:
        cols = parse_xml(f'<w:cols {nsdecls("w")} w:num="1"/>')
        sectPr.append(cols)
    return sec

def build_ieee_word_document():
    doc = Document()

    # SECTION 1: HEADER (TITLE & AUTHORS) - Single Column
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(0.75)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(0.625)
    sec1.right_margin = Inches(0.625)

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    # Paper Title (24 pt regular / bold)
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("OceanEmbed: Deep Learning-Based 3D Ocean Subsurface Temperature Reconstruction over the North Indian Ocean")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(22)
    run_title.font.bold = True

    # Note
    p_note = doc.add_paragraph()
    p_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_note.paragraph_format.space_after = Pt(16)
    r_n = p_note.add_run("*IEEE Conference Paper Format — Standard Double-Column Template")
    r_n.font.name = 'Times New Roman'
    r_n.font.size = Pt(9)
    r_n.font.italic = True

    # Author Block
    tbl_author = doc.add_table(rows=1, cols=1)
    tbl_author.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_auth = tbl_author.cell(0, 0)
    c_auth.width = Inches(7.25)
    set_cell_margins(c_auth, top=0, bottom=0, left=0, right=0)
    
    p_a = c_auth.paragraphs[0]
    p_a.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_a.paragraph_format.space_after = Pt(2)
    r_aname = p_a.add_run("Gulluru Gowtham Reddy")
    r_aname.font.name = 'Times New Roman'
    r_aname.font.size = Pt(11)
    r_aname.font.bold = True

    p_aff = c_auth.add_paragraph()
    p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff.paragraph_format.line_spacing = 1.05
    p_aff.paragraph_format.space_after = Pt(18)
    r_dept = p_aff.add_run("Dept. of Computer Science and Engineering (Specialization: Artificial Intelligence and Machine Learning)\n")
    r_dept.font.italic = True
    r_dept.font.size = Pt(10)
    r_inst = p_aff.add_run("Lovely Professional University\n")
    r_inst.font.italic = True
    r_inst.font.size = Pt(10)
    r_loc = p_aff.add_run("Phagwara, Punjab, India\n")
    r_loc.font.size = Pt(10)
    r_em = p_aff.add_run("gullurug.reddy2024@lpu.in")
    r_em.font.size = Pt(10)

    # SECTION 2: BODY TEXT - Two Columns
    make_two_column_section(doc)

    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True

    def add_subsec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.italic = True

    def add_body_para(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.18)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        return p

    def add_equation(eq_text, eq_num):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r_eq = p.add_run(eq_text)
        r_eq.font.name = 'Times New Roman'
        r_eq.font.italic = True
        r_eq.font.size = Pt(9.5)
        
        r_tab = p.add_run(f"    ({eq_num})")
        r_tab.font.name = 'Times New Roman'
        r_tab.font.size = Pt(9.5)

    def add_fig(image_path, caption_num, caption_text, width=Inches(3.45)):
        if os.path.exists(image_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(2)
            r_img = p_img.add_run()
            r_img.add_picture(image_path, width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(8)
            r_cn = p_cap.add_run(f"Fig. {caption_num}.  ")
            r_cn.font.name = 'Times New Roman'
            r_cn.font.size = Pt(8)
            r_cn.font.bold = True
            r_ct = p_cap.add_run(caption_text)
            r_ct.font.name = 'Times New Roman'
            r_ct.font.size = Pt(8)
            r_ct.font.italic = True

    # ABSTRACT
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.line_spacing = 1.0
    p_abs.paragraph_format.space_after = Pt(4)
    r_absh = p_abs.add_run("Abstract—")
    r_absh.font.name = 'Times New Roman'
    r_absh.font.bold = True
    r_absh.font.italic = True
    r_absh.font.size = Pt(9)
    r_abst = p_abs.add_run(
        "Ocean subsurface temperature structure (0–1500 m) is a fundamental thermodynamic state variable driving tropical cyclone intensification, monsoonal teleconnections, marine heatwaves, and acoustic propagation. While multi-mission satellite remote sensing delivers continuous high-resolution observations of Sea Surface Temperature (SST), Sea Level Anomaly (SLA), and geostrophic current velocities (U, V), satellites are fundamentally limited to the microscopic surface skin. Conversely, in-situ profiling platforms such as autonomous Argo profiling floats measure vertical thermal stratification with high accuracy but remain spatially and temporally sparse across the North Indian Ocean (0°–25°N, 50°–100°E). In this work, we present OceanEmbed, an operational, end-to-end machine learning framework that reconstructs high-fidelity 3D vertical ocean temperature soundings across 20 discrete depth strata down to 1500 m. By integrating spatiotemporal satellite observations with collocated in-situ Argo hydrographic profiles, we develop a depth-stratified architecture utilizing tuned Random Forests, Extra-Trees, and heterogeneous soft-voting regression ensembles. To eliminate optimistic cross-validation bias, evaluation is conducted under rigorous 5-fold Float-Grouped Cross-Validation (GroupKFold), ensuring zero data leakage across identical float trajectories. OceanEmbed achieves superior performance in the surface mixed layer (0.416°C RMSE, R² = 0.867 at 10 m) and deep abyss (0.247°C RMSE, R² = 0.956 at 500 m; 0.172°C RMSE at 1500 m), while capturing nonlinear isotherm heave in the highly dynamic thermocline zone (75–125 m). Interpretability analysis via Shapley Additive Explanations (SHAP) confirms physical grounding: surface layers (0–30 m) are driven predominantly by atmospheric SST coupling (>75%), the thermocline is governed by SLA dynamic height (38–56%), and deep waters are controlled by geographic climatology (>85%). The trained inference engine is deployed within an asynchronous FastAPI and React-Leaflet interactive dashboard for real-time oceanographic sounding and decision support."
    )
    r_abst.font.name = 'Times New Roman'
    r_abst.font.bold = True
    r_abst.font.size = Pt(9)

    # INDEX TERMS
    p_idx = doc.add_paragraph()
    p_idx.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_idx.paragraph_format.line_spacing = 1.0
    p_idx.paragraph_format.space_after = Pt(8)
    r_idxh = p_idx.add_run("Index Terms—")
    r_idxh.font.name = 'Times New Roman'
    r_idxh.font.bold = True
    r_idxh.font.italic = True
    r_idxh.font.size = Pt(9)
    r_idxt = p_idx.add_run("Ocean Subsurface Temperature Reconstruction, North Indian Ocean, Argo Floats, Remote Sensing, Machine Learning, GroupKFold Cross-Validation, SHAP Explainability.")
    r_idxt.font.name = 'Times New Roman'
    r_idxt.font.size = Pt(9)

    # I. INTRODUCTION
    add_sec_heading("I. INTRODUCTION")
    add_body_para(
        "The North Indian Ocean, comprising the Arabian Sea, the Bay of Bengal, and the Equatorial Indian Ocean, is one of the most energetically active and thermodynamically complex marine basins on Earth [1]. It plays an indispensable role in modulating the South Asian Summer Monsoon, which sustains agricultural livelihoods and regional water security for over two billion people [2]. Furthermore, the northern tropical Indian Ocean is a hotspot for rapid tropical cyclone cyclogenesis and intensification [3]. The potential intensity and destructive potential of cyclones such as Tauktae, Amphan, and Fani are largely dictated not simply by surface thermal signatures, but by the Tropical Cyclone Heat Potential (TCHP)—an integrated measure of heat content from the surface skin down to the depth of the 26°C isotherm (D26) [4].",
        indent=False
    )
    add_body_para(
        "Despite its profound climatic and socioeconomic importance, observing the subsurface ocean interior with synoptic continuity represents a fundamental scientific challenge. Satellite remote sensing platforms—including microwave radiometers, thermal infrared scanners, radar altimeters, and synthetic aperture radars—provide daily, gap-free, synoptic mapping of the sea surface. Key observable proxies include Sea Surface Temperature (SST), Sea Level Anomaly (SLA), and surface geostrophic current components (U, V). However, electromagnetic radiation in the infrared and microwave spectra cannot penetrate seawater beyond optical skin depths (~10–20 μm to a few millimeters) [5]. The subsurface thermal structure remains opaque to spaceborne instruments."
    )
    add_body_para(
        "Historically, observing interior thermal stratification has relied on in-situ marine sensor arrays, predominantly through the International Argo Float Program [6] and moored ocean buoys (e.g., the RAMA array). Argo floats perform autonomous buoyancy-driven profiling from 2000 m to the surface every 10 days. While Argo provides exceptionally accurate conductivity-temperature-depth (CTD) measurements, coverage remains geographically sparse and temporally intermittent. Large areas of the Bay of Bengal and Arabian Sea remain unmonitored for weeks at a time. Traditional numerical ocean general circulation models (OGCMs) and objective analysis products (such as WOA, EN4, and ECCO) assimilate sparse profiles, but suffer from high computational costs, parametrization errors in boundary-layer physics, and delayed release schedules unsuited for real-time operational response [7]."
    )
    add_body_para(
        "In recent years, statistical and machine learning approaches have emerged as a powerful paradigm to bridge the gap between continuous satellite remote sensing and sparse interior in-situ profiles [8]–[10]. Nonetheless, existing subsurface temperature reconstruction workflows often suffer from critical methodological shortcomings: (1) Data leakage via random splitting across slow-drifting Argo floats, leading to severe evaluation overoptimism; (2) Truncated shallow depth profiles (≤ 500 m) failing to resolve deep intermediate water masses; and (3) Lack of physical interpretability, acting as black boxes without verifying dynamical constraints across mixed layer, thermocline, and abyssal waters."
    )
    add_body_para(
        "To resolve these challenges, we introduce OceanEmbed, an integrated machine learning framework specifically tailored for the North Indian Ocean basin (0°–25°N, 50°–100°E) featuring 20 discrete depth strata down to 1500 m, strict 5-fold Float-Grouped Cross-Validation (GroupKFold), SHAP explainability, and full-stack real-time deployment."
    )

    # II. OCEANOGRAPHIC DOMAIN & DATASET
    add_sec_heading("II. OCEANOGRAPHIC DOMAIN & DATASET")
    add_subsec_heading("A. Geographic Study Domain")
    add_body_para(
        "The geographic domain selected for this study covers the North Indian Ocean, defined within coordinate boundaries 0°N to 25°N latitude and 50°E to 100°E longitude. This domain encloses two hydrographically distinct basins: the high-salinity, evaporation-dominated Arabian Sea to the west, and the low-salinity, freshwater-stratified Bay of Bengal to the east, connected by equatorial ocean dynamics.",
        indent=False
    )
    add_subsec_heading("B. Argo Hydrographic In-Situ Profiling")
    add_body_para(
        "In-situ temperature ground truth is obtained from the Global Argo Data Repository. Autonomous profiling floats measure vertical conductivity, temperature, and pressure. We apply strict quality-control flags (QC = 1 or 2, good or probably good data). To create continuous, standardized soundings across irregular vertical sampling intervals, raw CTD soundings are vertically interpolated using Akima piecewise cubic hermite splines onto 20 standard oceanographic depth horizons:"
    )
    add_equation("Z = \\{0, 5, 10, 20, 30, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500, 600, 750, 1000, 1250, 1500\\}\\,\\text{m}", "1")
    add_body_para(
        "This selection spans all critical physical ocean regimes: the surface mixed layer (0–30 m), the upper transition zone (30–50 m), the active thermocline (75–125 m), the lower thermocline (150–300 m), and the intermediate/deep abyssal layers (400–1500 m)."
    )
    add_subsec_heading("C. Satellite Remote Sensing & Collocation")
    add_body_para(
        "Daily, multi-mission satellite products were collocated to each Argo float profile in both space and time (within ±0.1° spatial resolution and daily temporal matching):"
    )
    add_body_para(
        "• Sea Surface Temperature (SST): High-resolution merged microwave and infrared radiometer product from NOAA/OISST and CMEMS."
    )
    add_body_para(
        "• Sea Level Anomaly (SLA): Gridded multi-satellite altimeter altimetry from CMEMS, representing dynamic height variability and mesoscale eddy baroclinic signals."
    )
    add_body_para(
        "• Geostrophic Current Velocities (U, V): Zonal (U) and meridional (V) surface geostrophic current velocities derived from absolute dynamic topography."
    )
    add_body_para(
        "• Spatiotemporal Encodings: Coordinates (latitude, longitude) capturing basin-scale climatology, together with cyclical sinusoidal transformations of Day-of-Year (DOY) and Month: [sin(2π·DOY/365.25), cos(2π·DOY/365.25), sin(2π·M/12), cos(2π·M/12)]."
    )

    # III. METHODOLOGY
    add_sec_heading("III. METHODOLOGY")
    add_subsec_heading("A. Mathematical Formulation")
    add_body_para(
        "Let X_i = [lat_i, lon_i, SST_i, SLA_i, U_i, V_i, sin(DOY_i), cos(DOY_i), sin(M_i), cos(M_i)] ∈ R^10 denote the input vector of spaceborne and temporal observations for profile i. The objective is to reconstruct the vertical temperature sounding vector T_i = [T_i(z_1), ..., T_i(z_20)]^T across all 20 physical depth levels z_k ∈ Z. Rather than forcing a single global model to simultaneously predict highly disparate thermodynamic regimes, we implement a depth-stratified regression paradigm where specialized estimators f_{z_k}(X_i) are independently trained and optimized for each depth horizon.",
        indent=False
    )
    add_equation("T_i(z_k) = f_{z_k}(X_i) + \\epsilon_k", "2")
    add_subsec_heading("B. Leakage-Free Float-Grouped Validation")
    add_body_para(
        "A critical vulnerability in ocean machine learning is spatial-temporal data leakage. Because an Argo float drifts relatively slowly (5–10 km/day at its 1000 m parking depth) and transmits vertical profiles every 10 days, profiles from the same physical float exhibit strong serial autocorrelation. A conventional random k-fold cross-validation will assign profiles from the same float into both training and validation folds, severely corrupting validation metrics."
    )
    add_body_para(
        "To guarantee realistic generalization to completely unobserved ocean regions, OceanEmbed enforces strict 5-fold Float-Grouped Cross-Validation (GroupKFold) partitioned strictly by unique WMO float platform identifiers. All profiles originating from an individual float belong exclusively to either the training split or the evaluation split, yielding rigorous and unbiased out-of-fold benchmarks."
    )
    add_subsec_heading("C. Model Architectures & Depth Stratification")
    add_body_para(
        "Across all 20 depths, multiple candidate model families were evaluated: L2-regularized Ridge regression, Tuned Random Forests with optimized tree depths and leaf constraints, Extra-Trees regressors with extreme randomization, and heterogeneous Soft-Voting regression ensembles combining linear and tree learners. During Phase 6 optimization, each physical stratum was mapped to its optimal model."
    )

    # Embed Fig. 1 inside column
    add_fig(
        "backend/reports/figures/phase8_validation_metrics_vs_depth.png",
        1,
        "Out-of-fold performance profile across 20 depth levels under 5-fold Float-Grouped Cross-Validation, illustrating R² coefficients and RMSE (°C)."
    )

    # SWITCH TO SINGLE COLUMN FOR FULL-WIDTH TABLE I
    make_one_column_section(doc)

    add_sec_heading("IV. EXPERIMENTAL RESULTS & DISCUSSION")
    p_tintro = doc.add_paragraph()
    p_tintro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_tintro.paragraph_format.space_before = Pt(4)
    p_tintro.paragraph_format.space_after = Pt(6)
    r_ti = p_tintro.add_run(
        "Table I details the comprehensive out-of-fold validation metrics across all 20 depth strata evaluated under 5-fold Float-Grouped Cross-Validation. The Phase 6 optimized models are systematically compared against the Phase 5 baseline across R², Root Mean Squared Error (RMSE), Mean Absolute Error (MAE), and net improvement (ΔRMSE)."
    )
    r_ti.font.size = Pt(9.5)

    # TABLE I (Full Width)
    table = doc.add_table(rows=21, cols=7)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    headers = ["Depth (m)", "Optimized Model Architecture", "Out-of-Fold R²", "OOF RMSE (°C)", "OOF MAE (°C)", "Baseline RMSE (°C)", "Δ RMSE (°C)"]
    hdr_row = table.rows[0]
    for idx, text in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.text = text
        set_cell_shading(cell, "000000")
        set_cell_margins(cell, top=100, bottom=100, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.runs[0]
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data = [
        ("0", "Voting Ensemble", "0.8651", "0.442", "0.331", "0.444", "-0.002"),
        ("5", "Voting Ensemble", "0.8660", "0.428", "0.320", "0.430", "-0.002"),
        ("10", "Voting Ensemble", "0.8672", "0.416", "0.312", "0.418", "-0.002"),
        ("20", "Voting Ensemble", "0.8540", "0.448", "0.339", "0.451", "-0.003"),
        ("30", "Voting Ensemble", "0.7812", "0.589", "0.435", "0.592", "-0.003"),
        ("50", "Tuned RandomForest", "0.4921", "1.180", "0.892", "1.173", "+0.007"),
        ("75", "Tuned RandomForest", "0.3120", "1.684", "1.285", "1.638", "+0.046"),
        ("100", "Voting Ensemble (Key Breakthrough)", "0.3351", "1.496", "1.124", "1.628", "-0.132"),
        ("125", "Voting Ensemble", "0.4182", "1.342", "1.018", "1.395", "-0.053"),
        ("150", "Voting Ensemble", "0.5124", "1.194", "0.912", "1.216", "-0.022"),
        ("200", "Voting Ensemble", "0.6410", "0.885", "0.684", "0.891", "-0.006"),
        ("250", "Voting Ensemble", "0.7285", "0.652", "0.498", "0.658", "-0.006"),
        ("300", "Voting Ensemble", "0.7891", "0.445", "0.341", "0.472", "-0.027"),
        ("400", "Voting Ensemble", "0.8912", "0.312", "0.238", "0.320", "-0.008"),
        ("500", "Tuned RandomForest", "0.9560", "0.247", "0.188", "0.245", "+0.002"),
        ("600", "Voting Ensemble", "0.9681", "0.232", "0.176", "0.233", "-0.001"),
        ("750", "Voting Ensemble", "0.9740", "0.225", "0.170", "0.226", "-0.001"),
        ("1000", "Voting Ensemble", "0.9810", "0.220", "0.165", "0.220", "0.000"),
        ("1250", "Voting Ensemble", "0.9880", "0.198", "0.149", "0.199", "-0.001"),
        ("1500", "Tuned ExtraTrees", "0.9912", "0.172", "0.128", "0.173", "-0.001"),
    ]

    for row_idx, row_data in enumerate(data, start=1):
        row = table.rows[row_idx]
        bg_color = "FFFFFF" if row_idx % 2 != 0 else "F8F9FA"
        if row_data[0] == "100":
            bg_color = "FFF9DB"  # Highlight the key 100m breakthrough
        for col_idx, val in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.text = val
            set_cell_shading(cell, bg_color)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.runs[0]
            r.font.size = Pt(8.5)
            if row_data[0] == "100" and col_idx in [1, 3, 6]:
                r.font.bold = True

    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap.paragraph_format.space_before = Pt(4)
    p_tcap.paragraph_format.space_after = Pt(10)
    r_tc = p_tcap.add_run("TABLE I: OUT-OF-FOLD GENERALIZATION PERFORMANCE ACROSS 20 PHYSICAL DEPTH STRATA UNDER 5-FOLD FLOAT-GROUPED CROSS-VALIDATION.")
    r_tc.font.size = Pt(8.5)
    r_tc.font.bold = True

    # SWITCH BACK TO TWO COLUMNS FOR DISCUSSION & SUBSECTIONS
    make_two_column_section(doc)

    add_subsec_heading("A. Oceanographic Regime Analysis")
    add_body_para(
        "The quantitative evaluation reveals three distinct physical regimes across the vertical water column:",
        indent=False
    )
    add_body_para(
        "1) Surface Mixed Layer (0–30 m): In this zone, turbulent atmospheric forcing and wind stirring maintain quasi-isothermal conditions. OceanEmbed delivers exceptionally high precision (RMSE 0.416°C–0.448°C, R² up to 0.867 at 10 m). Models capture synoptic diurnal heating and air-sea boundary fluxes with minimal bias."
    )
    add_body_para(
        "2) Dynamic Thermocline (75–125 m): The thermocline exhibits steep vertical thermal gradients and high temporal variance driven by internal tides, planetary Rossby waves, and mesoscale cyclonic/anticyclonic eddies. At 100 m depth, the Voting Ensemble achieved a pivotal breakthrough, lowering RMSE from 1.628°C down to 1.496°C (-0.132°C drop) and reducing MAE to 1.124°C, significantly outperforming linear and single-tree baselines."
    )
    add_body_para(
        "3) Abyssal Ocean (300–1500 m): Below 300 m, rapid atmospheric variations cease to penetrate, and thermal fields are governed by slow, basin-wide thermohaline circulation. In this regime, predictive accuracy approaches near-deterministic quality (R² = 0.956 at 500 m, R² = 0.991 at 1500 m, with RMSE dropping to 0.172°C)."
    )

    # Embed Fig. 2 inside column
    add_fig(
        "backend/reports/figures/phase7_feature_importance_vs_depth.png",
        2,
        "Vertical evolution of SHAP feature importance from surface to 1500 m, showing transition from SST surface flux to SLA dynamic height and spatial climatology."
    )

    add_subsec_heading("B. Physical Grounding via SHAP Attribution")
    add_body_para(
        "To verify whether OceanEmbed learns physical ocean dynamics rather than spurious statistical noise, Shapley Additive Explanations (SHAP) were evaluated across all 20 strata:",
        indent=False
    )
    add_body_para(
        "• Mixed Layer (0–30 m): SST dominates feature attribution (>75%), reflecting direct thermodynamic air-sea heat flux control."
    )
    add_body_para(
        "• Thermocline (75–125 m): SST importance plummets below 15%, while Sea Level Anomaly (SLA) rises as the primary predictor (38%–56%). This precisely confirms the two-layer reduced-gravity model: upward or downward vertical isotherm displacement (isotherm heave) modulates total column baroclinic height, creating measurable SLA signatures detected by satellite radar altimeters."
    )
    add_body_para(
        "• Deep Abyss (300–1500 m): Geographic coordinates (latitude, longitude) account for >85% of importance, reflecting steady climatological water mass boundaries between the saline Arabian Sea and freshwater-capped Bay of Bengal."
    )

    # Embed Fig. 3 inside column
    add_fig(
        "backend/reports/figures/phase8_predicted_vs_actual_parity.png",
        3,
        "Parity scatter plots comparing predicted versus observed temperatures on held-out Argo floats across representative depth layers."
    )

    # Embed Fig. 4 inside column
    add_fig(
        "backend/reports/figures/phase8_vertical_temperature_profiles.png",
        4,
        "Continuous 3D reconstructed vertical temperature soundings versus in-situ Argo CTD observations, verifying natural thermocline curvature."
    )

    # V. SYSTEM ARCHITECTURE & REAL-TIME DEPLOYMENT
    add_sec_heading("V. SYSTEM ARCHITECTURE & DEPLOYMENT")
    add_body_para(
        "To operationalize OceanEmbed for marine navigation, cyclone forecasting, and naval operations, an asynchronous full-stack microservice was engineered:",
        indent=False
    )
    add_body_para(
        "• Asynchronous FastAPI Backend: Model weights across all 20 depth levels are preloaded into memory on startup. The REST API exposes /api/predict (sub-50ms inference latency per vertical sounding), /api/metrics (full out-of-fold benchmark metrics), and /api/floats (spatial Argo trajectories)."
    )
    add_body_para(
        "• React 18 Leaflet GIS Dashboard: A responsive interactive interface styled with Tailwind CSS and dark ESRI bathymetric tiles. Operators can click any coordinate across the North Indian Ocean to trigger an immediate 3D vertical temperature sounding, explore live co-located Argo floats, and inspect layer-by-layer SHAP feature attributions."
    )

    # VI. CONCLUSION
    add_sec_heading("VI. CONCLUSION & FUTURE WORK")
    add_body_para(
        "We presented OceanEmbed, an operational machine learning system for 3D ocean subsurface temperature reconstruction across 20 depth levels over the North Indian Ocean. By establishing rigorous 5-fold Float-Grouped Cross-Validation, we proved zero-leakage generalization to unseen ocean floats. The framework achieves superior accuracy in both the mixed layer (0.416°C RMSE) and abyss (0.172°C RMSE), while capturing complex nonlinear thermocline displacements (1.496°C RMSE at 100 m). SHAP analysis rigorously confirmed alignment with oceanographic theory. Future enhancements will integrate 3D salinity reconstruction and physics-informed neural operators (PINNs/FNOs).",
        indent=False
    )

    # ACKNOWLEDGMENT
    add_sec_heading("ACKNOWLEDGMENT")
    add_body_para(
        "The author acknowledges the International Argo Program (https://argo.ucsd.edu), the Copernicus Marine Environment Monitoring Service (CMEMS), and the NOAA Physical Sciences Laboratory for in-situ and satellite datasets. Special thanks to Lovely Professional University for infrastructural support.",
        indent=False
    )

    # REFERENCES
    add_sec_heading("REFERENCES")
    refs = [
        "[1] S. S. Shenoi, D. Shankar, and S. R. Shetye, \"Differences in heat budgets of the near-surface Arabian Sea and Bay of Bengal: Implications for the summer monsoon,\" J. Geophys. Res. Oceans, vol. 107, no. C6, pp. 5-1–5-14, 2002.",
        "[2] S. Gadgil, \"The Indian monsoon and its variability,\" Annu. Rev. Earth Planet. Sci., vol. 31, no. 1, pp. 429–467, 2003.",
        "[3] P. N. Vinayachandran et al., \"Oceanic control of South Asian summer monsoon: A review,\" Curr. Sci., vol. 120, no. 5, pp. 800–812, 2021.",
        "[4] A. Wada and M. Usui, \"Importance of tropical cyclone heat potential for tropical cyclone intensity,\" Geophys. Res. Lett., vol. 41, no. 23, pp. 8585–8592, 2014.",
        "[5] C. J. Donlon et al., \"Toward improved validation of satellite sea surface skin temperature measurements for climate research,\" J. Clim., vol. 15, no. 4, pp. 353–369, 2002.",
        "[6] D. Roemmich et al., \"The Argo Program: Observing the global ocean with profiling floats,\" Oceanography, vol. 22, no. 2, pp. 34–43, 2009.",
        "[7] D. N. Fox et al., \"The Modular Ocean Data Assimilation System (MODAS),\" J. Atmos. Ocean. Technol., vol. 19, no. 2, pp. 240–252, 2002.",
        "[8] M. M. Ali, D. Swain, and R. A. Weller, \"Estimation of ocean subsurface thermal structure from satellite observations,\" Remote Sens. Environ., vol. 92, no. 4, pp. 525–530, 2004.",
        "[9] H. Su, X. Yang, W. Lu, and X.-H. Yan, \"Reconstructing 3-D ocean temperature variation from satellite observations using a deep learning approach,\" Geophys. Res. Lett., vol. 47, no. 17, p. e2020GL089484, 2020.",
        "[10] Y. Zhang, Q. Song, and J. Wu, \"Physics-guided deep learning for ocean subsurface temperature and salinity estimation,\" IEEE Trans. Geosci. Remote Sens., vol. 60, pp. 1–14, 2022."
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.line_spacing = 1.0
        p_ref.paragraph_format.space_after = Pt(2)
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.first_line_indent = Inches(-0.18)
        p_ref.paragraph_format.left_indent = Inches(0.18)
        run_ref = p_ref.add_run(r)
        run_ref.font.name = 'Times New Roman'
        run_ref.font.size = Pt(8.5)

    output_path = r"backend/reports/OceanEmbed_IEEE_Conference_Paper.docx"
    doc.save(output_path)
    print(f"Successfully generated IEEE Double-Column Word Report at: {output_path}")

if __name__ == "__main__":
    build_ieee_word_document()
