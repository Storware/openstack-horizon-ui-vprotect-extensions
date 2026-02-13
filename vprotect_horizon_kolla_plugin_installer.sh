#!/bin/bash
# ====================================================================================
# Script Name	: vprotect_horizon_kolla_plugin_installer.sh
# Version	: 0.6
# Author	: Tomasz Lipczyński
# Email		: t.lipczynski@storware.eu
# Created	: 2026-02-04
# Updated	: 2026-02-11
# Description	: vProtect Horizon plugin installation tool. Designed to use inside
# 		  the horizon pod with kolla.
# ====================================================================================
#
IS_STATIC_FILES_UPDATE=1
CERTIFICATE_PATH="/tmp/vprotect/vprotect.crt"
KOLLA_WORKING_DIR=""

NC='\033[0m'
BOLD='\033[1m'

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'

sbr_hostname=''
sbr_user=''
sbr_pass=''
seleted_version=''

static_zip_path=''

NON_INTERACTIVE=false
SHOW_VERSIONS=false
UNINSTALL=false
NO_COLORS=false


welcome() {
	echo -e "${BLUE}"
	echo ""
	echo "          @@@@@@@@@@@@  @@@@                                                                                                                      "
	echo "        @@@@@@@@@@@@  @@@@@@@@@                                                                                                                   "
	echo "      @@@@@@@@@@@@  @@@@@@@@@@@@@               @@@@@@ @@@@@@@@@@@@   @@@@           @@@ @@@@   @@@   @@@@      @@@            @@@@     @@@@      "
	echo "   @@@@@@@@@@@@  @@@@@@@@@@@@@@@@@@           @@@@@@@@ @@@@@@@@@@  @@@@@@@@@@@    @@@@@@ @@@@   @@@   @@@@  @@@@@@@@@@@    @@@@@@@@ @@@@@@@@@@@   "
	echo " @@@@@@@@@@@@  @@@@@@@@@@@@@@@@@@@@@@@       @@@@         @@@@    @@@@     @@@@  @@@@    @@@@   @@@   @@@@ @@@@@    @@@@@ @@@@     @@@@     @@@@  "
	echo "@@@@@@@@@@@  @@@@@@@@@@@@  @@@@@@@@@@@@       @@@@@@@@@@@ @@@@   @@@@      @@@@ @@@@     @@@@   @@@   @@@@ @@@@      @@@@@@@@      @@@@  @@@@@@@@ "
	echo " @@@@@@@@@@@@@@@@@@@@@@  @@@@@@@@@@@@                @@@@ @@@@    @@@@@   @@@@@ @@@@     @@@@  @@@@   @@@@ @@@@@     @@@@@@@@      @@@@@          "
	echo "    @@@@@@@@@@@@@@@@  @@@@@@@@@@@@@            @@@@@@@@@@ @@@@     @@@@@@@@@@   @@@@      @@@@@@@@@@@@@@@    @@@@@@@@@@@@@@@@        @@@@@@@@@    "
	echo "      @@@@@@@@@@@@  @@@@@@@@@@@@                                                                                                                  "
	echo "        @@@@@@@@  @@@@@@@@@@@@                                                                                                                    "
	echo "           @@  @@@@@@@@@@@@@                                                                                                                      "
	echo ""
	echo -e "${CYAN}vProtect Horizon plugin installator v0.5"
	echo -e "${CYAN}Use ${YELLOW}--help${CYAN} for more information."
	echo ""
	echo -e "${NC}"
}

menu() {
	get_and_check_kolla_dir
	echo -e "${CYAN}${BOLD}Menu: "
	echo "  1) Install vProtect plugin."
	echo "  2) Uninstall vProtect plugin."
	echo "  3) Exit."
	echo -e "${NC}"
	read -p "Choose option: " CHOICE

	case $CHOICE in
		1) interactive_install ;;
		2) uninstall ;;
		3) exit 0 ;;
	esac

	echo -e "${NC}"
}

get_and_check_kolla_dir() {
	KOLLA_WORKING_DIR=$(ls -d /var/lib/kolla/venv/lib/python3*/site-packages/openstack_dashboard/ | sort -r | tail -n 1)
	if ! [[ -n "${KOLLA_WORKING_DIR:-}" ]]; then
		echo -e "${RED}${BOLD}Kolla working directory not found! ${YELLOW}/var/lib/kolla/venv/lib/python3*/site-packages/openstack_dashboard/${NC}"
		echo -e "${RED}${BOLD}Is this script running inside the horizon container?${NC}"
		echo
		exit 1;
	fi
}

show_available_versions() {
	echo "Available vProtect versions:"
	VPROTECT_VERSIONS=$(curl https://api.github.com/repos/Storware/ovirt-engine-ui-vprotect-extensions/releases -s | grep "browser_download_url" | grep "openstack" | tr "/" " " | awk '{ print $8 }' | tac | grep -E '^([0-9]+\.){2,3}[0-9]+-[0-9]+$')
	echo -e "${CYAN}"
	for ver in "${VPROTECT_VERSIONS[@]}"; do
		echo -e "${CYAN}$ver${NC}"
	done
}

select_version() {
	show_available_versions

	latest=$(echo "$VPROTECT_VERSIONS" | tail -n 1)

	while true; do
		echo -en "${NC}Select version [default: ${CYAN}${BOLD}${latest}${NC}]"
		read -e -i "$latest" -p ": " selected_version
		if [[ $VPROTECT_VERSIONS =~ $selected_version ]]; then
		      break;
	      	else
			echo -e "${RED}Version ${selected_version} doesn't exist!${NC}"
		fi
	done

}

get_sbr_credentials() {
	echo -e "${CYAN}${BOLD}Type in credentials of SBR and its horizon user account (the one with enabled Horizon plugin access restriction)${NC}"
	read -p "Type your SBR hostname: " sbr_hostname
	read -p "Type your SBR username: " sbr_user
	read -sp "Type your SBR password: " sbr_pass
	echo
}

get_certificate() {
	echo -e "${CYAN}${BOLD}Receiving certificate from ${YELLOW}${sbr_hostname}${CYAN}...${NC}"
	openssl s_client -connect ${sbr_hostname}:443 -showcerts </dev/null \
  | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /tmp/vprotect/vprotect.crt
}

preinstall_check() {
	local invalid_parameters=0
	echo -e "${BOLD}"

	if [[ -n "${static_zip_path:-}" ]]; then
		echo -e "${GREEN}vProtect static files .zip: ${static_zip_path}"
	elif ! [[ -n "${selected_version:-}" ]]; then
		echo -e "${RED}Invalid vProtect version! (${selected_version})"
		invalid_parameters=1
	else
		echo -e "${GREEN}vProtect version: ${selected_version}"
	fi

	if ! [[ -n "${sbr_hostname:-}" ]]; then
		echo -e "${RED}Invalid SBR hostname! (${sbr_hostname})"
		invalid_parameters=1
	else
		echo -e "${GREEN}SBR hostname: ${sbr_hostname}"
	fi

	if ! [[ -n "${sbr_user:-}" ]]; then
		echo -e "${RED}Invalid SBR username! (${sbr_user})"
		invalid_parameters=1
	else
		echo -e "${GREEN}SBR username: ${sbr_user}"
	fi

	if ! [[ -n "${sbr_pass:-}" ]]; then
		echo -e "${RED}Invalid SBR password!"
		invalid_parameters=1
	else
		echo -e "${GREEN}SBR password ok."
	fi

	if ! [[ -s "/tmp/vprotect/vprotect.crt" ]]; then
		echo -e "${RED}Could not get a SBR certificate! Check connection to the ${YELLOW}${sbr_hostname}"
		invalid_parameters=1
	else
		echo -e "${GREEN}SBR certificate ok."
	fi

	echo -e "${NC}"

	return $invalid_parameters
}

interactive_install() {
	clear
	select_version;
	get_sbr_credentials;
	install;
}

install() {
	echo
	get_and_check_kolla_dir
	echo -e "${CYAN}${BOLD}Creating ${YELLOW}/tmp/vprotect${CYAN} directory...${NC}"
	mkdir -p /tmp/vprotect
	if ! [[ -d "/tmp/vprotect" ]]; then
		echo -e "${RED}${BOLD}Could not create /tmp/vprotect directory...${NC}"
		exit 1
	fi
	cd /tmp/vprotect
	get_certificate;

	if ! preinstall_check; then
		echo ""
		echo -e "${RED}${BOLD}Invalid fields. Installation cancelled.${NC}"
		exit 1
	fi

	echo -e "${CYAN}${BOLD}Installing vProtect plugin..."
	echo ""
	echo -e "${NC}"

	if (( IS_STATIC_FILES_UPDATE )); then
		git clone https://github.com/Storware/openstack-horizon-ui-vprotect-extensions.git -b caracal
	else
		git clone https://github.com/Storware/openstack-horizon-ui-vprotect-extensions.git
	fi

	if ! [[ -d "/tmp/vprotect/openstack-horizon-ui-vprotect-extensions" ]]; then
		echo -e "${RED}${BOLD}Could not clone git repository: https://github.com/Storware/openstack-horizon-ui-vprotect-extensions.git  ...${NC}"
		exit 1
	fi

	if ! [[ -n "${static_zip_path}" ]]; then
		vprotect_static_files_url=https://github.com/Storware/ovirt-engine-ui-vprotect-extensions/releases/download/${selected_version}/openstack.zip
		curl -O ${vprotect_static_files_url}
	else
		if ! [[ -f "${static_zip_path}" ]]; then
			echo -e "${RED}${BOLD}Static files .zip file not found! (${static_zip_path})...${NC}"
			exit 1
		fi
		cp ${static_zip_path} /tmp/vprotect/openstack.zip
	fi

	if ! [[ -f "/tmp/vprotect/openstack.zip" ]]; then
		echo -e "${RED}${BOLD}Could not download vProtect plugin static files (${vprotect_static_files_url})...${NC}"
		exit 1
	fi

	python3 -m zipfile -e openstack.zip vprotect
	if ! [[ -d "/tmp/vprotect/vprotect" ]]; then
		echo -e "${RED}${BOLD}Could not unpack vProtect plugin .zip static files...${NC}"
		exit 1
	fi

	echo -e "PASSWORD: ${sbr_pass}\nREST_API_URL: https://${sbr_hostname}/api\nUSER: ${sbr_user}" > /tmp/vprotect/openstack-horizon-ui-vprotect-extensions/dashboards/vprotect/config.yaml

	if (( IS_STATIC_FILES_UPDATE )); then
		sed -i 's/dashboard\/static/static/g' $(grep -irl "dashboard/static" /tmp/vprotect/openstack-horizon-ui-vprotect-extensions | grep html)
		cd /tmp/vprotect/vprotect
		sed -i "s/dashboard\/static\/vprotect/static\/vprotect/g" index.*
		sed -i "s/dashboard\/vprotect/vprotect/g" index.*
		echo -e "${CYAN}${BOLD}Static files updated for Caracal.${NC}"
	fi

	if ! [[ -d "$KOLLA_WORKING_DIR" ]]; then
		echo -e "${RED}${BOLD}Kolla horizon directory not found. Check the following path - ${YELLOW}/var/lib/kolla/venv/lib/python3*/site-packages/openstack_dashboard/${NC}"
		exit 1
	fi

	cd $KOLLA_WORKING_DIR
	cp /tmp/vprotect/openstack-horizon-ui-vprotect-extensions/enabled/_50_vprotect.py ./enabled/
	cp -r /tmp/vprotect/openstack-horizon-ui-vprotect-extensions/dashboards/vprotect ./dashboards/
	cp -r /tmp/vprotect/vprotect ../static/
	mkdir -p /usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect
	ln -s /tmp/vprotect/openstack-horizon-ui-vprotect-extensions/dashboards/vprotect/config.yaml /usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect/config.yaml

	cat /tmp/vprotect/vprotect.crt >> ../certifi/cacert.pem

	echo -e "${GREEN}${BOLD}Installation completed."
	sleep 1

	echo
	echo -en "${CYAN}Restarting apache2 in 3 seconds${NC}"

	for i in {3..1}; do
		echo -n "."
		sleep 1
	done

	/etc/init.d/apache2 restart

}

disable_colors() {
	NC=''
	BOLD=''
	RED=''
	GREEN=''
	YELLOW=''
	BLUE=''
	CYAN=''
}

uninstall() {
	echo -e "${CYAN}${BOLD}Uninstalling vProtect plugin from horizon...${NC}"
	echo
	get_and_check_kolla_dir
	cd $KOLLA_WORKING_DIR
	rm -rf ../static/vprotect
	echo -e "${CYAN}${BOLD}Removed vProtect static files.${NC}"
	rm -rf ./dashboards/vprotect
	rm ./enabled/_50_vprotect.py
	echo -e "${CYAN}${BOLD}Removed vProtect plugin.${NC}"
	rm /usr/share/openstack-dashboard/openstack_dashboard/dashboards/vprotect/config.yaml
	rm -rf /tmp/vprotect
	echo
	echo -e "${GREEN}${BOLD}vProtect plugin uninstalled successfully.${NV}"

	echo
	echo -en "${CYAN}Restarting apache2 in 3 seconds${NC}"

	for i in {3..1}; do
		echo -n "."
		sleep 1
	done

	/etc/init.d/apache2 restart

}

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Installs vProtect Horizon plugin.
Run script from inside the Horizon pod.

Options:
	--no-colors					Disables text colors

	--show-versions				Downloads available vProtect plugin versions

	--uninstall					Uninstalls vProtect horizon plugin

	--non-interactive			Installs the plugin without further interaction with a script - requires the four arguments below:
	--sbr-hostname=<host>		IP or hostname of SBR server
	--sbr-user=<username>		Username for the SBR account with horizon restrictions
	--sbr-pass=<password>		Password for the SBR account with horizon restrictions
	--vprotect-version=<ver>	vProtect plugin version to install

	--static-zip-path=<path>	Path to the static files archive (openstack.zip). Avoids downloading static files. Can be used instead of --vprotect-version
								Static files can be downloaded from: https://github.com/Storware/ovirt-engine-ui-vprotect-extensions/releases/

	-h, --help               	Show this help and exit

Examples:
  $(basename "$0")
  $(basename "$0") --show-versions
  $(basename "$0") --uninstall
  $(basename "$0") --non-interactive --sbr-hostname=10.40.14.51 --sbr-user=horizon --sbr-pass=vPr0tect --vprotect-version=7.0.0-3
  $(basename "$0") --non-interactive --sbr-hostname=10.40.14.51 --sbr-user=horizon --sbr-pass=vPr0tect --static-zip-path=/root/openstack.zip
EOF
}


ARGS=$(getopt -o h -l sbr-hostname:,sbr-user:,sbr-pass:,vprotect-version:,static-zip-path:,non-interactive,no-colors,show-versions,uninstall,help -- "$@") || exit 1
eval set -- "$ARGS"

SHOW_VERSIONS=false

while true; do
    case "$1" in
		--no-colors) NO_COLORS=true; shift ;;
        --sbr-hostname) sbr_hostname="$2"; shift 2 ;;
        --sbr-user) sbr_user="$2"; shift 2 ;;
        --sbr-pass) sbr_pass="$2"; shift 2 ;;
        --vprotect-version) selected_version="$2"; shift 2 ;;
        --static-zip-path) static_zip_path="$2"; shift 2 ;;
        --non-interactive) NON_INTERACTIVE=true; shift ;;
        --show-versions) SHOW_VERSIONS=true; shift ;;
        --uninstall) UNINSTALL=true; shift ;;
        -h|--help)
			usage
			exit 0
			;;
        --) shift; break ;;
        *)
			echo "Unknown option: $1" >&2
			usage
			exit 1
			;;
    esac
done

main() {
	if $NO_COLORS; then
		disable_colors
	fi


	if $SHOW_VERSIONS; then
		show_available_versions
	elif $UNINSTALL; then
		uninstall
	elif $NON_INTERACTIVE; then
		welcome
		install
	else
		welcome
		menu
	fi
}

main "$@"
