document.addEventListener('DOMContentLoaded', function () {
    const currencySelect = document.getElementById('id_currency');
    const accountSelect = document.getElementById('id_account');
    const categorySelect = document.getElementById('id_category');
    const defaultCurrencyDiv = document.getElementById('amount_converted_field');
    const amountAccountCurrencyText = document.getElementById('amount_converted_text');
    const amount_converted_input = document.getElementById('amount_converted');
    const amountTransactionType = document.querySelector('.amount_transaction_type');

    if (!currencySelect || !defaultCurrencyDiv || !accountSelect || !categorySelect || !amountTransactionType) {
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
            amount_converted_input['required'] = false;
        } else {
            defaultCurrencyDiv.classList.remove('visually-hidden');
            amount_converted_input['required'] = true;
        }
    }


    function updateTransactionTypeSymbol() {
        const selectedCategoryId = categorySelect.options[categorySelect.selectedIndex].value;

        const category = categories.find(cat => cat.id.toString() === selectedCategoryId);
        if (category) {
            // Get all elements with the class `.amount_transaction_type`
            const transactionTypeElements = document.querySelectorAll('.amount_transaction_type');

            // Update each of them
            transactionTypeElements.forEach(element => {
                element.textContent = category.category_type === '+' ? '+' : '-';
            });
        } else {
            console.error('Selected category not found in the categories list');
        }
    }

    currencySelect.addEventListener('change', updateCurrencyDiv);
    accountSelect.addEventListener('change', updateCurrencyDiv);
    categorySelect.addEventListener('change', updateTransactionTypeSymbol);

    // Initial call to set the correct state on page load
    updateCurrencyDiv();
    updateTransactionTypeSymbol();
});
