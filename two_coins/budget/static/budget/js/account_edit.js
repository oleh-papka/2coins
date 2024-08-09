document.addEventListener('DOMContentLoaded', (event) => {
    const accountTypeSelector = document.getElementById('id_account_type');
    const savingsAccountElements = document.querySelectorAll('.savings-account');

    function toggleSavingsAccountFields() {
        const selectedAccountType = accountTypeSelector.value;
        const isSavingsAccount = selectedAccountType === 's'; // Replace 'savings' with the actual value for savings account type
        savingsAccountElements.forEach(element => {
            element.style.display = isSavingsAccount ? 'block' : 'none';
        });

        const allow_negative_input = document.getElementById('id_allow_negative_balance');
        if (isSavingsAccount) {
            allow_negative_input['checked'] = false;
            allow_negative_input['disabled'] = true;
        } else {
            allow_negative_input['disabled'] = false;
        }
    }


    // Toggle savings account fields on page load
    toggleSavingsAccountFields();

    // Add event listeners for changes
    accountTypeSelector.addEventListener('change', toggleSavingsAccountFields);
});