FROM neo4j:latest

ENV NEO4J_PLUGINS="[\"apoc\"]"


EXPOSE 7474 7473 7687
COPY ./zscaler.crt /usr/local/share/ca-certificates/zscaler.crt
USER neo4j:neo4j
WORKDIR /var/lib/neo4j
ENTRYPOINT [ "tini", "-g", "--", "/startup/docker-entrypoint.sh" ]
CMD ["neo4j"]
