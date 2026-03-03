#!/usr/bin/env /opt/kompot/bin/setup-kompot

set -f

function etc_cron_kompot() {
    grep -qF naghistory- /etc/cron.d/kompot && return 0
    info 'Add naghistory tasks to /etc/cron.d/kompot'
    explain sh -c "printf '\n' >> /etc/cron.d/kompot"
    explain sh -c "printf '10 3 * * * root naghistory-mark-deleted\n' >> /etc/cron.d/kompot"
    explain sh -c "printf '15 3 * * * root naghistory-cache-availability\n' >> /etc/cron.d/kompot"
}

function rebuild_menu() {
    info 'Rebuild menu'
    explain sh -c 'update-menus build && update-menus apply'
}

function start_nagios_history() {
    info 'Starting new nagios-history service'
    explain zservice restart nagios-history
}

# continue on error
start_nagios_history
etc_cron_kompot
rebuild_menu

exit 0
