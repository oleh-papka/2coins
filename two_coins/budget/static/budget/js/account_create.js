document.addEventListener('DOMContentLoaded', (event) => {
    const currencySelector = document.getElementById('id_currency');
    const initialBalanceTextSpan = document.querySelector('#id_initial_balance + .input-group-text');
    const targetBalanceTextSpan = document.querySelector('#id_target_balance + .input-group-text');

    function updateCurrencyText() {
        const selectedOption = currencySelector.options[currencySelector.selectedIndex];
        const currencyText = selectedOption.textContent.trim();
        initialBalanceTextSpan.textContent = currencyText;
        targetBalanceTextSpan.textContent = currencyText;
    }

    // Update the currency text on page load
    updateCurrencyText();


    // Add event listeners for changes
    currencySelector.addEventListener('change', updateCurrencyText);
});