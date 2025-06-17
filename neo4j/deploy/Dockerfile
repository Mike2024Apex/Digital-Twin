FROM neo4j:latest

# TODO: follow guide for production deployment of apoc
#        @ https://neo4j.com/labs/apoc/4.0/installation/#docker
ENV NEO4J_PLUGINS="[\"apoc\"]"
ENV NEO4J_AUTH="neo4j/atlas#12345"

WORKDIR /var/lib/neo4j

RUN <<EOF
	chmod 640 ./conf/* &&
	chown -R neo4j:neo4j . &&
	chown -R neo4j:neo4j /data
EOF

USER neo4j

COPY --chown=neo4j:neo4j ./neo4j/import/neo4j.dump ./backup/neo4j.dump

RUN neo4j-admin database load --from-path=./backup \
		--expand-commands --overwrite-destination=true --verbose neo4j

EXPOSE 7474 7473 7687

ENTRYPOINT [ "tini", "-g", "--", "/startup/docker-entrypoint.sh" ]
CMD ["neo4j"]
