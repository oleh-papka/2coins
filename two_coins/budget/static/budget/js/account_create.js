document.getElementById('acct_typeSelect').addEventListener('change', function (e) {
    var selectedValue = e.target.value;

    var initial_balance_usd = document.getElementById('initial_balance_usd');

    if (selectedValue === 's') {
        initial_balance_usd.disabled = false;
    } else {
        initial_balance_usd.disabled = true;
    }
});