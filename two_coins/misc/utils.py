import operator
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union, List

from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import TruncDate

from budget.models import Transaction, Transfer
from budget.templatetags.number_filters import strip_trailing_zeros


def get_current_month_dates():
    """
    Returns the start and end dates for the current month.

    Returns:
        Tuple[datetime, datetime]: A tuple containing the first and last datetime objects of the current month.
    """
    today = datetime.today()
    # First day of the current month
    first_day = today.replace(day=1)
    first_day = datetime.combine(first_day, datetime.min.time())

    # First day of the next month, then subtract one day to get the last day of the current month
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    last_day = datetime.combine(last_day, datetime.max.time())  # Include the full last day

    return first_day, last_day


def get_date_range(start_date: Optional[datetime | str] = None, end_date: Optional[datetime | str] = None) -> Tuple[
    datetime, datetime]:
    """
    Returns a tuple of start and end dates based on input strings.
    If both dates are None, it defaults to the current month's range.

    Args:
        start_date (Optional[str]): The start date in 'YYYY-MM-DD' format, or None.
        end_date (Optional[str]): The end date in 'YYYY-MM-DD' format, or None.

    Returns:
        Tuple[datetime, datetime]: A tuple containing the start and end datetime objects.
    """
    if start_date and end_date:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        end_date_parsed = datetime.combine(end_date, datetime.max.time())
        return start_date, end_date_parsed
    else:
        return get_current_month_dates()


def get_combined_actions(
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        all_transfers: bool = False,
) -> Optional[List[Union[Transaction, Transfer]]]:
    """
        Retrieves combined actions (transactions and transfers) within a specified date range,
        optionally filtered by account and/or category.

        Args:
            user_id (int): The user ID to filter by.
            start_date (Optional[datetime]): The start date in 'YYYY-MM-DD' format.
            end_date (Optional[datetime]): The end date in 'YYYY-MM-DD' format.
            account_id (Optional[int]): The account ID to filter by.
            category_id (Optional[int]): The category ID to filter by.
            all_transfers (bool): Whether to include all transfers in the results (default is False).

        Returns:
            Optional[List[Union[Transaction, Transfer]]]: A sorted list of transactions and transfers,
                                                          or None if no actions are found.
        """
    if not start_date or not end_date:
        start_date, end_date = get_current_month_dates()

    transaction_filters = {
        "date__range": (start_date, end_date),
    }
    if account_id:
        transaction_filters["account_id"] = account_id
    if category_id:
        transaction_filters["category_id"] = category_id
    if user_id:
        transaction_filters["account__profile__user_id"] = user_id

    transactions_queryset = Transaction.objects.filter(**transaction_filters).order_by(
        '-date'
    ).annotate(truncated_date=TruncDate('date'))

    if all_transfers:
        transfer_filters = Q(account_to__profile__user_id=user_id) | Q(account_from__profile__user_id=user_id)
    elif account_id:
        transfer_filters = Q(account_to=account_id) | Q(account_from=account_id)
    else:
        transfer_filters = None

    if transfer_filters:
        transfers_queryset = Transfer.objects.filter(
            transfer_filters,
            date__range=(start_date, end_date)
        ).order_by('-date').annotate(truncated_date=TruncDate('date'))
    else:
        transfers_queryset = Transfer.objects.none()

    transactions_list = list(transactions_queryset)
    transfers_list = list(transfers_queryset)

    combined_list = transactions_list + transfers_list

    combined_list.sort(key=operator.attrgetter('date'), reverse=True)

    if not combined_list:
        return None

    for action in combined_list:
        action.action_type = 'txn' if isinstance(action, Transaction) else 'trf'

    return combined_list


def add_transfer_messages(request, account_from, account_to):
    """
    Adds success and info messages for a transfer operation.

    Args:
        request: The HTTP request object.
        account_from: The account object the transfer is debited from.
        account_to: The account object the transfer is credited to.
    """
    messages.success(request, f"Transfer {account_from.name}->{account_to.name} done!")

    for account in (account_from, account_to):
        messages.info(
            request,
            f"Updated balance of {account.name} account!\n"
            f"Your balance is {strip_trailing_zeros(account.balance)} {account.currency.symbol}"
        )
