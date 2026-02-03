from __future__ import annotations

from django import forms
from django.utils import timezone

from .models import Project, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Project name...",
                    "maxlength": "120",
                    "required": True,
                    "autofocus": "autofocus",
                }
            )
        }
    
    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.owner = owner

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Project name is required.")
        if self.owner and Project.objects.filter(owner=self.owner, name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("You already have a project with this name.")
        return name


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "deadline", "is_done"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control app-task-input",
                    "placeholder": "Start typing here to create a task...",
                    "maxlength": "255",
                    "required": True,
                    "autocomplete": "off",
                }
            ),
            "deadline": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "is_done": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_name(self) -> str:
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("Task name is required.")
        return name

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if not deadline:
            return deadline

        today = timezone.localdate()
        if deadline < today:
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline
