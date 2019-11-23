// 以下のクラスの style が定義されていること
// .header_cell
// .data_cell

// 以下のデータを View から受け取ること
var rhsl;               // 稽古のリスト

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

// テーブルを描画
function draw(){
    // モードを取得
    mode = document.getElementById("mode_menu").value;
    
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
        
        // ヘッダを出欠グラフへのリンクにする
        link = `<a href=\"/rhsl/atnd_graph/${rhsl['id']}/\">` + dateStr + "<br>"
            + rhsl['place'] + "<br>" + rhsl['start_time'] + "-" + rhsl['end_time'];
        thead += `<th class=\"header_cell\">${link}</th>`;
    });
    
    thead += "</tr>";
    
    document.getElementById("t_header").innerHTML = thead;
    
    // tbody
    // var tbody = "<tr>";
    // scns.forEach((scn, scn_idx) => {
        
    //     var time_slots = "";
    //     var offset = 0;
    //     scns_time_slots[scn_idx].forEach((slot, slot_idx) => {
    //         // 出席者が演じるキャラのリストと合計セリフ数
    //         var atnd_chrs = [];
    //         var atnd_lines_num = 0;
    //         scn['chr_idxs'].forEach((chr_idx, chr_idx_idx) => {
    //             if (slot['attendee'].indexOf(chrs[chr_idx]['actr_idx']) >= 0){
    //                 atnd_chrs.push(chrs[chr_idx]);
    //                 atnd_lines_num += scn['lines_nums'][chr_idx_idx];
    //             }
    //         });
            
    //         // スロットの高さ
    //         var height = height_for_time(slot['from_time'], slot['to_time']);
            
    //         // 出席率
    //         var atnd_num;
    //         var total_num;
    //         switch (mode){
    //             // 登場人物の数を指標とする場合
    //             case "by_chrs":
    //                 atnd_num = atnd_chrs.length;
    //                 total_num = scn['chr_idxs'].length;
    //                 break;
    //             // 役者の数を指標とする場合
    //             case "by_actrs":
    //                 atnd_num = slot['attendee'].length;
    //                 total_num = scn_actr_idxs(scn_idx).length;
    //                 break;
    //             // セリフの数を指標とする場合
    //             case "by_lines":
    //                 atnd_num = atnd_lines_num;
    //                 total_num = scn['lines_nums'].reduce((a,x) => a += x, 0);
    //                 break;
    //         }
    //         var atnd_rate = 0;
    //         if (total_num > 0)
    //             atnd_rate = atnd_num / total_num;
            
    //         // スロットの色
    //         var color = color_for_rate(atnd_rate);
            
    //         // 内容
    //         time_slots += `<div style=\"position:absolute; top:${offset}px; left:0; width:100%; height:${height}px; `
    //             + `background-color:${color}; border:solid 1px #eee;\">`;
    //         time_slots += slot['from_time'] + "-" + slot['to_time'] + "<br>";
    //         time_slots += `<a href=\"javascript:void(0)\" onclick=\"show_info(${scn_idx}, ${slot_idx})\">`;
    //         time_slots += `${atnd_num}/${total_num}</a>`;
    //         time_slots += "</div>\n";
            
    //         offset += height;
    //     });
        
    //     tbody += `<td class=\"data_cell\" style=\"position:relative; height:${offset}px;\">`
    //         + time_slots + "</td>";
    // });
    // tbody += "</tr>";
    // document.getElementById("t_data").innerHTML = tbody;
}
