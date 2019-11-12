// 以下のクラスの style が定義されていること
// .header_cell
// .data_cell

// 以下のデータを View から受け取ること
var scns;               // シーンのリスト
var scns_time_slots;    // シーンごとの時間スロット
var actrs;              // 役者のリスト
var chrs;               // 登場人物のリスト

// 定数 (寸法)
var px_per_hour = 60;

// "HH:MM" を分に変換
function str_to_min(time_str){
    var strs = time_str.split(":", 2);
    return parseInt(strs[0], 10) * 60 + parseInt(strs[1], 10);
}

// 時間を寸法に変換
function height_for_time(from, to){
    from_min = str_to_min(from);
    to_min = str_to_min(to);
    return (to_min - from_min) / 60 * px_per_hour;
}

// 出席率を色に変換
function color_for_rate(rate){
    var r = 240 - (rate * 8) ** 2 - rate * 64;
    var g = 240;
    var b = r;
    return `rgb(${r}, ${g}, ${b})`;
}

// 初期化
function init(){
    document.getElementById("mode_menu").selectedIndex = 0;
    mode = document.getElementById("mode_menu").value;
}

// シーンに出る役者のインデックスリスト
function scn_actr_idxs(scn_idx){
    var actr_idxs = [];
    // そのシーンに出ている各登場人物について
    scns[scn_idx]['chr_idxs'].forEach((chr_idx) => {
        var chr = chrs[chr_idx];
        // 役者のインデックスを取得
        var actr_idx = chr['actr_idx'];
        if (actr_idx >= 0 && actr_idxs.indexOf(actr_idx) < 0)
            actr_idxs.push(actr_idx);
    });
    return actr_idxs;
}

// テーブルを描画
function draw(){
    // モードを取得
    mode = document.getElementById("mode_menu").value;
    
    // thead
    var thead = "<tr>";
    scns.forEach((scn) => {
        // 各シーンの名前
        thead += `<th class=\"header_cell\">${scn['name']}</th>`;
    });
    thead += "</tr>";
    document.getElementById("t_header").innerHTML = thead;
    
    // tbody
    var tbody = "<tr>";
    scns.forEach((scn, scn_idx) => {
        
        var time_slots = "";
        var offset = 0;
        scns_time_slots[scn_idx].forEach((slot) => {
            // 出席者が演じるキャラのリストと合計セリフ数
            var atnd_chrs = [];
            var atnd_lines_num = 0;
            scn['chr_idxs'].forEach((chr_idx, chr_idx_idx) => {
                if (slot['attendee'].indexOf(chrs[chr_idx]['actr_idx']) >= 0){
                    atnd_chrs.push(chrs[chr_idx]);
                    atnd_lines_num += scn['lines_nums'][chr_idx_idx];
                }
            });
            
            // スロットの高さ
            var height = height_for_time(slot['from_time'], slot['to_time']);
            
            // 出席率
            var atnd_num;
            var total_num;
            switch (mode){
                // 登場人物の数を指標とする場合
                case "by_chrs":
                    atnd_num = atnd_chrs.length;
                    total_num = scn['chr_idxs'].length;
                    break;
                // 役者の数を指標とする場合
                case "by_actrs":
                    atnd_num = slot['attendee'].length;
                    total_num = scn_actr_idxs(scn_idx).length;
                    break;
                // セリフの数を指標とする場合
                case "by_lines":
                    atnd_num = atnd_lines_num;
                    total_num = scn['lines_nums'].reduce((a,x) => a += x, 0);
                    break;
            }
            var atnd_rate = 0;
            if (total_num > 0)
                atnd_rate = atnd_num / total_num;
            
            // スロットの色
            var color = color_for_rate(atnd_rate);
            
            time_slots += `<div style=\"position:absolute; top:${offset}px; left:0; width:100%; height:${height}px; `
                + `background-color:${color}; border:solid 1px #eee;\">`;
            time_slots += slot['from_time'] + "-" + slot['to_time'] + "<br>";
            time_slots += atnd_num + "/" + total_num;
            time_slots += "</div>\n";
            offset += height;
        });
        
        tbody += `<td class=\"data_cell\" style=\"position:relative; height:${offset}px;\">`
            + time_slots + "</td>";
    });
    tbody += "</tr>";
    document.getElementById("t_data").innerHTML = tbody;
}
