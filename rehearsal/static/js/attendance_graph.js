// 以下のクラスの style が定義されていること
// .header_cell
// .data_cell

// 以下のデータを View から受け取ること
var scns;               // シーンのリスト
var scns_time_slots;    // シーンごとの時間スロット
var actrs;              // 役者のリスト
var chrs;               // 登場人物のリスト
var date;               // 日付 (スロット情報表示用)

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
        scns_time_slots[scn_idx].forEach((slot, slot_idx) => {
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
            
            // 内容
            time_slots += `<div style=\"position:absolute; top:${offset}px; left:0; width:100%; height:${height}px; `
                + `background-color:${color}; border:solid 1px #eee;\">`;
            time_slots += slot['from_time'] + "-" + slot['to_time'] + "<br>";
            time_slots += `<a href=\"javascript:void(0)\" onclick=\"show_info(${scn_idx}, ${slot_idx})\">`;
            time_slots += `${atnd_num}/${total_num}</a>`;
            time_slots += "</div>\n";
            
            offset += height;
        });
        
        tbody += `<td class=\"data_cell\" style=\"position:relative; height:${offset}px;\">`
            + time_slots + "</td>";
    });
    tbody += "</tr>";
    document.getElementById("t_data").innerHTML = tbody;
}

// 時間スロットの情報を表示
function show_info(scn_idx, slot_idx){
    // 表示するシーンと時間スロット
    var scn = scns[scn_idx];
    var slot = scns_time_slots[scn_idx][slot_idx];
    
    // 日付と時間帯とシーン名
    var content = "<h2 id=\"dt_scn\" style=\"float:left;\">";
    content += `${date} ${slot['from_time']}-${slot['to_time']}<br>${scn['name']}</h2>\n`;
    
    // 閉じるボタン
    content += "<div style=\"text-align:right; padding:16px 0 0\"><a href=\"javascript:void(0)\" ";
    content += "onclick=\"hide_info();\">✕</a></div>\n"
    
    // いる役者といない役者のリストを作る
    var attendee = [];
    var absentee = [];
    scn_actr_idxs(scn_idx).forEach((actr_idx) => {
        // リストの要素1を役者名にする
        var actr = [actrs[actr_idx]['name']];
        // リストの要素2を登場人物名とセリフ数のリストにする
        var chrs_info = [];
        scn['chr_idxs'].forEach((chr_idx, chr_idx_idx) => {
            if (chrs[chr_idx]['actr_idx'] == actr_idx){
                chrs_info.push(chrs[chr_idx]['name'] + ` (${scn['lines_nums'][chr_idx_idx]})`);
            }
        });
        actr.push(chrs_info);
        
        if (slot['attendee'].indexOf(actr_idx) >= 0)
            attendee.push(actr);
        else
            absentee.push(actr);
    });
    
    // いる役者
    content += "<h3 style=\"clear:left;\">いる役者</h3>\n<table>\n";
    attendee.forEach((actr) => {
        var left_cell = actr[0];
        actr[1].forEach((chrs_info) => {
            content += `<tr><td>${left_cell}</td><td>${chrs_info}</td></tr>\n`;
            left_cell = "";
        });
    });
    content += "</table>\n"

    // いない役者
    content += "<h3>いない役者</h3>\n<table>\n";
    absentee.forEach((actr) => {
        var left_cell = actr[0];
        actr[1].forEach((chrs_info) => {
            content += `<tr><td>${left_cell}</td><td>${chrs_info}</td></tr>\n`;
            left_cell = "";
        });
    });
    content += "</table>\n"
    
    content += "<input type=\"button\" onclick=\"copy_dt_scn();\" ";
    content += "style=\"margin:16px\" value=\"日時とシーン名をコピー\">";
    
    document.getElementById("slot_info_content").innerHTML = content;
    document.getElementById("slot_info_panel").style.display = "block";
}

function hide_info(){
    console.log("hide_info called.");
    var slot_info_panel = document.getElementById("slot_info_panel");
    slot_info_panel.style.display = "none";
}

function copy_dt_scn(){
    // パネルの h2 に表示している日時とシーン名を取得
    var str = document.getElementById("dt_scn").innerHTML.replace("<br>", "\n");
    
    var listener = function(e){
        e.clipboardData.setData("text/plain" , str);    
        // 本来のイベントをキャンセル
        e.preventDefault();
        // リスナーを削除
        document.removeEventListener("copy", listener);
    }
    // コピーイベントが発生したときに、クリップボードに書き込むようにしておく
    document.addEventListener("copy" , listener);
    // コピーイベントを起こす
    document.execCommand("copy");
}
