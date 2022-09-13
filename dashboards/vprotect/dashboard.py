import horizon

class VirtualEnvironmentsGroup(horizon.PanelGroup):
    slug = "virtualEnvironmentsGroup"
    name = "Virtual Environments"
    panels = ('virtual_environments', 'policies_and_schedules', 'mounted_backups')

class DashboardGroup(horizon.PanelGroup):
    slug = "dashboardGroup"
    name = "Overview"
    panels = ('dashboard2', 'reporting',)

class TaskConsoleGroup(horizon.PanelGroup):
    slug = "taskConsoleGroup"
    name = "Task Console"
    panels = ('task_console','workflow_execution')

class SettingsGroup(horizon.PanelGroup):
    slug = "settingsGroup"
    name = "Settings"
    panels = ('settings',)


class VProtect(horizon.Dashboard):
    name = "Backup & Recovery"
    slug = "vprotect"
    panels = (DashboardGroup, VirtualEnvironmentsGroup, TaskConsoleGroup, SettingsGroup,)
    default_panel = "dashboard2"




horizon.register(VProtect)
