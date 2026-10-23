from .reports.report_console import MutationReportConsole
from .reports.report_data import MutationReportData
from .reports.report_run import MutationReportRun


class MutationReporting(MutationReportRun, MutationReportConsole, MutationReportData):
    """Compose report execution, rendering, and persistence helpers."""
