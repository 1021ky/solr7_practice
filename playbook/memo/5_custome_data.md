O Modify the Schema and Index Films Data

Y
まず2つのノードをたちあげる

```
./bin/solr start -c -p 8983 -s example/cloud/node1/solr
./bin/solr start -c -p 7574 -s example/cloud/node2/solr -z localhost:9983
```

filmsというshard2つの
```
solr@dev:/opt/solr$ bin/solr create -c films -s 2 -rf 2
WARNING: Using _default configset with data driven schema functionality. NOT RECOMMENDED for production use.
         To turn off: bin/solr config -c films -p 7574 -action set-user-property -property update.autoCreateFields -value false
INFO  - 2019-01-15 09:38:12.606; org.apache.solr.util.configuration.SSLCredentialProviderFactory; Processing SSL Credential Provider chain: env;sysprop
Created collection 'films' with 2 shard(s), 2 replica(s) with config-set 'films'
solr@dev:/opt/solr$
```
bin/solr create -c films -s 2 -rf 2