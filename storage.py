import json
from pathlib import Path


INVOICE_DIRECTORY = Path("invoices")


def ensure_invoice_directory():
    """Create the invoice storage directory if it does not exist."""
    INVOICE_DIRECTORY.mkdir(exist_ok=True)


def invoice_path(invoice_number):
    """Return the JSON path for an invoice number."""
    ensure_invoice_directory()

    safe_number = "".join(
        char for char in str(invoice_number)
        if char.isalnum() or char in ("-", "_")
    )

    if not safe_number:
        raise ValueError("Invoice number must contain valid characters.")

    return INVOICE_DIRECTORY / f"{safe_number}.json"


def save_invoice(invoice):
    """Save an invoice dictionary as JSON."""
    if not invoice.get("invoice_number", "").strip():
        raise ValueError("Invoice number is required.")

    path = invoice_path(invoice["invoice_number"])

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            invoice,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return path


def load_invoice(invoice_number):
    """Load a saved invoice from JSON."""
    path = invoice_path(invoice_number)

    if not path.exists():
        raise FileNotFoundError(
            f"Invoice {invoice_number} was not found."
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def list_invoices():
    """Return the invoice numbers for all saved invoices."""
    ensure_invoice_directory()

    return sorted(
        path.stem
        for path in INVOICE_DIRECTORY.glob("*.json")
    )