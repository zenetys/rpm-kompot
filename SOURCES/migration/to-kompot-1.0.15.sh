#!/usr/bin/env /opt/kompot/bin/setup-kompot

set -f

function norm_menu_item() {
    jq '
if (.type == "div" or .type == "frame" or .type == "rrdmenu") then del(.type)
else . end |
if (.url) then .to = .url |del(.url)
else . end |
((.to|capture("^/drawio/drawio-app.*#U(?<schema>.*)")) // {}) as $cap |
if ($cap.schema) then del(.to) |.schema = $cap.schema |.type = "drawio"
else . end
    '
}

function etc_kompot_diagrams_perms() {
    info 'Set apache perms to /etc/kompot/diagrams'
    explain chown apache /etc/kompot/diagrams
    explain find -L /etc/kompot/diagrams/ -mindepth 1 -maxdepth 1 -type f \
        -name '*.xml' -exec chown apache: {} \;
}

function etc_kompot_menus_normalize() {
    local files=($(find -L /etc/kompot/menus/ -mindepth 1 -maxdepth 1 -type f \
        \( -name '*.json' -o -name '*.json.disabled' \)))
    for i in "${files[@]}"; do
        info "Update menu file $i"
        norm_menu_item < "$i" > "$i.tmp" || continue
        cat "$i.tmp" > "$i" || continue
        rm "$i.tmp"
    done
    info 'Rebuild menu'
    explain sh -c 'update-menus build && update-menus apply'
}

# continue on error
etc_kompot_diagrams_perms
etc_kompot_menus_normalize

exit 0
