#!/bin/bash

#
# Creates the Athena database
#

#
# Environment variables to be set in the CodeBuild project
#
# $ATHENA_DB    		Name of the Athena database
# $ATHENA_BUCKET		Name of the S3 bucket where the data is stored
# $ATHENA_BUCKET_REGION		Region for the S3 bucket where the data is stored
# $ATHENA_DB_DESCRIPTION	Description for the Athena database
#

echo "Starting build-db.sh"
echo '$ATHENA_DB' "= $ATHENA_DB"
echo '$ATHENA_BUCKET' "= $ATHENA_BUCKET"
echo '$ATHENA_BUCKET_REGION' "= $ATHENA_BUCKET_REGION"
echo '$ATHENA_DB_DESCRIPTION' "= $ATHENA_DB_DESCRIPTION"
echo

# Create JOB_DETAILS database
echo "Creating Athena database $ATHENA_DB"
aws glue create-database --database-input "Name=$ATHENA_DB,Description=$ATHENA_DB_DESCRIPTION" >/dev/null

# Create JOB_DETAILS ba_dl table in Athena
echo "Creating ba_dl table..."
aws athena start-query-execution \
    --query-string "create external table ba_dl (dl_id INT, dl_name STRING, description STRING, template_id INT, refesh_date TIMESTAMP, start_date TIMESTAMP, end_date TIMESTAMP, status STRING, notes STRING, attribute1 STRING,attribute2 STRING,attribute3 STRING,attribute4 STRING,attribute5 STRING,attribute6 STRING,attribute7 INT,attribute8 INT,attribute9 INT, created_by STRING, created_date TIMESTAMP, last_updated_by STRING, last_updated_date TIMESTAMP, sla_time TIMESTAMP) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '$ATHENA_BUCKET/ba_dl';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create JOB_DETAILS ba_dl_baseline table in Athena
echo "Creating ba_dl_baseline table..."
aws athena start-query-execution \
    --query-string "create external table ba_dl_baseline (baseline_id INT, object_name STRING, description STRING, baseline_min INT, category STRING, subcategory STRING, notes STRING, attribute1 STRING,attribute2 STRING,attribute3 STRING,attribute4 STRING,attribute5 STRING,attribute6 STRING,attribute7 INT,attribute8 INT,attribute9 INT,created_by STRING, created_date STRING, last_updated_by STRING, last_updated_date STRING,parent_baseline_id INT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '$ATHENA_BUCKET/ba_dl_baseline';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create JOB_DETAILS ba_dl_details table in Athena
echo "Creating ba_dl_details table..."
aws athena start-query-execution \
    --query-string "create external table ba_dl_details (dl_detail_id INT, dl_id INT, sequence_num INT, baseline_id INT,start_time STRING, end_time STRING, issue_count INT, time_lost_mins INT, notes STRING, attribute1 STRING,attribute2 STRING,attribute3 STRING,attribute4 STRING,attribute5 STRING,attribute6 STRING,attribute7 INT,attribute8 INT,attribute9 INT,created_by STRING, created_date STRING, last_updated_by STRING, last_updated_date STRING, template_id INT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '$ATHENA_BUCKET/ba_dl_details';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null


# Create JOB_DETAILS date table in Athena
echo "Creating date_dim table..."
aws athena start-query-execution \
    --query-string "create external table date_dim (date_id INT, cal_date DATE, day STRING, week STRING, month STRING, quarter STRING, year INT, holiday BOOLEAN) ROW FORMAT DELIMITED FIELDS TERMINATED BY '|' LOCATION '$ATHENA_BUCKET/date';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null

# Create JOB_DETAILS ba_dashboard_master_details table in Athena
echo "Creating ba_dashboard_master_details table..."
aws athena start-query-execution \
    --query-string "create external table ba_dashboard_master_details (date_id INT, sequence_name STRING, sequence_num INT, master_sequencer_id INT, job_sequencer_id INT, baseline_id INT, template_id INT, template_name STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' LOCATION '$ATHENA_BUCKET/ba_dashboard_master_details';" \
    --query-execution-context "Database=$ATHENA_DB" \
    --result-configuration "OutputLocation=$ATHENA_BUCKET/output/" \
    >/dev/null
