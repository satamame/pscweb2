// 以下のクラスの style が定義されていること
// .top_left_cell
// .header_cell
// .name_cell
// .data_cell

// 以下のデータを View から受け取ること
var rhsls;      // 稽古のコマのデータの配列
var actrs;      // 役者の配列
var actr_atnds; // 役者ごとの出欠の、稽古の配列に対応する配列

// フィルタのための変数
var name_keyword;   // 名前フィルタ用キーワード
var by_chrs;        // 役者名でなく役名で表示

// 定数 (色)
var name_cell_color = "aliceblue";
var cell_color = "Transparent";
var allday_color = "mintcream";
var absent_color = "snow";

// 初期化
function init(){
}

// 条件をグローバル変数にセット
function set_condition(){
}

// テーブルを現在の条件で描画
function draw(){
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
    actrs.forEach((actr, actr_idx) => {
        
        // 役者名のセル
        tbody += "<tr><th class=\"name_cell\" style=\"background-color:"
            + name_cell_color + ";\">" + actr['short_name'] + "</th>";
        
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
