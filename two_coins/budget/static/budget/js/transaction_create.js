document.addEventListener('DOMContentLoaded', function () {
    const currencySelect = document.getElementById('id_currency');
    const accountSelect = document.getElementById('id_account');
    const defaultCurrencyDiv = document.getElementById('amount_converted_field');
    const amountAccountCurrencyText = document.getElementById('amount_converted_text');
    const amount_converted_input = document.getElementById('amount_converted');


    if (!currencySelect || !defaultCurrencyDiv || !accountSelect) {
        console.error('One or more elements are not found in the DOM');
        return;
    }

    function updateCurrencyDiv() {
        const selectedAccountId = accountSelect.options[accountSelect.selectedIndex].value;
        const selectedCurrencyId = currencySelect.options[currencySelect.selectedIndex].value;

        let account = null;
        let currencyText = null;

        for (const acc of accounts) {
            if (acc['id'].toString() === selectedAccountId) {
                account = acc;
                if (acc['currency__abbr'].toString() === acc['currency__symbol'].toString()) {
                    currencyText = acc['currency__abbr'];
                } else {
                    currencyText = acc['currency__abbr'].toString() + '\u00A0\u00A0' + acc['currency__symbol'].toString();
                }

                amountAccountCurrencyText.textContent = currencyText;
                break;
            }
        }

        if (!account) {
            console.error('Selected account not found in the accounts list');
            return;
        }

        if (selectedCurrencyId === account['currency_id'].toString()) {
            defaultCurrencyDiv.classList.add('visually-hidden');
            amount_converted_input.setAttribute("required", "false");
        } else {
            defaultCurrencyDiv.classList.remove('visually-hidden');
            amount_converted_input.setAttribute("required", "true");
        }
    }


    currencySelect.addEventListener('change', updateCurrencyDiv);
    accountSelect.addEventListener('change', updateCurrencyDiv);

    // Initial call to set the correct state on page load
    updateCurrencyDiv();
});
