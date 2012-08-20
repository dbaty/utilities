#!/bin/bash

#
# Request AWStats to process all logs of a directory
#
# Syntax:
#     awstats_process_all_logs <conf> <log_dir>
#
# Example:
#   awstats_process_all_logs.sh site.com /var/log/www/site.com
#
#   (supposing "/etc/awstats/awstats.site.com.conf" exists)
#

# Adapt the following to your system (this is for Debian).
AWSTATS="/usr/lib/cgi-bin/awstats.pl"
LOG_MERGER="/usr/share/awstats/tools/logresolvemerge.pl"


conf=$1
log_dir=$2
tmp="/tmp/awstats-merge-$conf.txt"

$LOG_MERGER $log_dir/access.* > $tmp
$AWSTATS -config="$conf" -LogFile="$tmp" -update
rm $tmp