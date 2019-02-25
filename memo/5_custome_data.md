O Modify the Schema and Index Films Data

Y
まず2つのノードをたちあげる

```
./bin/solr start -c -p 8983 -s example/cloud/node1/solr
./bin/solr start -c -p 7574 -s example/cloud/node2/solr -z localhost:9983
```
-c でsolrcloud
-p でHTTPリクエストをうけつけるポート番号を指定
-s でsolrのホームディレクトリを指定
-z zookeeper(冗長構成を維持するためのサーバー) のホストとポート


filmsというcollectionをshard2つとレプリカ2つで作る
```
solr@dev:/opt/solr$ ./bin/solr create -c films -s 2 -rf 2
WARNING: Using _default configset with data driven schema functionality. NOT RECOMMENDED for production use.
         To turn off: bin/solr config -c films -p 7574 -action set-user-property -property update.autoCreateFields -value false
INFO  - 2019-01-17 11:40:59.233; org.apache.solr.util.configuration.SSLCredentialProviderFactory; Processing SSL Credential Provider chain: env;sysprop
Created collection 'films' with 2 shard(s), 2 replica(s) with config-set 'films'
solr@dev:/opt/solr$
```

W
ドキュメントp23にあったが、solrにはインデクスするデータが渡されたときにfieldの定義がなければ、field guessingというインデックスされるフィールドの定義を推測する機能によって自動でデータタイプを定義したスキーマを作成する。ただし、この機能で完全なスキーマはできないので、自前で修正は必要。またこのときconfigsetは_defaultという名前のものになる。というわけで
```
WARNING: Using _default configset with data driven schema functionality. NOT RECOMMENDED for production use.
```
という警告がでている。
また、field guessingはbrute force(総当たり)で処理をするのと、誤りがあってインデックス後に修正作業が必要となる。大量のデータを扱うプロダクション環境では使うべきではないとのこと。

そもそもconfig setってなんだ？ってなったので_defaultの中身を探す。
それらしきものは
/opt/solr-7.6.0/server/solr/configsets/_default
にあった。schema定義などがある。がschemaの読み方はまだわからないので、詳細は飛ばす。
```
solr@dev:/opt/solr$ less /opt/solr-7.6.0/server/solr/configsets/_default/conf/
lang/           managed-schema  params.json     protwords.txt   solrconfig.xml  stopwords.txt   synonyms.txt
```
T
configsetをデータにあわせてつくる。

Y
p24によるとやるべきことは２つ
* configSetのmanaged schemaをSolr のSchema APIで修正する（直接ファイル編集は非推奨のよう)
* solrconfig.xmlで設定されているfield guessingによって決まったschema定義を修正する
まずはドキュメントにあるように用意されている、filmsのデータの定義を作って、その次にwikipediaのデータのschema定義を作ってみよう。

まずnameフィールドを作る
定義はドキュメントにある通りで
```
solr@dev:/opt/solr$ curl -X POST -H 'Content-type:application/json' --data-binary '{"add-field": {"name":"name",
  "type":"text_general", "multiValued":false, "stored":true}}' http://localhost:8983/solr/films/schema
{
  "responseHeader":{
    "status":0,
    "QTime":1994}}
solr@dev:/opt/solr$
```
これは管理コンソールのコアのschemaからでもできるらしい。

その他のフィールドは他のコピーでよいので、以下のようなAPIをコールする。
```
solr@dev:/opt/solr$ curl -X POST -H 'Content-type:application/json' --data-binary '{"add-copy-field" :
>   {"source":"*","dest":"_text_"}}' http://localhost:8983/solr/films/schema
{
  "responseHeader":{
    "status":0,
    "QTime":1700}}
solr@dev:/opt/solr$
```

T
Index Sample Film Data
Faceting

Y
Filmのfieldを作る
まずname fieldをtext fieldとして定義するために以下のAPIをたたく
※この設定はtext_general型となって複数の値を持てない(multiValued false)、stored(クエリによる検索で返る)となる
```
curl -X POST -H 'Content-type:application/json' --data-binary '{"add-field": {"name":"name",  "type":"text_general", "multiValued":false, "stored":true}}' http://localhost:8983/solr/films/schema
```
これもコンソールで設定可能。

次に全データを検索できるようにする。
```
curl -X POST -H 'Content-type:application/json' --data-binary '{"add-copy-field" :
  {"source":"*","dest":"_text_"}}' http://localhost:8983/solr/films/schema
```
※全部検索できるようにしてしまうと、indexing処理も遅くなるし、indexデータは大きくなる。プロダクション環境では必要な文だけ_text_にする

Y
Index用のサンプルデータはexample/filmにあるので、それをsolrにいれる
JSON, XML, csv各データ形式でスクリプトの実行方法は違う。

せっかくなので３通り試して処理時間に違いがあるかみてみる
。
JSONで入れてみる
```
solr@dev:/opt/solr$ time bin/post -c films example/films/films.json
java -classpath /opt/solr/dist/solr-core-7.6.0.jar -Dauto=yes -Dc=films -Ddata=files org.apache.solr.util.SimplePostTool example/films/films.json
SimplePostTool version 5.0.0
Posting files to [base] url http://localhost:8983/solr/films/update...
Entering auto mode. File endings considered are xml,json,jsonl,csv,pdf,doc,docx,ppt,pptx,xls,xlsx,odt,odp,ods,ott,otp,ots,rtf,htm,html,txt,log
POSTing file films.json (application/json) to [base]/json/docs
1 files indexed.
COMMITting Solr index changes to http://localhost:8983/solr/films/update...
Time spent: 0:00:03.642

real    0m3.871s
user    0m0.345s
sys     0m0.069s
```
3.871s

```
http://localhost:8983/solr/films/select?q=*:*
```
検索したらデータが入っている
1100件

データを入れ直すために一度消す
```
bin/solr delete -c films
```
http://localhost:8983/solr/films/select?q=*:*
で404になる。collectionごと消えた・・・。データだけ消したかったんだが。

Y
というわけで最初からやり直す。
nodeをつくる
```
./bin/solr start -c -p 8983 -s example/cloud/node1/solr
./bin/solr start -c -p 7574 -s example/cloud/node2/solr -z localhost:9983
```

W
```
solr@dev:/opt/solr$ ./bin/solr start -c -p 8983 -s example/cloud/node1/solr
*** [WARN] *** Your open file limit is currently 1024.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
*** [WARN] ***  Your Max Processes Limit is currently 7898.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh

Port 8983 is already being used by another process (pid: 2360)
Please choose a different port using the -p option.

solr@dev:/opt/solr$ ./bin/solr start -c -p 7574 -s example/cloud/node2/solr -z localhost:9983
*** [WARN] *** Your open file limit is currently 1024.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
*** [WARN] ***  Your Max Processes Limit is currently 7898.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh

Port 7574 is already being used by another process (pid: 2566)
Please choose a different port using the -p option.

solr@dev:/opt/solr$
```
すでにポートはあると言われている。つまりcollectionは消されてもnodeは消えない。
よく考えるとあたりまえか、collection消したらノードごと全部消えたら困る。

次、filmsというcollectionをshard2つとレプリカ2つで作る
```
solr@dev:/opt/solr$ ./bin/solr create -c films -s 2 -rf 2
WARNING: Using _default configset with data driven schema functionality. NOT RECOMMENDED for production use.
         To turn off: bin/solr config -c films -p 7574 -action set-user-property -property update.autoCreateFields -value false
INFO  - 2019-01-20 22:41:03.490; org.apache.solr.util.configuration.SSLCredentialProviderFactory; Processing SSL Credential Provider chain: env;sysprop
Created collection 'films' with 2 shard(s), 2 replica(s) with config-set 'films'
solr@dev:/opt/solr$
```
OK


name フィールドを作る
```
solr@dev:/opt/solr$ curl -X POST -H 'Content-type:application/json' --data-binary '{"add-field": {"name":"name",
>   "type":"text_general", "multiValued":false, "stored":true}}' http://localhost:8983/solr/films/schema
{
  "responseHeader":{
    "status":0,
    "QTime":131}}
solr@dev:/opt/solr$
```
他のフィールドの定義も作る
```
solr@dev:/opt/solr$ curl -X POST -H 'Content-type:application/json' --data-binary '{"add-copy-field" :{"source":"*","dest":"_text_"}}' http://localhost:8983/solr/films/schema
{
  "responseHeader":{
    "status":0,
    "QTime":50}}
solr@dev:/opt/solr$
```

フィールドはもとに戻せた。
xmlで入れてみる
```
solr@dev:/opt/solr$ time bin/post -c films example/films/films.xmljava -classpath /opt/solr/dist/solr-core-7.6.0.jar -Dauto=yes -Dc=films -Ddata=files org.apache.solr.util.SimplePostTool example/films/films.xml
SimplePostTool version 5.0.0
Posting files to [base] url http://localhost:8983/solr/films/update...
Entering auto mode. File endings considered are xml,json,jsonl,csv,pdf,doc,docx,ppt,pptx,xls,xlsx,odt,odp,ods,ott,otp,ots,rtf,htm,html,txt,log
POSTing file films.xml (application/xml) to [base]
1 files indexed.
COMMITting Solr index changes to http://localhost:8983/solr/films/update...
Time spent: 0:00:00.886

real    0m1.104s
user    0m0.359s
sys     0m0.059s
solr@dev:/opt/solr$
```

W
1.1sとJSONより早い？？

よくみたらコマンド実行結果にかかった時間が書いてあった。
JSON→Time spent: 0:00:03.642
XML→Time spent: 0:00:00.886

ただこれでみてもXMLのほうが早いんだな。

T
Faceting

Y
そもそもFacetingってなんだ？
ドキュメント(Apache Solr Reference Guide 7.6)を参照した
```
Faceting allows the search results to be arranged into subsets (or buckets, or categories), providing a count for each subset. There are several types of faceting: field values, numeric and date ranges, pivots (decision tree), and arbitrary query faceting.
```

W
Facetingとはsolrの機能の1つ。
検索結果をsubset(バケットやカテゴリなどの部分集合)にすること。
ファセットの種類はいろいろあって、fieldの値、数値や日付での範囲と任意のクエリでのファセットがある。

*Field Facet*
フィールドによっては複数の値が入っているものがある。全ての値の中で各値がいくつあるのかをField Facetによって調べられる。

サンプル
```
curl "http://localhost:8983/solr/films/select?q=*:*&rows=0&facet=true&facet.field=genre_str"
```
q=*:*ですべてのドキュメントが対象になる
rowsでレスポンスで返るドキュメントの数を指定する。今回は0。
facet=trueファセットを使うことを指定。
facet.field=genre_str で調べたいフィールドを指定。

```
MacBook-Pro-2:solr7 vaivailx$ curl "http://localhost:8983/solr/films/select?q=*:*&rows=0&facet=true&facet.field=genre_str"
{
  "responseHeader":{
    "status":0,
    "QTime":5,
    "params":{
      "q":"*:*",
      "facet.field":"genre_str",
      "rows":"0",
      "facet":"true"}},
  "response":{"numFound":1100,"start":0,"docs":[]
  },
  "facet_counts":{
    "facet_queries":{},
    "facet_fields":{
      "genre_str":[
        "Drama",552,
        "Comedy",389,
        "Romance Film",270,
        "Thriller",259,
        "Action Film",196,
        "Crime Fiction",170,
        "World cinema",167,
・・・
```

検索条件でfacet.mincount=200など200以上じゃないとレスポンスを返さないと絞ることもできる

*Range Facet*
数値や日付といった区間があるものであれば区間ごとの集合を取得できる。
ただし、これは管理コンソールでは確認できない。
以下は1年ごとで区切ったもの。(%2B1YEARはデコードすると+1)
```
curl 'http://localhost:8983/solr/films/select?q=*:*&rows=0'\
      '&facet=true'\
      '&facet.range=initial_release_date'\
      '&facet.range.start=NOW-20YEAR'\
      '&facet.range.end=NOW'\
      '&facet.range.gap=%2B1YEAR'
```

```
vagrant@dev:~$ curl 'http://localhost:8983/solr/films/select?q=*:*&rows=0&facet=true&facet.range=initial_release_date&facet.range.start=NOW-20YEAR&facet.range.end=NOW&facet.range.gap=%2B1YEAR'
{
  "responseHeader":{
    "status":0,
    "QTime":51,
    "params":{
      "facet.range":"initial_release_date",
      "q":"*:*",
      "facet.range.gap":"+1YEAR",
      "rows":"0",
      "facet":"true",
      "facet.range.start":"NOW-20YEAR",
      "facet.range.end":"NOW"}},
  "response":{"numFound":1100,"start":0,"docs":[]
  },
  "facet_counts":{
    "facet_queries":{},
    "facet_fields":{},
    "facet_ranges":{
      "initial_release_date":{
        "counts":[
          "1999-01-23T08:54:44.322Z",3,
          "2000-01-23T08:54:44.322Z",85,
          "2001-01-23T08:54:44.322Z",94,
          "2002-01-23T08:54:44.322Z",114,
          "2003-01-23T08:54:44.322Z",125,
          "2004-01-23T08:54:44.322Z",165,
          "2005-01-23T08:54:44.322Z",173,
          "2006-01-23T08:54:44.322Z",164,
          "2007-01-23T08:54:44.322Z",42,
          "2008-01-23T08:54:44.322Z",10,
          "2009-01-23T08:54:44.322Z",5,
          "2010-01-23T08:54:44.322Z",1,
          "2011-01-23T08:54:44.322Z",0,
          "2012-01-23T08:54:44.322Z",0,
          "2013-01-23T08:54:44.322Z",2,
          "2014-01-23T08:54:44.322Z",0,
          "2015-01-23T08:54:44.322Z",1,
          "2016-01-23T08:54:44.322Z",0,
          "2017-01-23T08:54:44.322Z",0,
          "2018-01-23T08:54:44.322Z",0],
        "gap":"+1YEAR",
        "start":"1999-01-23T08:54:44.322Z",
        "end":"2019-01-23T08:54:44.322Z"}},
    "facet_intervals":{},
    "facet_heatmaps":{}}}
```

*pivot facet*
decision treeとしても知られるファセット。
2つ以上のフィールドを組み合わせることができるものらしい。
せつめいだけだとよくわからないので実行してみた。


以下を実行した。
```
vagrant@dev:~$ curl "http://localhost:8983/solr/films/select?q=*:*&rows=0&facet=on&facet.pivot=genre_str,directed_by_str" 
```

```
    "facet_pivot":{
      "genre_str,directed_by_str":[{
          "field":"genre_str",
          "value":"Drama",
          "count":552,
          "pivot":[{
              "field":"directed_by_str",
              "value":"Ridley Scott",
              "count":5},
            {
              "field":"directed_by_str",
              "value":"Steven Soderbergh",
              "count":5},
            {
              "field":"directed_by_str",
              "value":"Michael Winterbottom",
              "count":4},
            {
              "field":"directed_by_str",
              "value":"Vikram Bhatt",
              "count":4},
```

genre_strのサブセットの中でさらにdirected_by_strのサブセットができあがっている。
サブセットの入れ子を作ることがわかった。

ここまででいろんな検索方法があるとわかった。

次は P34にあるとおり、自分でindexしてみる

Y
Exercise 3: Index Your Own Data
Create Your Own Collection
wikipediaのdocなのでwikipediaDocと名付けてシャード2つレプリカ2つで作る


W
```
solr@dev:/opt/solr$ ./bin/solr create -c wikipediaDocs -s 2 -rf 2
WARNING: Using _default configset with data driven schema functionality. NOT RECOMMENDED for production use.
         To turn off: bin/solr config -c wikipediaDocs -p 8983 -action set-user-property -property update.autoCreateFields -value false
INFO  - 2019-01-24 22:35:34.867; org.apache.solr.util.configuration.SSLCredentialProviderFactory; Processing SSL Credential Provider chain: env;sysprop

Created new core 'wikipediaDocs'
solr@dev:/opt/solr$
```

ガイドに

> Again, as we saw from Exercise 2 above, this will use the _default configSet and all the schemaless features it provides. As we noted previously, this may cause problems when we index our data. You may need to iterate on indexing a few times before you get the schema right.
あるとおりWARNINGがでているが、schemaは少しずつあとでなおしていく


T
Indexing Ideas

Y
データのインデックス方法はたくさんあるらしいので読んだ

W

* SOLR_HOMEのbin/postでいれる
** 入れるデータはローカルにある必要がある
** JSON, XML, CSVの他にHTML,PDF, MS Officeのファイル, プレーンテキストを扱える
** field guessssing でエラーが出るので試行錯誤する必要あり
* DataImportHandlerで入れる
** dbに接続して取得する
** example/example-DIH の README.txtに使い方がある
* Solrjを使う：javaベースのsolrへのクライアント。JVMベースのプログラミング言語用のもの。プログラマティックSolrを操作したいときに使う
* Solr clients を使う：プログラマティックにSolrを操作したいときに使う
* Documents Screen：管理画面経由で入れる

Y
Updating Dataを読んだ

W
numDocsは、インデックス内の検索可能なドキュメントの数を表す
maxDoc値には、インデックスからまだ物理的に削除されていない論理的に削除された文書がmaxDocカウントに含まれる。そのため、numDocよりも大きくなる場合がある。

T
詳細なデータのアップロード方法を探す

Y
p333 Uploading Data with Index Handlers
p336 にcurlでhttp api叩いてデータアップロード方法があるので、それをやってみる。


まずxmlを解凍する
```
bzip -dkv -jxvf jawiki-20181220-pages-articles.xml.bz2
```

solr用にxmlを加工する。
今回はpageを1ドキュメントとして扱うのでpageタグをdocタグに
```
cat jawiki-20181220-pages-articles.xml |  sed -e 's/<page>/<doc>/g' | sed -e 's/<\/page>/<\/doc>/g' > jawiki-pages_docs.xml
```
xmlの冒頭と最終行はいらないので削除して不要なインデントを消す
```
vagrant@dev:/vagrant$ sed -i -e '1,38d' jawiki-pages_docs.xml
vagrant@dev:/vagrant$ sed -i -e '$d' jawiki@-pages_docs.xml
vagrant@dev:/vagrant$ cut -c 2- jawiki@-pages_docs.xml > jawiki@-pages_docs.xml
```

solrにcurlで入れる
```
vagrant@dev:/vagrant$ curl http://localhost:8983/solr/wikipediaDocs/update -H "Content-Type: text/xml" -d@jawiki-pages_docs_formatted.xml
<?xml version="1.0" encoding="UTF-8"?>
<response>

<lst name="responseHeader">
  <int name="status">400</int>
  <int name="QTime">6</int>
</lst>
<lst name="error">
  <lst name="metadata">
    <str name="error-class">org.apache.solr.common.SolrException</str>
    <str name="root-error-class">org.apache.solr.common.SolrException</str>
  </lst>
  <str name="msg">Unexpected &lt;doc&gt; tag without an &lt;add&gt; tag surrounding it.</str>
  <int name="code">400</int>
</lst>
</response>
vagrant@dev:/vagrant$
```

調べたら入れるドキュメントのフォーマットがぜんぜん違う。
変換する。

変換して送信した

```
vagrant@dev:/vagrant$ curl http://localhost:8983/solr/wikipediaDocs/update -H "Content-Type: text/xml" -d@parsed.xml
<?xml version="1.0" encoding="UTF-8"?>
<response>

<lst name="responseHeader">
  <int name="status">500</int>
  <int name="QTime">1</int>
</lst>
<lst name="error">
  <str name="trace">java.lang.NullPointerException
       at org.apache.solr.update.processor.FieldMutatingUpdateProcessor.processAdd(FieldMutatingUpdateProcessor.java:110)
 ```

うまくいかない。
FieldかんれんでNPE?
field定義はしていないが、field guessにしているので初回は適当にしてくれるはず。

T
fieldの定義を確認する

Y
確認した
schemaは何もなし
```
http://localhost:8983/solr/#/wikipediaDocs/schema
```

管理コンソールでふと目に入ったdataimport
```
http://localhost:8983/solr/#/wikipediaDocs/dataimport/undefined
```
```
The solrconfig.xml file for this index does not have an operational DataImportHandler defined!
```
と表示されている。
一度設定をみてみよう

opt/solrにあるかと思ったら違って探し回ったら/var/solrにあった
```
solr@dev:/opt/solr$ ls /var/solr/data/wikipediaDocs/conf/solrconfig.xml
/var/solr/data/wikipediaDocs/conf/solrconfig.xml
solr@dev:/opt/solr$
```
どうもデフォルトでは追加したものは/var/solrに追加されるよう

中身を見てみる
```
       These require that the schema is both managed and mutable, by
       declaring schemaFactory as ManagedIndexSchemaFactory, with
       mutable specified as true.

       See http://wiki.apache.org/solr/GuessingFieldTypes
```
どこで勘違いしたのか、デフォルトでschema guessになっていないみたい。
リンク先を見てみると、起動時にshemalessにするか、手動で設定する必要があるとのこと。

手動で設定する方法があったので、これをやってみる。
https://lucene.apache.org/solr/guide/7_6/schemaless-mode.html#enable-managed-schema



Y
変更を加えた

```
solr@dev:/var/solr/data/wikipediaDocs/conf$ diff solrconfig.xml solrconfig.xml.org 
782c782
<   <!--  <initParams path="/update/**,/query,/select,/tvrh,/elevate,/spell,/browse">
---
>   <initParams path="/update/**,/query,/select,/tvrh,/elevate,/spell,/browse">
787,793d786
< -->
<   <!-- Set the Default UpdateRequestProcessorChain -->
<   <initParams path="/update/**">
<     <lst name="defaults">
<       <str name="update.chain">add-unknown-fields-to-the-schema</str>
<     </lst>
<   </initParams>
1138,1143d1130
< 
<   <schemaFactory class="ManagedIndexSchemaFactory">
<     <bool name="mutable">true</bool>
<     <str name="managedSchemaResourceName">managed-schema</str>
<   </schemaFactory>
< 
solr@dev:/var/solr/data/wikipediaDocs/conf$ 
```
