document.addEventListener('DOMContentLoaded', (event) => {
    const currencySelector = document.getElementById('id_currency');
    const initialBalanceTextSpan = document.querySelector('#id_initial_balance + .input-group-text');
    const targetBalanceTextSpan = document.querySelector('#id_target_balance + .input-group-text');
    const accountTypeSelector = document.getElementById('id_account_type');
    const savingsAccountElements = document.querySelectorAll('.savings-account');

    function updateCurrencyText() {
        const selectedOption = currencySelector.options[currencySelector.selectedIndex];
        const currencyText = selectedOption.textContent.trim();
        initialBalanceTextSpan.textContent = currencyText;
        targetBalanceTextSpan.textContent = currencyText;
    }

    function toggleSavingsAccountFields() {
        const selectedAccountType = accountTypeSelector.value;
        const isSavingsAccount = selectedAccountType === 's'; // Replace 'savings' with the actual value for savings account type
        savingsAccountElements.forEach(element => {
            element.style.display = isSavingsAccount ? 'block' : 'none';
        });
    }

    // Update the currency text on page load
    updateCurrencyText();

    // Toggle savings account fields on page load
    toggleSavingsAccountFields();

    // Add event listeners for changes
    currencySelector.addEventListener('change', updateCurrencyText);
    accountTypeSelector.addEventListener('change', toggleSavingsAccountFields);
});