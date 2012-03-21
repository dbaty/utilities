#!/bin/bash

#
# A wrapper around Duplicity to backup files, restore them, etc. Run
# without any argument to show the help.
#
# Needs a `conf.sh` file that exports the following environment
# variables:
# 
# HOST
#     used in the subject of the mail report
#
# LOG_FILE_DIR
#     directory where the logs will be written
#
# GPG_KEY
#     GPG key to be used
#
# PASSPHRASE
#     passphrase of the key
#
# AWS_ACCESS_KEY_ID
#     Amazon Web Service access key
#
# AWS_SECRET_ACCESS_KEY
#     Amazon Web Service secret access key
#
# AWS_S3_BUCKET_NAME
#     Amazon S3 bucket name
#
# MAIL_TO
#     e-mail address to sent the mail report to
#
# DIR_TO_BACKUP
#     directory to backup
#
# INCLUDES
#     a list of "--include=FOO" parameters, for example:
#       INCLUDES="--include=/home/svn/dumps \
#                 --include=/etc"
#
# EXCLUDES
#     a list of "--exclude=FOO" parameters
#

function usage {
    echo "Usage: "
    echo "       $0 backup"
    echo "or:"
    echo "       $0 list-current-files"
    echo "or:"
    echo "       $0 restore <T> <FILE-TO-RESTORE> <TARGET-FILE>"
    echo "where: "
    echo "  <T> indicates which backup to choose from, for example:"
    echo "      '1D': yesterday"
    echo "      '3D': three days ago"
    echo "  <FILE-TO-RESTORE> is relative to the directory you backed up."
    echo "     (For example, if you backed up '/' and want to restore '/etc/foo',"
    echo "     you must indicate 'etc/foo' as the relative path.)"
    echo "  <TARGET-PATH> is where the restored file will be written locally."
}

. ./conf.sh

DATE=`date +%Y-%m-%d`
LOG_FILE="$LOG_FILE_DIR/$DATE.log"
MAIL_SUBJECT="Backup report [$DATE][$HOST]"

case $1 in
    backup)
        # Delete backups older than 3 months.
        duplicity \
            remove-older-than 3M \
            --encrypt-key=$GPG_KEY \
            --sign-key=$GPG_KEY \
            --s3-use-new-style \
            s3+http://$AWS_S3_BUCKET_NAME \
            > $LOG_FILE

        # Make the backup (which will be a full backup if older than 1
        # month).
        duplicity \
            --full-if-older-than 1M \
            --encrypt-key=$GPG_KEY \
            --sign-key=$GPG_KEY \
            --s3-use-new-style \
            $INCLUDES \
            $EXCLUDES \
            $DIR_TO_BACKUP \
            s3+http://$AWS_S3_BUCKET_NAME/ \
            >> $LOG_FILE

        # Mail report.
        mail -s "$MAIL_SUBJECT" $MAIL_TO < $LOG_FILE
        ;;
    list-current-files)
	duplicity \
	    list-current-files \
            --s3-use-new-style \
	    s3+http://$AWS_S3_BUCKET_NAME/
	;;
    restore)
        if [ $# -ne 4 ]
	then
	    echo "Wrong syntax."
	    usage
	    exit 1
	fi
        duplicity \
            -t $2 \
	    --file-to-restore $3 \
            --s3-use-new-style \
            -v8 \
            s3+http://$AWS_S3_BUCKET_NAME/ \
	    $4 && \
	    echo "File has been restored at '$4'"
        ;;
    *)
        usage
        exit 1
        ;;
esac


export GPG_KEY=
export PASSPHRASE=
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_S3_BUCKET_NAME=