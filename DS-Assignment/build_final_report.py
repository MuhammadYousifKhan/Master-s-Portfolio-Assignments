"""
Build the FINAL report.docx with all tasks properly included:
- Full step-by-step mathematical working (matching sample assignment style)
- Actual Python console outputs embedded (not placeholders)
- Python code sections properly formatted
- Figure references with actual output verification
- Complete appendix with full code
"""

from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import os

doc = Document()

# ============================================================
# STYLES
# ============================================================
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)

# ============================================================
# HELPERS
# ============================================================
def add_heading_styled(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = 'Times New Roman'
    return h

def add_para(text, bold=False, italic=False, alignment=None, size=12, space_after=6):
    p = doc.add_paragraph()
    if alignment:
        p.alignment = alignment
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_equation(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.italic = True
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    return p

def add_bullet(text, level=0):
    p = doc.add_paragraph(text, style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.27 + level * 1.27)
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    return p

def add_empty_line():
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    return p

def add_code_block(code_text, size=8):
    """Add a code block with monospace font"""
    for line in code_text.split('\n'):
        p = doc.add_paragraph()
        run = p.add_run(line)
        run.font.name = 'Courier New'
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.5)
    return p

def add_output_block(output_text, size=8):
    """Add console output with monospace font"""
    for line in output_text.split('\n'):
        p = doc.add_paragraph()
        run = p.add_run(line)
        run.font.name = 'Courier New'
        run.font.size = Pt(size)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(1.0)

# ============================================================
# FIGURE PATHS
# ============================================================
FIG_TASK1 = 'figures/fig_task1_zone_demands.png'
FIG_TASK2 = 'figures/fig_task2_demand_curve.png'
FIG_TASK3 = 'figures/fig_task3_normal_curve.png'
FIG_TASK4 = 'figures/fig_task4_boxplot.png'

# ============================================================
# TITLE PAGE
# ============================================================
for _ in range(4):
    add_empty_line()

add_para('Arden University', bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, size=18)
add_empty_line()
add_para('Masters in Data Science', bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, size=16)
add_empty_line()
add_empty_line()
add_para('COM7023 - Mathematics for Data Science', bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, size=14)
add_empty_line()
add_empty_line()
add_para('Urban Resource Intelligence Portfolio', bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, size=14)
add_empty_line()
add_empty_line()
add_para('Student ID: [YOUR STUDENT ID]', alignment=WD_ALIGN_PARAGRAPH.CENTER, size=12)
add_para('Student Name: [YOUR NAME]', alignment=WD_ALIGN_PARAGRAPH.CENTER, size=12)
add_empty_line()
add_empty_line()
add_para('Word Count: [TBC - final submission]', alignment=WD_ALIGN_PARAGRAPH.CENTER, size=12)

doc.add_page_break()

# ============================================================
# TABLE OF CONTENTS
# ============================================================
add_heading_styled('Table of Contents', level=1)
toc = [
    ('1. Introduction', '3'),
    ('   1.1 Background and Purpose of the Study', '3'),
    ('2. Methodology', '3'),
    ('3. Task 1: Steady-State Resource Demand (Linear Algebra)', '3'),
    ('   3.1 Mathematical Analysis', '3'),
    ('   3.2 Solution', '4'),
    ('      3.2.1 Formation of the Augmented Matrix', '4'),
    ('      3.2.2 Gaussian Elimination Step-by-Step', '4'),
    ('      3.2.3 Back Substitution', '5'),
    ('      3.2.4 Python Verification with Console Output', '5'),
    ('   3.3 Analysis and Results', '6'),
    ('   3.4 Visualisation', '7'),
    ('4. Task 2: Demand Over Time (Calculus)', '8'),
    ('   4.1 Mathematical Analysis', '8'),
    ('   4.2 Solution', '8'),
    ('      4.2.1 Application of the Power Rule for Differentiation', '9'),
    ('      4.2.2 Identification of Critical Points', '10'),
    ('      4.2.3 Second Derivative Test for Classification', '10'),
    ('      4.2.4 Inflection Point Analysis', '11'),
    ('      4.2.5 Intervals of Increase and Decrease', '11'),
    ('      4.2.6 Python Verification with Console Output', '12'),
    ('   4.3 Analysis and Results', '13'),
    ('   4.4 Visualisation', '13'),
    ('5. Task 3: Forecasting Error Risk (Probability)', '14'),
    ('6. Task 4: Consumption by Building Type (Statistics)', '15'),
    ('10. References', '16'),
    ('11. Appendix', '17'),
]
for item, page in toc:
    p = doc.add_paragraph()
    run = p.add_run(f'{item}\t{page}')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)

doc.add_page_break()

# ============================================================
# 1. INTRODUCTION
# ============================================================
add_heading_styled('1. Introduction', level=1)
add_heading_styled('1.1 Background and Purpose of the Study', level=2)

add_para(
    "The study's background and purpose are set out in this section. Mathematics offers a "
    "strong toolbox to help understand and control urban resource systems. The assignment is "
    "a continuation of the Urban Resource Intelligence (URI) consultancy scenario and uses "
    "four main mathematical disciplines (linear algebra, calculus, probability, and statistics) "
    "to analyse the demand and consumption of resources for houses located within an urban area."
)

add_para('Four tasks are structured in the analysis:')
add_bullet('Solving a system of linear equations to obtain the steady state resource demand in four urban zones (Task 1);')
add_bullet('Analyzing a cubic demand function to identify the periods of peak and trough demands (Task 2);')
add_bullet('Evaluating the probability of forecast errors based on the normal distribution (Task 3);')
add_bullet('Comparing mean daily consumption across three building types (Apartments, Terraced, Detached) using one-way ANOVA with post-hoc testing (Task 4).')

doc.add_page_break()

# ============================================================
# 2. METHODOLOGY
# ============================================================
add_heading_styled('2. Methodology', level=1)

add_para(
    'Each task is done in a step-by-step manner. All mathematical working is typed using '
    'standard notation. The calculations are done in Python with the help of NumPy, SciPy, '
    'Seaborn and Matplotlib libraries. For each task section, the mathematical theory is given, '
    'followed by a worked solution, verification using Python (with full console output shown), '
    'a visualisation and an interpretation of the solution to non-technical stakeholders.'
)

add_para(
    'The approach followed in this assignment is a structured and step-by-step process. '
    'The methodologies adopted in each task are mathematical methods that are applicable '
    'to the nature of the resource management problem being investigated. All calculations '
    'have been performed with the aid of digital tools in order to be precise and reproducible.'
)

add_para(
    'Task 1 involves solving a system of linear equations using matrix algebra methods. '
    "The steady-state demand is found by solving Ax = b using Gaussian elimination and "
    "verified with NumPy's linear algebra solver."
)

add_para(
    'Task 2 applies differential calculus to analyse a cubic demand function over a 4-hour '
    'window. First and second derivatives are used to locate and classify critical points '
    'and identify periods of increasing and decreasing demand.'
)

add_para(
    'Task 3 uses probability theory with the normal distribution to evaluate the likelihood '
    'of forecast errors of different magnitudes, informing risk management and contingency planning.'
)

add_para(
    'Task 4 applies inferential statistics through one-way ANOVA to determine whether there are '
    'statistically significant differences in mean daily consumption between three building types '
    'with unequal sample sizes. Assumption checks (Shapiro-Wilk for normality, Levene for equal '
    'variances) precede the ANOVA, and Tukey HSD post-hoc testing identifies which specific groups differ.'
)

doc.add_page_break()

# ============================================================
# 3. TASK 1: STEADY-STATE RESOURCE DEMAND (LINEAR ALGEBRA)
# ============================================================
add_heading_styled('3. Task 1: Steady-State Resource Demand (Linear Algebra)', level=1)

# 3.1
add_heading_styled('3.1 Mathematical Analysis (Method Used: System of Linear Equations and Matrix Algebra)', level=2)

add_para(
    'The goal is to identify the daily resource demand equilibrium in the four interrelated '
    'urban areas. The relationship between zones is given by a set of four linear equations '
    'in four unknowns: x\u2081, x\u2082, x\u2083, x\u2084, where x\u2081 is the net daily demand (units) for zone 1, '
    'x\u2082 is the net daily demand (units) for zone 2, and so on.'
)

add_para('The system of equations is:')
for eq in ['2x\u2081 \u2212 x\u2082 + x\u2083 = 120', '\u2212x\u2081 + 3x\u2082 \u2212 x\u2084 = 150', 'x\u2081 + x\u2082 + 2x\u2083 \u2212 x\u2084 = 180', '\u2212x\u2082 + x\u2083 + 2x\u2084 = 140']:
    add_equation(eq)

add_para('The system can be expressed in matrix form as Ax = b:')
add_equation('A = [[2, \u22121, 1, 0], [\u22121, 3, 0, \u22121], [1, 1, 2, \u22121], [0, \u22121, 1, 2]]')
add_equation('x = [x\u2081, x\u2082, x\u2083, x\u2084]\u1d40')
add_equation('b = [120, 150, 180, 140]\u1d40')

add_para(
    'The analysis requires checking three properties of matrix A to ensure a unique, stable '
    'solution exists: (1) the determinant should be non-zero (ensures a unique solution), '
    '(2) the rank should be equal to the number of equations (ensures full linear independence), '
    'and (3) the condition number should be small (indicates numerical stability).'
)

# 3.2
add_heading_styled('3.2 Solution', level=2)

# 3.2.1
add_heading_styled('3.2.1 Formation of the Augmented Matrix', level=3)

add_para(
    'To solve the system using Gaussian elimination, we first construct the augmented matrix '
    '[A|b] which combines the coefficient matrix A with the constant vector b.'
)

add_equation('[A|b] = [2   \u22121   1    0   | 120]')
add_equation('        [\u22121   3    0   \u22121   | 150]')
add_equation('        [1    1    2   \u22121   | 180]')
add_equation('        [0   \u22121   1    2   | 140]')

# 3.2.2
add_heading_styled('3.2.2 Gaussian Elimination Step-by-Step', level=3)

add_para(
    'Gaussian elimination proceeds by performing row operations to transform the augmented '
    'matrix into row-echelon form (upper triangular).'
)

add_para('Step 1: Eliminate x\u2081 from rows 2 and 3 using row 1 as the pivot row.', bold=True)

add_para('Row 2 \u2192 Row 2 + (1/2) \u00d7 Row 1:')
add_equation('R\u2082 = R\u2082 + 0.5R\u2081: [\u22121+1, 3\u22120.5, 0+0.5, \u22121+0 | 150+60]')
add_equation('R\u2082 = [0, 2.5, 0.5, \u22121 | 210]')

add_para('Row 3 \u2192 Row 3 \u2212 (1/2) \u00d7 Row 1:')
add_equation('R\u2083 = R\u2083 \u2212 0.5R\u2081: [1\u22121, 1+0.5, 2\u22120.5, \u22121\u22120 | 180\u221260]')
add_equation('R\u2083 = [0, 1.5, 1.5, \u22121 | 120]')

add_para('The matrix after Step 1:')
add_equation('[2    \u22121   1    0   | 120]')
add_equation('[0    2.5  0.5 \u22121   | 210]')
add_equation('[0    1.5  1.5 \u22121   | 120]')
add_equation('[0    \u22121   1    2   | 140]')

add_para('Step 2: Eliminate x\u2082 from rows 3 and 4 using row 2 as the pivot row.', bold=True)

add_para('Row 3 \u2192 Row 3 \u2212 (1.5/2.5) \u00d7 Row 2 = Row 3 \u2212 0.6 \u00d7 Row 2:')
add_equation('R\u2083 = R\u2083 \u2212 0.6R\u2082: [0, 1.5\u22121.5, 1.5\u22120.3, \u22121+0.6 | 120\u2212126]')
add_equation('R\u2083 = [0, 0, 1.2, \u22120.4 | \u22126]')

add_para('Row 4 \u2192 Row 4 + (1/2.5) \u00d7 Row 2 = Row 4 + 0.4 \u00d7 Row 2:')
add_equation('R\u2084 = R\u2084 + 0.4R\u2082: [0, \u22121+1, 1+0.2, 2\u22120.4 | 140+84]')
add_equation('R\u2084 = [0, 0, 1.2, 1.6 | 224]')

add_para('The matrix after Step 2:')
add_equation('[2    \u22121   1    0   | 120]')
add_equation('[0    2.5  0.5 \u22121   | 210]')
add_equation('[0    0    1.2 \u22120.4 | \u22126]')
add_equation('[0    0    1.2  1.6 | 224]')

add_para('Step 3: Eliminate x\u2083 from row 4 using row 3 as the pivot row.', bold=True)

add_para('Row 4 \u2192 Row 4 \u2212 Row 3:')
add_equation('R\u2084 = R\u2084 \u2212 R\u2083: [0, 0, 1.2\u22121.2, 1.6+0.4 | 224+6]')
add_equation('R\u2084 = [0, 0, 0, 2.0 | 230]')

add_para('The final row-echelon form is:')
add_equation('[2    \u22121   1    0   | 120]')
add_equation('[0    2.5  0.5 \u22121   | 210]')
add_equation('[0    0    1.2 \u22120.4 | \u22126]')
add_equation('[0    0    0    2.0 | 230]')

# 3.2.3
add_heading_styled('3.2.3 Back Substitution', level=3)

add_para('Now that the matrix is in row-echelon form, we solve from the bottom up.')

add_para('From row 4: 2x\u2084 = 230', bold=True)
add_equation('x\u2084 = 230/2 = 115 units/day')

add_para('From row 3: 1.2x\u2083 \u2212 0.4x\u2084 = \u22126', bold=True)
add_equation('1.2x\u2083 \u2212 0.4(115) = \u22126')
add_equation('1.2x\u2083 \u2212 46 = \u22126')
add_equation('1.2x\u2083 = 40')
add_equation('x\u2083 = 40/1.2 = 33.33 units/day')

add_para('From row 2: 2.5x\u2082 + 0.5x\u2083 \u2212 x\u2084 = 210', bold=True)
add_equation('2.5x\u2082 + 0.5(33.33) \u2212 115 = 210')
add_equation('2.5x\u2082 + 16.67 \u2212 115 = 210')
add_equation('2.5x\u2082 \u2212 98.33 = 210')
add_equation('2.5x\u2082 = 308.33')
add_equation('x\u2082 = 308.33/2.5 = 123.33 units/day')

add_para('From row 1: 2x\u2081 \u2212 x\u2082 + x\u2083 = 120', bold=True)
add_equation('2x\u2081 \u2212 123.33 + 33.33 = 120')
add_equation('2x\u2081 \u2212 90 = 120')
add_equation('2x\u2081 = 210')
add_equation('x\u2081 = 210/2 = 105 units/day')

add_para('The complete solution:', bold=True)
add_equation('x\u2081 = 105.00 units/day  (Zone 1)')
add_equation('x\u2082 = 123.33 units/day  (Zone 2)')
add_equation('x\u2083 = 33.33 units/day   (Zone 3)')
add_equation('x\u2084 = 115.00 units/day  (Zone 4)')

# 3.2.4
add_heading_styled('3.2.4 Python Verification with Console Output', level=3)

add_para(
    "We used numpy.linalg.solve to verify the solution. The full Python code and its "
    "executed console output are shown below:"
)

# Task 1 code
add_para('Python Script (code/task1_linear_algebra.py):', bold=True, size=10)
task1_code = open('code/task1_linear_algebra.py', 'r').read()
add_code_block(task1_code, size=7)

add_para('')
add_para('Console Output:', bold=True, size=10)
task1_output = """============================================================
TASK 1 - STEADY-STATE RESOURCE DEMAND
============================================================

Matrix A (coefficients):
[[ 2. -1.  1.  0.]
 [-1.  3.  0. -1.]
 [ 1.  1.  2. -1.]
 [ 0. -1.  1.  2.]]

Vector b (demand targets):
[120. 150. 180. 140.]

--------------------------------------------------
EXISTENCE & UNIQUENESS CHECKS
--------------------------------------------------
det(A) = 12.0000
=> det(A) != 0 -> A is invertible, so a UNIQUE solution exists.

rank(A) = 4
=> Full rank -> all rows are linearly independent.

Condition number kappa(A) = 7.9245
=> Well-conditioned (kappa < 100) - solution is numerically stable.

--------------------------------------------------
SOLUTION
--------------------------------------------------
Equilibrium daily demand per zone (x1..x4):
  x1 (Zone 1) = 105.0000  units/day
  x2 (Zone 2) = 123.3333  units/day
  x3 (Zone 3) = 33.3333   units/day
  x4 (Zone 4) = 115.0000  units/day

Verification (A @ x should equal b):
  Residual (max error): 2.84e-14
  => Solution checks out (error approx machine precision).
============================================================
TASK 1 COMPLETE
============================================================"""
add_output_block(task1_output, size=7)

add_para('')
add_para('Summary of matrix properties:', bold=True)

# Properties table
table = doc.add_table(rows=5, cols=3)
table.style = 'Table Grid'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
h = table.rows[0].cells
h[0].text = 'Property'; h[1].text = 'Value'; h[2].text = 'Interpretation'
data = [
    ('det(A)', '12.00', 'Non-zero \u2192 unique solution exists'),
    ('rank(A)', '4', 'Full rank \u2192 all equations are independent'),
    ('\u03ba(A) (condition number)', '7.92', 'Well-conditioned \u2192 numerically stable'),
    ('Max residual error', '2.84 \u00d7 10\u207b\u00b9\u2074', 'Essentially zero \u2192 solution is correct')
]
for i, (p, v, inv) in enumerate(data):
    c = table.rows[i+1].cells
    c[0].text = p; c[1].text = v; c[2].text = inv
    for cell in c:
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)

add_empty_line()
add_para(
    'The determinant is 12.00 (non-zero), confirming that matrix A is invertible and '
    'a unique solution exists. The matrix has full rank (4), meaning all four equations are '
    'linearly independent. The condition number of 7.92 is well below 100, indicating the '
    'system is well-conditioned. The maximum residual of 2.84 \u00d7 10\u207b\u00b9\u2074 confirms '
    'the solution satisfies the original system to within machine precision.'
)

# 3.3
add_heading_styled('3.3 Analysis and Results', level=2)

add_para(
    'The solution shows the unique demand patterns in each of the four zones. The equilibrium '
    'demand of Zone 2 is highest at 123.33 units/day and the lowest equilibrium demand is '
    'Zone 3 at 33.33 units/day. Zone 1 (105.00) and Zone 4 (115.00) fall in between. A non-zero '
    'determinant and full rank assure that this is a unique, stable equilibrium \u2014 the system '
    'settles to a single set of demands, no matter what starting position is assumed.'
)

add_para(
    'The important urban planning implication is that the distribution of resources has a single '
    'predictable steady state. Resources can be provided in a proportional manner with certainty. '
    'Zone 2 has the highest demand (approximately 3.7 times Zone 3), suggesting it is a high-density '
    'residential or commercial area. Low demand in Zone 3 could represent a green zone or a low '
    'density residential area.'
)

# 3.4
add_heading_styled('3.4 Visualisation', level=2)

# Insert figure 1
if os.path.exists(FIG_TASK1):
    doc.add_picture(FIG_TASK1, width=Inches(5.5))
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

add_empty_line()
add_para(
    'Figure 1: Daily demand for each urban area at steady state. The dashed line represents '
    'the average of the demands from all four zones.',
    bold=True, italic=True, size=10, alignment=WD_ALIGN_PARAGRAPH.CENTER
)
add_empty_line()

add_para(
    'The equilibrium demand of each zone is represented as a bar graph in Figure 1. Zone 2 '
    '(123.33 units/day) has the highest demand, while Zone 3 (33.33 units/day) has the lowest. '
    'The average demand line (106.67 units/day) helps planners visualise which zones are above '
    'or below average. Zone 2 and Zone 4 are above average, while Zones 1 and 3 are below.'
)

doc.add_page_break()

# ============================================================
# 4. TASK 2: DEMAND OVER TIME (CALCULUS)
# ============================================================
add_heading_styled('4. Task 2: Demand Over Time (Calculus)', level=1)

# 4.1
add_heading_styled('4.1 Mathematical Analysis (Method Used: Differential Calculus)', level=2)

add_para(
    'Resource demand is modelled by the demand function D(t) = 4t\u00b3 \u2212 18t\u00b2 + 24t + 90 for '
    'a 4-hour period (t in hours). The aim is to help locate high and low demand times, the '
    'rate of change of demand, and the implications for operational planning.'
)

add_para('We use differential calculus to analyse this function:')
add_bullet("The first derivative D'(t) gives the rate of change of demand at any instant.")
add_bullet("The second derivative D''(t) tells us about concavity (the acceleration of change).")
add_bullet("Critical points are found by setting D'(t) = 0. These are candidate points for local maxima or minima.")
add_bullet("The second derivative test (D''(t) > 0 \u2192 local minimum; D''(t) < 0 \u2192 local maximum) classifies each critical point.")
add_bullet("Inflection points occur where D''(t) = 0, indicating a change in concavity.")

# 4.2
add_heading_styled('4.2 Solution', level=2)

# 4.2.1
add_heading_styled('4.2.1 Application of the Power Rule for Differentiation', level=3)

add_para(
    "To find the first derivative, we apply the power rule to each term of D(t). "
    "The power rule states that for any term at\u207f, the derivative is n\u00b7at\u207f\u207b\u00b9."
)

add_para('Given D(t) = 4t\u00b3 \u2212 18t\u00b2 + 24t + 90:')
add_para('Applying the power rule term by term:')
add_equation('d/dt(4t\u00b3) = 3 \u00d7 4t\u00b2 = 12t\u00b2')
add_equation('d/dt(\u221218t\u00b2) = 2 \u00d7 (\u221218)t = \u221236t')
add_equation('d/dt(24t) = 24')
add_equation('d/dt(90) = 0')

add_para("Therefore, the first derivative is:")
add_equation("D'(t) = 12t\u00b2 \u2212 36t + 24")

add_para("The second derivative is obtained by differentiating D'(t):")
add_equation("D''(t) = 24t \u2212 36")

# 4.2.2
add_heading_styled('4.2.2 Identification of Critical Points', level=3)

add_para(
    "Critical points occur where D'(t) = 0, i.e., where the instantaneous rate of change "
    "is zero. At these points, demand is neither increasing nor decreasing."
)

add_para("Set D'(t) = 0:")
add_equation('12t\u00b2 \u2212 36t + 24 = 0')
add_para('Divide both sides by 12 to simplify:')
add_equation('t\u00b2 \u2212 3t + 2 = 0')
add_para('Factor the quadratic:')
add_equation('(t \u2212 1)(t \u2212 2) = 0')
add_para('Therefore, the critical points are:')
add_equation('t\u2081 = 1 hour')
add_equation('t\u2082 = 2 hours')

# 4.2.3
add_heading_styled('4.2.3 Second Derivative Test for Classification', level=3)

add_para('For t = 1:')
add_equation("D''(1) = 24(1) \u2212 36 = \u221212")

add_para(
    "Since D''(1) = \u221212 < 0, the curve is concave down at t = 1, meaning this is a "
    "local maximum. The demand value at this point is:"
)
add_equation('D(1) = 4(1)\u00b3 \u2212 18(1)\u00b2 + 24(1) + 90')
add_equation('D(1) = 4 \u2212 18 + 24 + 90 = 100 units')

add_para('For t = 2:')
add_equation("D''(2) = 24(2) \u2212 36 = 12")

add_para(
    "Since D''(2) = 12 > 0, the curve is concave up at t = 2, meaning this is a "
    "local minimum. The demand value at this point is:"
)
add_equation('D(2) = 4(2)\u00b3 \u2212 18(2)\u00b2 + 24(2) + 90')
add_equation('D(2) = 32 \u2212 72 + 48 + 90 = 98 units')

# 4.2.4
add_heading_styled('4.2.4 Inflection Point Analysis', level=3)

add_para(
    "An inflection point occurs where the concavity of the function changes, i.e., where D''(t) = 0."
)

add_para("Set D''(t) = 0:")
add_equation('24t \u2212 36 = 0')
add_equation('24t = 36')
add_equation('t = 36/24 = 1.5 hours')

add_para('The demand at the inflection point is:')
add_equation('D(1.5) = 4(1.5)\u00b3 \u2212 18(1.5)\u00b2 + 24(1.5) + 90')
add_equation('D(1.5) = 13.5 \u2212 40.5 + 36 + 90 = 99 units')

add_para(
    'This inflection point at t = 1.5 hours marks where the rate of decrease of demand '
    'itself starts to slow down \u2014 the demand curve changes from concave down to concave up.'
)

# 4.2.5
add_heading_styled('4.2.5 Intervals of Increase and Decrease', level=3)

add_para("The sign of D'(t) tells us whether demand is increasing or decreasing over each interval:")

# Table
table2 = doc.add_table(rows=4, cols=4)
table2.style = 'Table Grid'
table2.alignment = WD_TABLE_ALIGNMENT.CENTER
h2 = table2.rows[0].cells
h2[0].text = 'Interval'; h2[1].text = 'Test Point'; h2[2].text = "Sign of D'(t)"; h2[3].text = 'Behaviour'
rows2 = [
    ('t < 1', 't = 0', "D'(0) = 24 > 0", 'Demand INCREASING (ramp-up)'),
    ('1 < t < 2', 't = 1.5', "D'(1.5) = \u22123 < 0", 'Demand DECREASING (mid-period dip)'),
    ('t > 2', 't = 3', "D'(3) = 24 > 0", 'Demand INCREASING (renewed growth)'),
]
for i, (interval, test, sign, behaviour) in enumerate(rows2):
    c = table2.rows[i+1].cells
    c[0].text = interval; c[1].text = test; c[2].text = sign; c[3].text = behaviour
    for cell in c:
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)

add_empty_line()

# 4.2.6
add_heading_styled('4.2.6 Python Verification with Console Output', level=3)

add_para(
    "The symbolic computation of derivatives and the solving of critical points was done "
    "using SymPy. The full Python code and its executed console output are shown below:"
)

add_para('Python Script (code/task2_calculus.py):', bold=True, size=10)
task2_code = open('code/task2_calculus.py', 'r').read()
add_code_block(task2_code, size=7)

add_para('')
add_para('Console Output:', bold=True, size=10)
task2_output = """============================================================
TASK 2 - DEMAND OVER TIME (CALCULUS)
============================================================

Demand function: D(t) = 4t^3 - 18t^2 + 24t + 90
Domain: t >= 0 (t in hours)

--------------------------------------------------
DERIVATIVES
--------------------------------------------------
D'(t) = 12*t**2 - 36*t + 24  = 12t^2 - 36t + 24
D''(t) = 24*t - 36  = 24t - 36

Evaluating at key time points:
  t=0.0: D=90.00,  D'=24.00, D''=-36.00
  t=0.5: D=98.00,  D'=9.00,  D''=-24.00
  t=1.0: D=100.00, D'=0.00,  D''=-12.00
  t=1.5: D=99.00,  D'=-3.00, D''=0.00
  t=2.0: D=98.00,  D'=0.00,  D''=12.00
  t=2.5: D=100.00, D'=9.00,  D''=24.00
  t=3.0: D=108.00, D'=24.00, D''=36.00
  t=4.0: D=154.00, D'=72.00, D''=60.00

--------------------------------------------------
CRITICAL POINTS
--------------------------------------------------
Setting D'(t) = 0:
  12t^2 - 36t + 24 = 0
  Divide by 12: t^2 - 3t + 2 = 0
  Factor: (t-1)(t-2) = 0
  Critical points: t = 1, t = 2

Classification using D''(t):
  t = 1: D''(1) = -12 -> LOCAL MAXIMUM (D'' < 0)
     D(1) = 100.00
  t = 2: D''(2) = 12 -> LOCAL MINIMUM (D'' > 0)
     D(2) = 98.00

--------------------------------------------------
INFLECTION POINT
--------------------------------------------------
Setting D''(t) = 0:
  24t - 36 = 0
  t = 1.5
  D(1.5) = 99.00

--------------------------------------------------
SYMPY VERIFICATION
--------------------------------------------------
Critical points from sympy: [1, 2]
Inflection point from sympy: [3/2]
============================================================
TASK 2 COMPLETE
============================================================"""
add_output_block(task2_output, size=7)

# 4.3
add_heading_styled('4.3 Analysis and Results', level=2)

add_para(
    'The analysis shows a definite demand pattern in the 4-hour window. Demand is 90 at the '
    'beginning and increases to a morning peak of 100 units at t = 1 hour. It then falls to '
    '98 units at t = 2 hours and rises to 154 units at t = 4 hours.'
)

add_para(
    'Of particular interest is the inflection point at t = 1.5 hours \u2014 the rate of decrease is '
    'itself decreasing, thereby indicating that the system will begin to recover even prior to '
    'the beginning of the demand increase at t = 2 hours. This early warning mechanism is useful '
    'for automated resource management systems.'
)

add_para(
    'For operational planning, the period t = 1 to t = 2 hours (the dip) is the best time for '
    'scheduled maintenance or reallocation of resources, as demand is at a minimum and the system '
    'is under the least stress. Pre-positioned capacity is needed for the morning peak at t = 1, '
    'and plans for continued growth must be in place for the growth phase after t = 2.'
)

# 4.4
add_heading_styled('4.4 Visualisation', level=2)

# Insert figure 2
if os.path.exists(FIG_TASK2):
    doc.add_picture(FIG_TASK2, width=Inches(5.5))
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

add_empty_line()
add_para(
    "Figure 2: Demand over time D(t) (top panel) with critical points highlighted, and "
    "the rate of change D'(t) (bottom panel) with shaded increasing/decreasing regions.",
    bold=True, italic=True, size=10, alignment=WD_ALIGN_PARAGRAPH.CENTER
)
add_empty_line()

add_para(
    'Two related plots are shown in Figure 2. The top panel displays the demand curve D(t) '
    'with the inflection point (red dotted), the local minimum (orange), and the local '
    'maximum (red) highlighted. The bottom panel is the rate of change D\'(t), with green '
    'shading for increasing demand and red shading for decreasing demand. The critical points '
    "of the demand curve are the zeros of D'(t) at t = 1 and t = 2."
)

doc.add_page_break()

# ============================================================
# 5. TASK 3: FORECASTING ERROR RISK (PROBABILITY)
# ============================================================
add_heading_styled('5. Task 3: Forecasting Error Risk (Probability)', level=1)

# 5.1
add_heading_styled('5.1 Mathematical Analysis (Method Used: Normal Distribution and Z-Scores)', level=2)

add_para(
    'Forecasting errors in resource demand follow a normal distribution with mean zero '
    '(no systematic bias) and standard deviation of 5 units. This means that while errors '
    'are equally likely to overestimate and underestimate, their magnitude follows the '
    'bell-shaped curve of the normal distribution.'
)

add_para(
    'The empirical rule (68-95-99.7 rule) provides an intuitive starting point for stakeholders. '
    'Three key thresholds are analysed: \u00b15 units (1\u03c3), \u00b110 units (2\u03c3), and '
    '\u00b115 units (3\u03c3). The probability that an error exceeds the threshold is computed using '
    'z-scores and the cumulative distribution function (CDF).'
)

add_para('The z-score formula is:')
add_equation('z = (x - \u03bc) / \u03c3')
add_para('where x is the threshold value, \u03bc = 0 is the mean, and \u03c3 = 5 is the standard deviation.')
add_para('For a two-tailed test (errors can exceed the threshold in either direction):')
add_equation('P(|error| > x) = 2 \u00d7 P(error > x) = 2 \u00d7 (1 \u2212 \u03a6(z))')
add_para('where \u03a6(z) is the standard normal CDF.')

# 5.2
add_heading_styled('5.2 Solution', level=2)

add_heading_styled('5.2.1 Z-Score Calculation', level=3)
add_para('For threshold \u00b15 units:')
add_equation('z = 5/5 = 1.0 \u2192 P(|error| > 5) = 2 \u00d7 (1 \u2212 \u03a6(1.0)) = 2 \u00d7 (1 \u2212 0.8413) = 0.3173 (31.73%)')
add_para('For threshold \u00b110 units:')
add_equation('z = 10/5 = 2.0 \u2192 P(|error| > 10) = 2 \u00d7 (1 \u2212 \u03a6(2.0)) = 2 \u00d7 (1 \u2212 0.9772) = 0.0456 (4.56%)')
add_para('For threshold \u00b115 units:')
add_equation('z = 15/5 = 3.0 \u2192 P(|error| > 15) = 2 \u00d7 (1 \u2212 \u03a6(3.0)) = 2 \u00d7 (1 \u2212 0.9987) = 0.0027 (0.27%)')

add_heading_styled('5.2.2 Buffer Coverage', level=3)
add_para('The complement probabilities show what buffer level covers what proportion of days:')
add_para('\u00b15 units: covers 68.27% of days \u2014 inadequate (nearly one-third of days exceed this)')
add_para('\u00b110 units: covers 95.45% of days \u2014 adequate for almost all normal operations')
add_para('\u00b115 units: covers 99.73% of days \u2014 conservative (only 1 day per year exceeds)')

add_heading_styled('5.2.3 Python Verification with Console Output', level=3)

add_para(
    'The probability calculations were verified using scipy.stats.norm. The full Python code '
    'and its executed console output are shown below:'
)

add_para('Python Script (code/task3_probability.py):', bold=True, size=10)
task3_code = open('code/task3_probability.py', 'r').read()
add_code_block(task3_code, size=7)

add_para('')
add_para('Console Output:', bold=True, size=10)
task3_output = """P(|error| > 5) = 0.317311 (31.7311%)
P(|error| > 10) = 0.045500 (4.5500%)
P(|error| > 15) = 0.002700 (0.2700%)

--- Buffer Coverage ---
P(|error| <= 5) = 0.682689 (68.2689%)
P(|error| <= 10) = 0.954500 (95.4500%)
P(|error| <= 15) = 0.997300 (99.7300%)

--- Z-Scores ---
z for threshold 5: 1.00
z for threshold 10: 2.00
z for threshold 15: 3.00

--- Risk Management Summary ---
Buffer +/-5: covers 68.27% | risk: 31.73%
Buffer +/-10: covers 95.45% | risk: 4.55%
Buffer +/-15: covers 99.73% | risk: 0.27%"""
add_output_block(task3_output, size=7)

# 5.3
add_heading_styled('5.3 Analysis and Results', level=2)

add_para(
    'The probability computations show the decreasing likelihood of large forecast errors: '
    'about one-third of daily forecasts will have errors exceeding 5 units, but only about '
    '1 in 20 days (4.55%) will see errors beyond 10 units, and only about 1 in 370 days '
    '(0.27%) will exceed 15 units.'
)

add_para(
    'For risk management, a buffer of \u00b110 units represents a good balance between coverage '
    'and resource efficiency \u2014 it covers 95.45% of all days. A \u00b115 unit buffer would cover '
    '99.73% of days but ties up three times the reserve capacity, which is likely inefficient. '
    'The remaining 0.27% of exceptional days (about 1 in 370, or roughly once per year for a '
    'daily forecast) can be managed through emergency escalation procedures rather than standing reserves.'
)

# 5.4
add_heading_styled('5.4 Visualisation', level=2)

if os.path.exists(FIG_TASK3):
    doc.add_picture(FIG_TASK3, width=Inches(5.5))
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

add_empty_line()
add_para(
    'Figure 3: Normal distribution of forecast errors with shaded tail regions. The blue, green, '
    'and cyan regions represent the probability of errors exceeding \u00b15, \u00b110, and \u00b115 units '
    'respectively. The dashed vertical lines mark each threshold.',
    bold=True, italic=True, size=10, alignment=WD_ALIGN_PARAGRAPH.CENTER
)
add_empty_line()

add_para(
    'Figure 3 shows the normal distribution of forecast errors centered at zero. The shaded '
    'tail regions beyond each threshold decrease rapidly as the threshold increases. The empirical '
    'rule is visually confirmed: most of the probability mass lies within \u00b12\u03c3 (\u00b110) and almost '
    'all within \u00b13\u03c3 (\u00b115). This visual presentation helps non-technical stakeholders quickly '
    'grasp the risk profile of the forecasting system.'
)

doc.add_page_break()

# ============================================================
# 6. TASK 4: CONSUMPTION BY BUILDING TYPE (STATISTICS)
# ============================================================
add_heading_styled('6. Task 4: Consumption by Building Type (Statistics)', level=1)

# 6.1
add_heading_styled('6.1 Mathematical Analysis (Method Used: One-Way ANOVA and Post-Hoc Testing)', level=2)

add_para(
    'This task investigates whether mean daily water consumption differs across three building types: '
    'Apartments (n=8), Terraced houses (n=10), and Detached houses (n=6). The sample sizes are unequal, '
    'so one-way ANOVA is used as it naturally handles unequal group sizes.'
)

add_para('The data for each group:')
add_bullet('Apartments (n=8): 16.8, 17.2, 16.5, 17.9, 18.1, 17.4, 16.9, 17.6')
add_bullet('Terraced (n=10): 18.4, 18.9, 19.1, 18.7, 19.3, 18.6, 19.0, 18.8, 19.2, 18.5')
add_bullet('Detached (n=6): 20.1, 19.7, 20.4, 19.9, 20.6, 20.2')

add_para('Hypothesis testing framework:')
add_para('H\u2080: \u03bc\u2090 = \u03bc\u1d40 = \u03bc\u1d30 (all group means are equal)', bold=True)
add_para('H\u2081: At least one group mean differs from the others', bold=True)
add_para('Significance level: \u03b1 = 0.05')

add_para(
    'Before conducting ANOVA, two assumptions must be checked: (1) normality of each group\'s data '
    '(Shapiro-Wilk test), and (2) equality of variances across groups (Levene\'s test). If both '
    'assumptions hold, standard one-way ANOVA is valid. If variances are unequal, Welch\'s ANOVA '
    'provides a robust alternative.'
)

# 6.2
add_heading_styled('6.2 Solution', level=2)

add_heading_styled('6.2.1 Descriptive Statistics', level=3)
add_para('Group means and standard deviations:')
add_equation('Apartments: x\u0304 = 17.30, s = 0.56, n = 8')
add_equation('Terraced:   x\u0304 = 18.85, s = 0.30, n = 10')
add_equation('Detached:   x\u0304 = 20.15, s = 0.33, n = 6')
add_para(
    'Detached homes show the highest mean consumption (20.15 units), followed by terraced '
    '(18.85 units), and apartments (17.30 units). The standard deviations suggest the variation '
    'within each group is small relative to the differences between groups.'
)

add_heading_styled('6.2.2 Assumption Checks', level=3)

add_para('Normality (Shapiro-Wilk Test):', bold=True)
add_para(
    'The Shapiro-Wilk test evaluates whether each group\'s data follows a normal distribution. '
    'A p-value > 0.05 indicates normality cannot be rejected.'
)
add_para('Apartments: W = 0.9733, p = 0.9222 \u2192 Data appears normal')
add_para('Terraced:   W = 0.9702, p = 0.8924 \u2192 Data appears normal')
add_para('Detached:   W = 0.9902, p = 0.9897 \u2192 Data appears normal')
add_para('All groups satisfy the normality assumption (p > 0.05).')

add_para('Equal Variances (Levene\'s Test):', bold=True)
add_para(
    'Levene\'s test checks whether the variances of the three groups are equal. '
    'A p-value > 0.05 indicates equal variances cannot be rejected.'
)
add_para('Levene statistic = 2.4889, p = 0.1071 \u2192 Variances are equal')
add_para('Both assumptions are satisfied, so standard one-way ANOVA is appropriate.')

add_heading_styled('6.2.3 One-Way ANOVA', level=3)
add_para('ANOVA partitions the total variance into between-group and within-group components:')
add_equation('SS_total = SS_between + SS_within')
add_para('The F-statistic is computed as:')
add_equation('F = MS_between / MS_within')
add_para('where MS = SS / df (mean square).')
add_para('Results:')
add_equation('F(2, 21) = 84.95, p < 0.000001')
add_para(
    'Since p < 0.05, we reject the null hypothesis and conclude that there is a statistically '
    'significant difference in mean daily consumption between at least one pair of building types.'
)

add_heading_styled('6.2.4 Post-Hoc Analysis (Tukey HSD)', level=3)
add_para(
    'Tukey\'s Honestly Significant Difference test identifies which specific pairs of groups '
    'differ significantly, while controlling the family-wise error rate at \u03b1 = 0.05. '
    'The test automatically adjusts for unequal sample sizes.'
)

add_para('Pairwise comparisons:')
add_equation('Apartments vs Detached: mean diff = 2.85, p < 0.001, 95% CI [2.29, 3.41]')
add_equation('Apartments vs Terraced: mean diff = 1.55, p < 0.001, 95% CI [1.06, 2.04]')
add_equation('Detached vs Terraced: mean diff = -1.30, p < 0.001, 95% CI [-1.83, -0.77]')

add_para(
    'All three pairwise comparisons are statistically significant (p < 0.001). This means each '
    'building type has a distinct mean consumption level, with no two groups being statistically '
    'indistinguishable.'
)

add_heading_styled('6.2.5 Python Verification with Console Output', level=3)

add_para(
    'The full statistical analysis was performed using scipy.stats and statsmodels. '
    'The Python code and its executed console output are shown below:'
)

add_para('Python Script (code/task4_statistics.py):', bold=True, size=10)
task4_code = open('code/task4_statistics.py', 'r').read()
add_code_block(task4_code, size=7)

add_para('')
add_para('Console Output:', bold=True, size=10)
task4_output = """======================================================================
TASK 4 - CONSUMPTION BY BUILDING TYPE (STATISTICS)
======================================================================

----------------------------------------------------------------------
1. DESCRIPTIVE STATISTICS PER GROUP
----------------------------------------------------------------------
Group           n      Mean       SD         Min      Max
------------------------------------------------------------
Apartments      8      17.3000    0.5555     16.50    18.10
Terraced        10     18.8500    0.3028     18.40    19.30
Detached        6      20.1500    0.3271     19.70    20.60

----------------------------------------------------------------------
2. ASSUMPTION CHECKS
----------------------------------------------------------------------

2a. Normality Check (Shapiro-Wilk):
    H0: Data follows a normal distribution
    H1: Data does NOT follow a normal distribution
Group           W-statistic     p-value         Normal?
-------------------------------------------------------
Apartments      0.9733          0.9222          Yes
Terraced        0.9702          0.8924          Yes
Detached        0.9902          0.9897          Yes

  -> All groups appear normally distributed (p > 0.05).

2b. Equal Variances Check (Levene's Test):
    H0: All group variances are equal
    H1: At least one group variance differs
    Levene statistic = 2.4889
    p-value          = 0.1071

  -> Variances are equal (p > 0.05) - standard ANOVA is appropriate.

----------------------------------------------------------------------
3. ONE-WAY ANOVA
----------------------------------------------------------------------
    H0: mean_apartments = mean_terraced = mean_detached (all means equal)
    H1: At least one group mean differs from the others
    alpha = 0.05

    F-statistic = 84.9496
    p-value      = 0.000000

  -> p = 0.000000 < 0.05 -> REJECT H0.
  -> There is a statistically significant difference in mean daily
     consumption between building types.

----------------------------------------------------------------------
4. POST-HOC ANALYSIS (Tukey HSD)
----------------------------------------------------------------------
   Multiple Comparison of Means - Tukey HSD, FWER=0.05
=========================================================
  group1    group2  meandiff p-adj  lower   upper  reject
---------------------------------------------------------
Apartments Detached     2.85   0.0  2.2927  3.4073   True
Apartments Terraced     1.55   0.0  1.0605  2.0395   True
  Detached Terraced     -1.3   0.0 -1.8329 -0.7671   True
---------------------------------------------------------

Tukey HSD interpretation:
  Groups sharing the same letter/reject=False are NOT significantly different.
  Groups with reject=True have significantly different means.

----------------------------------------------------------------------
5. VISUALISATION - Boxplot by Building Type
----------------------------------------------------------------------

Figure saved: figures/fig_task4_boxplot.png

----------------------------------------------------------------------
6. SUMMARY OF FINDINGS
----------------------------------------------------------------------
  Apartments: mean = 17.30, n = 8
  Terraced:   mean = 18.85, n = 10
  Detached:   mean = 20.15, n = 6
  ANOVA:      F(2,21) = 84.95, p = 0.000000
  Tukey HSD:  See table above for pairwise comparisons.

  Key interpretation:
  - Detached homes show the highest consumption, suggesting they are
    the priority segment for efficiency interventions.
  - Apartments show the lowest consumption, likely due to shared
    infrastructure and smaller living spaces.
  - Terraced homes fall in between, but may differ significantly
    from both other groups (check Tukey HSD results).
======================================================================
TASK 4 COMPLETE
======================================================================"""
add_output_block(task4_output, size=7)

# 6.3
add_heading_styled('6.3 Analysis and Results', level=2)

add_para(
    'The ANOVA results show a highly significant difference between building types '
    '(F(2,21) = 84.95, p < 0.001). The Tukey HSD post-hoc test reveals that all three '
    'pairwise comparisons are significant, meaning each building type has a distinct '
    'consumption profile. Detached homes have the highest mean consumption (20.15 units/day), '
    'followed by terraced houses (18.85), and apartments (17.30).'
)

add_para(
    'The effect size is substantial: the difference between detached and apartment consumption '
    'is 2.85 units, which represents a 16.5% increase over apartment consumption. The difference '
    'between terraced and apartment consumption is 1.55 units (9.0% increase).'
)

add_para(
    'For urban planners, these results suggest that energy efficiency interventions should be '
    'prioritised for detached homes, as they consume the most resources per household. The lower '
    'consumption in apartments likely reflects shared infrastructure and more compact living spaces, '
    'which are inherently more efficient.'
)

# 6.4
add_heading_styled('6.4 Visualisation', level=2)

if os.path.exists(FIG_TASK4):
    doc.add_picture(FIG_TASK4, width=Inches(5.5))
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

add_empty_line()
add_para(
    'Figure 4: Boxplot of daily consumption by building type. The boxes show the interquartile '
    'range, whiskers show the range, and black dots show individual observations. Red diamonds '
    'indicate group means.',
    bold=True, italic=True, size=10, alignment=WD_ALIGN_PARAGRAPH.CENTER
)
add_empty_line()

add_para(
    'Figure 4 presents a boxplot for each building type. The visual separation between the three '
    'groups is clear: the boxes do not overlap, confirming the statistical results. The apartments '
    'show the widest spread (due to their larger sample size relative to consumption variation), '
    'while detached homes have the tightest clustering around their higher mean. Individual data '
    'points (black dots) show the actual observations, and the red diamonds highlight the group means.'
)

doc.add_page_break()

# ============================================================
# 10. REFERENCES
# ============================================================
add_heading_styled('10. References', level=1)

refs = [
    'Anton, H., Rorres, C. and Kaul, A. (2014) Elementary Linear Algebra: Applications Version. 11th edn. Hoboken: Wiley.',
    'Stewart, J. (2016) Calculus: Early Transcendentals. 8th edn. Boston: Cengage Learning.',
    'Thomas, G.B., Weir, M.D. and Hass, J. (2018) Thomas\' Calculus. 14th edn. Boston: Pearson.',
    'Ross, S.M. (2019) Introduction to Probability Models. 12th edn. London: Academic Press.',
    'Devore, J.L. (2015) Probability and Statistics for Engineering and the Sciences. 9th edn. Boston: Cengage Learning.',
    'Montgomery, D.C. (2017) Design and Analysis of Experiments. 9th edn. Hoboken: Wiley.',
]
for ref in refs:
    p = doc.add_paragraph()
    run = p.add_run(ref)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.first_line_indent = Cm(-1.27)

doc.add_page_break()

# ============================================================
# 11. APPENDIX
# ============================================================
add_heading_styled('11. Appendix', level=1)
add_para('Full Python code for all tasks is provided below.', bold=True)

add_heading_styled('Task 1: Linear Algebra', level=2)
add_code_block(open('code/task1_linear_algebra.py', 'r').read(), size=8)

doc.add_page_break()
add_heading_styled('Task 2: Calculus', level=2)
add_code_block(open('code/task2_calculus.py', 'r').read(), size=8)

doc.add_page_break()
add_heading_styled('Task 3: Probability', level=2)
add_code_block(open('code/task3_probability.py', 'r').read(), size=8)

doc.add_page_break()
add_heading_styled('Task 4: Statistics', level=2)
add_code_block(open('code/task4_statistics.py', 'r').read(), size=8)

# ============================================================
# SAVE
# ============================================================
output_path = 'report.docx'
doc.save(output_path)
print(f'FINAL report saved to {output_path}')
print(f'File size: {os.path.getsize(output_path)} bytes')
print(f'Task 1 figure exists: {os.path.exists(FIG_TASK1)}')
print(f'Task 2 figure exists: {os.path.exists(FIG_TASK2)}')
print(f'Task 3 figure exists: {os.path.exists(FIG_TASK3)}')
print(f'Task 4 figure exists: {os.path.exists(FIG_TASK4)}')