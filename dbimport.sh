#!/bin/sh
set -e
TABLE="boards"

fail() {
	echo "$@" >&2
	exit 1
}

board_type=
board_revision=
input=
while [ $# -gt 0 ]; do
	case "$1" in
		-h|--help)
			echo "Usage: dbimport.sh [OPTION].. INPUT -- [PSQL].."
			echo
			echo "Options:"
			echo "  -t, --type TYPE"
			echo "    Specify board type. There is special meaning for board A."
			echo "    Any other value is regarded as to be expansion board."
			echo "  -r, --revision REV"
			echo "    Revision number of these boards. It is hardware revision"
			echo "    number from board it self."
			echo "  -h, --help"
			echo "    Print this help text and exit."
			echo "Any argument passed after -- is passed to psql command."
			echo "This way you can configure connecton to database."
			exit 0
			;;
		-t|--type)
			shift
			board_type="$1"
			;;
		-r|--revision)
			shift
			board_revision="$1"
			;;
		--)
			shift
			break
			;;
		*)
			if [ -z "$input" ]; then
				input="$1"
			elif [ -z "$output" ]; then
				output="$1"
			else
				fail "Unknown option: $1"
			fi
			;;
	esac
	shift
done

[ -n "$input" ] || fail "No INPUT specified"
[ -n "$board_type" ] || fail "Missing required option --type"
[ -n "$board_revision" ] || fail "Missing required option --revision"

if [ "$board_type" = "A" ]; then
	awk -F ',' -v tp="$board_type" -v rev="$board_revision" \
		'/^\S+$/ { print $2","$3","$4","rev","tp }' \
		"$input" | \
		psql "$@" -c "COPY $TABLE (serial, mac_wan, mac_sgmii, revision, type)  FROM STDIN WITH (FORMAT csv)"
else
	awk -F ',' -v tp="$board_type" -v rev="$board_revision" \
		'{ print $2","rev","tp }' \
		"$input" | \
		psql -d "$DATABASE" "$@" -c "COPY $TABLE (serial, revision, type)  FROM STDIN WITH (FORMAT csv)"
fi
