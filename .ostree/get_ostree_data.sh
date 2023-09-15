#!/bin/bash

set -euo pipefail

role_collection_dir="${ROLE_COLLECTION_DIR:-fedora/linux_system_roles}"
ostree_dir="${OSTREE_DIR:-$(dirname "$0")}"
category="$1"
pkgtype="$2"
distro_ver="$3"
format="$4"
pkgtypes=("$pkgtype")
if [ "$pkgtype" = testing ]; then
    pkgtypes+=(runtime)
fi

get_rolepath() {
    local ostree_dir role rolesdir
    ostree_dir="$1"
    role="$2"
    rolesdir="$(dirname "$(dirname "$ostree_dir")")/$role/.ostree"
    if [ -d "$rolesdir" ]; then
        echo "$rolesdir"
        return 0
    fi
    if [ -n "${ANSIBLE_COLLECTIONS_PATHS:-}" ]; then
        for pth in ${ANSIBLE_COLLECTIONS_PATHS//:/ }; do
            rolesdir="$pth/ansible_collections/$role_collection_dir/roles/$role/.ostree"
            if [ -d "$rolesdir" ]; then
                echo "$rolesdir"
                return 0
            fi
        done
    fi
    return 1
}

get_packages() {
    local ostree_dir pkgtype pkgfile role rolefile rolepath
    ostree_dir="$1"
    for pkgtype in "${pkgtypes[@]}"; do
        for suff in "" "-$distro" "-${distro}-${major_ver}" "-${distro}-${ver}"; do
            pkgfile="$ostree_dir/packages-${pkgtype}${suff}.txt"
            if [ -f "$pkgfile" ]; then
                cat "$pkgfile"
            fi
        done
        rolefile="$ostree_dir/roles-${pkgtype}.txt"
        if [ -f "$rolefile" ]; then
            local roles
            roles="$(cat "$rolefile")"
            for role in $roles; do
                rolepath="$(get_rolepath "$ostree_dir" "$role")"
                get_packages "$rolepath"
            done
        fi
    done | sort
}

format_packages_json() {
    local comma pkgs pkg
    comma=""
    pkgs="["
    while read -r pkg; do
        pkgs="${pkgs}${comma}\"${pkg}\""
        comma=,
    done
    pkgs="${pkgs}]"
    echo "$pkgs"
}

distro="${distro_ver%%-*}"
ver="${distro_ver##*-}"
if [[ "$ver" =~ ^([0-9]*) ]]; then
    major_ver="${BASH_REMATCH[1]}"
else
    echo ERROR: cannot parse major version number from version "$ver"
    exit 1
fi

"get_$category" "$ostree_dir" | "format_${category}_$format"
