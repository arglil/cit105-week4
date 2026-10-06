\# CIT 105 Week 4 - Invoicing Application



A Streamlit invoicing application that creates invoices, performs exact currency calculations, saves invoices as JSON, reloads saved invoices, and exports printable PDF invoices.



\## Features



\- Enter client name and address

\- Enter invoice number and date

\- Dynamically add and remove invoice line items

\- Enter quantity and unit price for each item

\- Live subtotal calculation

\- Percentage discount

\- Percentage tax

\- Discount is applied before tax

\- Exact currency calculations using Python `Decimal`

\- Save invoices as JSON

\- Load previously saved invoices

\- Export invoices as PDF

\- Automated calculation tests with pytest



\## Project Structure



```text

cit105-week4/

├── app.py

├── calculations.py

├── storage.py

├── pdf\_export.py

├── test\_calculations.py

├── requirements.txt

├── sample\_invoice.pdf

├── screenshots/

│   └── invoice-app.png

└── README.md

```



\### `calculations.py`



Contains the invoice arithmetic. Streamlit is not used in this module. Currency calculations use `Decimal` instead of floating-point arithmetic.



\### `storage.py`



Handles saving invoices to JSON, loading saved invoices, and listing available invoices.



\### `pdf\_export.py`



Creates printable PDF invoices using `fpdf2`.



\### `app.py`



Contains the Streamlit user interface and calls the calculation, storage, and PDF modules.



\### `test\_calculations.py`



Contains automated pytest tests for normal calculations and edge cases.



\## Installation



Clone the repository:



```bash

git clone <repository-url>

cd cit105-week4

```



Create and activate a virtual environment if desired, then install the dependencies:



```bash

python -m pip install -r requirements.txt

```



\## Run the Application



```bash

streamlit run app.py

```



The Streamlit application will open in a web browser.



\## Run the Tests



```bash

python -m pytest -v

```



The calculation test suite contains 9 tests.



### Test Results

```text
collected 9 items

test_calculations.py::test_normal_invoice_calculation PASSED
test_calculations.py::test_empty_invoice PASSED
test_calculations.py::test_zero_quantity PASSED
test_calculations.py::test_negative_quantity_rejected PASSED
test_calculations.py::test_half_cent_rounding PASSED
test_calculations.py::test_one_hundred_percent_discount PASSED
test_calculations.py::test_large_money_value_keeps_precision PASSED
test_calculations.py::test_discount_is_applied_before_tax PASSED
test_calculations.py::test_discount_above_one_hundred_rejected PASSED

9 passed in 0.03s
```

\## Currency Calculation Design



All monetary calculations are performed with Python's `Decimal` class rather than binary floating-point arithmetic.



Currency values are rounded to the nearest cent using `ROUND\_HALF\_UP`.



The application calculates totals in this order:



```text

Subtotal

\- Discount

= Taxable Amount

\+ Tax

= Grand Total

```



This ensures that the discount is applied before tax.



\## Edge Cases and Protections Tested



In addition to the normal invoice calculation, the test suite includes the following cases:



1\. \*\*Empty invoice\*\* - verifies an invoice with no line items produces a $0.00 subtotal and grand total.

2\. \*\*Zero and negative quantity\*\* - verifies zero quantity produces $0.00 and a negative quantity is rejected.

3\. \*\*Exact half-cent rounding\*\* - verifies `10.005` correctly rounds to `10.01` using `ROUND\_HALF\_UP`.

4\. \*\*100% discount\*\* - verifies a full discount reduces the taxable amount, tax, and grand total to $0.00.

5\. \*\*Large monetary value\*\* - verifies a very large invoice total maintains exact decimal precision.

6\. \*\*Discount before tax\*\* - explicitly verifies tax is calculated after the discount has been subtracted.

7\. \*\*Invalid discount protection\*\* - verifies discounts greater than 100% are rejected.



These tests protect the calculation layer from common invoice and floating-point precision errors.



\## Dynamic Line Item Protection



Each invoice line item receives a unique session-state ID. This allows a user to:



1\. Add a line item.

2\. Remove a line item.

3\. Add another line item.



The remaining line-item data stays associated with the correct row instead of being reassigned to another Streamlit widget.



Saved invoices are also loaded before the invoice widgets are instantiated during a rerun. This prevents Streamlit widget/session-state conflicts when restoring an invoice.



\## Application Screenshot



!\[Invoice application](screenshots/invoice-app.png)



\## Sample PDF



A generated invoice is included in the repository as:



```text

sample\_invoice.pdf

```



The sample demonstrates the application's PDF export functionality.



\## Example Calculation



For the sample invoice:



```text

Subtotal:       $508.25

Discount:       $50.83

Tax:            $32.02

Grand Total:    $489.44

```



\## Technologies



\- Python

\- Streamlit

\- Decimal

\- JSON

\- fpdf2

\- pytest

