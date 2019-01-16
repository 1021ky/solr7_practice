O solr cloudを試す

Y
```
solr@dev:/opt/solr-7.6.0$ ./bin/solr start -e cloud
*** [WARN] *** Your open file limit is currently 1024.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
*** [WARN] ***  Your Max Processes Limit is currently 7898.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
INFO  - 2019-01-08 06:41:01.637; org.apache.solr.util.configuration.SSLCredentialProviderFactory; Processing SSL Credential Provider chain: env;sysprop

Welcome to the SolrCloud example!

This interactive session will help you launch a SolrCloud cluster on your local workstation.
To begin, how many Solr nodes would you like to run in your local cluster? (specify 1-4 nodes) [2]:
2
Ok, let's start up 2 Solr nodes for your example SolrCloud cluster.
Please enter the port for node1 [8983]:

Please enter the port for node2 [7574]:

Creating Solr home directory /opt/solr-7.6.0/example/cloud/node1/solr
Cloning /opt/solr-7.6.0/example/cloud/node1 into
   /opt/solr-7.6.0/example/cloud/node2

Starting up Solr on port 8983 using command:
"bin/solr" start -cloud -p 8983 -s "example/cloud/node1/solr"

*** [WARN] ***  Your Max Processes Limit is currently 7898.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
Waiting up to 180 seconds to see Solr running on port 8983 [|]
Started Solr server on port 8983 (pid=6977). Happy searching!


Starting up Solr on port 7574 using command:
"bin/solr" start -cloud -p 7574 -s "example/cloud/node2/solr" -z localhost:9983

*** [WARN] ***  Your Max Processes Limit is currently 7898.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
Waiting up to 180 seconds to see Solr running on port 7574 [/]
Started Solr server on port 7574 (pid=7148). Happy searching!

INFO  - 2019-01-08 06:41:29.758; org.apache.solr.common.cloud.ConnectionManager; zkClient has connected
INFO  - 2019-01-08 06:41:29.814; org.apache.solr.common.cloud.ZkStateReader; Updated live nodes fromZooKeeper... (0) -> (2)
INFO  - 2019-01-08 06:41:29.863; org.apache.solr.client.solrj.impl.ZkClientClusterStateProvider; Cluster at localhost:9983 ready

Now let's create a new collection for indexing documents in your 2-node cluster.
Please provide a name for your new collection: [gettingstarted]
techproducts
How many shards would you like to split techproducts into? [2]
2
How many replicas per shard would you like to create? [2]
2
Please choose a configuration for the techproducts collection, available options are:
_default or sample_techproducts_configs [_default]
sample_techproducts_configs
Created collection 'techproducts' with 2 shard(s), 2 replica(s) with config-set 'techproducts'

Enabling auto soft-commits with maxTime 3 secs using the Config API

POSTing request to Config API: http://localhost:8983/solr/techproducts/config
{"set-property":{"updateHandler.autoSoftCommit.maxTime":"3000"}}
Successfully set-property updateHandler.autoSoftCommit.maxTime to 3000


SolrCloud example running, please visit: http://localhost:8983/solr

solr@dev:/opt/solr-7.6.0$
```

W
コンソールでcloud設定できていることを確認できた
用語
Collection：一つ以上のドキュメント群。single nodeのインストール(Solr Cloudではないインストール)ではコアにあたる。
shard：Solr Cloudで単一のCollectionをlogical partition(論理的なパーティションで分割)したもの。どのshardもReplicaを1つ以上含む。
Replica：Solr Cloudでコアとして動くもの。shardの物理的なコピー
Node：Solrを実行しているJVMインスタンス

T
serviceとしてsolrをインストールする

ここまでのまとめ
Solr Cloudは起動時に設定する。
コンソールでcloud設定できていることを確認できる。
Solr Cloudはportをわければ、1台のホストでもこうちくできる。

