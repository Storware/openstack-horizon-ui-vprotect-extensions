from django.utils.translation import ugettext_lazy as _

import horizon

class VirtualEnvironmentsGroup(horizon.PanelGroup):
    slug = "virtualEnvironmentsGroup"
    name = _("Virtual Environments")
    panels = ('virtual_environments', 'policies_and_schedules', 'mounted_backups')

class DashboardGroup(horizon.PanelGroup):
    slug = "dashboardGroup"
    name = _("Overview")
    panels = ('dashboard2', 'reporting',)

class TaskConsoleGroup(horizon.PanelGroup):
    slug = "taskConsoleGroup"
    name = _("Task Console")
    panels = ('task_console',)

class BackupAndRecovery(horizon.Dashboard):
    name = _("Backup & Recovery")
    slug = "vprotect"
    panels = (DashboardGroup, VirtualEnvironmentsGroup, TaskConsoleGroup,)
    default_panel = "dashboard2"

horizon.register(BackupAndRecovery)
