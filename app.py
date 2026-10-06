from datetime import date
from decimal import Decimal, InvalidOperation

import streamlit as st

from calculations import calculate_invoice, line_total
from pdf_export import create_invoice_pdf
from storage import list_invoices, load_invoice, save_invoice


st.set_page_config(
    page_title="Invoice Generator",
    page_icon="🧾",
    layout="wide",
)


def new_line_item():
    """Return a new blank line item with a unique session ID."""
    item_id = st.session_state.next_item_id
    st.session_state.next_item_id += 1

    return {
        "id": item_id,
        "description": "",
        "quantity": "1",
        "unit_price": "0.00",
    }


def initialize_state():
    """Create the initial Streamlit session state."""
    if "next_item_id" not in st.session_state:
        st.session_state.next_item_id = 1

    if "line_items" not in st.session_state:
        st.session_state.line_items = [new_line_item()]

    if "client_name" not in st.session_state:
        st.session_state.client_name = ""

    if "client_address" not in st.session_state:
        st.session_state.client_address = ""

    if "invoice_number" not in st.session_state:
        st.session_state.invoice_number = ""

    if "invoice_date" not in st.session_state:
        st.session_state.invoice_date = date.today()

    if "discount_percent" not in st.session_state:
        st.session_state.discount_percent = "0"

    if "tax_percent" not in st.session_state:
        st.session_state.tax_percent = "0"


def add_line_item():
    """Add another invoice line item."""
    st.session_state.line_items.append(new_line_item())


def remove_line_item(item_id):
    """Remove a line item using its unique ID."""
    st.session_state.line_items = [
        item
        for item in st.session_state.line_items
        if item["id"] != item_id
    ]


def decimal_from_text(text, default="0"):
    """Convert text input to Decimal without using float."""
    try:
        value = str(text).strip()

        if value == "":
            return Decimal(default)

        return Decimal(value)
    except (InvalidOperation, ValueError):
        return Decimal(default)


def build_invoice_data(totals):
    """Build a JSON-safe invoice dictionary."""
    items = []

    for item in st.session_state.line_items:
        quantity = decimal_from_text(item["quantity"])
        unit_price = decimal_from_text(item["unit_price"])

        try:
            item_total = line_total(quantity, unit_price)
        except ValueError:
            item_total = Decimal("0.00")

        items.append(
            {
                "description": item["description"],
                "quantity": str(quantity),
                "unit_price": str(unit_price),
                "line_total": str(item_total),
            }
        )

    return {
        "client_name": st.session_state.client_name,
        "client_address": st.session_state.client_address,
        "invoice_number": st.session_state.invoice_number,
        "date": str(st.session_state.invoice_date),
        "discount_percent": st.session_state.discount_percent,
        "tax_percent": st.session_state.tax_percent,
        "line_items": items,
        "totals": {
            key: str(value)
            for key, value in totals.items()
        },
    }


def load_selected_invoice(invoice_number):
    """Load invoice data into session state."""
    invoice = load_invoice(invoice_number)

    # Clear old line-item widget values before loading saved data.
    widget_prefixes = (
        "description_",
        "quantity_",
        "price_",
        "remove_",
    )

    for key in list(st.session_state.keys()):
        if key.startswith(widget_prefixes):
            del st.session_state[key]

    st.session_state.client_name = invoice.get("client_name", "")
    st.session_state.client_address = invoice.get("client_address", "")
    st.session_state.invoice_number = invoice.get("invoice_number", "")

    saved_date = invoice.get("date", str(date.today()))
    st.session_state.invoice_date = date.fromisoformat(saved_date)

    st.session_state.discount_percent = str(
        invoice.get("discount_percent", "0")
    )
    st.session_state.tax_percent = str(
        invoice.get("tax_percent", "0")
    )

    loaded_items = []

    for item in invoice.get("line_items", []):
        item_id = st.session_state.next_item_id
        st.session_state.next_item_id += 1

        loaded_items.append(
            {
                "id": item_id,
                "description": item.get("description", ""),
                "quantity": str(item.get("quantity", "1")),
                "unit_price": str(item.get("unit_price", "0.00")),
            }
        )

    if not loaded_items:
        loaded_items = [new_line_item()]

    st.session_state.line_items = loaded_items

initialize_state()

if "invoice_to_load" in st.session_state:
    invoice_number_to_load = st.session_state.pop("invoice_to_load")
    load_selected_invoice(invoice_number_to_load)


st.title("Invoice Generator")
st.write(
    "Create invoices, calculate totals, save them as JSON, "
    "and export printable PDFs."
)

st.subheader("Client and Invoice Information")

left, right = st.columns(2)

with left:
    st.text_input(
        "Client name",
        key="client_name",
    )

    st.text_area(
        "Client address",
        key="client_address",
        height=100,
    )

with right:
    st.text_input(
        "Invoice number",
        key="invoice_number",
    )

    st.date_input(
        "Invoice date",
        key="invoice_date",
    )


st.subheader("Line Items")

header = st.columns([4, 1.5, 2, 2, 1])
header[0].markdown("**Description**")
header[1].markdown("**Quantity**")
header[2].markdown("**Unit Price**")
header[3].markdown("**Line Total**")
header[4].markdown("**Remove**")

calculation_items = []
item_to_remove = None

for item in st.session_state.line_items:
    item_id = item["id"]

    columns = st.columns([4, 1.5, 2, 2, 1])

    description = columns[0].text_input(
        "Description",
        value=item["description"],
        key=f"description_{item_id}",
        label_visibility="collapsed",
    )

    quantity_text = columns[1].text_input(
        "Quantity",
        value=item["quantity"],
        key=f"quantity_{item_id}",
        label_visibility="collapsed",
    )

    price_text = columns[2].text_input(
        "Unit Price",
        value=item["unit_price"],
        key=f"price_{item_id}",
        label_visibility="collapsed",
    )

    item["description"] = description
    item["quantity"] = quantity_text
    item["unit_price"] = price_text

    quantity = decimal_from_text(quantity_text)
    unit_price = decimal_from_text(price_text)

    try:
        current_line_total = line_total(
            quantity,
            unit_price,
        )
        columns[3].write(f"${current_line_total}")
    except ValueError as error:
        current_line_total = Decimal("0.00")
        columns[3].error(str(error))

    calculation_items.append(
        {
            "quantity": quantity,
            "unit_price": unit_price,
        }
    )

    if columns[4].button(
        "Remove",
        key=f"remove_{item_id}",
    ):
        item_to_remove = item_id


if item_to_remove is not None:
    remove_line_item(item_to_remove)
    st.rerun()


st.button(
    "Add Line Item",
    on_click=add_line_item,
)


st.subheader("Discount and Tax")

discount_col, tax_col = st.columns(2)

with discount_col:
    st.text_input(
        "Discount (%)",
        key="discount_percent",
    )

with tax_col:
    st.text_input(
        "Tax (%)",
        key="tax_percent",
    )


discount = decimal_from_text(
    st.session_state.discount_percent
)

tax = decimal_from_text(
    st.session_state.tax_percent
)

calculation_error = None

try:
    totals = calculate_invoice(
        calculation_items,
        discount_percent=discount,
        tax_percent=tax,
    )
except ValueError as error:
    calculation_error = str(error)
    totals = {
        "subtotal": Decimal("0.00"),
        "discount": Decimal("0.00"),
        "taxable_amount": Decimal("0.00"),
        "tax": Decimal("0.00"),
        "grand_total": Decimal("0.00"),
    }

if calculation_error:
    st.error(calculation_error)


st.subheader("Invoice Totals")

total_col1, total_col2, total_col3, total_col4 = st.columns(4)

total_col1.metric(
    "Subtotal",
    f"${totals['subtotal']}",
)

total_col2.metric(
    "Discount",
    f"-${totals['discount']}",
)

total_col3.metric(
    "Tax",
    f"${totals['tax']}",
)

total_col4.metric(
    "Grand Total",
    f"${totals['grand_total']}",
)


st.divider()

st.subheader("Save and Export")

invoice_data = build_invoice_data(totals)

save_col, pdf_col = st.columns(2)

with save_col:
    if st.button("Save Invoice"):
        if not st.session_state.invoice_number.strip():
            st.error("Enter an invoice number before saving.")
        elif not st.session_state.client_name.strip():
            st.error("Enter a client name before saving.")
        else:
            path = save_invoice(invoice_data)
            st.success(f"Invoice saved to {path}.")

with pdf_col:
    if st.session_state.invoice_number.strip():
        pdf_bytes = create_invoice_pdf(
            invoice_data,
            totals,
        )

        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=(
                f"invoice_"
                f"{st.session_state.invoice_number}.pdf"
            ),
            mime="application/pdf",
        )
    else:
        st.info(
            "Enter an invoice number to enable PDF export."
        )


st.subheader("Load Saved Invoice")

saved_invoices = list_invoices()

if saved_invoices:
    selected_invoice = st.selectbox(
        "Saved invoices",
        saved_invoices,
    )

    if st.button("Load Invoice"):
        st.session_state.invoice_to_load = selected_invoice
        st.rerun()
else:
    st.info("No saved invoices yet.")