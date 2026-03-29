from core.forms import BaseStyledModelForm

from .models import ReminderRule


class ReminderRuleForm(BaseStyledModelForm):
    class Meta:
        model = ReminderRule
        fields = ("name", "days_before", "is_active")
