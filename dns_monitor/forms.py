from core.forms import BaseStyledModelForm

from .models import DNSMonitorTarget


class DNSMonitorTargetForm(BaseStyledModelForm):
    class Meta:
        model = DNSMonitorTarget
        fields = ("order", "domain", "record_type", "expected_value", "is_active")
