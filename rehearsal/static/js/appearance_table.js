// 以下のクラスの style が定義されていること
// .top_left_cell
// .header_cell
// .scn_name_cell
// .scn_btn
// .data_cell

// 以下のデータを View から受け取ること
var scenes;     // シーン名の配列
var chrs;       // 登場人物名の配列
var chr_apprs;  // シーンごとの、登場人物ごとのセリフ数
var cast;       // 役者名の配列
var cast_apprs; // シーンごとの、役者ごとのセリフ数

// フィルタやソートのための変数
var scn_keyword;
var by_cast;
var selected_scn;
var chr_order;
var cast_order;

// 定数 (色)
var scn_btn_color = "aliceblue";
var scn_btn_color_selected = "lightcyan";
var cell_color = "Transparent";
var cell_color_appr = "aliceblue";
var cell_color_selected = "lightcyan";

// 初期化
function init(){
    scn_pattern = ".*";
    by_cast = false;
    selected_scn = -1;
    chr_order = Array.from(chrs, (_, n) => {return n});
    cast_order = Array.from(cast, (_, n) => {return n});
    
    document.getElementById("scn_keyword").value = "";
    document.getElementById("by_cast").checked = false;
}

// 入力されたキーワードから正規表現パターンを得る
function make_pattern(scn_keyword){
    
    // 入力から先頭と末尾の空白を除去
    scn_keyword = scn_keyword.trim();
    
    // キーワードがなければすべてのシーンにマッチ
    if (!scn_keyword)
        return ".*";
    
    // 空白文字で分割
    var keywords = scn_keyword.split(/\s+/);
    
    // パターン生成
    var scn_pattern = "^";
    keywords.forEach(keyword => {
        var pattern = keyword.replace(/[\\^$.*+?()[\]{}|]/g, '\\$&');
        if (pattern.length > 1 && pattern.slice(0, 1) == "-")
            // "-" がついていれば、そのワードを含まないシーンに限る
            scn_pattern += "(?!.*" + pattern.slice(1) + ")";
        else
            // "-" がついていなければ、そのワードを含むシーンに限る
            scn_pattern += "(?=.*" + pattern + ")";
    });
    
    return scn_pattern;
}

// 選択されたシーンによって列のソート順を生成する
function sort_columns(){
    // シーンが選択されていなければ、順番を初期化
    if (selected_scn < 0 || selected_scn >= scenes.length){
        chr_order = Array.from(chrs, (_, n) => {return n});
        cast_order = Array.from(cast, (_, n) => {return n});
        return;
    }
    
    // 登場人物のソート順を生成
    chr_order = [];
    // 順番の配列を元々の順番で初期化
    var order_work = Array.from(chrs, (_, n) => {return n});
    // セリフ数を元々の順番で初期化
    var apprs_work = Array.from(chr_apprs[selected_scn]);
    // 空になるまで最大値のインデックスを取得していく
    while (apprs_work.length){
        // セリフ数のワーク配列の最大値のインデックスを取得
        var idx = apprs_work.indexOf(Math.max.apply(null,apprs_work));
        // 順番のワーク配列のその位置にある「順番」を追加
        chr_order.push(order_work[idx]);
        // 追加した「順番」の位置にある要素をワーク配列から削除
        order_work.splice(idx, 1);
        apprs_work.splice(idx, 1);
    }

    // 役者のソート順を生成
    cast_order = [];
    // 順番の配列を元々の順番で初期化
    order_work = Array.from(cast, (_, n) => {return n});
    // セリフ数を元々の順番で初期化
    apprs_work = Array.from(cast_apprs[selected_scn]);
    // 空になるまで最大値のインデックスを取得していく
    while (apprs_work.length){
        // セリフ数のワーク配列の最大値のインデックスを取得
        var idx = apprs_work.indexOf(Math.max.apply(null,apprs_work));
        // 順番のワーク配列のその位置にある「順番」を追加
        cast_order.push(order_work[idx]);
        // 追加した「順番」の位置にある要素をワーク配列から削除
        order_work.splice(idx, 1);
        apprs_work.splice(idx, 1);
    }
}

// 条件をグローバル変数にセット
function set_condition(){
    // シーンのフィルタパターン
    var scn_keyword = document.getElementById("scn_keyword").value;
    scn_pattern = make_pattern(scn_keyword);
    
    // 役者を表示するか役を表示するか
    by_cast = document.getElementById("by_cast").checked;
    
    // 選択されたシーンによって列のソート順を生成する
    sort_columns();
}

// シーンを選択した時に呼ばれる関数
function select_scene(scn_idx){
    selected_scn = scn_idx;
    draw();
}

// テーブルを現在の条件で描画
function draw(){
    // 条件をグローバル変数にセット
    set_condition();
    
    // thead
    var thead = "<tr><th class=\"top_left_cell\"></th>";
    
    // 役者か役名か
    var names = by_cast ? cast : chrs;
    var name_order = by_cast ? cast_order : chr_order;
    
    // ヘッダの名前をソート順に表示
    name_order.forEach(idx => {
        thead += "<th class=\"header_cell\">" + names[idx] + "</th>";
    });
    thead += "</tr>";

    document.getElementById("t_header").innerHTML = thead;

    // tbody
    var tbody = "";
    
    // 役者か役名か
    var scn_apprs = by_cast ? cast_apprs : chr_apprs;
    var appr_order = by_cast ? cast_order : chr_order;
    
    scenes.forEach((scene, scn_idx) => {
        // パターンにマッチするシーン名だけを追加
        if (scene.match(new RegExp(scn_pattern))){
            // シーン名（ボタン）生成
            var color = scn_idx == selected_scn ? scn_btn_color_selected : scn_btn_color;
            var scn_btn = "<button class=\"scn_btn\" style=\"background-color:"
                + color + ";\" onclick=\"select_scene("
                + scn_idx + ");\">" + scene + "</button>";
            
            // シーン名のセル
            tbody += "<tr><th class=\"scn_name_cell\" style=\"background-color:"
                + color + ";\">" + scn_btn + "</th>";
            
            appearance = scn_apprs[scn_idx];
            // セリフ数のセルをソート順に表示
            appr_order.forEach(appr_idx => {
                // セルの色 (-1 なら出番なし)
                color = appearance[appr_idx] < 0
                    ? cell_color
                    : scn_idx == selected_scn
                        ? cell_color_selected
                        : cell_color_appr;
                // 出番がなければ空白、あれば整数に丸める
                text = appearance[appr_idx] < 0
                    ? ""
                    : Math.round(appearance[appr_idx]);
                
                tbody += "<td class=\"data_cell\" style=\"background-color:"
                    + color + ";\">" + text + "</td>";
            });
        }
        tbody += "</tr>";
    });

    document.getElementById("t_data").innerHTML = tbody;
}
