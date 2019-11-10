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

// テーブルを描画
function draw(){
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
            // 出席者が演じるキャラのリスト
            var atnd_chrs = [];
            scn['chr_idxs'].forEach((chr_idx) => {
                if (slot['attendee'].indexOf(chrs[chr_idx]['actr_idx']) >= 0)
                    atnd_chrs.push(chrs[chr_idx]);
            });
            
            // スロットの高さ
            var height = height_for_time(slot['from_time'], slot['to_time']);
            // スロットの色
            var atnd_rate = atnd_chrs.length / scn['chr_idxs'].length;
            var r = 240 - (atnd_rate * 8) ** 2 - atnd_rate * 64;
            var g = 240;
            var b = r;
            var color = `rgb(${r}, ${g}, ${b})`;
            
            time_slots += `<div style=\"position:absolute; top:${offset}px; left:0; width:100%; height:${height}px; `
                + `background-color:${color}; border:solid 1px #eee;\">`;
            time_slots += slot['from_time'] + "-" + slot['to_time'] + "<br>";
            time_slots += atnd_chrs.length + "/" + scn['chr_idxs'].length;
            time_slots += "</div>\n";
            offset += height;
        });
        
        tbody += `<td class=\"data_cell\" style=\"position:relative; height:${offset}px;\">`
            + time_slots + "</td>";
    });
    tbody += "</tr>";
    document.getElementById("t_data").innerHTML = tbody;
}
