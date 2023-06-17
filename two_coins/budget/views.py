from django.http import HttpResponse

from django.shortcuts import render


# Accounts
def accounts(request):
    return HttpResponse("Accounts")


def account(request, pk):
    return HttpResponse(f"Account {pk}")


def account_add(request):
    return HttpResponse("Form for creating your account")


def account_edit(request, pk):
    return HttpResponse(f"Form for editing your account {pk}")


def account_delete(request, pk):
    return HttpResponse(f"Form for deleting your account {pk}")
