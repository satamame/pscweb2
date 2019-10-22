// 以下のクラスの style が定義されていること
// .top_left_cell
// .header_cell
// .name_cell
// .data_cell

// 以下のデータを View から受け取ること
var rhsls;              // 稽古のコマのデータの配列
var actrs;              // 役者の配列
var actr_atnds;         // 役者ごとの出欠の、稽古の配列に対応する配列
var chrs;               // 登場人物のリスト
var scenes;             // シーン名のリスト
var scenes_chr_apprs    // シーンごとの登場人物とセリフ数のリスト

// フィルタやソートのためのグローバル変数
var by_chrs;        // 役者でなく役で表示
var selected_scn;   // 選択されたシーンのインデックス
var cast_order;     // シーンが選択された場合の役者の表示順

// 定数 (色)
var name_cell_color = "aliceblue";
var cell_color = "Transparent";
var allday_color = "mintcream";
var absent_color = "snow";

// シーンメニューの初期化
function init_scene_menu(){
    var options = "<option value=\"-1\">---------</option>";
    scenes.forEach((scene, scn_idx) => {
        options += "<option value=\"" + scn_idx.toString() + "\">"
            + scene + "</option>"
    });
    document.getElementById("scene_menu").innerHTML = options;
}

// 初期化
function init(){
    by_chrs = false;
    selected_scn = -1;
    
    // https://qiita.com/butchi_y/items/771a5bd56b03530363ec
    cast_order = Array.from(actrs, (_, n) => {return n});
    
    document.getElementById("scene_menu").selectedIndex = 0;
}

// 条件をグローバル変数にセット
function set_condition(){
    selected_scn = document.getElementById("scene_menu").value;
    cast_order = actr_index_list_in_scene(selected_scn);
}

// シーンのインデックスから、出ている役者のインデックス・リストを得る
function actr_index_list_in_scene(scn_idx){
    // シーンが選択されていなければ、順番を初期化して返す
    if (selected_scn < 0 || selected_scn >= scenes.length)
        return Array.from(actrs, (_, n) => {return n});
    
    // 出ている登場人物のインデックスとセリフ数のリスト
    var chr_apprs = scenes_chr_apprs[scn_idx];
    
    var actr_idxs = [];
    var lines_nums = [];
    chr_apprs.forEach((apprs) => {
        // そのインデックスの登場人物の、配役のインデックス
        var cast_idx = chrs[apprs['chr_idx']]['cast_idx'];
        // actr_idxs にあればセリフ数を加算、なければ新規追加
        var idx = actr_idxs.indexOf(cast_idx);
        if (idx >= 0)
            lines_nums[idx] += apprs['lines_num'];
        // cast_idx が -1 の場合、配役未定なので追加しない
        else if (cast_idx >= 0) {
            actr_idxs.push(cast_idx);
            lines_nums.push(apprs['lines_num']);
        }
    });
    
    // セリフ数順にソートする
    var cast_order = [];
    // 空になるまで最大値のインデックスを取得していく
    while (lines_nums.length){
        // セリフ数のワーク配列の最大値のインデックスを取得
        var idx = lines_nums.indexOf(Math.max.apply(null,lines_nums));
        // 順番のワーク配列のその位置にある「順番」を追加
        cast_order.push(actr_idxs[idx]);
        // 追加した「順番」の位置にある要素をワーク配列から削除
        actr_idxs.splice(idx, 1);
        lines_nums.splice(idx, 1);
    }
    
    return cast_order;
}

// テーブルを現在の条件で描画
function draw(){
    // 条件をグローバル変数にセット
    set_condition();
    
    // thead
    var thead = "<tr><th class=\"top_left_cell\"></th>";
    
    rhsls.forEach((rhsl, rhsl_idx) => {
        // 日付を整形
        var d = new Date(rhsl['date']);
        var dateStr = `
            ${(d.getMonth()+1).toString().padStart(2, '0')}/
            ${d.getDate().toString().padStart(2, '0')}(
            ${dowChars.charAt(d.getDay())})
        `.replace(/[\n\r]+\s*/g, '');
        
        thead += "<th class=\"header_cell\">" + dateStr + "<br>" + rhsl['place']
        + "<br>" + rhsl['start_time'] + "-" + rhsl['end_time'] + "</th>";
    });
    
    thead += "</tr>";
    
    document.getElementById("t_header").innerHTML = thead;
    
    // tbody
    var tbody = "";
    cast_order.forEach((actr_idx) => {
        actr = actrs[actr_idx];
        
        // 役者名のセル
        tbody += "<tr><td class=\"name_cell\" style=\"background-color:"
            + name_cell_color + ";\">" + actr['short_name'] + "</td>";
        
        // 出欠データ
        actr_atnds[actr_idx].forEach((rhsl_atnds) => {
            var atnd_data = "";
            rhsl_atnds.forEach((slot, slot_idx) => {
                if (slot_idx > 0)
                atnd_data += "<br>";
                atnd_data += slot == "*" ? "◯"
                    : slot == "-" ? "✕"
                    : slot;
            });
            
            var color = atnd_data == "◯" ? allday_color
                : atnd_data == "✕" ? absent_color
                : cell_color;
            
            tbody += "<td class=\"data_cell\" style=\"background-color:"
                + color + ";\">" + atnd_data + "</td>";
        });
        
        tbody += "</tr>";
    });
    
    document.getElementById("t_data").innerHTML = tbody;
}
