# Exit on Error
set -e

#mkdir -p /usr/share/elasticsearch/config/credentials/keystore/elasticsearch.keystore
#mkdir -p /usr/share/elasticsearch/credentials
# mkdir -p /usr/share/elasticsearch/config/credentials/service_tokens

GENERATED_KEYSTORE=/usr/share/elasticsearch/config/elasticsearch.keystore
OUTPUT_KEYSTORE=/secrets/keystore/elasticsearch.keystore

GENERATED_SERVICE_TOKENS=/usr/share/elasticsearch/config/service_tokens
OUTPUT_SERVICE_TOKENS=/secrets/service_tokens
OUTPUT_KIBANA_TOKEN=/secrets/.env.kibana.token


# GENERATED_KEYSTORE=/usr/share/elasticsearch/config/elasticsearch.keystore
# #OUTPUT_KEYSTORE=/usr/share/elasticsearch/credentials/keystore/elasticsearch.keystore
# #OUTPUT_KEYSTORE=/usr/share/elasticsearch/credentials/keystore

# GENERATED_SERVICE_TOKENS=/usr/share/elasticsearch/config/service_tokens
# #OUTPUT_SERVICE_TOKENS=/usr/share/elasticsearch/credentials/service_tokens
# #OUTPUT_SERVICE_TOKENS=/usr/share/elasticsearch/credentials

# #OUTPUT_KIBANA_TOKEN=/usr/share/elasticsearch/credentials/.env.kibana.token
# OUTPUT_KIBANA_TOKEN=/usr/share/elasticsearch/config/.env.kibana.token


# Password Generate
# PW=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 16 ;)
# ELASTIC_PASSWORD="${ELASTIC_PASSWORD:-$PW}"
PW="$ELASTIC_PASSWORD" # "banana"
export ELASTIC_PASSWORD


# Create Keystore, it will be stored in elasticsearch.keystore file
printf "========== Creating Elasticsearch Keystore ==========\n"
printf "=====================================================\n"
elasticsearch-keystore create >> /dev/null


# Setting Bootstrap Password
echo "Setting bootstrap.password..."
echo "$ELASTIC_PASSWORD" | elasticsearch-keystore add -x 'bootstrap.password'
echo "Elastic Bootstrap Password is: $ELASTIC_PASSWORD"

#not sure why setup above didnt set psswrd, so reset will be called
#echo "$ELASTIC_PASSWORD" | elasticsearch-reset-password -u elastic -i


# Generating Kibana Token
echo "Generating Kibana Service Token..."

# Delete old token if exists
/usr/share/elasticsearch/bin/elasticsearch-service-tokens delete elastic/kibana default &> /dev/null || true

# Generate new token
TOKEN=$(/usr/share/elasticsearch/bin/elasticsearch-service-tokens create elastic/kibana default | cut -d '=' -f2 | tr -d ' ')
echo "Kibana Service Token is: $TOKEN"
echo "KIBANA_SERVICE_ACCOUNT_TOKEN=$TOKEN" > $OUTPUT_KIBANA_TOKEN

#Replace current Keystore
if [ -f "$OUTPUT_KEYSTORE" ]; then
    echo "Remove old elasticsearch.keystore"
    rm $OUTPUT_KEYSTORE
fi

echo "Saving new elasticsearch.keystore"
mkdir -p "$(dirname $OUTPUT_KEYSTORE)"
mv $GENERATED_KEYSTORE $OUTPUT_KEYSTORE
#cp $GENERATED_KEYSTORE $OUTPUT_KEYSTORE
chmod 0644 $OUTPUT_KEYSTORE

# Replace current Service Tokens File
if [ -f "$OUTPUT_SERVICE_TOKENS" ]; then
    echo "Remove old service_tokens file"
    rm $OUTPUT_SERVICE_TOKENS
fi

echo "Saving new service_tokens file"
mv $GENERATED_SERVICE_TOKENS $OUTPUT_SERVICE_TOKENS
#cp $GENERATED_SERVICE_TOKENS $OUTPUT_SERVICE_TOKENS
chmod 0644 $OUTPUT_SERVICE_TOKENS

printf "======= Keystore setup completed successfully =======\n"
printf "=====================================================\n"
printf "Remember to restart the stack, or reload secure settings if changed settings are hot-reloadable.\n"
printf "About Reloading Settings: https://www.elastic.co/guide/en/elasticsearch/reference/current/secure-settings.html#reloadable-secure-settings\n"
printf "=====================================================\n"
printf "Your 'elastic' user password is: $ELASTIC_PASSWORD\n"
printf "Your Kibana Service Token is: $TOKEN\n"
printf "=====================================================\n"


sh /scripts/gen-cert.sh