# O Solrにサンプルデータを入れる。基本的な検索についてしっておく。

Y
p15にあるとおり、サンプルデータをpostスクリプトで入れる
```
solr@dev:/opt/solr-7.6.0$ ./bin/post -c techproducts example/exampledocs/*
java -classpath /opt/solr-7.6.0/dist/solr-core-7.6.0.jar -Dauto=yes -Dc=techproducts -Ddata=files org.apache.solr.util.SimplePostTool example/exampledocs/books.csv example/exampledocs/books.json example/exampledocs/gb18030-example.xml example/exampledocs/hd.xml example/exampledocs/ipod_other.xml example/exampledocs/ipod_video.xml example/exampledocs/manufacturers.xml example/exampledocs/mem.xml example/exampledocs/money.xml example/exampledocs/monitor.xml example/exampledocs/monitor2.xml example/exampledocs/more_books.jsonl example/exampledocs/mp500.xml example/exampledocs/post.jar example/exampledocs/sample.html example/exampledocs/sd500.xml example/exampledocs/solr-word.pdf example/exampledocs/solr.xml example/exampledocs/test_utf8.sh example/exampledocs/utf8-example.xml example/exampledocs/vidcard.xml
SimplePostTool version 5.0.0
Posting files to [base] url http://localhost:8983/solr/techproducts/update...
Entering auto mode. File endings considered are xml,json,jsonl,csv,pdf,doc,docx,ppt,pptx,xls,xlsx,odt,odp,ods,ott,otp,ots,rtf,htm,html,txt,log
POSTing file books.csv (text/csv) to [base]
POSTing file books.json (application/json) to [base]/json/docs
POSTing file gb18030-example.xml (application/xml) to [base]
POSTing file hd.xml (application/xml) to [base]
POSTing file ipod_other.xml (application/xml) to [base]
POSTing file ipod_video.xml (application/xml) to [base]
POSTing file manufacturers.xml (application/xml) to [base]
POSTing file mem.xml (application/xml) to [base]
POSTing file money.xml (application/xml) to [base]
POSTing file monitor.xml (application/xml) to [base]
POSTing file monitor2.xml (application/xml) to [base]
POSTing file more_books.jsonl (application/json) to [base]/json/docs
POSTing file mp500.xml (application/xml) to [base]
POSTing file post.jar (application/octet-stream) to [base]/extract
POSTing file sample.html (text/html) to [base]/extract
POSTing file sd500.xml (application/xml) to [base]
POSTing file solr-word.pdf (application/pdf) to [base]/extract
POSTing file solr.xml (application/xml) to [base]
POSTing file test_utf8.sh (application/octet-stream) to [base]/extract
POSTing file utf8-example.xml (application/xml) to [base]
POSTing file vidcard.xml (application/xml) to [base]
21 files indexed.
COMMITting Solr index changes to http://localhost:8983/solr/techproducts/update...
Time spent: 0:00:04.906
solr@dev:/opt/solr-7.6.0$
```

W
http://localhost:8983/solr/#/techproducts/query
で検索したらデータがかえるようになった。

curl "http://localhost:8983/solr/techproducts/select?indent=on&q=*:*"
でも検索したらデータがかえるようになった。

T
基本的な検索方法をしっておく

Y
```
curl "http://localhost:8983/solr/techproducts/select?indent=on&q=*:*"
```

```
curl "http://localhost:8983/solr/techproducts/select?q=foundation"
```

W
```
curl "http://localhost:8983/solr/techproducts/select?indent=on&q=*:*"
```
→全データ取得。ただし、デフォルトで１０件しかとれないようになっていないので１０件しかとれない
```
curl "http://localhost:8983/solr/techproducts/select?q=foundation"
```
→foundationとパラメータにふくまれるもののみかえる
"name":"Foundation",
"manu":"Apache Software Foundation",とか４件
DBと違って、フィールドが違っても、横断的に検索できている

Y
レスポンスのしぼりこみ
```
curl "http://localhost:8983/solr/techproducts/select?q=foundation&fl=id"
```

W
→レスポンスのドキュメントはidしか含まれないものだけになる

Y
フィールドで絞り込んで検索

W
フィールド絞り込みなし
curl "http://localhost:8983/solr/techproducts/select?q=electronics"

フィールド絞り込みあり
curl "http://localhost:8983/solr/techproducts/select?q=cat:electronics"

Y
フレーズ検索

W
フレーズ検索ではダブルクォートを使う
```
vagrant@dev:~$ curl "http://localhost:8983/solr/techproducts/select?q=\"CAS+latency\""
```
※curlでリクエストを送るときはダブルクォートをエスケープする

Y
AND検索

W
AND検索では必ず含めたいキーワードに+をつける。例：+electronics +music
URLで+つけるときはエンコードするのが必須。

AND検索で特定のキーワードを除きたいときは-をつける
curl "http://localhost:8983/solr/techproducts/select?q=%2Belectronics+-music"


Y
solrをとめるときは
bin/solr stop -all

```
solr@dev:/opt/solr$ bin/solr stop -all
Sending stop command to Solr running on port 7573 ... waiting up to 180 seconds to allow Jetty process 11832 to stop gracefully.
Sending stop command to Solr running on port 8983 ... waiting up to 180 seconds to allow Jetty process 11657 to stop gracefully.
solr@dev:/opt/solr$
```

# ここまでのまとめ

* postスクリプトでデータを入れられる
* 検索はcurlでも管理コンソールでもできるけど、curlのときはURLエンコードすることを忘れずに
* * レスポンスのしぼりこみ→flを指定
* * フィールドで絞り込んで検索→指定フィールド:hogeとqに指定
* * フレーズ検索するときは"でくくる(curlのときは要エスケープ)
* * AND検索のときは+をつける(curlのときは要エンコード)
* * 除外検索のときは-をつける
