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
    panels = ('task_console','workflow_execution')

class SettingsGroup(horizon.PanelGroup):
    slug = "settingsGroup"
    name = _("Settings")
    panels = ('mailing',)


class VProtect(horizon.Dashboard):
    name = _("Backup & Recovery")
    slug = "vprotect"
    panels = (DashboardGroup, VirtualEnvironmentsGroup, TaskConsoleGroup, SettingsGroup,)
    default_panel = "dashboard2"

class Dashboard2(horizon.Panel):
    name = _("Dashboard")
    slug = "dashboard2"

class Mailing(horizon.Panel):
    name = _("Mailing")
    slug = "mailing"

class MountedBackups(horizon.Panel):
    name = _("Mounted Backups")
    slug = "mounted_backups"

class PoliciesAndSchedules(horizon.Panel):
    name = _("Backup SLAs")
    slug = "policies_and_schedules"

class MountedBackups(horizon.Panel):
    name = _("Reporting")
    slug = "reporting"

class TaskConsole(horizon.Panel):
    name = _("Task Console")
    slug = "task_console"

class VirtualEnvironments(horizon.Panel):
    name = _("Instances")
    slug = "virtual_environments"

class WorkflowExecution(horizon.Panel):
    name = _("Workflow Execution")
    slug = "workflow_execution"

horizon.register(VProtect)
