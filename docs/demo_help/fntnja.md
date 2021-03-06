## [pscweb2](../index.md) > [Help](index.md)

# Fountain JA

PSCWEB2 で使う台本のフォーマット `Fountain JA` の説明です。
元になっているフォーマットは [Fountain](https://fountain.io/) です。
Fountain は英語で書くことが前提となっていて、日本語を考慮した書き方を便宜的に `Fountain JA` と呼んでいます。

日本語で書く場合の詳しい考察については下記のリンクを御覧ください。

- [Fountain for Japanese](https://satamame.github.io/pscn/fountain/for_japanese.html)

## 記法

ここでは PSCWEB2 で使っている `Fountain JA` の記法について、各要素の例を紹介します。
この記法で書いたサンプルが [こちら](https://github.com/satamame/pscn/blob/master/docs/fountain/example.fountain) にあります。

### 題名と著者名

```
Title: アンダーコントロール
Author: 沙汰青豆
```

- `Title:` の後に題名、`Author:` の後に著者名を書きます。

### 登場人物のブロック

```
# 登場人物

捨村: 保存容器会社の社員
京野: 保存容器会社の社員
荻島: 捨村たちの先輩
```

- `# 登場人物` という行がブロックの開始を示します。
- 空行までがブロックになります (開始直後の空行を除く)。
- 台本から公演を作成する際に、このブロックは無視されます (いずれ使うようになるかも知れません)。

### 柱

```
# 第一幕
## シーン1
### 研究室
```

- `#` で始まる行が柱となります。
- 台本から公演を作成する際に、シーンのはじまりとして認識されます。
- 柱は階層化できます。

### セリフ

```
@京野
置く場所ねえぞこれ。
```

- 空行に続けて、人物名の行とセリフの行を書きます。
- `@` で始まる行が人物名となります。
- その次の行から空行までがセリフの行となります。

### ト書き

```
舞台中央やや奥めにデスク。左右から座れるようになっている。
```

- パターン定義されていない書き方の行は、ト書きになります。

### エンドマーク

```
> おわり
```

- `>` ではじまる行がエンドマークとなります。
- 本家の Fountain ではこの書き方は [Transition](https://fountain.io/syntax#section-trans) として扱われ、右寄せになります。
