#!/usr/bin/env /opt/kompot/bin/setup-kompot

set -f

function rsyslog_to_opt() {
    info 'Rsyslog config has moved to /opt/kompot/lib/rsyslog'
    [[ -d /etc/rsyslog.d ]] || return 0
    local files=( $(find /etc/rsyslog.d/ -mindepth 1 -maxdepth 1 \
        -regextype egrep \
        -regex '.*(listen-dev-log|listen-udp|listen-relp|check-pattern|archives).*\.conf(\.disabled)?' \
        -not -name 50-kompot.conf -printf '%P\n') )
    [[ -n $files ]] || return 0
    local backup=/etc/rsyslog.d/kbak-$(date +%Y%m%d-%H%M%S).tar.gz
    info "Backup files to be removed in $backup, check yourself then remove"
    if ! explain tar czf "$backup" -C /etc/rsyslog.d/ "${files[@]}"; then
        error 'Backup failed! Cleanup /etc/rsyslog.d manually!'
        return 1
    fi
    explain rm -f "${files[@]/#//etc/rsyslog.d/}"
    local files_remaining=$(find /etc/rsyslog.d/ -name '*.conf' -not -name 50-kompot.conf |wc -l)
    if (( files_remaining > 0 )); then
        local s= them=it; (( files_remaining > 1 )) && { s=s; them=them; }
        warning "You have $files_remaining file$s other than 50-kompot.conf in /etc/rsyslog.d."
        warning "You should consider moving $them to /etc/kompot/rsyslog/conf.d if related to kompot."
    fi
}

# normally docker only
function etc_kompot_rsyslog() {
    info 'Handle reorg in /etc/kompot/rsyslog'
    [[ -d /etc/kompot/rsyslog ]] || return 0
    local files=( $(find /etc/kompot/rsyslog/ -mindepth 1 -maxdepth 1 \
        \( -name 'rsyslog.conf' -o -name 'rsyslog.d' \)  -printf '%P\n') )
    [[ -n $files ]] || return 0
    local backup=/etc/kompot/rsyslog/kbak-$(date +%Y%m%d-%H%M%S).tar.gz
    info "Backup files to be (re)moved in $backup, check yourself then remove"
    if ! explain tar czf "$backup" -C /etc/kompot/rsyslog/ "${files[@]}"; then
        error 'Backup failed! Cleanup /etc/kompot/rsyslog manually!'
        return 1
    fi
    local files_to_move_to_conf_d=( $(find /etc/kompot/rsyslog/rsyslog.d/ -mindepth 1 -maxdepth 1 \
        -regextype egrep -not -regex '.*(listen-dev-log|listen-udp|listen-relp|check-pattern|archives).*\.conf(\.disabled)?' \
        -not -name 50-kompot.conf) )
    if [[ -n $files_to_move_to_conf_d ]]; then
        if ! { [[ -d /etc/kompot/rsyslog/conf.d ]] || explain mkdir -p /etc/kompot/rsyslog/conf.d; } ||
           ! explain mv "${files_to_move_to_conf_d[@]}" /etc/kompot/rsyslog/conf.d/; then
            error "Move failed, do it manually from the backup tarball!"
        fi
    fi
    explain rm -rf "${files[@]/#//etc/kompot/rsyslog/}"
}

# normally docker only
function etc_kompot_logrotate() {
    info 'Handle reorg in /etc/kompot/logrotate'
    [[ -d /etc/kompot/logrotate ]] || return 0
    local files=( $(find /etc/kompot/logrotate/ -mindepth 1 -maxdepth 1 \
        \( -name 'logrotate.conf' -o -name 'logrotate.d' \)  -printf '%P\n') )
    [[ -n $files ]] || return 0
    local backup=/etc/kompot/logrotate/kbak-$(date +%Y%m%d-%H%M%S).tar.gz
    info "Backup files to be (re)moved in $backup, check yourself then remove"
    if ! explain tar czf "$backup" -C /etc/kompot/logrotate/ "${files[@]}"; then
        error 'Backup failed! Cleanup /etc/kompot/logrotate manually!'
        return 1
    fi
    local files_to_move_to_conf_d=( $(find /etc/kompot/logrotate/logrotate.d/ -mindepth 1 -maxdepth 1 \
        -regextype egrep -not -regex '.*/(btmp|dnf|httpd|influxdb|logmatch|nagios|rsyslog-network|syslog|wtmp)$' \
        -not -name 00-kompot.conf) )
    if [[ -n $files_to_move_to_conf_d ]]; then
        if ! { [[ -d /etc/kompot/logrotate/conf.d ]] || explain mkdir -p /etc/kompot/logrotate/conf.d; } ||
           ! explain mv "${files_to_move_to_conf_d[@]}" /etc/kompot/logrotate/conf.d/; then
            error "Move failed, do it manually from the backup tarball!"
        fi
    fi
    explain rm -rf "${files[@]/#//etc/kompot/logrotate/}"
}

function unused_sample_inventory() {
    info 'Remove disabled sample nagzen inventory files'
    [[ -d /etc/kompot/nagzen ]] || return 0
    local files=( $(find /etc/kompot/nagzen/ -mindepth 1 -maxdepth 1 \
        \( -name '100_inventory.cfg.disabled' -o -name 'inventory.xls.disabled' \) -printf '%P\n') )
    [[ -n $files ]] || return 0
    local backup=/etc/kompot/nagzen/kbak-$(date +%Y%m%d-%H%M%S).tar.gz
    info "Backup files to be removed in $backup, check yourself then remove"
    if ! explain tar czf "$backup" -C /etc/kompot/nagzen/ "${files[@]}"; then
        error 'Backup failed! Cleanup /etc/kompot/nagzen manually!'
        return 1
    fi
    explain rm -f "${files[@]/#//etc/kompot/nagzen/}"
}

function need_credential_name() {
    local wanted=$1 inc=
    REPLY=$wanted
    while [[ -e /etc/kompot/nagios/credentials/$REPLY.cfg ]]; do
        [[ -z $inc ]] && inc=2 || (( inc++ ))
        REPLY="$wanted-$inc"
    done
}

function move_credentials() {
    info 'Nagios credentials have moved to /etc/kompot/nagios/credentials'
    [[ -d /etc/kompot/nagios/objects ]] || return 0
    local files=( $(find /etc/kompot/nagios/objects/ -mindepth 1 -maxdepth 1 -name 'credentials[.-]?*.cfg') )
    [[ -n $files ]] || return 0
    local i
    for i in "${files[@]}"; do
        name=${i##*/credentials[.-]}
        name=${name%.cfg}
        need_credential_name "$name"
        if ! explain mv "$i" "/etc/kompot/nagios/credentials/$REPLY.cfg"; then
            error "Move failed! Move $i manually to /etc/kompot/nagios/credentials and remove the credential[.-] prefix from the filename!"
        fi
    done
}

function update_resources() {
    info 'Add $USER98$=; and cleanup Nagios resource.cfg'
    grep -vE '\$USER98\$=' /etc/nagios/resource.cfg |
        sed -re 's/^\s*#\s*Symbol.*/# Special characters/' -e '/\$USER99\$/i$USER98$=\;' |
        cat -s > /etc/nagios/resource.cfg.tmp &&
            cat /etc/nagios/resource.cfg.tmp > /etc/nagios/resource.cfg
    rm -f /etc/nagios/resource.cfg.tmp
    grep -qE '\$USER98\$=' /etc/nagios/resource.cfg || echo '$USER98$=;' >> /etc/nagios/resource.cfg
}

function enable_livestatus() {
    local config=/var/lib/kompot/configs/menus/current/config.json
    info "Set apiType livestatus in $config"
    if [[ -f $config ]]; then
        cp -a "$config"{,.bak} &&
        jq '. + { apiType: "livestatus" }' < "$config.bak" > "$config" &&
        return 0
    fi
    error 'Could not update config.json, check and do it manually!'
    return 1
}

function conf_apache() {
    info 'Remove obsolete /etc/httpd/conf.d/kompot.conf'
    explain rm -f /etc/httpd/conf.d/kompot.conf
}

function rebuild_logmatch() {
    info 'Rebuild logmatch configuration'
    explain sh -c 'update-passive build /etc/kompot/logmatch/* && APPLY_NO_RESTART=1 update-passive apply'
    # servies are (cond)restarted at the end of %posttrans
}

# continue on error
rsyslog_to_opt
etc_kompot_rsyslog
etc_kompot_logrotate
unused_sample_inventory
move_credentials
update_resources
enable_livestatus
conf_apache
rebuild_logmatch

exit 0
