from django.contrib import messages
from django.db import models
from django.forms import BaseModelForm
from django.views.generic import UpdateView


class TimeStampMixin(models.Model):
    """
    Mixin for ease adding created_at and updated_at to models.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StyleFormUpdateMixin(UpdateView):
    model_verbose_name = ''

    def form_valid(self, form: BaseModelForm):
        instance = form.save(commit=False)

        color_updated = form.cleaned_data.get('color')
        icon_updated = form.cleaned_data.get('icon')
        instance.style.update_style(color=color_updated, icon=icon_updated)

        instance.save()

        instance_name = form.cleaned_data.get('name')
        messages.success(self.request, f"{instance._meta.verbose_name.title()} '{instance_name}' updated!")

        return super().form_valid(form)


class FormInvalidMixin:
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f"{form[field].label}: {error}")

        return super().form_invalid(form)
