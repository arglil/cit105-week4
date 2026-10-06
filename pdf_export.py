import io

from fpdf import FPDF


def create_invoice_pdf(invoice, totals):
    """Create a formatted invoice PDF and return its bytes."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "INVOICE", align="C")
    pdf.ln(18)

    # Invoice information
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(35, 8, "Invoice Number:")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, str(invoice["invoice_number"]))
    pdf.ln()

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(35, 8, "Date:")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, str(invoice["date"]))
    pdf.ln(12)

    # Client information
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Bill To")
    pdf.ln()

    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, str(invoice["client_name"]))
    pdf.ln()

    for line in str(invoice["client_address"]).splitlines():
        pdf.cell(0, 7, line)
        pdf.ln()

    pdf.ln(8)

    # Line item table headings
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(75, 8, "Description", border=1)
    pdf.cell(25, 8, "Quantity", border=1, align="R")
    pdf.cell(40, 8, "Unit Price", border=1, align="R")
    pdf.cell(40, 8, "Line Total", border=1, align="R")
    pdf.ln()

    # Line items
    pdf.set_font("Helvetica", size=10)

    for item in invoice["line_items"]:
        description = str(item["description"])[:35]
        quantity = str(item["quantity"])
        unit_price = str(item["unit_price"])
        line_total = str(item["line_total"])

        pdf.cell(75, 8, description, border=1)
        pdf.cell(25, 8, quantity, border=1, align="R")
        pdf.cell(40, 8, f"${unit_price}", border=1, align="R")
        pdf.cell(40, 8, f"${line_total}", border=1, align="R")
        pdf.ln()

    pdf.ln(8)

    # Totals
    pdf.set_font("Helvetica", size=11)

    pdf.cell(140, 8, "Subtotal:", align="R")
    pdf.cell(40, 8, f"${totals['subtotal']}", align="R")
    pdf.ln()

    pdf.cell(140, 8, "Discount:", align="R")
    pdf.cell(40, 8, f"-${totals['discount']}", align="R")
    pdf.ln()

    pdf.cell(140, 8, "Tax:", align="R")
    pdf.cell(40, 8, f"${totals['tax']}", align="R")
    pdf.ln()

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(140, 9, "Grand Total:", align="R")
    pdf.cell(40, 9, f"${totals['grand_total']}", align="R")

    pdf.ln(15)

    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 8, "Thank you for your business.", align="C")

    pdf_bytes = pdf.output()
    return bytes(pdf_bytes)