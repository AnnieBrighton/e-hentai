# e-hentai ダウンローダー

## 環境
  MAC(おそらくLinux環境でも動くかと)
  Python 2.7

## 使い方
### 単一指定

     ./ehentai.py 'http://g.e-hentai.org/g/974526/d23a209be0/'

正常にダウンロードできた場合、カレントディレクトリにzipファイルを作成

     (C90) [魔太郎 (魔太郎)] レムのエッチな悩みを解決してくださいっ (Reゼロから始める異世界生活).zip

### 複数指定

ダウンロードしたいリストファイルを作成

sample.txt

    http://g.e-hentai.org/g/972366/fd27efe48b/
    http://g.e-hentai.org/g/959278/e05ac56d5a/

ダウンロード実行

    ./getEhentai.sh sample.txt
